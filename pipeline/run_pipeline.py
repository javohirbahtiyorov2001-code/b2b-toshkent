"""
Full automated pipeline:
1. Load 50 leads from seed_leads.json
2. Generate editable HTML site for each (from template, no API calls needed)
3. Deploy each to Netlify (requires NETLIFY_TOKEN env var)
4. Generate QR code PNG for each live URL
5. Build master dashboard HTML with all 50 sites + QR codes
"""

import json
import os
import re
import sys
import time
import zipfile
import tempfile
import shutil
from pathlib import Path

import requests

try:
    import qrcode
    from qrcode.image.pure import PyPNGImage
    HAS_QR = True
except ImportError:
    HAS_QR = False
    print("[WARN] qrcode not installed. Run: pip install qrcode[pil]")

ROOT = Path(__file__).parent.parent
TEMPLATE = ROOT / "templates" / "site_template.html"
SITES_DIR = ROOT / "generated_sites"
QR_DIR = ROOT / "qr_codes"
DASHBOARD_DIR = ROOT / "dashboard"
LEADS_FILE = Path(__file__).parent / "seed_leads.json"
RESULTS_FILE = Path(__file__).parent / "results.json"

SITES_DIR.mkdir(exist_ok=True)
QR_DIR.mkdir(exist_ok=True)
DASHBOARD_DIR.mkdir(exist_ok=True)

NETLIFY_TOKEN = os.environ.get("NETLIFY_TOKEN", "")
NETLIFY_BASE = "https://api.netlify.com/api/v1"

TAGLINES = {
    "Restaurant": "Eng mazali taomlar, eng iliq muhit",
    "Clinic": "Sog'ligingiz — bizning ustuvorligimiz",
    "Construction": "Qurilishda sifat va ishonch",
    "Auto Service": "Avtomobilingiz — bizning g'amxo'rligimizda",
    "Dentistry": "Chiroyli tabassum — sog'lom hayot",
    "Logistics": "Yukingizni o'z vaqtida yetkazamiz",
    "Education": "Bilim — kelajak kaliti",
    "Hotel": "Qulay dam olish, iliq mehmonxona",
    "Fitness": "Sog'lom tana — baxtiyor hayot",
    "Retail": "Sifatli mahsulotlar, qulay narxlar",
    "Real Estate": "Orzuingizdagi uyni topamiz",
    "Electronics Repair": "Qurilmangizni tezda tuzatamiz",
    "Furniture": "Uyingizni yangitdan bezamiz",
    "Printing": "Tasavvuringizni qog'ozga tushiramiz",
    "Bakery": "Yangi va mazali, har kun",
    "Landscaping": "Bog'ingizni jannatga aylantiramiz",
    "Wholesale": "Ulgurji savdoda ishonchli hamkor",
    "Kindergarten": "Farzandingiz uchun eng yaxshisi",
    "Laundry": "Kiyimlaringiz — doim toza va yangi",
    "Event Hall": "Unutilmas tadbirlar uchun mukammal joy",
    "Electrical": "Elektr ishlarida xavfsiz va sifatli",
    "Pharmacy": "Sog'ligingiz uchun kerakli dorilar",
    "Courier": "Tez, xavfsiz, ishonchli yetkazish",
    "Beauty": "Go'zalligingizni yanada ochib beramiz",
    "Travel": "Sayohat — hayotning eng yaxshi lahzalari",
    "Auto Glass": "Shishalarni tezda va sifatli tiklaymiz",
    "Bridal": "Kelin kunini unutilmas qilamiz",
    "Metalwork": "Metall ishlarda mustahkamlik va chiroyli dizayn",
    "Gas Station": "To'xtovsiz yoqilg'i xizmati",
    "Accounting": "Moliyangizni ishonchli qo'llarda saqlang",
    "IT Services": "Texnologiya orqali biznesingizni o'stiramiz",
    "Photography": "Hayotning eng chiroyli lahzalarini abadiylashtiring",
    "Cleaning": "Toza uy — toza fikr",
    "Elevators": "Liftlar o'rnatish va xizmat ko'rsatish",
    "Flowers": "Sevgi va xursandchilikni gullar bilan ifodalang",
    "Building Materials": "Qurilishingiz uchun sifatli materiallar",
    "Funeral": "Muruvvat va hurmat bilan xizmat",
    "Auto Sales": "Orzuingizdagi avtomobilni topping",
}


