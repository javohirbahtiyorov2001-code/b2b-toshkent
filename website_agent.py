#!/usr/bin/env python3
"""
Website Designer Agent
- Generates 3 AI images per lead via HuggingFace FLUX
- Claude builds a unique cinematic HTML site around them
- Design inspired by motionsites.ai

Usage:
  python3 website_agent.py                          # first 5 Dentistry leads
  python3 website_agent.py --slug dream-dental
  python3 website_agent.py --id 101
  python3 website_agent.py --niche Dentistry --limit 9
  python3 website_agent.py --all
"""

import json, sys, os, re, time, argparse
from urllib.parse import quote
import anthropic

# ── Config ────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
ENV  = os.path.join(BASE, ".env")

def load_env():
    if os.path.exists(ENV):
        for line in open(ENV):
            k, _, v = line.strip().partition("=")
            if k and v:
                os.environ.setdefault(k.strip(), v.strip())

load_env()

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
HF_TOKEN      = os.environ.get("HF_TOKEN", "")          # optional, higher rate limit
OUT_DIR       = os.path.join(BASE, "generated_sites")
ASSETS_DIR    = os.path.join(OUT_DIR, "assets")

LEAD_FILES = [
    os.path.join(BASE, "pipeline", "dental_clinic_leads.json"),
    os.path.join(BASE, "pipeline", "new_leads_100.json"),
    os.path.join(BASE, "pipeline", "seed_leads.json"),
]
FAKE_SOURCES = {"auto-generated", "none", ""}

# ── Pollinations.ai image URLs (free, no API key, seed=deterministic) ─────────
# URL format: https://image.pollinations.ai/prompt/{encoded}?width=W&height=H&seed=N&nologo=true

IMAGE_PROMPTS = {
    "Dentistry": [
        "modern premium dental clinic interior, sleek reception area, soft blue ambient lighting, minimalist architecture, no people, cinematic wide shot, professional architectural photography, sharp details",
        "dental treatment room with advanced equipment, bright clinical lighting, gleaming white surfaces, futuristic medical aesthetic, no people, architectural photography",
        "close-up dental tools and equipment on clean surface, soft dramatic shadows, blue and white color palette, premium product photography, dark studio background",
    ],
    "Clinic": [
        "modern private medical clinic interior, premium reception desk, warm ambient lighting, clean contemporary architecture, no people, cinematic photography",
        "medical consultation room, professional equipment, clean white and blue design, soft window light, architectural photography",
        "abstract medical concept, blue light rays, premium healthcare aesthetic, dark background, artistic photography",
    ],
    "Restaurant": [
        "upscale restaurant interior at night, warm candlelight, elegant table settings, dark wood and gold, moody cinematic atmosphere",
        "gourmet dish beautifully plated on dark slate, professional food photography, dramatic studio lighting, steam rising",
        "luxury restaurant bar, premium spirits backlit, dark ambient lighting, bokeh foreground, editorial photography",
    ],
    "Fitness": [
        "premium gym interior, modern equipment in rows, dramatic dark lighting with neon blue accents, no people, architectural photography",
        "fitness equipment close-up, black chrome dumbbells, dramatic shadows, dark background, product photography",
        "modern gym training area wide shot, orange and blue accent lighting, high ceilings, cinematic",
    ],
    "Hotel": [
        "luxury hotel lobby interior, marble floors, high ceilings, golden warm lighting, premium materials, cinematic wide angle, no people",
        "luxury hotel room, immaculate white bedding, dramatic side lighting, floor to ceiling windows, city view",
        "hotel rooftop infinity pool at dusk, city skyline, dramatic sky, premium hospitality photography",
    ],
    "Beauty": [
        "luxury beauty salon interior, rose gold and white palette, soft ring lighting, premium minimalist aesthetic, no people",
        "beauty and skincare products arranged on white marble, editorial photography, soft natural light, clean aesthetic",
        "modern spa treatment room, candles, clean white design, ambient mood lighting, premium atmosphere",
    ],
    "Education": [
        "modern university or academy building exterior, dramatic architectural photography, blue sky, contemporary design",
        "premium modern classroom, large windows, natural light, clean minimalist furniture, no students",
        "library interior, dramatic bookshelves, warm lighting, academic atmosphere, cinematic",
    ],
    "Construction": [
        "modern architectural project under construction, dramatic sky, cranes, cinematic golden hour photography",
        "premium construction materials arranged aesthetically, concrete and steel, industrial photography, dramatic lighting",
        "modern completed building exterior, glass facade, dramatic sky reflection, architectural photography",
    ],
    "Real Estate": [
        "luxury modern apartment interior, floor to ceiling windows, city view, minimalist design, golden hour lighting",
        "premium real estate exterior, modern architecture, manicured garden, dramatic sky",
        "luxury living room interior, designer furniture, soft ambient lighting, premium aesthetic",
    ],
    "Auto Service": [
        "premium auto service center interior, clean epoxy floor, modern equipment, dramatic lighting, no people",
        "sports car in luxury garage, dramatic studio lighting, dark background, reflective floor",
        "automotive tools and equipment arranged professionally, industrial aesthetic, dark dramatic background",
    ],
}

