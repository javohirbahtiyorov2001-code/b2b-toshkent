"""
Netlify Auto-Deploy — pushes a generated HTML file to a new Netlify site.
Returns the live URL. Triggered after website_generator.py completes.
"""

import os
import requests
import zipfile
import tempfile
from pathlib import Path

NETLIFY_TOKEN = os.environ.get("NETLIFY_TOKEN")
BASE_URL = "https://api.netlify.com/api/v1"
HEADERS = {"Authorization": f"Bearer {NETLIFY_TOKEN}", "Content-Type": "application/json"}


def create_site(site_name: str) -> dict:
    """Create a new Netlify site with a custom subdomain."""
    slug = site_name.lower().replace(" ", "-").replace("_", "-")
    resp = requests.post(
        f"{BASE_URL}/sites",
        headers=HEADERS,
        json={"name": slug},
    )
    if resp.status_code not in (200, 201):
        # Name taken — add random suffix
        import random, string
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        resp = requests.post(
            f"{BASE_URL}/sites",
            headers=HEADERS,
            json={"name": f"{slug}-{suffix}"},
        )
    resp.raise_for_status()
    return resp.json()


def deploy_html(html_path: str, site_name: str = None) -> str:
    """
    Deploy a single HTML file to Netlify.
    Returns the live URL (https://xxx.netlify.app).
    """
    path = Path(html_path)
    if not path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    name = site_name or path.stem

    print(f"Creating Netlify site: {name}")
    site = create_site(name)
    site_id = site["id"]
    site_url = site["ssl_url"] or site["url"]
    print(f"  Site created: {site_url}")

    # Zip the HTML as index.html
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        zip_path = tmp.name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(path, "index.html")

    print("Deploying...")
    with open(zip_path, "rb") as f:
        deploy_resp = requests.post(
            f"{BASE_URL}/sites/{site_id}/deploys",
            headers={
                "Authorization": f"Bearer {NETLIFY_TOKEN}",
                "Content-Type": "application/zip",
            },
            data=f,
        )
    deploy_resp.raise_for_status()
    deploy_data = deploy_resp.json()

    live_url = deploy_data.get("ssl_url") or deploy_data.get("url") or site_url
    print(f"\n Live: {live_url}")
    return live_url


def full_pipeline(html_path: str, business_name: str = None) -> str:
    """Generate site → deploy → return URL."""
    return deploy_html(html_path, business_name)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python netlify_deploy.py path/to/site.html [Business Name]")
    else:
        url = deploy_html(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
        print(f"\nDeploy complete: {url}")
