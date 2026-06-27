#!/usr/bin/env python3
"""
Scrape 2GIS Tashkent for real businesses (no website) per niche.
Updates seed_leads.json with real names + phone numbers.
"""

import json, re, time, pathlib, random
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

ROOT = pathlib.Path(__file__).parent.parent

# Map our niches → 2GIS search queries (Uzbek/Russian)
NICHE_QUERIES = {
    "Restaurant":          ["кафе Ташкент", "ресторан Ташкент", "ошхона Тошкент"],
    "Clinic":              ["клиника Ташкент", "медцентр Ташкент", "klinika Toshkent"],
    "Construction":        ["строительная компания Ташкент", "qurilish kompaniya Toshkent"],
    "Auto Service":        ["автосервис Ташкент", "СТО Ташкент", "avtoservis Toshkent"],
    "Dentistry":           ["стоматология Ташкент", "стоматологическая клиника Ташкент"],
    "Logistics":           ["логистика Ташкент", "грузоперевозки Ташкент"],
    "Education":           ["учебный центр Ташкент", "o'quv markaz Toshkent", "курсы Ташкент"],
    "Hotel":               ["гостиница Ташкент", "отель Ташкент", "mehmonxona Toshkent"],
    "Fitness":             ["фитнес клуб Ташкент", "спортзал Ташкент", "sport markaz Toshkent"],
    "Retail":              ["магазин Ташкент", "супермаркет Ташкент"],
    "Real Estate":         ["агентство недвижимости Ташкент", "риелтор Ташкент"],
    "Electronics Repair":  ["ремонт телефонов Ташкент", "сервис электроники Ташкент"],
    "Furniture":           ["мебельный магазин Ташкент", "мебель на заказ Ташкент"],
    "Printing":            ["типография Ташкент", "печать Ташкент"],
    "Bakery":              ["кондитерская Ташкент", "торты на заказ Ташкент", "qandolat Toshkent"],
    "Landscaping":         ["ландшафтный дизайн Ташкент", "озеленение Ташкент"],
    "Wholesale":           ["оптовый склад Ташкент", "оптовая торговля Ташкент"],
    "Kindergarten":        ["детский сад Ташкент", "частный детсад Ташкент", "boghcha Toshkent"],
    "Laundry":             ["химчистка Ташкент", "прачечная Ташкент"],
    "Event Hall":          ["банкетный зал Ташкент", "той зали Тошкент", "свадебный зал Ташкент"],
    "Electrical":          ["электромонтаж Ташкент", "электрик Ташкент"],
    "Pharmacy":            ["аптека Ташкент", "dorixona Toshkent"],
    "Beauty":              ["салон красоты Ташкент", "косметология Ташкент"],
    "Travel":              ["туристическое агентство Ташкент", "туры из Ташкента"],
    "Auto Glass":          ["автостекло Ташкент", "замена стекла авто Ташкент"],
    "Bridal":              ["свадебный салон Ташкент", "платья невесты Ташкент"],
    "Metalwork":           ["металлоконструкции Ташкент", "сварка Ташкент"],
    "Gas Station":         ["АЗС Ташкент", "бензозаправка Ташкент", "yoqilgi quyish Toshkent"],
    "Accounting":          ["бухгалтерские услуги Ташкент", "аутсорсинг бухгалтерии Ташкент"],
    "IT Services":         ["IT компания Ташкент", "разработка сайтов Ташкент"],
    "Photography":         ["фотостудия Ташкент", "фотограф Ташкент", "foto studiya Toshkent"],
    "Cleaning":            ["клининговая компания Ташкент", "уборка квартир Ташкент"],
    "Elevators":           ["лифтовая компания Ташкент", "монтаж лифтов Ташкент"],
    "Flowers":             ["цветочный магазин Ташкент", "доставка цветов Ташкент"],
    "Courier":             ["курьерская служба Ташкент", "доставка Ташкент"],
    "Funeral":             ["ритуальные услуги Ташкент", "похоронное бюро Ташкент"],
    "Building Materials":  ["строительные материалы Ташкент", "стройматериалы Ташкент"],
    "HVAC":                ["кондиционеры Ташкент", "установка кондиционеров Ташкент"],
    "Auto Sales":          ["автосалон Ташкент", "продажа авто Ташкент"],
}

def clean_phone(raw: str) -> str:
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 9:
        return f"+998{digits}"
    if len(digits) == 12 and digits.startswith('998'):
        return f"+{digits}"
    if len(digits) == 11 and digits.startswith('8998'):
        return f"+{digits[1:]}"
    if len(digits) >= 9:
        return f"+998{digits[-9:]}"
    return raw

