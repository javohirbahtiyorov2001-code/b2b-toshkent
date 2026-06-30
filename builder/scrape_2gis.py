#!/usr/bin/env python3
"""
Scrape REAL Tashkent businesses from 2GIS Catalog API.
Requires a free 2GIS API key from: https://dev.2gis.com/

Usage:
  export GIS_KEY="your_key_here"
  python3 builder/scrape_2gis.py
"""

import json, re, time, sys, os
from pathlib import Path

try:
    import requests
except ImportError:
    import subprocess; subprocess.run([sys.executable,"-m","pip","install","requests","-q"])
    import requests

ROOT = Path(__file__).parent.parent
OUT  = ROOT / "pipeline" / "real_leads.json"

KEY = os.environ.get("GIS_KEY", "")

# 2GIS category codes for Tashkent — use rubric_id for precise category
# https://catalog.api.2gis.com/3.0/rubrics?q=...&key=YOUR_KEY
SEARCHES = [
    ("stomatologiya",   "Dentistry",   "70000001008862"),   # Dentistry rubric
    ("restoran",        "Restaurant",  "70000001079464"),   # Restaurants
    ("kafe",            "Restaurant",  "70000001080567"),   # Cafes
    ("salon krasoty",   "Beauty",      "70000001079798"),   # Beauty salons
    ("avtoservis",      "Auto",        "70000001008866"),   # Auto service
]

def clean_phone(raw):
    digits = re.sub(r'[^0-9]', '', str(raw))
    if len(digits) == 9:               return f"+998{digits}"
    if digits.startswith('998') and len(digits)==12: return f"+{digits}"
    if digits.startswith('8') and len(digits)==11:   return f"+998{digits[1:]}"
    if len(digits) >= 10:              return f"+{digits}"
    return None

def slug(name):
    s = name.lower()
    s = re.sub(r"[''']", "", s)
    s = re.sub(r'[^a-z0-9а-яё\- ]+', ' ', s)
    s = re.sub(r'\s+', '-', s.strip())
    return s[:60]

def fetch_page(query, rubric_id, page):
    params = {
        "q": query,
        "location": "69.2401,41.2995",   # Tashkent center lon,lat
        "radius": 25000,                   # 25km radius covers all of Tashkent
        "type": "branch",
        "fields": "items.contact_groups,items.address,items.name_ex",
        "page": page,
        "page_size": 50,
        "locale": "ru_UZ",
        "key": KEY,
    }
    r = requests.get("https://catalog.api.2gis.com/3.0/items", params=params, timeout=15)
    return r.json()

def scrape_niche(query, niche, rubric_id, max_leads=100):
    leads = []
    seen = set()

    for page in range(1, 20):
        try:
            data = fetch_page(query, rubric_id, page)
        except Exception as e:
            print(f"  ⚠ Request error: {e}")
            break

        code = data.get("meta", {}).get("code")
        if code == 403:
            print(f"\n❌ API KEY ERROR: {data['meta']['error']['message']}")
            print(f"   Get your free key at: https://dev.2gis.com/")
            print(f"   Then run: GIS_KEY=your_key python3 builder/scrape_2gis.py")
            sys.exit(1)

        items = data.get("result", {}).get("items", [])
        total = data.get("result", {}).get("total", 0)
        if not items:
            break

        new_this_page = 0
        for item in items:
            name = item.get("name_ex", {}).get("primary") or item.get("name", "")
            if not name or name in seen:
                continue

            # Check contacts for website and phone
            has_web = False
            phone = None
            for cg in item.get("contact_groups", []):
                for c in cg.get("contacts", []):
                    if c.get("type") in ("website", "instagram", "vk"):
                        has_web = True
                    if c.get("type") == "phone" and not phone:
                        phone = clean_phone(c["value"])

            # Skip if already has website — they don't need us
            if has_web:
                continue
            # Skip if no phone — can't pitch them
            if not phone:
                continue

            addr = item.get("address", {})
            address_str = addr.get("name", "")
            district = next((
                c["value"] for c in addr.get("components", [])
                if c.get("type") in ("district", "subregion")
            ), "Toshkent")

            seen.add(name)
            leads.append({
                "name": name,
                "niche": niche,
                "phone": phone,
                "address": address_str,
                "district": district,
                "has_website": False,
                "source": "2gis",
                "slug": slug(name),
                "services": [],
            })
            new_this_page += 1
            print(f"  ✅ {name[:50]:<50} {phone}")

        print(f"  page {page}: +{new_this_page} | total so far: {len(leads)} / {total} in 2GIS")

        if len(leads) >= max_leads or page * 50 >= total:
            break
        time.sleep(0.4)

    return leads

def main():
    if not KEY:
        print("""
╔══════════════════════════════════════════════════════════╗
║  2GIS API KEY REQUIRED — GET IT FREE IN 5 MINUTES       ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  1. Go to: https://dev.2gis.com/                         ║
║  2. Click "Получить ключ" (Get key) — sign up free       ║
║  3. Create a project → copy your API key                 ║
║  4. Run:                                                 ║
║     export GIS_KEY="your_key_here"                       ║
║     python3 builder/scrape_2gis.py                       ║
║                                                          ║
║  Free tier: 1,000 requests/day — enough for 500 leads    ║
╚══════════════════════════════════════════════════════════╝
""")
        sys.exit(0)

    print(f"🔑 Using 2GIS API key: {KEY[:8]}...")
    all_leads = []
    seen_phones = set()

    for query, niche, rubric_id in SEARCHES:
        print(f"\n{'─'*55}")
        print(f"🔍 Scraping: {niche} (query: {query})")
        batch = scrape_niche(query, niche, rubric_id, max_leads=100)
        unique = [l for l in batch if l["phone"] not in seen_phones]
        seen_phones.update(l["phone"] for l in unique)
        all_leads.extend(unique)
        print(f"  → {len(unique)} unique real leads added")

    OUT.write_text(json.dumps(all_leads, ensure_ascii=False, indent=2), encoding="utf-8")

    by_niche = {}
    for l in all_leads:
        by_niche[l['niche']] = by_niche.get(l['niche'], 0) + 1

    print(f"\n{'='*55}")
    print(f"✅ REAL leads saved: {len(all_leads)}")
    for n, c in sorted(by_niche.items()):
        print(f"  {n}: {c}")
    print(f"\n📁 {OUT}")
    print(f"\n🚀 Now build their websites:")
    print(f"   python3 builder/template_generator.py --real")

if __name__ == "__main__":
    main()
