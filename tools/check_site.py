#!/usr/bin/env python3
"""Validate this static site without external packages or network access."""
from __future__ import annotations
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'site'

class Document(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.errors: list[str] = []
        self.h1 = 0
        self.title = 0
        self.lang = False
        self.description = False
        self.robots = ''

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids:
                self.errors.append(f"Duplicate ID: {a['id']}")
            self.ids.add(a['id'] or '')
        if tag == 'html': self.lang = bool(a.get('lang'))
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.title += 1
        if tag == 'meta' and a.get('name') == 'description': self.description = bool(a.get('content'))
        if tag == 'meta' and a.get('name') == 'robots': self.robots = a.get('content') or ''
        if tag == 'img' and 'alt' not in a: self.errors.append('Image without an alt attribute')
        if tag == 'script' and a.get('src') and urlsplit(a['src']).scheme:
            self.errors.append('Unexpected third-party runtime script')
        for key in ('href', 'src'):
            if a.get(key): self.links.append(a[key])

    handle_startendtag = handle_starttag


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', action='store_true', help='Also require an approved contact email, canonical URL and search indexing.')
    args = parser.parse_args()
    errors: list[str] = []
    docs: dict[Path, Document] = {}
    for path in sorted(ROOT.rglob('*.html')):
        doc = Document(path)
        doc.feed(path.read_text(encoding='utf-8'))
        docs[path.resolve()] = doc
        if not doc.lang: doc.errors.append('Missing HTML language')
        if doc.h1 != 1: doc.errors.append(f'Expected one h1, found {doc.h1}')
        if doc.title != 1: doc.errors.append(f'Expected one title, found {doc.title}')
        if not doc.description: doc.errors.append('Missing meta description')
        errors.extend(f'{path.relative_to(ROOT)}: {e}' for e in doc.errors)
    for path, doc in docs.items():
        for link in doc.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                if parts.scheme == 'javascript': errors.append(f'{path.name}: javascript URL is not allowed')
                continue
            decoded = unquote(parts.path)
            target = (ROOT / decoded.lstrip('/') if decoded.startswith('/') else path.parent / decoded).resolve() if decoded else path
            if not target.is_relative_to(ROOT.resolve()):
                errors.append(f'{path.name}: local link escapes site: {link}')
                continue
            if target.is_dir(): target /= 'index.html'
            if not target.exists(): errors.append(f'{path.name}: missing target: {link}')
            elif parts.fragment and target in docs and unquote(parts.fragment) not in docs[target].ids:
                errors.append(f'{path.name}: missing fragment: {link}')
    try:
        text = (ROOT / 'site-config.js').read_text(encoding='utf-8')
        match = re.search(r'Object\.freeze\((\{.*?\})\);', text, re.S)
        if not match: raise ValueError('Cannot parse site-config.js')
        config = json.loads(match.group(1))
        if args.release:
            email = config.get('contactEmail', '')
            if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email):
                errors.append('Release needs an approved contact email')
            if not config.get('launchApproved'): errors.append('Release needs launchApproved=true')
            if not config.get('siteUrl', '').startswith('https://'): errors.append('Release needs an HTTPS siteUrl')
            for path, doc in docs.items():
                if path.name != '404.html' and 'noindex' in doc.robots:
                    errors.append(f'{path.name}: still noindex in release mode')
            if not (ROOT / 'sitemap.xml').exists(): errors.append('Release needs a sitemap')
    except (ValueError, OSError) as exc:
        errors.append(str(exc))
    if errors:
        print('\n'.join('ERROR: ' + e for e in errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(docs)} HTML pages; local targets, fragments, core metadata and configuration checked.')
    if not args.release: print('Preview validation only. Run --release after completing owner approval and configuration.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
