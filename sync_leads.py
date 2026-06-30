"""
Watches generated_sites/ for new HTML files and auto-adds them to
dental_clinic_leads.json. Runs forever alongside the HTTP server.
"""
import json, os, re, time, sys
from pathlib import Path

ROOT        = Path(__file__).parent
SITES_DIR   = ROOT / "generated_sites"
LEADS_FILE  = ROOT / "pipeline" / "dental_clinic_leads.json"
POLL_SECS   = 3   # check every 3 seconds

def load_leads():
    try:
        return json.loads(LEADS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_leads(leads):
    LEADS_FILE.write_text(json.dumps(leads, ensure_ascii=False, indent=2), encoding="utf-8")

def known_slugs(leads):
    return {l.get("slug", "") for l in leads}

def parse_html(path: Path) -> dict:
    """Extract name, phone, address, niche from a generated HTML file."""
    try:
        html = path.read_text(encoding="utf-8")
    except Exception:
        return {}

    slug = path.stem

    # Title  → clinic name
    m = re.search(r"<title>([^<|—–]+)", html)
    name = m.group(1).strip() if m else slug.replace("-", " ").title()

    # tel: href → phone
    m = re.search(r'href="tel:(\+[\d\s\-]+)"', html)
    phone = m.group(1).strip() if m else ""
    wa = re.sub(r"[^\d]", "", phone)

    # address heuristic: look for "ул.", "мкр.", "ko'chasi", "massiv"
    m = re.search(r'((?:ул\.|мкр\.|ko\'chasi|massivi|Babura|Furqat|Almazar|Beshyogoch)[^<\n"]{4,60})', html)
    address = m.group(1).strip() if m else ""

    # niche guess from title/content
    niche = "Business"
    keywords = {
        "Dentistry":    ["dental","dentist","stom","dent","smile","зуб","тиш"],
        "Restaurant":   ["restoran","cafe","kebab","oshxon","restaurant","кафе"],
        "Clinic":       ["klinik","tibbiy","медиц","clinic","hospital"],
        "Fitness":      ["fitness","sport","gym","bassey"],
        "Beauty":       ["beauty","salon","kosm","nail","hair","spa"],
        "Hotel":        ["hotel","mehmonxon","hostel"],
        "Auto":         ["avto","auto","servis","car"],
    }
    lower = html.lower()
    for n, kws in keywords.items():
        if any(k in lower for k in kws):
            niche = n
            break

    # primary/accent colors from CSS variables
    m1 = re.search(r"--(?:navy|ink|slate|coral|off-white|bg|white).*?:(#[0-9a-fA-F]{3,6})", html)
    m2 = re.search(r"--(?:cyan|gold|teal|amber|coral).*?:(#[0-9a-fA-F]{3,6})", html)
    primary = m1.group(1) if m1 else "#1a1a1a"
    accent  = m2.group(1) if m2 else "#00e5ff"

    return {
        "name":    name,
        "niche":   niche,
        "phone":   phone,
        "wa_number": wa,
        "address": address,
        "slug":    slug,
        "colors":  {"primary": primary, "accent": accent},
        "source":  "auto-generated",
    }

def next_id(leads):
    return max((l.get("id", 0) for l in leads), default=0) + 1

def sync():
    leads = load_leads()
    slugs = known_slugs(leads)
    added = []

    for html_file in sorted(SITES_DIR.glob("*.html")):
        slug = html_file.stem
        if slug in slugs:
            continue
        info = parse_html(html_file)
        if not info:
            continue
        entry = {"id": next_id(leads), **info}
        leads.append(entry)
        slugs.add(slug)
        added.append(entry["name"])

    if added:
        save_leads(leads)
        print(f"[sync] +{len(added)} leads: {', '.join(added)}", flush=True)

    return len(added)

if __name__ == "__main__":
    print(f"[sync] watching {SITES_DIR} every {POLL_SECS}s …", flush=True)
    # initial full sync
    n = sync()
    print(f"[sync] initial sync done (+{n} new leads)", flush=True)
    while True:
        time.sleep(POLL_SECS)
        sync()
