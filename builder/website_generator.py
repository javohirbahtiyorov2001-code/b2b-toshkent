"""
AI Website Builder — generates full HTML/CSS/JS websites using Claude API.
Trigger: CRM deal marked "Won" → onboarding form → this script → Netlify deploy
"""

import os
import json
import asyncio
from pathlib import Path
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
OUTPUT_DIR = Path(__file__).parent.parent / "generated_sites"
OUTPUT_DIR.mkdir(exist_ok=True)


SYSTEM_PROMPT = """You are an elite web designer and developer specializing in modern,
conversion-optimized business websites for Uzbekistan companies. Your designs are:
- Visually stunning with smooth animations and micro-interactions
- Mobile-first and fully responsive
- Fast-loading (minimal dependencies, inline CSS/JS)
- Built for trust: professional, clean, modern aesthetic
- Inspired by top-tier agencies like motionsites.ai — bold typography,
  subtle gradients, scroll animations, glassmorphism effects where appropriate
- Bilingual-ready (Uzbek/Russian content slots)
- CTA-focused: every section drives toward phone call or WhatsApp contact

Output ONLY a single complete HTML file. No explanations, no markdown code blocks.
The file must work standalone — all CSS and JS inline."""


def build_prompt(brief: dict) -> str:
    niche = brief.get("niche", "Business")
    name = brief.get("business_name", "Company")
    services = brief.get("services", [])
    colors = brief.get("colors", {"primary": "#1a1a2e", "accent": "#e94560"})
    phone = brief.get("phone", "+998 XX XXX XX XX")
    address = brief.get("address", "Toshkent, O'zbekiston")
    language = brief.get("language", "uzbek")
    website_type = brief.get("type", "landing")  # landing | multipage | webapp

    services_text = "\n".join(f"- {s}" for s in services) if services else "- Main services here"

    lang_instruction = {
        "uzbek": "Write all content in Uzbek language",
        "russian": "Write all content in Russian language",
        "bilingual": "Write content in both Uzbek and Russian (Uzbek primary, Russian below each section)",
    }.get(language, "Write content in Uzbek language")

    return f"""Create a complete, production-ready {website_type} page for:

BUSINESS: {name}
NICHE: {niche}
PHONE: {phone}
ADDRESS: {address}
PRIMARY COLOR: {colors.get('primary', '#1a1a2e')}
ACCENT COLOR: {colors.get('accent', '#e94560')}
LANGUAGE: {lang_instruction}

SERVICES/PRODUCTS:
{services_text}

DESIGN REQUIREMENTS:
1. Hero section with animated gradient background, bold headline, subheadline, and two CTAs
   (Call Now button + WhatsApp button linking to wa.me/{phone.replace('+','').replace(' ','')})
2. Services section — card grid with hover effects and subtle icons (use emoji or SVG)
3. Why Choose Us — 4 trust signals with icon + stat + description
4. Gallery/Portfolio placeholder section (3-6 image placeholder cards with gradient fills)
5. Testimonials — 3 fake but realistic Uzbek client quotes with names and star ratings
6. Contact section — phone, address, WhatsApp CTA, simple contact form (name, phone, message)
7. Sticky header with smooth scroll navigation and mobile hamburger menu
8. Scroll reveal animations using Intersection Observer (no external libraries)
9. Footer with social links, phone, address, copyright

TECHNICAL:
- Single HTML file, all CSS in <style>, all JS in <script>
- CSS variables for colors, dark/light mode toggle optional
- Smooth scroll, sticky nav, hamburger menu all in vanilla JS
- WhatsApp floating button fixed bottom-right
- Meta tags for SEO (Uzbek/Russian keywords for {niche})
- Google Fonts: use 'Inter' loaded from Google Fonts CDN
- Total output should be 800-1200 lines of clean, production HTML

Output the complete HTML file starting with <!DOCTYPE html>"""


async def generate_website(brief: dict, stream: bool = True) -> str:
    """Generate a website from a client brief. Returns complete HTML."""
    prompt = build_prompt(brief)
    slug = brief.get("business_name", "site").lower().replace(" ", "-")

    print(f"\n Generating website for: {brief.get('business_name')}")
    print(f"   Niche: {brief.get('niche')} | Type: {brief.get('type', 'landing')}")
    print(f"   Language: {brief.get('language', 'uzbek')}")
    print("   Calling Claude API (streaming)...\n")

    html_parts = []

    if stream:
        with client.messages.stream(
            model="claude-opus-4-8",
            max_tokens=8000,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        ) as stream_ctx:
            for text in stream_ctx.text_stream:
                print(text, end="", flush=True)
                html_parts.append(text)
        html = "".join(html_parts)
    else:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=8000,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        html = response.content[-1].text

    # Save the file
    output_path = OUTPUT_DIR / f"{slug}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = len(html.encode()) / 1024
    print(f"\n\n Website saved: {output_path} ({size_kb:.1f} KB)")
    return str(output_path)


async def generate_batch(briefs: list[dict]) -> list[str]:
    """Generate multiple websites sequentially (rate limit safe)."""
    paths = []
    for brief in briefs:
        try:
            path = await generate_website(brief)
            paths.append(path)
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error generating {brief.get('business_name')}: {e}")
    return paths


# ── Demo briefs for testing ──────────────────────────────────────────────────

DEMO_BRIEFS = [
    {
        "business_name": "Shifo Medical Center",
        "niche": "Clinic",
        "type": "landing",
        "services": [
            "Terapevt va umumiy amaliyot",
            "Stomatologiya",
            "Ko'z shifokori",
            "Laboratoriya tahlillari",
            "UZI va diagnostika",
        ],
        "colors": {"primary": "#0a2342", "accent": "#00b4d8"},
        "phone": "+998 90 123 45 67",
        "address": "Toshkent, Yunusobod tumani, 14-mavze",
        "language": "uzbek",
    },
    {
        "business_name": "BuildPro Qurilish",
        "niche": "Construction",
        "type": "landing",
        "services": [
            "Turar-joy qurilishi",
            "Ofis va tijoriy ob'ektlar",
            "Remont va ta'mirlash",
            "Loyihalash va dizayn",
            "Kalit topshiriq",
        ],
        "colors": {"primary": "#1c1c1e", "accent": "#f4a261"},
        "phone": "+998 91 234 56 78",
        "address": "Toshkent, Chilonzor tumani",
        "language": "uzbek",
    },
    {
        "business_name": "Baraka Restoran",
        "niche": "Restaurant",
        "type": "landing",
        "services": [
            "O'zbek milliy taomlari",
            "Banket va to'ylar",
            "Korporativ ziyofatlar",
            "Yetkazib berish",
            "Kafeteri va fast food",
        ],
        "colors": {"primary": "#2d0a00", "accent": "#e63946"},
        "phone": "+998 99 345 67 89",
        "address": "Toshkent, Mirzo Ulug'bek tumani",
        "language": "uzbek",
    },
]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Generate one demo site
        asyncio.run(generate_website(DEMO_BRIEFS[0]))
    elif len(sys.argv) > 1 and sys.argv[1] == "all":
        # Generate all demo sites
        asyncio.run(generate_batch(DEMO_BRIEFS))
    elif len(sys.argv) > 1:
        # Load brief from JSON file
        with open(sys.argv[1]) as f:
            brief = json.load(f)
        asyncio.run(generate_website(brief))
    else:
        print("Usage:")
        print("  python website_generator.py demo      # Generate clinic demo")
        print("  python website_generator.py all       # Generate all 3 demos")
        print("  python website_generator.py brief.json # Generate from JSON file")
