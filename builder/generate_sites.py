#!/usr/bin/env python3
"""
Unique website generator — applies niche-specific design systems per lead.
Each niche gets a completely different layout, fonts, color treatment, and style.
"""

import os, json, time
from pathlib import Path
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

ROOT = Path(__file__).parent.parent
OUTPUT_DIR = ROOT / "generated_sites"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── NICHE DESIGN SYSTEMS ──────────────────────────────────────────────────────

DESIGN_SYSTEMS = {
    "Restaurant": {
        "style": "Bold & Vibrant — Playfair Display SC headings, warm red/gold palette, full-bleed food photography placeholders, large menu cards, festive feel",
        "fonts": "Google Fonts: 'Playfair Display SC' for headings (weight 700-900), 'Karla' for body",
        "hero": "Full-screen hero with parallax overlay, big bold restaurant name in serif font, 'Rezervatsiya qilish' CTA button in deep red",
        "sections": "Menu section with card grid (emoji dish icons, UZS prices), Atmosphere gallery (3 gradient image placeholders), Chef intro, Testimonials in quote blocks, Map + hours",
        "colors": "Deep burgundy #2D0A00 as primary, crimson #DC2626 as accent, warm gold #A16207 as highlight, cream #FEF2F2 background for light sections",
        "animations": "Fade-in menu cards, hover scale on dishes, smooth parallax on hero",
        "unique": "Large menu grid with categories (Asosiy taomlar, Ichimliklar, Shirinliklar), reservation form with date picker"
    },
    "Fitness": {
        "style": "Dark Neon Energy — Orbitron headings, electric orange on near-black, aggressive typography, gym energy",
        "fonts": "Google Fonts: 'Orbitron' for headings (weight 800-900), 'JetBrains Mono' for stats/numbers, 'Inter' for body",
        "hero": "Full-screen dark hero #0F1923 with orange gradient glow, large stat counters (500+ Members, 50+ Classes), energy text 'KUCHINGIZNI KASHF ETING'",
        "sections": "Services as dark bento grid, Coaches with neon border cards, Membership pricing as 3 tier cards (highlight middle), Class schedule table, Before/after transformation section",
        "colors": "Deep charcoal #0F1923 primary, electric orange #F97316 accent, neon yellow #FACC15 for stats, white text",
        "animations": "Counter animation on stats, slide-in from left for sections, pulsing glow on CTA buttons",
        "unique": "Animated counter numbers (0 → 500+ members), class timetable with filter by day, BMI calculator widget"
    },
    "Beauty": {
        "style": "Soft Luxury — Playfair Display headings, rose pink palette, soft shadows, feminine elegance, glassmorphism cards",
        "fonts": "Google Fonts: 'Playfair Display' italic for headings (weight 400-700), 'Inter' for body",
        "hero": "Soft gradient hero #FDF2F8 → #EDE9FE, floating glass card with booking form, large elegant headline in italic serif",
        "sections": "Services as soft pink cards with hover glow, Masters/team section with circular photos, Before-After slider, Loyalty program section, Reviews with star ratings and pink accents",
        "colors": "Blush #FDF2F8 background, rose pink #EC4899 primary, soft violet #8B5CF6 accent, champagne gold for highlights",
        "animations": "Soft fade-in, gentle scale on hover, floating elements",
        "unique": "Online booking widget with service selector + master selector + date/time picker, before-after image comparison slider, loyalty card display"
    },
    "Auto": {
        "style": "Industrial Minimalism — Space Grotesk bold headings, dark slate palette, technical precision, high contrast",
        "fonts": "Google Fonts: 'Space Grotesk' weight 700-800 for headings, 'Inter' for body",
        "hero": "Dark full-screen hero with diagonal stripe accent, large bold service headline, car silhouette SVG graphic, urgent CTA 'HOZIROQ YOZING'",
        "sections": "Services as numbered list cards (01, 02, 03...), Diagnostic checklist section, Work stages timeline (Qabul → Diagnostika → Ta'mirlash → Topshirish), Price table, Trust badges (10+ yil, 5000+ mashina)",
        "colors": "Dark slate #1E293B primary, emerald green #059669 accent, light gray #F8FAFC for backgrounds, white text on dark",
        "animations": "Slide-in from left on service cards, count-up on stats, hover underline effect",
        "unique": "Service cost calculator (choose services → get estimate), work stages progress bar, downloadable service checklist"
    },
    "Hotel": {
        "style": "Liquid Glass Luxury — Playfair Display SC headings, navy/gold palette, glassmorphism panels, premium hotel feel",
        "fonts": "Google Fonts: 'Playfair Display SC' for headings, 'Karla' for body text",
        "hero": "Full-bleed luxury hero with glass panel overlay, gold shimmer border, 'Toshkent yuragida dam oling' headline, two CTAs: Book Now + Virtual Tour",
        "sections": "Rooms as large horizontal cards with gradient previews and gold price tags, Amenities as icon grid, About hotel with gold timeline, Guest reviews in elegant blockquotes, Location map section",
        "colors": "Deep navy #1E3A8A primary, warm gold #A16207 accent, champagne white, midnight blue for dark sections",
        "animations": "Parallax hero, fade-in room cards, shimmer on gold elements",
        "unique": "Room availability checker (check-in/out dates + guests → price), amenity icons with tooltips, virtual tour button"
    },
    "Construction": {
        "style": "Bold Architecture — Inter weight 800 headings, dark concrete palette, strong geometry, professional authority",
        "fonts": "Google Fonts: 'Inter' weight 800-900 for headings, 'Inter' 400 for body",
        "hero": "Split hero: left dark #0F172A with big bold headline + stats, right with diagonal construction site gradient image placeholder",
        "sections": "Projects as masonry portfolio grid (3-column with different sizes), Services as icon cards with orange accent borders, Process timeline (5 steps), Team section, Materials/tech badges, Client logos row",
        "colors": "Near-black #0F172A primary, burnt orange #EA580C accent, concrete gray #64748B, white for contrast",
        "animations": "Stagger reveal on project cards, counter animation on years/projects/clients, horizontal scroll on project gallery",
        "unique": "Project calculator (m² input → price estimate), before/after project photos, materials quality certificates section"
    },
    "Dentistry": {
        "style": "Clean Medical Trust — Inter headings, calming blue/teal palette, clinical cleanliness, professional medical aesthetic",
        "fonts": "Google Fonts: 'Inter' weight 700 for headings, 'Inter' 400 for body",
        "hero": "Clean white/light blue hero, large confident headline 'Sog\'lom tish — baxtli hayot', doctor team photo placeholder, appointment booking form embedded",
        "sections": "Services as clean card grid with tooth emoji icons and price ranges, Doctors as professional cards with specialties, Technology/equipment section, Before-After smile gallery, Patient reviews, FAQ accordion",
        "colors": "Clinical blue #0A1628 primary, bright teal #00b4d8 accent, clean white #F8FAFC background, soft blue tints",
        "animations": "Smooth fade-in, subtle shadow on hover, accordion open/close for FAQ",
        "unique": "Appointment booking form with service selector + doctor selector + date, tooth pain checker widget, payment installment calculator"
    },
    "Clinic": {
        "style": "Medical Authority — Trust-building design, Nunito headings, medical green palette, calm and professional",
        "fonts": "Google Fonts: 'Nunito' weight 700-800 for headings, 'Inter' for body",
        "hero": "Split hero with medical cross motif, 'Sog\'lig\'ingiz — bizning ustuvorligimiz' headline, doctor stats (15+ shifokor, 10,000+ bemor), appointment CTA",
        "sections": "Departments as icon cards (Terapevt, Kardiolog, Nevropatolog...), Doctors roster with specialties, Laboratory services, Insurance/payment section, Emergency contacts prominently displayed",
        "colors": "Medical green #065F46 primary, bright green #10B981 accent, clean white, light gray backgrounds",
        "animations": "Fade in sections, hover lift on doctor cards, pulse on emergency contact",
        "unique": "Department finder (symptom → recommend department), online appointment form with doctor selector, lab test price list accordion"
    }
}

