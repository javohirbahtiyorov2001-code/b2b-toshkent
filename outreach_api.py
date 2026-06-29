#!/usr/bin/env python3
"""
Outreach API — port 5057
Handles Telegram personal account connection via Telethon + mass sending.

Endpoints:
  GET  /status          → auth status
  POST /connect         → {api_id, api_hash, phone} → send OTP
  POST /verify          → {code, password?}         → complete auth
  POST /disconnect      → logout + delete session
  POST /send            → {lead_slugs, template}     → start campaign
  GET  /campaign        → SSE stream of send progress
  GET  /leads           → list of real leads
"""
import json, os, sys, asyncio, threading, time, re, uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

BASE = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(BASE, ".tg_session")
CREDS_FILE   = os.path.join(BASE, ".tg_creds.json")

LEAD_FILES = [
    os.path.join(BASE, "pipeline", "dental_clinic_leads.json"),
    os.path.join(BASE, "pipeline", "new_leads_100.json"),
    os.path.join(BASE, "pipeline", "seed_leads.json"),
]
FAKE_SOURCES = {"auto-generated", "none", ""}

# Global state
state = {
    "status": "disconnected",   # disconnected | awaiting_code | awaiting_2fa | connected
    "me": None,                 # {name, username, phone}
    "campaign": None,           # {id, total, sent, failed, log, running}
    "client": None,
    "phone_code_hash": None,
    "folder_id": None,          # Telegram dialog filter id for "SmartDev Leads"
}
loop = asyncio.new_event_loop()

# ── Helpers ───────────────────────────────────────────────────────────────────
def load_leads():
    leads = []
    for f in LEAD_FILES:
        if os.path.exists(f):
            try: leads.extend(json.load(open(f)))
            except: pass
    return sorted(
        [l for l in leads if (l.get("source") or "") not in FAKE_SOURCES],
        key=lambda l: (l.get("niche",""), l.get("name",""))
    )

def load_creds():
    if os.path.exists(CREDS_FILE):
        return json.load(open(CREDS_FILE))
    return {}

def save_creds(d):
    json.dump(d, open(CREDS_FILE, "w"))

def clean_phone(p):
    digits = re.sub(r"\D", "", p)
    return "+" + digits if not digits.startswith("+") else digits

def run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, loop).result(timeout=30)

def fill_template(template, lead):
    name    = lead.get("name", "")
    niche   = lead.get("niche", "")
    phone   = lead.get("phone", "")
    address = lead.get("address", "")
    return (template
        .replace("{name}", name)
        .replace("{niche}", niche)
        .replace("{phone}", phone)
        .replace("{address}", address)
    )

# ── Telethon async ops ────────────────────────────────────────────────────────
async def _connect(api_id, api_hash, phone):
    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError

    client = TelegramClient(SESSION_FILE, int(api_id), api_hash, loop=loop)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        state["client"] = client
        state["status"] = "connected"
        state["me"] = {"name": me.first_name, "username": me.username, "phone": me.phone}
        try:
            await _ensure_folder(client)
        except Exception:
            pass
        return {"ok": True, "already_auth": True}

    result = await client.send_code_request(phone)
    state["client"] = client
    state["phone_code_hash"] = result.phone_code_hash
    state["status"] = "awaiting_code"
    state["_phone"] = phone
    return {"ok": True, "already_auth": False}

async def _ensure_folder(client):
    """Create 'SmartDev Leads' folder if it doesn't exist. Return its filter id."""
    from telethon.tl.functions.messages import GetDialogFiltersRequest, UpdateDialogFilterRequest
    from telethon.tl.types import DialogFilter

    FOLDER_NAME = "SmartDev Leads"
    result = await client(GetDialogFiltersRequest())
    for f in result:
        if hasattr(f, "title") and f.title == FOLDER_NAME:
            state["folder_id"] = f.id
            return f.id

    existing_ids = {f.id for f in result if hasattr(f, "id")}
    new_id = next(i for i in range(2, 256) if i not in existing_ids)
    folder = DialogFilter(
        id=new_id,
        title=FOLDER_NAME,
        pinned_peers=[],
        include_peers=[],
        exclude_peers=[],
        contacts=False,
        non_contacts=False,
        groups=False,
        broadcasts=False,
        bots=False,
        exclude_muted=False,
        exclude_read=False,
        exclude_archived=False,
    )
    await client(UpdateDialogFilterRequest(id=new_id, filter=folder))
    state["folder_id"] = new_id
    return new_id

