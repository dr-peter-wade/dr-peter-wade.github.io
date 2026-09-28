#!/usr/bin/env python3
"""Configure an approved contact address, canonical URLs and preview/indexing state.
No domain registration, GitHub changes, email delivery or network activity occurs.
"""
from __future__ import annotations
import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'site'
MARKER = re.compile(r'<!-- SITE_URL_META -->(?:.*?<!-- END_SITE_URL_META -->)?', re.S)
EMAIL = re.compile(r"[A-Za-z0-9.!$%&'*+/=^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--email', help='Peter-approved public email address')
    p.add_argument('--url', help='Full HTTPS homepage URL, including project path when applicable')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--publish', action='store_true', help='Owner has reviewed content, contact, privacy, safeguarding and hosting suitability')
    group.add_argument('--preview', action='store_true', help='Disable contact activation and search indexing')
    args = p.parse_args()
    path = ROOT / 'site-config.js'
    source = path.read_text(encoding='utf-8')
    match = re.search(r'Object\.freeze\((\{.*?\})\);', source, re.S)
    if not match: p.error('Could not parse existing site-config.js')
    config = json.loads(match.group(1))
    if args.email is not None:
        email = args.email.strip()
        if email and (not EMAIL.fullmatch(email) or '..' in email): p.error('Provide a valid email address without URI control characters.')
        config['contactEmail'] = email
    if args.url is not None:
        raw = args.url.strip()
        u = urlsplit(raw)
        if (u.scheme != 'https' or not u.hostname or '.' not in u.hostname or u.username or u.password
                or u.query or u.fragment or re.search(r'[\s<>"\x00-\x1f]', raw) or '%' in raw or '..' in u.path):
            p.error('Use a full HTTPS homepage URL without queries, credentials, fragments or encoded paths.')
        config['siteUrl'] = raw.rstrip('/') + '/'
    if args.publish:
        if not config.get('contactEmail') or not config.get('siteUrl'):
            p.error('--publish requires both --email and --url (or existing configured values).')
        for host in (config['contactEmail'].rsplit('@', 1)[1], urlsplit(config['siteUrl']).hostname or ''):
            if host.lower() in {'example.com', 'example.org', 'example.net', 'your-domain.uk'} or host.lower().endswith(('.invalid', '.test')):
                p.error('Replace example contact/domain values before publishing.')
        config['launchApproved'] = True
    if args.preview: config['launchApproved'] = False
    approved = config.get('launchApproved') is True
    base = config.get('siteUrl', '')
    path.write_text('/* Public configuration. Never place passwords or tokens here.\n'
                    '   Update using tools/configure.py so search metadata stays consistent. */\n'
                    'window.PETER_WADE_SITE = Object.freeze(' + json.dumps(config, ensure_ascii=True, indent=2) + ');\n', encoding='utf-8')
    urls: list[str] = []
    for page in sorted(ROOT.rglob('*.html')):
        text = page.read_text(encoding='utf-8')
        indexable = approved and page.name != '404.html'
        robots = 'index, follow' if indexable else 'noindex, nofollow'
        text = re.sub(r'<meta name="robots" content="[^"]*">', f'<meta name="robots" content="{robots}">', text)
        block = '<!-- SITE_URL_META -->'
        if base and page.name != '404.html':
            relative = page.relative_to(ROOT).as_posix()
            url = base if relative == 'index.html' else base + relative
            urls.append(url)
            block += '\n  <link rel="canonical" href="' + html.escape(url, quote=True) + '">'
            block += '\n  <meta property="og:url" content="' + html.escape(url, quote=True) + '">'
            block += '\n  <meta property="og:image" content="' + html.escape(base + 'assets/social-card.png', quote=True) + '">'
        block += '\n  <!-- END_SITE_URL_META -->'
        text = MARKER.sub(lambda _: block, text)
        if base and page.name == '404.html':
            text = re.sub(r'<a id="home-link" href="[^"]*">', lambda _: '<a id="home-link" href="' + html.escape(base, quote=True) + '">', text)
        page.write_text(text, encoding='utf-8')
    robots = 'User-agent: *\nAllow: /\n' if approved else 'User-agent: *\nDisallow: /\n'
    if approved and base: robots += '\nSitemap: ' + base + 'sitemap.xml\n'
    (ROOT / 'robots.txt').write_text(robots, encoding='utf-8')
    sitemap = ROOT / 'sitemap.xml'
    if base:
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        lines += ['  <url><loc>' + html.escape(url) + '</loc></url>' for url in urls]
        sitemap.write_text('\n'.join(lines + ['</urlset>', '']), encoding='utf-8')
    elif sitemap.exists(): sitemap.unlink()
    print('Configuration updated. Mode: ' + ('approved for publication' if approved else 'preview'))
    print('No changes have been uploaded. Run tools/check_site.py' + (' --release' if approved else '') + ', then commit and deploy.')

if __name__ == '__main__': main()
