"""
Google Maps Business Scraper for Uzbekistan B2B leads.
Extracts: name, phone, address, website, rating, category
"""

import asyncio
import json
import re
import csv
import time
from pathlib import Path
from playwright.async_api import async_playwright
import phonenumbers

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

UZ_NICHES = [
    "restoran Toshkent",
    "klinika Toshkent",
    "qurilish kompaniyasi Toshkent",
    "logistika kompaniya Toshkent",
    "do'kon Toshkent",
    "avtoservis Toshkent",
    "mehmonxona Toshkent",
    "stomatologiya Toshkent",
    "fitnes markaz Toshkent",
    "ta'lim markazi Toshkent",
    "ombor Toshkent",
    "savdo markazi Toshkent",
    "bank Toshkent",
    "real estate Toshkent",
    "marketing agentlik Toshkent",
]

NICHE_MAP = {
    "restoran": "Restaurant",
    "klinika": "Clinic",
    "stomatologiya": "Dentistry",
    "qurilish": "Construction",
    "logistika": "Logistics",
    "do'kon": "Retail",
    "avtoservis": "Auto Service",
    "mehmonxona": "Hotel",
    "fitnes": "Fitness",
    "ta'lim": "Education",
    "ombor": "Warehouse",
    "savdo": "Trade Center",
    "bank": "Banking",
    "real estate": "Real Estate",
    "marketing": "Marketing Agency",
}


def detect_niche(query: str) -> str:
    query_lower = query.lower()
    for key, value in NICHE_MAP.items():
        if key in query_lower:
            return value
    return "Other"


def clean_phone(raw: str) -> str | None:
    """Parse and normalize Uzbek phone number to +998XXXXXXXXX format."""
    if not raw:
        return None
    try:
        parsed = phonenumbers.parse(raw, "UZ")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        pass
    # Try extracting digits manually
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("998") and len(digits) == 12:
        return f"+{digits}"
    if digits.startswith("0") and len(digits) == 9:
        return f"+998{digits[1:]}"
    if len(digits) == 9:
        return f"+998{digits}"
    return None


async def scrape_query(page, query: str, max_results: int = 30) -> list[dict]:
    """Scrape Google Maps for a single search query."""
    leads = []
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/"
    await page.goto(url, wait_until="networkidle", timeout=30000)
    await asyncio.sleep(2)

    niche = detect_niche(query)

    # Scroll the results panel to load more listings
    results_panel = page.locator('div[role="feed"]')
    for _ in range(8):
        await results_panel.evaluate("el => el.scrollBy(0, 800)")
        await asyncio.sleep(1.2)

    # Collect all result cards
    cards = await page.locator('a[href*="/maps/place/"]').all()
    print(f"  Found {len(cards)} cards for: {query}")

    for card in cards[:max_results]:
        try:
            href = await card.get_attribute("href")
            if not href:
                continue

            # Click into the listing
            await card.click()
            await asyncio.sleep(2.5)

            name_el = page.locator('h1.DUwDvf, h1[class*="fontHeadlineLarge"]').first
            name = (await name_el.inner_text()).strip() if await name_el.count() > 0 else ""

            phone_el = page.locator('button[data-tooltip="Copy phone number"], [data-item-id*="phone:tel"]').first
            phone_raw = ""
            if await phone_el.count() > 0:
                phone_raw = (await phone_el.get_attribute("data-item-id") or "").replace("phone:tel:", "")
                if not phone_raw:
                    phone_raw = await phone_el.inner_text()

            phone = clean_phone(phone_raw)

            website_el = page.locator('a[data-item-id="authority"]').first
            website = await website_el.get_attribute("href") if await website_el.count() > 0 else ""

            address_el = page.locator('button[data-item-id*="address"]').first
            address = (await address_el.inner_text()).strip() if await address_el.count() > 0 else ""

            rating_el = page.locator('div.F7nice span[aria-hidden="true"]').first
            rating = (await rating_el.inner_text()).strip() if await rating_el.count() > 0 else ""

            if name:
                leads.append({
                    "name": name,
                    "phone": phone,
                    "phone_raw": phone_raw,
                    "website": website,
                    "address": address,
                    "rating": rating,
                    "niche": niche,
                    "source": "Google Maps",
                    "query": query,
                    "maps_url": href,
                })

            # Go back to list
            await page.go_back()
            await asyncio.sleep(1.5)

        except Exception as e:
            print(f"  Error on card: {e}")
            continue

    return leads


def deduplicate(leads: list[dict]) -> list[dict]:
    seen_phones = set()
    seen_names = set()
    unique = []
    for lead in leads:
        key_phone = lead.get("phone")
        key_name = lead.get("name", "").lower().strip()
        if key_phone and key_phone in seen_phones:
            continue
        if key_name in seen_names:
            continue
        if key_phone:
            seen_phones.add(key_phone)
        seen_names.add(key_name)
        unique.append(lead)
    return unique


def score_lead(lead: dict) -> str:
    """Simple Hot/Warm/Cold scoring."""
    score = 0
    if lead.get("phone"):
        score += 3
    if lead.get("website"):
        score += 2
    try:
        rating = float(lead.get("rating", 0) or 0)
        if rating >= 4.5:
            score += 2
        elif rating >= 4.0:
            score += 1
    except ValueError:
        pass
    if score >= 5:
        return "Hot"
    if score >= 3:
        return "Warm"
    return "Cold"


def save_leads(leads: list[dict], filename: str = "leads.json"):
    path_json = OUTPUT_DIR / filename
    path_csv = OUTPUT_DIR / filename.replace(".json", ".csv")

    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

    if leads:
        with open(path_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=leads[0].keys())
            writer.writeheader()
            writer.writerows(leads)

    print(f"\nSaved {len(leads)} leads → {path_json}")
    print(f"CSV → {path_csv}")


async def main(queries: list[str] = None, max_per_query: int = 30, headless: bool = False):
    queries = queries or UZ_NICHES
    all_leads = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless, args=["--lang=uz-UZ,ru-RU"])
        context = await browser.new_context(
            locale="ru-RU",
            timezone_id="Asia/Tashkent",
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()

        for query in queries:
            print(f"\nScraping: {query}")
            try:
                leads = await scrape_query(page, query, max_per_query)
                all_leads.extend(leads)
                print(f"  Got {len(leads)} leads")
                time.sleep(2)
            except Exception as e:
                print(f"  Failed: {e}")

        await browser.close()

    # Score and deduplicate
    for lead in all_leads:
        lead["score"] = score_lead(lead)

    unique_leads = deduplicate(all_leads)
    print(f"\nTotal: {len(all_leads)} → After dedup: {len(unique_leads)}")
    print(f"Hot: {sum(1 for l in unique_leads if l['score']=='Hot')}")
    print(f"Warm: {sum(1 for l in unique_leads if l['score']=='Warm')}")
    print(f"Cold: {sum(1 for l in unique_leads if l['score']=='Cold')}")

    save_leads(unique_leads)
    return unique_leads


if __name__ == "__main__":
    import sys
    # Run with specific queries: python google_maps.py "restoran Toshkent" "klinika Toshkent"
    custom = sys.argv[1:] if len(sys.argv) > 1 else None
    asyncio.run(main(queries=custom, headless=False))