async def _add_to_folder(client, peer):
    """Add a peer (InputPeer) to the SmartDev Leads folder."""
    from telethon.tl.functions.messages import GetDialogFiltersRequest, UpdateDialogFilterRequest
    folder_id = state.get("folder_id")
    if not folder_id:
        return
    try:
        result = await client(GetDialogFiltersRequest())
        for f in result:
            if hasattr(f, "id") and f.id == folder_id:
                if peer not in f.include_peers:
                    f.include_peers.append(peer)
                await client(UpdateDialogFilterRequest(id=folder_id, filter=f))
                break
    except Exception:
        pass

async def _verify(code, password=None):
    from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
    client = state["client"]
    phone  = state["_phone"]
    try:
        await client.sign_in(phone, code, phone_code_hash=state["phone_code_hash"])
    except SessionPasswordNeededError:
        if password:
            await client.sign_in(password=password)
        else:
            state["status"] = "awaiting_2fa"
            return {"ok": False, "need_2fa": True}
    me = await client.get_me()
    state["status"] = "connected"
    state["me"] = {"name": me.first_name, "username": me.username, "phone": me.phone}
    # Ensure folder exists right after auth
    try:
        await _ensure_folder(client)
    except Exception:
        pass
    return {"ok": True}

async def _disconnect():
    client = state["client"]
    if client:
        await client.log_out()
    if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
    if os.path.exists(CREDS_FILE):   os.remove(CREDS_FILE)
    state.update({"status": "disconnected", "client": None, "me": None})

async def _send_campaign(lead_slugs, template, delay=5):
    campaign = state["campaign"]
    client   = state["client"]
    all_leads = load_leads()
    slug_map  = {l.get("slug"): l for l in all_leads}

    for slug in lead_slugs:
        if not campaign["running"]:
            campaign["log"].append({"t": now(), "msg": "⏹ Кампания остановлена", "ok": None})
            break

        lead = slug_map.get(slug)
        if not lead:
            campaign["failed"] += 1
            campaign["log"].append({"t": now(), "msg": f"✗ {slug} — лид не найден", "ok": False})
            continue

        phone = clean_phone(lead.get("phone",""))
        name  = lead.get("name","?")
        text  = fill_template(template, lead)

        try:
            await client.send_message(phone, text)
            campaign["sent"] += 1
            campaign["log"].append({"t": now(), "msg": f"✓ {name} ({phone})", "ok": True})
            # Add to SmartDev Leads folder
            try:
                peer = await client.get_input_entity(phone)
                await _add_to_folder(client, peer)
            except Exception:
                pass
        except Exception as e:
            campaign["failed"] += 1
            err = str(e)[:80]
            campaign["log"].append({"t": now(), "msg": f"✗ {name} — {err}", "ok": False})

        await asyncio.sleep(delay)

    campaign["running"] = False
    total = campaign["sent"] + campaign["failed"]
    campaign["log"].append({
        "t": now(),
        "msg": f"✅ Готово: {campaign['sent']}/{total} отправлено",
        "ok": True
    })

def now():
    return time.strftime("%H:%M:%S")

# Start event loop in background thread
def _start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=_start_loop, daemon=True).start()

# Try to restore session on startup
def _try_restore():
    creds = load_creds()
    if not creds or not os.path.exists(SESSION_FILE + ".session"):
        return
    try:
        run_async(_connect(creds.get("api_id"), creds.get("api_hash"), creds.get("phone","")))
    except Exception:
        pass

threading.Thread(target=_try_restore, daemon=True).start()

# ── HTTP Handler ──────────────────────────────────────────────────────────────
def cors(h):
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")