def scrape_2gis(page, query: str, max_results: int = 3) -> list[dict]:
    results = []
    try:
        url = f"https://2gis.uz/tashkent/search/{query.replace(' ', '%20')}"
        page.goto(url, timeout=25000, wait_until='domcontentloaded')
        time.sleep(2.5)

        # Wait for results list
        try:
            page.wait_for_selector('[class*="cardList"], [class*="miniCard"], [data-testid="search-result"]', timeout=8000)
        except PWTimeout:
            pass

        # Collect card elements
        cards = page.query_selector_all('[class*="_name_"], [class*="title"], ._name_')
        if not cards:
            cards = page.query_selector_all('a[href*="/firm/"]')

        seen_names = set()
        for card in cards[:15]:
            if len(results) >= max_results:
                break
            try:
                # Try to get the item container
                item = card.evaluate_handle('el => el.closest("[class*=\\"miniCard\\"], [class*=\\"card\\"], li")')
                if not item:
                    continue

                name_el = item.query_selector('[class*="_name_"], [class*="title_"], h3, h2')
                name = (name_el.inner_text().strip() if name_el else card.inner_text().strip())
                if not name or name in seen_names or len(name) < 3:
                    continue

                # Click to open card for phone
                try:
                    card.click()
                    time.sleep(1.5)
                except:
                    pass

                phone = ""
                try:
                    ph_el = page.query_selector('[class*="phone"], [href^="tel:"], [data-qa="phone"]')
                    if ph_el:
                        raw = ph_el.get_attribute('href') or ph_el.inner_text()
                        phone = clean_phone(raw.replace('tel:', '').strip())
                except:
                    pass

                # Check no website
                has_site = False
                try:
                    site_el = page.query_selector('[class*="website"], [href*="http"]:not([href*="2gis"])')
                    if site_el:
                        href = site_el.get_attribute('href') or ''
                        if href.startswith('http') and '2gis' not in href:
                            has_site = True
                except:
                    pass

                if phone and not has_site:
                    seen_names.add(name)
                    results.append({'name': name, 'phone': phone})
                    print(f"  ✓ {name} → {phone}")

            except Exception as e:
                continue

    except Exception as e:
        print(f"  ⚠ Error scraping '{query}': {e}")

    return results

def scrape_all_niches() -> dict:
    """Returns {niche: [{name, phone}, ...]}"""
    found = {}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            locale='ru-RU',
            viewport={'width': 1280, 'height': 800}
        )
        page = ctx.new_page()
        page.set_default_timeout(20000)

        for niche, queries in NICHE_QUERIES.items():
            print(f"\n🔍 {niche}")
            niche_results = []
            for q in queries:
                if len(niche_results) >= 2:
                    break
                results = scrape_2gis(page, q, max_results=2)
                for r in results:
                    if r not in niche_results:
                        niche_results.append(r)
            found[niche] = niche_results
            time.sleep(random.uniform(1, 2))

        browser.close()

    return found

def update_leads(found: dict):
    with open(ROOT / 'pipeline/seed_leads.json') as f:
        leads = json.load(f)

    # Track which niche we've used each result for
    niche_idx = {n: 0 for n in found}

    updated = 0
    for lead in leads:
        niche = lead['niche']
        if niche not in found or not found[niche]:
            continue
        idx = niche_idx.get(niche, 0)
        candidates = found[niche]
        if idx < len(candidates):
            c = candidates[idx]
            lead['phone'] = c['phone']
            lead['real_name_found'] = c['name']
            niche_idx[niche] = idx + 1
            updated += 1
            print(f"  Updated #{lead['id']} {lead['name']} → {c['phone']} (found as '{c['name']}')")

    with open(ROOT / 'pipeline/seed_leads.json', 'w', encoding='utf-8') as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Updated {updated}/50 leads with real phone numbers")
    return leads

if __name__ == '__main__':
    print("🚀 Scraping 2GIS Tashkent for real business phones...\n")
    found = scrape_all_niches()

    print("\n\n📊 Summary:")
    for niche, items in found.items():
        status = "✓" if items else "✗"
        print(f"  {status} {niche}: {len(items)} found")

    print("\n📝 Updating seed_leads.json...")
    update_leads(found)

    # Save raw findings
    out = ROOT / 'scraper/found_businesses.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(found, f, ensure_ascii=False, indent=2)
    print(f"💾 Raw findings saved to {out}")
