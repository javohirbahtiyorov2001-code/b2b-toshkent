#!/usr/bin/env python3
"""
Batch generator — 100 dental & clinic websites from dental_clinic_leads.json
Uses Claude API to generate each site. Saves to generated_sites/.
"""

import os, json, time
from pathlib import Path
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

ROOT = Path(__file__).parent.parent
LEADS_FILE = ROOT / "pipeline" / "dental_clinic_leads.json"
OUTPUT_DIR = ROOT / "generated_sites"
OUTPUT_DIR.mkdir(exist_ok=True)

SYSTEM_PROMPT = """You are an elite web designer specializing in healthcare and dental clinic websites for Uzbekistan.
Your designs are:
- Visually stunning, modern, trustworthy — patients must feel confident
- Mobile-first, fully responsive, fast-loading (all inline CSS/JS)
- Conversion-focused: every section drives toward phone call or WhatsApp
- Professional medical aesthetic: clean, calm, credible
Output ONLY a single complete HTML file. No explanations, no markdown code blocks. All CSS in <style>, all JS in <script>."""


def build_prompt(lead: dict) -> str:
    niche = lead["niche"]
    name = lead["name"]
    services = lead.get("services", [])
    colors = lead.get("colors", {"primary": "#0a1628", "accent": "#00b4d8"})
    phone = lead["phone"]
    wa = lead["wa_number"]
    address = lead.get("address", "Toshkent, O'zbekiston")
    slug = lead["slug"]

    services_text = "\n".join(f"- {s}" for s in services)
    niche_ru = "Стоматология" if niche == "Dentistry" else "Медицинская клиника"
    niche_uz = "Stomatologiya" if niche == "Dentistry" else "Tibbiyot klinikasi"

    hero_desc = (
        "Sog'lom tish — baxtli hayot. Zamonaviy uskunalar va tajribali shifokorlar."
        if niche == "Dentistry"
        else "Sog'lig'ingiz bizning ustuvorligimiz. Malakali shifokorlar, zamonaviy diagnostika."
    )

    return f"""Create a complete production-ready landing page for:

BUSINESS: {name}
TYPE: {niche_ru} / {niche_uz}
PHONE: {phone}
WHATSAPP: https://wa.me/{wa}?text=Salom!%20{name.replace(' ','%20')}ga%20murojaat%20qilmoqchiman
ADDRESS: {address}
PRIMARY COLOR: {colors.get('primary','#0a1628')}
ACCENT COLOR: {colors.get('accent','#00b4d8')}

SERVICES:
{services_text}

DESIGN REQUIREMENTS:
1. Sticky nav with logo ({name}), menu links, "Qo'ng'iroq" button in accent color
2. Hero: full-screen gradient background using primary+accent colors, large headline in Uzbek,
   subheadline "{hero_desc}", two CTA buttons: "📞 {phone}" and "💬 WhatsApp"
3. Services section: card grid with emoji icons, hover lift effect, accent border-top
4. Why Us: 4 trust blocks — "10+ yil tajriba", "Zamonaviy uskunalar", "Kafolatlangan natija", "24/7 maslahat"
   each with large number/icon and short description
5. Doctors section: 3 doctor cards with placeholder gradient avatar, name, specialty
6. Testimonials: 3 Uzbek patient reviews with 5-star rating, name, date
7. Pricing: 3 service packages with price in UZS (e.g. 150,000 — 500,000 UZS range)
8. Contact: phone, address, WhatsApp button, simple form (ism, telefon, xabar)
9. Footer: logo, address, phone, social icons, copyright {name} 2025
10. Floating WhatsApp button fixed bottom-right

TECHNICAL:
- Single HTML file, all CSS inline in <style>, all JS in <script>
- CSS variables for primary/accent colors
- Scroll reveal with IntersectionObserver (no libraries)
- Smooth scroll, mobile hamburger menu
- All text in Uzbek language
- WhatsApp link: https://wa.me/{wa}?text=Salom!
- Phone link: tel:{phone}"""


def generate_site(lead: dict) -> str:
    slug = lead["slug"]
    out_file = OUTPUT_DIR / f"{slug}.html"

    if out_file.exists():
        print(f"  ⏭ Skip (exists): {slug}.html")
        return str(out_file)

    prompt = build_prompt(lead)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    html = response.content[0].text.strip()
    # Strip markdown code fences if present
    if html.startswith("```"):
        html = html.split("\n", 1)[1]
        if html.endswith("```"):
            html = html.rsplit("```", 1)[0]

    out_file.write_text(html, encoding="utf-8")
    print(f"  ✅ Generated: {slug}.html ({len(html)//1024}KB)")
    return str(out_file)


def main():
    with open(LEADS_FILE, encoding="utf-8") as f:
        leads = json.load(f)

    print(f"🦷 Generating {len(leads)} dental/clinic websites...\n")
    success, failed = 0, []

    for i, lead in enumerate(leads, 1):
        print(f"[{i:3d}/{len(leads)}] {lead['name']} ({lead['niche']})")
        try:
            generate_site(lead)
            success += 1
            # Small delay to respect rate limits
            if i % 10 == 0:
                print(f"\n  ⏸ Pause 3s after {i} sites...\n")
                time.sleep(3)
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed.append(lead["slug"])

    print(f"\n{'='*50}")
    print(f"✅ Success: {success}/{len(leads)}")
    if failed:
        print(f"❌ Failed ({len(failed)}): {', '.join(failed)}")
    print(f"\n🌐 View at: http://localhost:5055/generated_sites/")


if __name__ == "__main__":
    main()