def get_prompts(niche):
    return IMAGE_PROMPTS.get(niche, [
        f"premium {niche.lower()} business interior, modern minimalist design, dramatic cinematic lighting, no people, architectural photography",
        f"professional {niche.lower()} workspace, clean aesthetic, ambient lighting, dark background, cinematic",
        f"abstract {niche.lower()} concept, premium materials, dramatic shadows, artistic editorial photography",
    ])

def pollinations_url(prompt, width, height, seed):
    """Returns a Pollinations.ai URL that generates a consistent AI image."""
    encoded = quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&enhance=true"

def get_image_urls(lead):
    """Returns 3 Pollinations.ai image URLs for a lead (no download needed)."""
    niche   = lead.get("niche", "Clinic")
    lid     = lead.get("id", 1)
    prompts = get_prompts(niche)
    sizes   = [(1400, 800), (1400, 700), (800, 800)]
    seeds   = [lid * 7, lid * 7 + 111, lid * 7 + 222]
    return [pollinations_url(p, w, h, s) for p, (w, h), s in zip(prompts[:3], sizes, seeds)]

# ── Lead helpers ──────────────────────────────────────────────────────────────
def load_all_leads():
    leads = []
    for f in LEAD_FILES:
        if os.path.exists(f):
            leads.extend(json.load(open(f)))
    return leads

def is_real(lead):
    return (lead.get("source") or "") not in FAKE_SOURCES

def find_lead(all_leads, slug=None, lead_id=None):
    for l in all_leads:
        if slug   and l.get("slug") == slug:            return l
        if lead_id and str(l.get("id")) == str(lead_id): return l
    return None

# ── Claude prompt ─────────────────────────────────────────────────────────────
SYSTEM = """You are a world-class web designer who creates cinematic, premium websites inspired by motionsites.ai. Your designs are dark, bold, and feel like they were made by a top agency in 2025.

ABSOLUTE RULES:
1. Output ONLY raw HTML. No markdown fences, no explanation. Start with <!DOCTYPE html>.
2. All CSS inside <style>. No frameworks.
3. Google Fonts via <link> — pick one strong display font (Syne, Cabinet Grotesk, Space Grotesk, Bebas Neue, or Clash Display feel) + Inter for body.
4. Write ALL HTML body content. Never stop at CSS. The <body> is the most important part.
5. Keep CSS under 300 lines. No over-engineering. Prioritize the HTML content.
6. All text in Uzbek language with realistic copy.
7. Make it look like motionsites.ai — cinematic dark base, glassmorphism cards, bold oversized type, gradient glows, scroll fade-in animations."""

def build_prompt(lead, img_paths):
    name    = lead.get("name", "Klinika")
    niche   = lead.get("niche", "Clinic")
    phone   = lead.get("phone", "+998900000000")
    address = lead.get("address", "Toshkent")
    primary = lead.get("colors", {}).get("primary", "#060d1f")
    accent  = lead.get("colors", {}).get("accent", "#00d4ff")
    slug    = lead.get("slug", "lead")

    hero_img     = img_paths[0] if len(img_paths) > 0 and img_paths[0] else None
    interior_img = img_paths[1] if len(img_paths) > 1 and img_paths[1] else None
    detail_img   = img_paths[2] if len(img_paths) > 2 and img_paths[2] else None

    hero_tag = f'<img src="{hero_img}" alt="{name}">' if hero_img else ""
    int_tag  = f'<img src="{interior_img}" alt="{niche}">' if interior_img else ""
    det_tag  = f'<img src="{detail_img}" alt="detail">' if detail_img else ""

    phone_clean = re.sub(r"\D", "", phone)

    return f"""Design a cinematic premium website for this Tashkent business.

BRAND:
- Name: {name}
- Niche: {niche}
- Phone: {phone}
- Address: {address}
- Primary: {primary} | Accent: {accent}

AI-GENERATED IMAGES (use these exact tags where shown):
- Hero background image: {hero_tag if hero_tag else "[no image — use CSS gradient]"}
- Interior/service section: {int_tag if int_tag else "[no image — use CSS gradient]"}
- Detail/atmosphere section: {det_tag if det_tag else "[no image — use CSS gradient]"}

DESIGN DIRECTION — motionsites.ai aesthetic:
- Dark cinematic base (near-black or deep navy from {primary})
- Hero: full-viewport split layout. LEFT = bold oversized headline (clamp 3rem→6rem), badge, subtext, 2 CTAs, 3 KPI stats. RIGHT = the hero image filling full height with a gradient overlay blending into left side.
- Glassmorphism service cards: backdrop-filter:blur(12px), semi-transparent background, glowing border
- Gradient glow blobs: radial-gradient accent color circles as decorative backgrounds (opacity 0.15-0.3)
- Scroll animations: use IntersectionObserver JS to add class "visible" → CSS transition opacity+translateY
- Typography: huge section numbers (01, 02, 03...) in accent color, oversized display headlines
- Services: 6 cards in a 2×3 grid, glassmorphism style, each with a number, title, description
- Mid section: full-width image with dark overlay + centered bold text on top
- Testimonials: 3 horizontal cards, dark glass style, star rating, Uzbek names
- CTA: full viewport dark section, huge phone number as clickable link, Telegram button
- Footer: minimal, dark

SECTIONS IN ORDER:
1. Nav — fixed, glass blur, logo + phone CTA
2. Hero — split viewport with image right and text left
3. Services — "Xizmatlar" heading with 01-06 numbered glass cards
4. Photo break — interior image full-width with overlay text
5. Why us — 3-4 big number stats
6. Testimonials — 3 glass cards
7. CTA — dark, huge phone
8. Footer

Write CSS first (max 300 lines), then the COMPLETE HTML body. Do not cut off."""

