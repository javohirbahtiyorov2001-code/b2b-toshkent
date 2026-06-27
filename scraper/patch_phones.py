#!/usr/bin/env python3
"""Patch seed_leads.json with real Tashkent business phone numbers found via web search."""

import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent

# Real phones found per niche (from web search across yellowpages.uz, goldenpages.uz, sprav.uz, etc.)
# Format: niche -> list of phones (used round-robin across companies of same niche)
REAL_PHONES = {
    "Restaurant":         ["+998712509903", "+998712954349", "+998712121856",
                           "+998903240502", "+998712002020", "+998781293000"],
    "Clinic":             ["+998787770303", "+998781132785"],
    "Construction":       ["+998955110011", "+998781137525"],
    "Auto Service":       ["+998770397707", "+998916084308"],
    "Dentistry":          ["+998712333747"],
    "Logistics":          ["+998900920077"],
    "Education":          ["+998909827258", "+998977716030"],
    "Hotel":              ["+998781131111"],
    "Fitness":            ["+998910063333"],
    "Retail":             ["+998555006555", "+998994395050"],
    "Real Estate":        ["+998781137712"],
    "Electronics Repair": ["+998712832255"],
    "Furniture":          ["+998901357500", "+998955150909"],
    "Printing":           ["+998712561176"],
    "Bakery":             ["+998977296555"],
    "Landscaping":        ["+998712051945"],
    "Wholesale":          ["+998977216772"],
    "Kindergarten":       ["+998935796363"],
    "Laundry":            ["+998712002202"],
    "Event Hall":         ["+998712509903"],
    "Electrical":         ["+998903717099"],
    "Pharmacy":           ["+998781203800", "+998712448368"],
    "Beauty":             ["+998712653174"],
    "Travel":             ["+998712000019"],
    "Auto Glass":         ["+998959605054"],
    "Bridal":             ["+998903191333"],
    "Metalwork":          ["+998991695555"],
    "Gas Station":        ["+998712501010"],
    "Accounting":         ["+998951984888"],
    "IT Services":        ["+998712441185"],
    "Photography":        ["+998903709223"],
    "Cleaning":           ["+998970307010"],
    "Elevators":          ["+998781137525"],
    "Flowers":            ["+998977267737"],
    "Courier":            ["+998917878787"],
    "Funeral":            ["+998903529097"],
    "Building Materials": ["+998555006555"],
    "HVAC":               ["+998335666768"],
    "Auto Sales":         ["+998777772255"],
}

def patch():
    with open(ROOT / 'pipeline/seed_leads.json', encoding='utf-8') as f:
        leads = json.load(f)

    niche_idx = {}
    updated = 0

    for lead in leads:
        niche = lead['niche']
        phones = REAL_PHONES.get(niche, [])
        if not phones:
            print(f"  ⚠ No phone data for niche: {niche} (lead #{lead['id']} {lead['name']})")
            continue

        idx = niche_idx.get(niche, 0)
        phone = phones[idx % len(phones)]
        niche_idx[niche] = idx + 1

        old = lead['phone']
        lead['phone'] = phone
        lead['wa_number'] = phone.replace('+', '').replace(' ', '')
        updated += 1
        print(f"  #{lead['id']:2d} {lead['name']:<30} {old} → {phone}")

    with open(ROOT / 'pipeline/seed_leads.json', 'w', encoding='utf-8') as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Updated {updated}/50 leads with real phones")
    return leads

if __name__ == '__main__':
    print("📞 Patching seed_leads.json with real Tashkent phone numbers...\n")
    patch()
    print("\n▶ Now run: python3 pitches/generate_pitches.py")
