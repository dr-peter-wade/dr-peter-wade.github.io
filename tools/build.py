#!/usr/bin/env python3
"""Render the educational profile from the workspace's shared Peter Wade data."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT.parents[1] / "shared_data" / "peter.json"
PAGE = ROOT / "site" / "index.html"
CONFIG = ROOT / "site" / "site-config.js"


def replace_block(source: str, marker: str, content: str) -> str:
    pattern = re.compile(
        rf"(<!-- SHARED_{marker}_START -->).*?(<!-- SHARED_{marker}_END -->)", re.S
    )
    updated, count = pattern.subn(lambda match: f"{match[1]}\n{content}\n{match[2]}", source)
    if count != 1:
        raise ValueError(f"Expected one {marker} block in {PAGE}")
    return updated


def render(data: dict) -> str:
    profile = data["education_profile"]
    publications = {item["url"]: item for item in data["publications"]}
    featured = [publications[url] for url in profile["featured_publication_urls"]]
    escape = html.escape
    tags = "".join(f"<span>{escape(topic)}</span>" for topic in profile["topics"])
    links = "".join(
        f'<a href="{escape(item["url"], quote=True)}" target="_blank" '
        f'rel="noopener noreferrer">{escape(item["title"])} · '
        f'{escape(item["journal"])} ({escape(str(item["year"]))}) ↗</a>'
        for item in featured
    )
    profile_html = (
        f'<span class="name-label">{escape(data["person"].upper())}</span>'
        f'<p class="large-copy">{escape(profile["heading"])}</p>'
        f'<p>{escape(profile["experience"])}</p>'
        f'<p>{escape(profile["purpose"])}</p>'
        f'<div class="about-tags">{tags}</div>'
        '<details class="research-links"><summary>Explore selected research '
        '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M12 5v14M5 12h14"/></svg></summary>'
        f'{links}<p>Selected co-authored research. Publication links do not imply '
        'institutional endorsement of this independent educational site.</p></details>'
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": data["person"].removeprefix("Dr "),
        "honorificPrefix": "Dr",
        "knowsAbout": profile["topics"],
    }
    schema_html = (
        '<script type="application/ld+json">'
        + json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )
    source = PAGE.read_text(encoding="utf-8")
    return replace_block(replace_block(source, "PROFILE", profile_html), "SCHEMA", schema_html)


def render_config(data: dict) -> str:
    source = CONFIG.read_text(encoding="utf-8")
    match = re.search(r"Object\.freeze\((\{.*?\})\);", source, re.S)
    if not match:
        raise ValueError(f"Could not read {CONFIG}")
    config = json.loads(match[1])
    service = data["enquiry_service"]
    config.update(
        enquiryEndpoint=service["endpoint"],
        turnstileSiteKey=service["turnstile_site_key"],
        enquiryServiceEnabled=service["enabled"],
    )
    return source[:match.start(1)] + json.dumps(config, indent=2, ensure_ascii=True) + source[match.end(1):]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the page is stale")
    args = parser.parse_args()
    data = json.loads(SHARED.read_text(encoding="utf-8"))
    outputs = ((PAGE, render(data)), (CONFIG, render_config(data)))
    if args.check:
        if any(rendered != path.read_text(encoding="utf-8") for path, rendered in outputs):
            parser.error("Shared educational output is stale; run tools/build.py")
        print("Shared educational output is current.")
    else:
        for path, rendered in outputs:
            if rendered != path.read_text(encoding="utf-8"):
                path.write_text(rendered, encoding="utf-8")
        print("Rendered shared educational output.")


if __name__ == "__main__":
    main()