def build_site_html(lead: dict) -> str:
    """Fill template with lead data — no API calls, instant generation."""
    template = TEMPLATE.read_text(encoding="utf-8")

    phone_clean = re.sub(r"\D", "", lead["phone"])
    if not phone_clean.startswith("998"):
        phone_clean = "998" + phone_clean[-9:]
    whatsapp = phone_clean

    tagline = TAGLINES.get(lead["niche"], "Sifatli xizmat, ishonchli hamkor")
    description = f"{lead['name']} — {lead['niche']} sohasida professional xizmatlar Toshkentda."
    edit_pwd = lead["phone"][-4:]

    services_json = json.dumps(lead["services"], ensure_ascii=False)

    replacements = {
        "{{BUSINESS_NAME}}": lead["name"],
        "{{TAGLINE}}": tagline,
        "{{DESCRIPTION}}": description,
        "{{PHONE}}": lead["phone"],
        "{{WHATSAPP}}": whatsapp,
        "{{ADDRESS}}": lead["address"],
        "{{INSTAGRAM}}": lead.get("instagram") or "",
        "{{NICHE}}": lead["niche"],
        "{{PRIMARY_COLOR}}": lead["colors"]["primary"],
        "{{ACCENT_COLOR}}": lead["colors"]["accent"],
        "{{SERVICES_JSON}}": services_json,
        "{{EDIT_PASSWORD}}": edit_pwd,
    }

    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)

    # Inject slug for localStorage key
    template = template.replace(
        "localStorage.getItem('site_config_' + C.slug || 'site')",
        f"localStorage.getItem('site_config_{lead['slug']}')"
    ).replace(
        "localStorage.setItem('site_config_' + (C.slug || 'site'),",
        f"localStorage.setItem('site_config_{lead['slug']}',"
    )

    return template


def netlify_deploy(html_path: Path, slug: str):
    """Deploy single HTML file to Netlify. Returns live URL or None."""
    if not NETLIFY_TOKEN:
        print(f"    [SKIP] No NETLIFY_TOKEN — skipping deploy for {slug}")
        return None

    headers_json = {"Authorization": f"Bearer {NETLIFY_TOKEN}", "Content-Type": "application/json"}

    # Create site
    import random, string
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    site_name = f"uz-biz-{slug}-{suffix}"[:63]
    resp = requests.post(f"{NETLIFY_BASE}/sites", headers=headers_json, json={"name": site_name}, timeout=15)
    if resp.status_code not in (200, 201):
        print(f"    [ERR] Netlify site creation failed: {resp.status_code}")
        return None

    site_id = resp.json()["id"]
    site_url = resp.json().get("ssl_url") or resp.json().get("url", "")

    # Zip and deploy
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        zip_path = tmp.name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(html_path, "index.html")

    with open(zip_path, "rb") as f:
        deploy_resp = requests.post(
            f"{NETLIFY_BASE}/sites/{site_id}/deploys",
            headers={"Authorization": f"Bearer {NETLIFY_TOKEN}", "Content-Type": "application/zip"},
            data=f, timeout=30
        )
    os.unlink(zip_path)

    if deploy_resp.status_code not in (200, 201):
        print(f"    [ERR] Deploy failed: {deploy_resp.status_code}")
        return None

    live_url = deploy_resp.json().get("ssl_url") or site_url
    return live_url


def make_qr(url: str, out_path: Path):
    """Generate QR code PNG for a URL."""
    if not HAS_QR:
        return
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=3)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(str(out_path))