def send_json(h, data, code=200):
    body = json.dumps(data).encode()
    h.send_response(code)
    cors(h)
    h.send_header("Content-Type", "application/json")
    h.send_header("Content-Length", len(body))
    h.end_headers()
    h.wfile.write(body)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_OPTIONS(self):
        self.send_response(200); cors(self); self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/status":
            send_json(self, {
                "status": state["status"],
                "me": state["me"],
                "campaign": {
                    "running": state["campaign"]["running"] if state["campaign"] else False,
                    "sent": state["campaign"]["sent"] if state["campaign"] else 0,
                    "failed": state["campaign"]["failed"] if state["campaign"] else 0,
                    "total": state["campaign"]["total"] if state["campaign"] else 0,
                } if state["campaign"] else None
            })

        elif path == "/leads":
            leads = load_leads()
            send_json(self, [
                {"id": l.get("id"), "slug": l.get("slug"), "name": l.get("name"),
                 "niche": l.get("niche"), "phone": l.get("phone"), "address": l.get("address","")}
                for l in leads
            ])

        elif path == "/campaign/log":
            # SSE stream of campaign log
            self.send_response(200)
            cors(self)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            sent_idx = 0
            try:
                while True:
                    c = state["campaign"]
                    if c:
                        logs = c["log"]
                        while sent_idx < len(logs):
                            msg = json.dumps({**logs[sent_idx], "sent": c["sent"],
                                              "failed": c["failed"], "total": c["total"],
                                              "running": c["running"]})
                            self.wfile.write(f"data: {msg}\n\n".encode())
                            self.wfile.flush()
                            sent_idx += 1
                        if not c["running"] and sent_idx >= len(logs):
                            done = json.dumps({"done": True, "sent": c["sent"],
                                               "failed": c["failed"], "total": c["total"]})
                            self.wfile.write(f"data: {done}\n\n".encode())
                            self.wfile.flush()
                            break
                    time.sleep(0.4)
            except: pass

        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if path == "/connect":
            api_id   = body.get("api_id","").strip()
            api_hash = body.get("api_hash","").strip()
            phone    = body.get("phone","").strip()
            if not all([api_id, api_hash, phone]):
                return send_json(self, {"ok": False, "error": "api_id, api_hash, phone required"}, 400)
            try:
                result = run_async(_connect(api_id, api_hash, phone))
                save_creds({"api_id": api_id, "api_hash": api_hash, "phone": phone})
                send_json(self, result)
            except Exception as e:
                send_json(self, {"ok": False, "error": str(e)}, 500)

        elif path == "/verify":
            code     = body.get("code","").strip()
            password = body.get("password","").strip() or None
            try:
                result = run_async(_verify(code, password))
                send_json(self, result)
            except Exception as e:
                send_json(self, {"ok": False, "error": str(e)}, 500)

        elif path == "/disconnect":
            try:
                run_async(_disconnect())
                send_json(self, {"ok": True})
            except Exception as e:
                send_json(self, {"ok": False, "error": str(e)}, 500)

        elif path == "/send":
            if state["status"] != "connected":
                return send_json(self, {"ok": False, "error": "Not connected"}, 400)
            slugs    = body.get("slugs", [])
            template = body.get("template","").strip()
            delay    = int(body.get("delay", 5))
            if not slugs or not template:
                return send_json(self, {"ok": False, "error": "slugs and template required"}, 400)

            state["campaign"] = {
                "id": str(uuid.uuid4())[:8], "total": len(slugs),
                "sent": 0, "failed": 0, "log": [], "running": True
            }
            state["campaign"]["log"].append({
                "t": now(), "msg": f"▶ Кампания запущена: {len(slugs)} лидов, задержка {delay}с", "ok": None
            })

            def run_campaign():
                asyncio.run_coroutine_threadsafe(
                    _send_campaign(slugs, template, delay), loop
                )

            threading.Thread(target=run_campaign, daemon=True).start()
            send_json(self, {"ok": True, "campaign_id": state["campaign"]["id"]})

        elif path == "/stop":
            if state["campaign"]:
                state["campaign"]["running"] = False
            send_json(self, {"ok": True})

        else:
            self.send_response(404); self.end_headers()

if __name__ == "__main__":
    port = 5057
    print(f"Outreach API → http://localhost:{port}")
    HTTPServer(("", port), Handler).serve_forever()