DEFAULT_DESIGN = DESIGN_SYSTEMS["Clinic"]

SYSTEM_PROMPT = """You are an elite frontend developer and designer specializing in unique, conversion-optimized business websites.
Your websites are:
- Visually STUNNING and completely unique per business type — no generic templates
- Production-ready with real polish: proper spacing, hierarchy, micro-interactions
- Mobile-first, fully responsive, fast-loading (all inline CSS/JS, no external libraries except Google Fonts)
- Conversion machines: every section drives toward WhatsApp or phone contact
- Technically excellent: CSS custom properties, smooth animations, accessible markup

Output ONLY a single complete HTML file. No explanations, no markdown code blocks, no comments about what you're doing.
The file starts with <!DOCTYPE html> and ends with </html>.
All CSS in <style> tags, all JS in <script> tags."""


def build_prompt(lead: dict) -> str:
    niche = lead.get("niche", "Clinic")
    ds = DESIGN_SYSTEMS.get(niche, DEFAULT_DESIGN)

    name = lead["name"]
    phone = lead["phone"]
    wa = lead.get("wa_number", phone.replace("+", "").replace(" ", ""))
    address = lead.get("address", "Toshkent, O'zbekiston")
    district = lead.get("district", "Toshkent")
    services = lead.get("services", [])
    colors = lead.get("colors", {})
    primary = colors.get("primary", "#0a1628")
    accent = colors.get("accent", "#00b4d8")
    instagram = lead.get("instagram", "")
    fonts = ds.get("fonts", "")
    design_style = lead.get("design_style", "")

    services_text = "\n".join(f"  - {s}" for s in services) if services else "  - Asosiy xizmatlar"

    wa_link = f"https://wa.me/{wa}?text=Salom!%20{name.replace(' ', '%20')}ga%20murojaat%20qilmoqchiman"
    insta_link = f"https://instagram.com/{instagram.replace('@', '')}" if instagram else ""

    return f"""Create a COMPLETE, PRODUCTION-READY, VISUALLY UNIQUE landing page for this business:

═══ BUSINESS INFO ═══
Name: {name}
Type: {niche}
Phone: {phone}  →  tel:{phone}
WhatsApp: {wa_link}
Address: {address}, {district} tumani
Instagram: {insta_link or 'Not available'}
Brand Primary Color: {primary}
Brand Accent Color: {accent}

Services offered:
{services_text}

═══ DESIGN SYSTEM — FOLLOW EXACTLY ═══
Style: {ds['style']}

Typography: {ds['fonts']}

Hero Section: {ds['hero']}

Page Sections (implement ALL of these):
{ds['sections']}

Color Palette:
{ds['colors']}
→ Also incorporate brand colors: Primary={primary}, Accent={accent}

Animations & Interactions:
{ds['animations']}

Unique Feature to Include:
{ds['unique']}

═══ TECHNICAL REQUIREMENTS ═══
1. Load fonts from Google Fonts CDN (use @import in CSS)
2. CSS custom properties: --primary, --accent, --bg, --text etc.
3. Hero must be visually impressive and fill viewport height
4. Sticky navigation with logo, menu links, CTA button
5. Smooth scroll, mobile hamburger menu (vanilla JS)
6. Floating WhatsApp button fixed bottom-right: {wa_link}
7. All CTAs use: tel:{phone} or {wa_link}
8. Scroll reveal animations using IntersectionObserver (no libraries)
9. All text content in UZBEK language
10. Mobile-first responsive (breakpoints: 768px, 1024px)
11. Footer: {name}, {address}, {phone}, social links, © 2025

═══ CONTENT RULES ═══
- Write realistic, professional Uzbek content for ALL sections
- Use realistic Uzbek names for testimonials (Aziz T., Malika R., Jahon S.)
- Prices in UZS (realistic for Tashkent market)
- 3-5 items per service section
- 3 testimonials minimum with 5-star ratings

Output the complete HTML starting with <!DOCTYPE html>. Make it genuinely impressive."""