def embed_qr_in_html(html: str, qr_path: Path, live_url: str) -> str:
    """Embed QR code as base64 PNG into the footer of the HTML."""
    if not qr_path.exists():
        return html
    import base64
    qr_b64 = base64.b64encode(qr_path.read_bytes()).decode()
    qr_html = f"""
  <!-- QR CODE SECTION -->
  <div style="text-align:center;padding:2rem 5%;background:#f8f9fa;border-top:1px solid #eee;">
    <p style="font-size:0.8rem;color:#6c757d;margin-bottom:1rem;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Saytga QR orqali kiring</p>
    <img src="data:image/png;base64,{qr_b64}" alt="QR Code" style="width:140px;height:140px;border-radius:8px;">
    <p style="font-size:0.75rem;color:#aaa;margin-top:0.75rem;word-break:break-all;">{live_url}</p>
  </div>"""
    return html.replace("<!-- WHATSAPP FLOAT -->", qr_html + "\n<!-- WHATSAPP FLOAT -->")


def build_dashboard(results: list[dict]) -> str:
    """Build master HTML dashboard showing all 50 sites with QR codes."""
    cards = ""
    for r in results:
        url = r.get("url") or f"file://{r['html_path']}"
        qr_section = ""
        qr_path = Path(r.get("qr_path", ""))
        if qr_path.exists():
            import base64
            qr_b64 = base64.b64encode(qr_path.read_bytes()).decode()
            qr_section = f'<img src="data:image/png;base64,{qr_b64}" style="width:80px;height:80px;border-radius:6px;margin-bottom:0.5rem;">'

        score_color = {"Hot": "#ef4444", "Warm": "#f59e0b", "Cold": "#3b82f6"}.get(r.get("score","Cold"), "#3b82f6")
        cards += f"""
        <div class="card">
          <div class="card-top" style="background:linear-gradient(135deg,{r['colors']['primary']},{r['colors']['accent']})">
            <div class="card-num">#{r['id']}</div>
            <div class="card-niche">{r['niche']}</div>
          </div>
          <div class="card-body">
            {qr_section}
            <div class="card-name">{r['name']}</div>
            <div class="card-phone">{r['phone']}</div>
            <div class="card-addr">{r['address'][:40]}...</div>
            <div class="card-actions">
              <a href="{url}" target="_blank" class="btn-visit">🌐 Saytni ko'rish</a>
              <span class="score-badge" style="background:{score_color}">{'Hot' if r.get('has_url') else 'Ready'}</span>
            </div>
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>B2B — 50 ta tayyor sayt</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;background:#030712;color:#f9fafb;min-height:100vh}}
.header{{padding:3rem 5%;text-align:center;border-bottom:1px solid #1f2937}}
.header h1{{font-size:2.5rem;font-weight:900;background:linear-gradient(135deg,#fff,#a5b4fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.5rem}}
.header p{{color:#6b7280;font-size:1rem}}
.stats-bar{{display:flex;justify-content:center;gap:3rem;padding:1.5rem 5%;background:#111827;border-bottom:1px solid #1f2937;flex-wrap:wrap}}
.stat{{text-align:center}}.stat-val{{font-size:1.8rem;font-weight:800;color:#818cf8}}.stat-lbl{{font-size:0.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:1px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.5rem;padding:2rem 5%;max-width:1400px;margin:0 auto}}
.card{{background:#111827;border:1px solid #1f2937;border-radius:12px;overflow:hidden;transition:transform 0.2s,box-shadow 0.2s}}
.card:hover{{transform:translateY(-4px);box-shadow:0 8px 32px rgba(0,0,0,0.4)}}
.card-top{{padding:1.5rem;position:relative;min-height:80px;display:flex;align-items:flex-end;justify-content:space-between}}
.card-num{{font-size:0.75rem;font-weight:700;color:rgba(255,255,255,0.5);background:rgba(0,0,0,0.3);padding:2px 8px;border-radius:50px}}
.card-niche{{font-size:0.7rem;font-weight:600;color:rgba(255,255,255,0.7);background:rgba(0,0,0,0.3);padding:2px 8px;border-radius:50px}}
.card-body{{padding:1.25rem;text-align:center}}
.card-name{{font-size:1rem;font-weight:700;color:#f9fafb;margin-bottom:0.25rem}}
.card-phone{{font-size:0.8rem;color:#818cf8;font-family:monospace;margin-bottom:0.25rem}}
.card-addr{{font-size:0.75rem;color:#6b7280;margin-bottom:1rem}}
.card-actions{{display:flex;gap:0.5rem;align-items:center;justify-content:center}}
.btn-visit{{background:#4f46e5;color:white;padding:0.4rem 0.9rem;border-radius:6px;text-decoration:none;font-size:0.8rem;font-weight:600;transition:background 0.2s}}
.btn-visit:hover{{background:#4338ca}}
.score-badge{{font-size:0.7rem;font-weight:700;padding:0.3rem 0.7rem;border-radius:50px;color:white}}
footer{{text-align:center;padding:2rem;color:#4b5563;font-size:0.8rem;border-top:1px solid #1f2937}}
</style>
</head>
<body>
<div class="header">
  <h1>🚀 50 ta Toshkent Biznesi</h1>
  <p>Avtomatik yaratilgan saytlar — QR kodi bilan yetkaziladi</p>
</div>
<div class="stats-bar">
  <div class="stat"><div class="stat-val">50</div><div class="stat-lbl">Kompaniya</div></div>
  <div class="stat"><div class="stat-val">{sum(1 for r in results if r.get('url'))}</div><div class="stat-lbl">Joylashtirilgan</div></div>
  <div class="stat"><div class="stat-val">{sum(1 for r in results if r.get('qr_path'))}</div><div class="stat-lbl">QR kod tayyor</div></div>
  <div class="stat"><div class="stat-val">0 so'm</div><div class="stat-lbl">Mijozdan to'lov</div></div>
</div>
<div class="grid">{cards}</div>
<footer>Barcha 50 ta sayt avtomatik yaratildi · {time.strftime('%Y-%m-%d %H:%M')}</footer>
</body>
</html>"""


