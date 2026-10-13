#!/usr/bin/env python3
"""Configure an approved contact address, canonical URLs and preview/indexing state.

The settings are stored in shared_data/education_site.json ("config"); the site is then rebuilt
from that shared data, so contact settings, canonical/share metadata, sitemap and robots stay
consistent. Run from the parent workspace. No domain registration, GitHub changes, email
delivery or network activity occurs.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT.parents[1] / 'shared_data' / 'education_site.json'
EMAIL = re.compile(r"[A-Za-z0-9.!$%&'*+/=^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--email', help='Peter-approved public email address')
    p.add_argument('--url', help='Full HTTPS homepage URL, including project path when applicable')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--publish', action='store_true', help='Owner has reviewed content, contact, privacy, safeguarding and hosting suitability')
    group.add_argument('--preview', action='store_true', help='Disable contact activation and search indexing')
    args = p.parse_args()
    if not SETTINGS.exists(): p.error(f'Run from the shared workspace: {SETTINGS} is missing.')
    data = json.loads(SETTINGS.read_text(encoding='utf-8'))
    config = data['config']
    if args.email is not None:
        email = args.email.strip()
        if email and (not EMAIL.fullmatch(email) or '..' in email): p.error('Provide a valid email address without URI control characters.')
        config['contact_email'] = email
    if args.url is not None:
        raw = args.url.strip()
        u = urlsplit(raw)
        if (u.scheme != 'https' or not u.hostname or '.' not in u.hostname or u.username or u.password
                or u.query or u.fragment or re.search(r'[\s<>"\x00-\x1f]', raw) or '%' in raw or '..' in u.path):
            p.error('Use a full HTTPS homepage URL without queries, credentials, fragments or encoded paths.')
        config['url'] = raw.rstrip('/') + '/'
    if args.publish:
        if not config.get('contact_email') or not config.get('url'):
            p.error('--publish requires both --email and --url (or existing configured values).')
        for host in (config['contact_email'].rsplit('@', 1)[1], urlsplit(config['url']).hostname or ''):
            if host.lower() in {'example.com', 'example.org', 'example.net', 'your-domain.uk'} or host.lower().endswith(('.invalid', '.test')):
                p.error('Replace example contact/domain values before publishing.')
        config['launch_approved'] = True
        config['preview'] = False
    if args.preview:
        config['launch_approved'] = False
        config['preview'] = True
    approved = config.get('launch_approved') is True
    SETTINGS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'build.py')], check=True)
    print('Configuration updated in shared_data/education_site.json. Mode: ' + ('approved for publication' if approved else 'preview'))
    print('No changes have been uploaded. Run tools/check_site.py' + (' --release' if approved else '') + ', then commit and deploy.')

if __name__ == '__main__': main()