def generate_site(lead: dict) -> str:
    slug = lead.get("slug") or lead["name"].lower().replace(" ", "-")
    out_file = OUTPUT_DIR / f"{slug}.html"

    if out_file.exists():
        print(f"  ⏭ Skip (exists): {slug}.html")
        return str(out_file)

    print(f"  🎨 Generating [{lead['niche']}] design for: {lead['name']}")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(lead)}]
    )

    html = response.content[0].text.strip()
    if html.startswith("```"):
        html = "\n".join(html.split("\n")[1:])
        if html.endswith("```"):
            html = html.rsplit("```", 1)[0]

    out_file.write_text(html, encoding="utf-8")
    print(f"  ✅ Done: {slug}.html ({len(html)//1024}KB)")
    return str(out_file)


def main():
    import sys
    all_files = [
        ROOT / "pipeline" / "dental_clinic_leads.json",
        ROOT / "pipeline" / "new_leads_100.json",
        ROOT / "pipeline" / "seed_leads.json",
    ]

    leads = []
    for f in all_files:
        if f.exists():
            with open(f, encoding="utf-8") as fp:
                leads.extend(json.load(fp))

    # Optional niche filter: python3 generate_sites.py Beauty
    if len(sys.argv) > 1:
        niche_filter = sys.argv[1]
        leads = [l for l in leads if l.get("niche", "").lower() == niche_filter.lower()]
        print(f"🎯 Filtered to niche: {niche_filter} ({len(leads)} leads)")

    print(f"\n🚀 Generating {len(leads)} unique websites...\n")
    print(f"Design systems: {list(DESIGN_SYSTEMS.keys())}\n")

    success, failed = 0, []
    for i, lead in enumerate(leads, 1):
        print(f"[{i:3d}/{len(leads)}] {lead['name']} ({lead.get('niche','?')})")
        try:
            generate_site(lead)
            success += 1
            if i % 10 == 0:
                print(f"\n  ⏸ Pause 3s...\n")
                time.sleep(3)
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed.append(lead.get("slug", lead["name"]))

    print(f"\n{'='*50}")
    print(f"✅ Success: {success}/{len(leads)}")
    if failed:
        print(f"❌ Failed: {', '.join(failed)}")
    print(f"\n🌐 View at: http://localhost:5055/generated_sites/")
    print(f"\nUsage:")
    print(f"  python3 builder/generate_sites.py              # all leads")
    print(f"  python3 builder/generate_sites.py Beauty       # beauty niche only")
    print(f"  python3 builder/generate_sites.py Restaurant   # restaurant only")


if __name__ == "__main__":
    main()
