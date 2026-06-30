#!/usr/bin/env python3
"""
Designer Agent API — port 5056
GET  /leads          → JSON list of real leads
POST /generate       → {slug, extra_prompt} → SSE stream of stdout
GET  /status/:job_id → job status
"""
import json, os, sys, subprocess, threading, uuid, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.abspath(__file__))

LEAD_FILES = [
    os.path.join(BASE, "pipeline", "dental_clinic_leads.json"),
    os.path.join(BASE, "pipeline", "new_leads_100.json"),
    os.path.join(BASE, "pipeline", "seed_leads.json"),
]
FAKE_SOURCES = {"auto-generated", "none", ""}

jobs = {}  # job_id -> {status, lines, slug}

def load_leads():
    leads = []
    for f in LEAD_FILES:
        if os.path.exists(f):
            try:
                leads.extend(json.load(open(f)))
            except Exception:
                pass
    real = [l for l in leads if (l.get("source") or "") not in FAKE_SOURCES]
    return sorted(real, key=lambda l: (l.get("niche",""), l.get("name","")))

def cors(h):
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress default logs

    def do_OPTIONS(self):
        self.send_response(200)
        cors(self)
        self.end_headers()

    def do_GET(self):
        p = urlparse(self.path)
        path = p.path

        if path == "/leads":
            leads = load_leads()
            data = [{"id": l.get("id"), "slug": l.get("slug"), "name": l.get("name"),
                     "niche": l.get("niche"), "phone": l.get("phone"), "address": l.get("address",""),
                     "colors": l.get("colors",{})} for l in leads]
            body = json.dumps(data).encode()
            self.send_response(200)
            cors(self)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        elif path.startswith("/stream/"):
            job_id = path[8:]
            job = jobs.get(job_id)
            if not job:
                self.send_response(404); self.end_headers(); return

            self.send_response(200)
            cors(self)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()

            sent = 0
            try:
                while True:
                    lines = job["lines"]
                    while sent < len(lines):
                        msg = json.dumps({"line": lines[sent], "status": job["status"]})
                        self.wfile.write(f"data: {msg}\n\n".encode())
                        self.wfile.flush()
                        sent += 1
                    if job["status"] in ("done", "error"):
                        done_msg = json.dumps({"line": None, "status": job["status"], "slug": job.get("slug","")})
                        self.wfile.write(f"data: {done_msg}\n\n".encode())
                        self.wfile.flush()
                        break
                    time.sleep(0.3)
            except Exception:
                pass

        elif path == "/sites":
            out_dir = os.path.join(BASE, "generated_sites")
            sites = []
            if os.path.exists(out_dir):
                for fn in sorted(os.listdir(out_dir)):
                    if fn.endswith(".html"):
                        sites.append(fn[:-5])
            body = json.dumps(sites).encode()
            self.send_response(200)
            cors(self)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path != "/generate":
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        slug = body.get("slug","").strip()
        extra = body.get("extra_prompt","").strip()

        if not slug:
            self.send_response(400)
            cors(self)
            self.end_headers()
            self.wfile.write(b'{"error":"slug required"}')
            return

        job_id = str(uuid.uuid4())[:8]
        jobs[job_id] = {"status": "running", "lines": [], "slug": slug}

        def run():
            cmd = [sys.executable, os.path.join(BASE, "website_agent.py"), "--slug", slug]
            if extra:
                cmd += ["--extra-prompt", extra]
            env = os.environ.copy()
            env_file = os.path.join(BASE, ".env")
            if os.path.exists(env_file):
                for line in open(env_file):
                    k, _, v = line.strip().partition("=")
                    if k and v:
                        env.setdefault(k.strip(), v.strip())
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, env=env, cwd=BASE)
                for line in proc.stdout:
                    jobs[job_id]["lines"].append(line.rstrip())
                proc.wait()
                jobs[job_id]["status"] = "done" if proc.returncode == 0 else "error"
            except Exception as e:
                jobs[job_id]["lines"].append(f"ERROR: {e}")
                jobs[job_id]["status"] = "error"

        threading.Thread(target=run, daemon=True).start()

        resp = json.dumps({"job_id": job_id}).encode()
        self.send_response(200)
        cors(self)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(resp))
        self.end_headers()
        self.wfile.write(resp)


if __name__ == "__main__":
    port = 5056
    print(f"Designer API → http://localhost:{port}")
    HTTPServer(("", port), Handler).serve_forever()
