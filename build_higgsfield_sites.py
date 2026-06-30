#!/usr/bin/env python3
"""
Build all 9 dental sites using Higgsfield local images + Claude.
Runs generate_site() from website_agent.py with local asset paths.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from website_agent import load_all_leads, generate_site, find_lead, load_env
import anthropic

load_env()
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BASE = os.path.dirname(os.path.abspath(__file__))

# Lead slug -> local image paths (relative from generated_sites/)
LEADS = [
    {"id": 102, "slug": "korean-dental-clinic"},
    {"id": 103, "slug": "denta-service"},
    {"id": 104, "slug": "estimed-stomatologiya"},
    {"id": 105, "slug": "pearl-dental"},
    {"id": 106, "slug": "dream-smile-dental"},
    {"id": 107, "slug": "denta-lights"},
    {"id": 108, "slug": "vitamed-stomatologiya"},
    {"id": 109, "slug": "smalto-dente"},
    {"id": 110, "slug": "32-profilaktik"},
]

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
all_leads = load_all_leads()

print(f"\n{'='*55}")
print(f"  Building {len(LEADS)} dental sites with Higgsfield images")
print(f"{'='*55}\n")

success, failed = 0, []
for i, info in enumerate(LEADS):
    lead = find_lead(all_leads, slug=info["slug"]) or find_lead(all_leads, lead_id=info["id"])
    if not lead:
        print(f"[{i+1}/{len(LEADS)}] SKIP — lead {info['slug']} not found")
        failed.append(info["slug"])
        continue

    slug = info["slug"]
    img_paths = [
        f"assets/{slug}/hero.png",
        f"assets/{slug}/interior.png",
        f"assets/{slug}/detail.png",
    ]

    print(f"[{i+1}/{len(LEADS)}] {lead.get('name', slug)}")
    try:
        generate_site(lead, client, img_paths)
        success += 1
    except Exception as e:
        print(f"  FAILED: {e}")
        failed.append(slug)

print(f"\n{'='*55}")
print(f"  Done: {success}/{len(LEADS)} sites generated", end="")
if failed:
    print(f"  Failed: {', '.join(failed)}", end="")
print(f"\n{'='*55}\n")
