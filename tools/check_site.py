#!/usr/bin/env python3
"""Validate this static site without external packages or network access."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'site'
# Each page carries the site settings inline (tools/build.py), so they are read from the pages.
SETTINGS = re.compile(r'window\.PETER_WADE_SITE = Object\.freeze\((\{.*?\})\);', re.S)
POLICY = re.compile(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)">')


def policy_errors(text: str) -> list[str]:
    """The page's own security policy must come before its inline style and scripts and admit each by hash,
    or browsers would refuse to apply them."""
    match = POLICY.search(text)
    if not match:
        return ['Missing Content-Security-Policy']
    errors = []
    first = min((i for i in (text.find('<style>'), text.find('<script>')) if i >= 0), default=len(text))
    if match.start() > first:
        errors.append('Content-Security-Policy comes after content it governs')
    directives = {part.split()[0]: part.split()[1:] for part in match.group(1).split(';') if part.strip()}
    for directive, element in (('script-src', 'script'), ('style-src', 'style')):
        for body in re.findall(rf'<{element}>(.*?)</{element}>', text, re.S):
            source = "'sha256-" + base64.b64encode(hashlib.sha256(body.encode('utf-8')).digest()).decode() + "'"
            if source not in directives.get(directive, []):
                errors.append(f'Inline {element} is not admitted by the Content-Security-Policy')
    return errors

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
        text = path.read_text(encoding='utf-8')
        doc.feed(text)
        doc.errors.extend(policy_errors(text))
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
        found = {path: SETTINGS.findall(path.read_text(encoding='utf-8')) for path in docs}
        if not found.get((ROOT / 'index.html').resolve()): raise ValueError('index.html does not carry the site settings')
        settings = {text for matches in found.values() for text in matches}
        if len(settings) != 1: raise ValueError('Pages carry different site settings; rebuild with tools/build.py')
        config = json.loads(settings.pop())
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
    print(f'PASS: {len(docs)} HTML pages; local targets, fragments, core metadata, security policies and configuration checked.')
    if not args.release: print('Preview validation only. Run --release after completing owner approval and configuration.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