# ── Site generator ─────────────────────────────────────────────────────────────
def generate_site(lead, client, img_urls, extra_prompt=""):
    name = lead.get("name", "Lead")
    slug = lead.get("slug") or re.sub(r"[^a-z0-9]+", "-", name.lower())

    print(f"  Claude designing {name}...", end=" ", flush=True)
    t0 = time.time()

    user_prompt = build_prompt(lead, img_urls)
    if extra_prompt:
        user_prompt += f"\n\nADDITIONAL INSTRUCTIONS FROM CLIENT:\n{extra_prompt}"

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": user_prompt}]
    )

    html = msg.content[0].text.strip()
    if html.startswith("```"):
        html = re.sub(r"^```[a-z]*\n?", "", html)
        html = re.sub(r"\n?```$", "", html)

    # Verify it has a body
    if "<body" not in html:
        print(f"WARN: no <body> in output ({msg.usage.output_tokens} tokens)")

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{slug}.html")
    with open(path, "w") as f:
        f.write(html)

    elapsed = time.time() - t0
    tokens  = msg.usage.input_tokens + msg.usage.output_tokens
    print(f"done ({elapsed:.0f}s, {tokens} tok) → {slug}.html")
    return path

# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug",         help="Lead slug")
    parser.add_argument("--id",           help="Lead id")
    parser.add_argument("--niche",        help="Niche filter")
    parser.add_argument("--limit",        type=int, default=5)
    parser.add_argument("--all",          action="store_true")
    parser.add_argument("--extra-prompt", dest="extra_prompt", default="", help="Extra design instructions")
    args = parser.parse_args()

    if not ANTHROPIC_KEY:
        print("Error: ANTHROPIC_API_KEY not set in .env"); sys.exit(1)

    client     = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    all_leads  = load_all_leads()
    real_leads = [l for l in all_leads if is_real(l)]

    if args.slug:
        lead = find_lead(all_leads, slug=args.slug)
        targets = [lead] if lead else []
    elif args.id:
        lead = find_lead(all_leads, lead_id=args.id)
        targets = [lead] if lead else []
    elif args.all:
        targets = real_leads
    elif args.niche:
        targets = [l for l in real_leads if args.niche.lower() in l.get("niche","").lower()][:args.limit]
    else:
        targets = [l for l in real_leads if "dent" in (l.get("niche","") + l.get("name","")).lower()][:args.limit]

    if not targets:
        print("No leads matched."); sys.exit(0)

    print(f"\n{'='*55}")
    print(f"  Website Designer Agent — {len(targets)} site(s)")
    print(f"  Images: Pollinations.ai (free AI generation, no key needed)")
    print(f"{'='*55}\n")

    success, failed = 0, []
    for i, lead in enumerate(targets):
        name = lead.get("name", "?")
        print(f"[{i+1}/{len(targets)}] {name}")

        # Step 1: get Pollinations.ai image URLs (instant, no download)
        img_urls = get_image_urls(lead)
        print(f"  Images: {len(img_urls)} AI-generated URLs (Pollinations.ai)")

        # Step 2: Claude builds the site
        try:
            generate_site(lead, client, img_urls, extra_prompt=args.extra_prompt)
            success += 1
        except Exception as e:
            print(f"  Claude FAILED: {e}")
            failed.append(name)

        if i < len(targets) - 1:
            time.sleep(1)

    print(f"\n{'='*55}")
    print(f"  Done: {success} generated", end="")
    if failed:
        print(f", {len(failed)} failed: {', '.join(failed)}", end="")
    print(f"\n{'='*55}\n")

if __name__ == "__main__":
    main()