def main():
    leads = json.loads(LEADS_FILE.read_text(encoding="utf-8"))
    results = []

    print(f"\n{'='*60}")
    print(f"  B2B Pipeline — {len(leads)} leads")
    print(f"  Netlify: {'✅ token set' if NETLIFY_TOKEN else '⚠️  no token (local files only)'}")
    print(f"  QR codes: {'✅' if HAS_QR else '⚠️  install qrcode[pil]'}")
    print(f"{'='*60}\n")

    for i, lead in enumerate(leads, 1):
        print(f"[{i:02d}/{len(leads)}] {lead['name']} ({lead['niche']})")

        # 1. Generate HTML
        html = build_site_html(lead)
        html_path = SITES_DIR / f"{lead['slug']}.html"
        html_path.write_text(html, encoding="utf-8")
        print(f"       ✅ HTML generated ({len(html)//1024}KB)")

        # 2. Deploy to Netlify
        live_url = netlify_deploy(html_path, lead["slug"])
        if live_url:
            print(f"       🚀 Deployed: {live_url}")
        else:
            live_url = None

        # 3. QR code
        qr_path = QR_DIR / f"{lead['slug']}.png"
        target_url = live_url or f"https://uz-biz-{lead['slug']}.netlify.app"
        make_qr(target_url, qr_path)
        if qr_path.exists():
            print(f"       📱 QR code generated")

        # 4. Embed QR in HTML
        if qr_path.exists():
            html_with_qr = embed_qr_in_html(html, qr_path, target_url)
            html_path.write_text(html_with_qr, encoding="utf-8")

        result = {
            **lead,
            "html_path": str(html_path),
            "url": live_url,
            "qr_path": str(qr_path) if qr_path.exists() else None,
            "has_url": bool(live_url),
            "edit_password": lead["phone"][-4:],
        }
        results.append(result)

        if NETLIFY_TOKEN and i < len(leads):
            time.sleep(0.5)  # gentle rate limiting

    # Save results
    RESULTS_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"  ✅ Results saved → {RESULTS_FILE}")

    # Build dashboard
    dashboard_html = build_dashboard(results)
    dashboard_path = DASHBOARD_DIR / "index.html"
    dashboard_path.write_text(dashboard_html, encoding="utf-8")
    print(f"  📊 Dashboard → {dashboard_path}")
    print(f"{'='*60}\n")

    deployed = sum(1 for r in results if r.get("url"))
    print(f"Summary: {len(results)} sites built, {deployed} deployed")
    print(f"Open dashboard: open {dashboard_path}")

    return results


if __name__ == "__main__":
    main()
