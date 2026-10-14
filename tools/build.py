#!/usr/bin/env python3
"""Build the educational website from the workspace's shared data.

Facts about Peter come from shared_data/peter.json; this site's copy and settings come from
shared_data/education_site.json. This file holds markup only.

    python3 tools/build.py           # regenerate the site/ pages, text downloads and settings
    python3 tools/build.py --check   # fail if any generated file is out of date

Run from the parent workspace, which holds shared_data/. Standard library only.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
sys.path.insert(0, str(ROOT.parents[1] / 'tools'))
import sitecontent as sc  # noqa: E402
import structured_data as sd  # noqa: E402

e = sc.escape
DATA = sc.load('peter.json')
GEOCHEMICAL_URL = sc.load('geochemical_site.json')['config']['url'].rstrip('/')
RAW = sc.load('education_site.json')
CONFIG = RAW['config']
sc.use_locale(CONFIG['locale'])
FACTS = sc.person_tokens(DATA) | {'resource_count': sum('card' in r for r in RAW['resources'])}
C = sc.load_site('education_site.json', FACTS)
T = C['tokens']
NAME = FACTS['name']
BASE = CONFIG['url'].rstrip('/') + '/' if CONFIG['url'] else ''
LOCALE = CONFIG['locale']
# Search indexing (preview) and contact activation (launch_approved) are separate decisions.
PREVIEW = CONFIG['preview'] is not False
APPROVED = CONFIG['launch_approved'] is True
ENTITIES = sd.Entities(DATA, GEOCHEMICAL_URL, CONFIG['url'])
ICON_PATHS = {
    'arrow': '<path d="M6 18 18 6M6 6h12v12"/>',
    'next': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'spark': '<path d="m12 2 2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5L12 2Z"/>',
    'check': '<path d="m5 12 4 4L19 6"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'print': '<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
    'flask': '<path d="M8 3h8M9 3v7l-5 8a2 2 0 0 0 2 3h12a2 2 0 0 0 2-3l-5-8V3M7 15h10"/><path d="M10 17h.01M14 18h.01"/>',
    'drop': '<path d="M12 3s7 7 7 12a7 7 0 0 1-14 0c0-5 7-12 7-12Z"/><path d="M8 15a4 4 0 0 0 4 4"/>',
    'crystal': '<path d="m12 2 8 6v10l-8 4-8-4V8l8-6Zm0 0v20M4 8l8 5 8-5M4 18l8-5 8 5"/>',
    'model': '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="m7 15 3-4 4 2 3-6M7 7h.01"/>',
    'book': '<path d="M4 4h6a3 3 0 0 1 3 3v14a4 4 0 0 0-4-2H4V4ZM20 4h-4a3 3 0 0 0-3 3v14a4 4 0 0 1 4-2h3V4Z"/>',
    'chart': '<path d="M4 3v18h17M8 17v-5M13 17V7M18 17v-8"/>',
}
WRITING_LINE = '<div class="writing-line"></div>'
HEAD_LINE = '\n  '
SRC = ROOT / 'src'
# GitHub Pages lets browsers keep files for only ten minutes, so each page carries its own styles,
# scripts and artwork: nothing to fetch again and nothing to hold up the first paint.
STYLES = (SRC / 'styles.css').read_text(encoding='utf-8').strip()
MAIN_JS = (SRC / 'main.js').read_text(encoding='utf-8').strip()
CLARITY = 'data:image/svg+xml;base64,' + base64.b64encode((SRC / 'clarity.svg').read_bytes()).decode()
NOT_FOUND_STYLE ='body{margin:0;background:#f7f7ef;color:#173c33;font:17px/1.7 system-ui,sans-serif;display:grid;min-height:100vh;place-items:center}main{max-width:620px;padding:40px}h1{font:54px/1.05 Georgia,serif;letter-spacing:-2px}p{color:#56665b}a{color:inherit}small{letter-spacing:2px;font-size:11px}'


def icon(name: str) -> str:
    return f'<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON_PATHS[name]}</svg>'


def head_assets(prefix: str = '') -> str:
    return (f'<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png">'
            f'<style>{STYLES}</style>')


def security_policy(style: str, scripts: tuple[str, ...] = ()) -> str:
    """The page's Content-Security-Policy. GitHub Pages cannot send headers, so it travels in the page:
    the inline style and scripts are admitted by hash, and the enquiry service's origins only when it is on."""
    service = DATA['enquiry_service']
    challenge = 'https://challenges.cloudflare.com'
    sending = [challenge] if service['enabled'] else []
    endpoint = ['{0.scheme}://{0.netloc}'.format(urlsplit(service['endpoint']))] if service['enabled'] else []
    policy = sc.content_security_policy({
        'default-src': ["'self'"],
        'script-src': [sc.sha256_source(script) for script in scripts] + sending or ["'none'"],
        'style-src': [sc.sha256_source(style)],
        'img-src': ["'self'", 'data:'],
        # 'self' lets page tools such as Lighthouse read robots.txt.
        'connect-src': ["'self'", *endpoint, *sending],
        'frame-src': sending or ["'none'"],
        'object-src': ["'none'"],
        'base-uri': ["'self'"],
        'form-action': ["'self'"],
    })
    if '"' in policy:
        raise ValueError('The security policy must not contain double quotes')
    return f'<meta http-equiv="Content-Security-Policy" content="{policy}">'


def page_scripts() -> tuple[str, str]:
    """The inline scripts every page carries: the site settings, then the page behaviour."""
    return site_config(), MAIN_JS


def page_policy() -> str:
    """The security policy of a page that carries the site stylesheet and scripts."""
    return security_policy(STYLES, page_scripts())


def scripts() -> str:
    """The site settings, then the page behaviour, at the end of the body where the page is already parsed."""
    code = page_scripts()
    if any('</script' in part.lower() for part in code):
        raise ValueError('Inline script would close its own element')
    return ''.join(f'<script>{part}</script>' for part in code)


def robots(page: str) -> str:
    return 'index, follow' if not PREVIEW and page != '404.html' else 'noindex, nofollow'


def url_meta(page: str, separator: str = '') -> str:
    """Canonical and sharing URLs, once a homepage URL is configured. The card's size and type let
    sharing previews draw it at once."""
    if not BASE or page == '404.html':
        return ''
    url = BASE if page == 'index.html' else BASE + page
    width, height = sc.png_size(SITE / 'assets' / 'social-card.png')
    alt = C['social_card']['image_alt']
    tags = (f'<link rel="canonical" href="{e(url)}">', f'<meta property="og:url" content="{e(url)}">',
            f'<meta property="og:image" content="{e(BASE + "assets/social-card.png")}">', '<meta property="og:image:type" content="image/png">',
            f'<meta property="og:image:width" content="{width}">', f'<meta property="og:image:height" content="{height}">',
            f'<meta property="og:image:alt" content="{alt}">', f'<meta name="twitter:image:alt" content="{alt}">')
    return ''.join(separator + tag for tag in tags)


def share_meta(page: str, title: str, description: str, separator: str = '') -> str:
    """Open Graph and card tags so every page previews properly when shared."""
    tags = ('<meta property="og:type" content="website">', f'<meta property="og:site_name" content="{e(sc.plain(C["home"]["title"]))}">',
            f'<meta property="og:title" content="{title}">',
            f'<meta property="og:description" content="{description}">', f'<meta property="og:locale" content="{LOCALE.replace("-", "_")}">',
            '<meta name="twitter:card" content="summary_large_image">')
    verification = [f'<meta name="{e(tool)}" content="{e(token)}">' for tool, token in CONFIG['site_verification'].items()] if page == 'index.html' else []
    return ''.join(separator + tag for tag in (*tags, *verification)) + url_meta(page, separator)


def brand(home: str) -> str:
    # The link is named by its visible text; the monogram is decoration.
    return f'<a class="brand" href="{home}"><span class="brand-mark" aria-hidden="true">{C["brand"]["mark"]}<span>·</span></span><span class="brand-name">{NAME} <span>{T["tagline"].upper()}</span></span></a>'


def paragraphs(items) -> str:
    return ''.join(f'<p>{p}</p>' for p in items)


def resource_tokens(resource: dict) -> dict:
    return {'step_count': sum('step' in block for block in resource['blocks']), 'date': sc.long_date(resource['updated'])}


def profile() -> str:
    about = C['home']['about']
    edu = DATA['education_profile']
    publications = {item['url']: item for item in DATA['publications']}
    professional = DATA['professional_profile']
    qualifications = '; '.join(sc.fill(about['qualification_format'], {'award': e(q['award']), 'year': str(q['year']), 'institution': e(q['institution'])}) for q in professional['qualifications'])
    roles = '; '.join(sc.fill(about['role_format'], {'title': e(r['title']), 'organisation': e(r['organisation'])}) for r in professional['former_roles'])
    tags = ''.join(f'<span>{e(topic)}</span>' for topic in edu['topics'])
    links = ''.join(
        f'<a href="{e(item["url"])}" target="_blank" rel="noopener noreferrer">{e(item["title"])} · {e(item["journal"])} ({e(str(item["year"]))}) ↗</a>'
        for item in (publications[url] for url in edu['featured_publication_urls']))
    return (f'<span class="name-label">{about["name_label"]}</span><p class="large-copy">{e(edu["heading"])}</p>'
            f'<p>{e(edu["experience"])}</p><p>{e(edu["purpose"])}</p>'
            f'<p>{sc.fill(about["profile"], {"qualifications": qualifications, "roles": roles})}</p>'
            f'<div class="about-tags">{tags}</div><details class="research-links"><summary>{about["research_summary"]} {icon("plus")}</summary>'
            f'{links}<p>{about["research_note"]}</p></details>')


def offer_url(offer: dict, absolute: bool = False) -> str:
    if 'geochemical_service' in offer:
        return f'{GEOCHEMICAL_URL}/{offer["geochemical_service"]}'
    return BASE + offer['href'] if absolute and offer['href'].startswith('#') else offer['href']


def structured(page: str, title: str, description: str, main=None, extra=()) -> str:
    """The page's JSON-LD graph: the site, Peter, the page itself and its breadcrumb trail."""
    if not BASE:
        return ''
    url = BASE if page == 'index.html' else BASE + page
    trail = None if page == 'index.html' else [(NAME, BASE), (sc.plain(title), url)]
    person = ENTITIES.person()
    if page == 'index.html':
        person['makesOffer'] = [ENTITIES.offer(o['title'], o['summary'], offer_url(o, absolute=True), o['label']) for o in DATA['education_offers']]
    return sd.script(
        sd.website(BASE, sc.plain(C['home']['title']), LOCALE, ENTITIES.person_id),
        person,
        ENTITIES.practice(),
        sd.webpage(url, sc.plain(title), sc.plain(description), BASE, LOCALE,
                   breadcrumb={'@id': url + '#breadcrumb'} if trail else None, mainEntity=main, about={'@id': ENTITIES.person_id}),
        sd.breadcrumbs(url, trail) if trail else None,
        *extra)


def resource(r: dict, page: str, description: str) -> dict | None:
    """A free worksheet or worked example as a schema.org LearningResource."""
    if not BASE:
        return None
    download = f'{BASE}resources/{r["slug"]}.txt' if r['kind'] == 'worksheet' else ''
    return ENTITIES.learning_resource(BASE + page, sc.plain(r['title']), sc.plain(description), LOCALE, r['updated'],
                                      C['resource_page']['kinds'][r['kind']], download)


def home_faq() -> dict:
    return {'@type': 'FAQPage', '@id': BASE + '#faq-heading', 'mainEntity': sd.questions(C['home']['faq']['items']),
            'isPartOf': {'@id': BASE + '#webpage'}, 'inLanguage': LOCALE}


def llms_text() -> str:
    """llms.txt (llmstxt.org): a plain-text map of the site for language models and answer engines."""
    h, rp, labels = C['home'], C['resource_page'], C['llms']
    lines = [f'# {sc.plain(h["title"])}', '', f'> {sc.plain(h["description"])}', '', f'## {labels["paths"]}', '']
    lines += [sc.md_link(o['title'], offer_url(o, absolute=True), o['summary']) for o in DATA['education_offers']]
    lines += ['', f'## {labels["resources"]}', '']
    lines += [sc.md_link(sc.plain(r['title']), f'{BASE}resources/{r["slug"]}.html', f'{rp["kinds"][r["kind"]]}. ' + sc.plain(sc.fill(r['description'], resource_tokens(r))))
              for r in C['resources']]
    # Sections hold link lists only (no sub-headings), so standard llms.txt parsers read every answer.
    lines += ['', f'## {labels["questions"]}', '']
    lines += [sc.md_link(sc.plain(item['question']), BASE + '#faq-heading', sc.plain(item['answer'])) for item in h['faq']['items']]
    lines += ['', f'## {labels["related"]}', '', sc.md_link(DATA['business_name'], GEOCHEMICAL_URL + '/', DATA['business_description']),
              sc.md_link(labels['geochemical_llms'], GEOCHEMICAL_URL + '/llms.txt'),
              sc.md_link(labels['data'], GEOCHEMICAL_URL + '/peter-wade.json'), '']
    return '\n'.join(lines)


def offers() -> str:
    h = C['home']['offers']
    cards = ''
    for offer in DATA['education_offers']:
        href = offer_url(offer)
        cards += (f'<article class="subject-card offer-card"><p class="eyebrow">{e(offer["label"])}</p><h3>{e(offer["title"])}</h3>'
                  f'<p>{e(offer["summary"])}</p><p class="offer-boundary">{e(offer["boundary"])}</p>'
                  f'<a class="text-link" href="{e(href)}" data-offer-level="{e(offer.get("level", ""))}">{e(offer["link_label"])} ↗</a></article>')
    return (f'<div class="subject-grid">{cards}</div><p class="offer-example">{h["example_intro"]} '
            f'<a href="resources/{h["example_resource"]}.html">{h["example_link"]}</a></p>')


def home_page() -> str:
    h = C['home']
    hero, card, lv, sj, ap, ab, rs, fq, ct, ft = (h[k] for k in ('hero', 'card', 'levels', 'subjects', 'approach', 'about', 'resources', 'faq', 'contact', 'footer'))
    nav = ''.join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in h['nav'])
    steps = ''.join(f'<span>{i:02d} &nbsp; {step}</span>' for i, step in enumerate(card['steps'], 1))
    tabs = ''.join(f'<button class="level-tab" type="button" id="tab-{x["id"]}" aria-controls="panel-{x["id"]}" data-level="{x["id"]}">{x["tab"]}</button>' for x in lv['items'])
    panels = ''.join(
        f'<article class="level-panel" id="panel-{x["id"]}" aria-labelledby="tab-{x["id"]}"><div class="panel-intro"><span class="section-number">{i:02d} / {x["tab"].upper()}</span>'
        f'<h3>{x["title"]}</h3><p>{x["text"]}</p><span class="level-caption">{x["caption"]}</span></div><div class="panel-detail">'
        + ''.join(f'<div class="support-point">{icon("check")}<div><h4>{p["title"]}</h4><p>{p["text"]}</p></div></div>' for p in x['points'])
        + f'<a class="text-link" href="#contact" data-select-level="{x["id"]}">{x["link"]} {icon("next")}</a></div><p class="panel-note">{x["note"]}</p></article>'
        for i, x in enumerate(lv['items'], 1))
    subjects = ''.join(f'<article class="subject-card"><span class="subject-icon">{icon(s["icon"])}</span><h3>{s["title"]}</h3><p>{s["text"]}</p></article>' for s in sj['items'])
    approach_steps = ''.join(f'<article><span class="step-number">{i:02d}</span><h3>{s["title"]}</h3><p>{s["text"]}</p></article>' for i, s in enumerate(ap['steps'], 1))
    cards = ''.join(
        f'<a class="resource-card" href="resources/{r["slug"]}.html"><div class="resource-top"><span>{i:02d} / {r["card"]["label"]}</span>{icon("arrow")}</div>'
        f'<h3>{r["card"]["title"]}</h3><h4>{r["card"]["subtitle"]}</h4><p>{sc.fill(r["card"]["text"], resource_tokens(r))}</p><span class="resource-bottom">{rs["open"]} {icon("next")}</span></a>'
        for i, r in enumerate((r for r in C['resources'] if 'card' in r), 1))
    faq = ''.join(f'<details><summary>{item["question"]}{icon("plus")}</summary><p>{item["answer"]}</p></details>' for item in fq['items'])
    levels = ''.join(f'<option value="{x["id"]}">{x["tab"]}</option>' for x in lv['items'])
    return f'''<!doctype html>
<html lang="{LOCALE}">
<head>
  <meta charset="utf-8">
  {page_policy()}
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{h['description']}">
  <meta name="robots" content="{robots('index.html')}">
  <meta name="theme-color" content="#183c33">
  <meta name="referrer" content="strict-origin-when-cross-origin">{share_meta('index.html', h['title'], h['og_description'], HEAD_LINE)}
  <title>{h['title']}</title>
  {head_assets()}
  {structured('index.html', h['title'], h['description'], extra=(home_faq(),))}
</head>
<body id="top" data-print-title="{h['title']}"><a class="skip-link" href="#main">{h['skip']}</a>
<header class="site-header">
  <div class="wrap header-inner">
    {brand('index.html')}
    <button class="menu-toggle" type="button" aria-controls="primary-nav" aria-expanded="false">{h['menu']} <span aria-hidden="true">☰</span></button>
    <nav class="primary-nav" id="primary-nav" aria-label="{h['nav_label']}">
      {nav}<a class="nav-cta" href="#contact">{h['nav_cta']} {icon('arrow')}</a>
    </nav>
  </div>
</header>
<main id="main">
<section class="hero wrap" aria-labelledby="hero-title">
  <div class="hero-copy"><p class="eyebrow"><span class="tiny-star">✳</span> {hero['eyebrow']}</p><h1 id="hero-title">{hero['title']}</h1><p class="hero-description">{hero['description']}</p><div class="hero-actions"><a class="button primary" href="#support">{hero['primary']} {icon('arrow')}</a><a class="quiet-link" href="#about">{hero['secondary']} {icon('next')}</a></div><div class="hero-footnote"><span class="small-line"></span> {hero['footnote']}</div></div>
  <div class="science-card" role="group" aria-label="{card['label']}"><div class="science-top"><span>{card['top']}</span>{icon('spark')}</div><img class="clarity-art" src="{CLARITY}" width="560" height="490" alt=""><div class="science-sticker">{card['sticker']}</div><div class="science-bottom">{steps}</div></div>
</section>
<div class="topic-strip"><div class="wrap topic-list">{'<i>✳</i>'.join(f'<span>{t}</span>' for t in h['topics'])}</div></div>
<section class="section wrap offer-paths" aria-labelledby="offer-paths-heading">
  <div class="section-heading"><div><p class="eyebrow">{h['offers']['eyebrow']}</p><h2 id="offer-paths-heading">{h['offers']['heading']}</h2></div><p>{h['offers']['text']}</p></div>
  {offers()}
</section>
<section class="section wrap" id="support" aria-labelledby="support-heading"><div class="section-heading"><div><p class="eyebrow">{lv['eyebrow']}</p><h2 id="support-heading">{lv['heading']}</h2></div><p>{lv['text']}</p></div><div class="level-tabs" role="group" aria-label="{lv['tabs_label']}">{tabs}</div><div class="level-panels">{panels}</div></section>
<section class="subjects-section section" id="subjects" aria-labelledby="subjects-heading"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">{sj['eyebrow']}</p><h2 id="subjects-heading">{sj['heading']}</h2></div><p>{sj['text']}</p></div><div class="subject-grid">{subjects}</div></div></section>
<section class="section wrap approach-section" id="approach" aria-labelledby="approach-heading"><div class="section-heading"><div><p class="eyebrow">{ap['eyebrow']}</p><h2 id="approach-heading">{ap['heading']}</h2></div><p>{ap['text']}</p></div><div class="steps">{approach_steps}</div><div class="integrity-note">{icon('spark')}<p>{ap['integrity']}</p></div></section>
<section class="about-section" id="about" aria-labelledby="about-heading"><div class="wrap about-grid"><div class="about-left"><p class="eyebrow">{ab['eyebrow']}</p><h2 id="about-heading">{ab['heading']}</h2><div class="experience"><span>{ab['experience_number']}<span>{ab['experience_suffix']}</span></span><p>{ab['experience_text']}</p></div><p class="experience-note">{ab['experience_note']}</p></div><div class="about-copy">{profile()}</div></div></section>
<section class="section wrap" id="resources" aria-labelledby="resources-heading"><div class="section-heading"><div><p class="eyebrow">{rs['eyebrow']}</p><h2 id="resources-heading">{rs['heading']}</h2></div><p>{rs['text']}</p></div><div class="resource-grid">{cards}</div></section>
<section class="faq-section section wrap" aria-labelledby="faq-heading"><div><p class="eyebrow">{fq['eyebrow']}</p><h2 id="faq-heading">{fq['heading']}</h2><p>{fq['text']}</p></div><div class="faq-list">{faq}</div></section>
<section class="contact-section" id="contact" aria-labelledby="contact-heading"><div class="wrap contact-grid"><div class="contact-copy"><p class="eyebrow">{ct['eyebrow']}</p><h2 id="contact-heading">{ct['heading']}</h2><p>{ct['text']}</p><div class="contact-note"><span>{icon('book')}</span><p>{ct['note']}</p></div><p class="contact-status" id="contact-status">{ct['status']}</p><a class="direct-email" id="direct-email" hidden></a></div>
<div class="contact-form-card"><form id="enquiry-form" action="#contact" method="get"><fieldset id="enquiry-fields" disabled><legend class="sr-only">{ct['legend']}</legend><div class="form-row"><div class="field"><label for="enquiry-name">{ct['name']}</label><input id="enquiry-name" name="name" autocomplete="name" maxlength="100" required placeholder="{ct['name_placeholder']}"></div><div class="field"><label for="enquiry-email">{ct['email']}</label><input id="enquiry-email" name="email" type="email" autocomplete="email" maxlength="200" required placeholder="{ct['email_placeholder']}"></div></div><div class="field"><label for="enquiry-level">{ct['level']}</label><select id="enquiry-level" name="level" required><option value="">{ct['level_placeholder']}</option>{levels}<option value="other">{ct['level_other']}</option></select></div><div class="field"><label for="enquiry-topic">{ct['topic']}</label><input id="enquiry-topic" name="topic" maxlength="160" required placeholder="{ct['topic_placeholder']}"></div><div class="field"><label for="enquiry-message">{ct['message']}</label><textarea id="enquiry-message" name="message" rows="4" maxlength="1800" required placeholder="{ct['message_placeholder']}"></textarea></div><label class="checkbox-label"><input id="enquiry-adult" name="adult" type="checkbox" required><span>{ct['adult']}</span></label><button class="button primary form-submit" type="submit">{ct['submit']} {icon('next')}</button><p class="form-footnote">{ct['footnote']}</p></fieldset></form><noscript><p class="notice">{ct['noscript']}</p></noscript><div id="draft-panel" class="draft-panel" hidden><h3>{ct['draft_heading']}</h3><p id="draft-status" role="status" aria-live="polite"></p><label class="sr-only" for="draft-text">{ct['draft_label']}</label><textarea id="draft-text" rows="9" readonly></textarea><div class="draft-actions"><a class="button primary" id="open-email" hidden>{ct['open']} {icon('arrow')}</a><button class="button secondary" id="copy-draft" type="button">{ct['copy']}</button></div><p class="form-footnote">{ct['draft_note']}</p></div></div></div></section>
</main><footer class="site-footer"><div class="wrap footer-inner"><a class="footer-brand" href="index.html">{NAME}<span>{T['motto']}</span></a><div class="footer-links"><a href="privacy.html">{ft['privacy']}</a><a href="#top">{ft['back_to_top']}</a><small>© <span data-year>{date.today().year}</span> {ft['copyright_holder']}</small></div></div></footer>{scripts()}</body></html>
'''


def privacy_page() -> str:
    p = C['privacy']
    sections = ''.join(f'<h2>{s["heading"]}</h2>{paragraphs(s["paragraphs"])}' for s in p['sections'])
    return (f'<!doctype html><html lang="{LOCALE}"><head><meta charset="utf-8">{page_policy()}<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="robots" content="{robots("privacy.html")}"><meta name="description" content="{p["description"]}">{share_meta("privacy.html", p["title"] + " | " + NAME, p["description"])}{structured("privacy.html", p["title"], p["description"])}'
            f'<title>{p["title"]} | {NAME}</title>{head_assets()}</head><body><header class="site-header article-header">'
            f'<div class="wrap header-inner">{brand("index.html")}<a class="back-link" href="index.html">{T["back_link"]}</a></div></header>'
            f'<main class="article-main"><p class="eyebrow">{p["eyebrow"]}</p><h1>{p["heading"]}</h1><p class="article-lead">{p["lead"]}</p>'
            f'<div class="notice" data-preview-only>{p["notice"]}</div>{sections}'
            f'<p class="resource-footer">{sc.fill(p["updated_note"], {"date": sc.long_date(p["updated"])})}</p></main>'
            f'<footer class="footer-simple">{p["footer"]}</footer>{scripts()}</body></html>\n')


def not_found_page() -> str:
    n = C['not_found']
    return (f'<!doctype html><html lang="{LOCALE}"><head><meta charset="utf-8">{security_policy(NOT_FOUND_STYLE)}<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="description" content="{n["description"]}"><meta name="robots" content="{robots("404.html")}"><title>{n["title"]} | {NAME}</title>'
            f'<style>{NOT_FOUND_STYLE}</style></head><body><main><small>{n["label"]}</small><h1>{n["heading"]}</h1><p>{n["text"]}</p>'
            f'<p><a id="home-link" href="{e(BASE or "index.html")}">{T["back_link"]}</a></p></main></body></html>\n')


def worksheet_page(r: dict) -> str:
    rp = C['resource_page']
    page = f'resources/{r["slug"]}.html'
    tokens = resource_tokens(r)
    blocks, number = '', 0
    for block in r['blocks']:
        if 'step' in block:
            number += 1
            blocks += f'\n<section class="worksheet-step"><h2>{number}. {block["step"]}</h2><p>{block["text"]}</p>{WRITING_LINE * block["lines"]}</section>'
        else:
            blocks += f'\n<div class="example-block">{paragraphs(block["example"])}</div>'
    description = sc.fill(r['description'], tokens)
    return (f'<!doctype html><html lang="{LOCALE}"><head><meta charset="utf-8">{page_policy()}<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="robots" content="{robots(page)}"><meta name="description" content="{description}"><meta name="theme-color" content="#183c33">{share_meta(page, r["title"] + " | " + NAME, description)}{structured(page, r["title"], description, resource(r, page, description))}'
            f'<title>{r["title"]} | {NAME}</title>{head_assets("../")}</head><body><header class="site-header article-header">'
            f'<div class="wrap header-inner">{brand("../index.html")}<a class="back-link" href="../index.html#resources">{rp["all_resources"]}</a></div></header>'
            f'<main class="article-main" id="main"><p class="eyebrow">{rp["eyebrow"]}</p><h1>{r["title"]}</h1><p class="article-lead">{sc.fill(r.get("lead", r["description"]), tokens)}</p>'
            f'<div class="article-actions"><button class="button primary" type="button" data-print>{rp["print"]} {icon("print")}</button>'
            f'<a class="button secondary" href="{r["slug"]}.txt" download>{rp["download"]}</a></div><p>{r["intro"]}</p>{blocks}'
            f'<div class="article-end"><h2>{rp["end_heading"]}</h2><p>{rp["end_text"]}</p><a class="text-link" href="../index.html#support">{rp["end_link"]} {icon("next")}</a></div>'
            f'<p class="resource-footer">{rp["footer_note"]} · {tokens["date"]}</p></main><footer class="footer-simple">{rp["footer"]}</footer>{scripts()}</body></html>\n')


def worked_example_page(r: dict) -> str:
    rp = C['resource_page']
    page = f'resources/{r["slug"]}.html'
    tokens = resource_tokens(r)
    steps = ''.join(f'    <section class="worksheet-step"><h2>{i}. {b["step"]}</h2><p>{b["text"]}</p></section>\n' for i, b in enumerate(r['blocks'], 1))
    end = r['end']
    description = sc.fill(r['description'], tokens)
    return f'''<!doctype html>
<html lang="{LOCALE}">
<head>
  <meta charset="utf-8">
  {page_policy()}
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="{robots(page)}">
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#183c33">{share_meta(page, r['title'] + ' | ' + NAME, description, HEAD_LINE)}
  {structured(page, r['title'], description, resource(r, page, description))}
  <title>{r['title']} | {NAME}</title>
  {head_assets('../')}
</head>
<body>
  <header class="site-header article-header"><div class="wrap header-inner">{brand('../index.html')}<a class="back-link" href="../index.html#offer-paths-heading">{rp['learning_paths']}</a></div></header>
  <main class="article-main" id="main">
    <p class="eyebrow">{rp['worked_example_eyebrow']}</p>
    <h1>{r['title']}</h1>
    <p class="article-lead">{sc.fill(r.get('lead', r['description']), tokens)}</p>
    <div class="article-actions"><button class="button primary" type="button" data-print>{rp['print']}</button></div>
    <div class="example-block">{paragraphs(r['example'])}</div>
{steps}    <div class="article-end"><h2>{end['heading']}</h2><p>{end['text']}</p><a class="text-link" href="{end['link_resource']}.html">{end['link']}</a></div>
    <p class="resource-footer">{r['footer_note']} · {tokens['date']}</p>
  </main>
  <footer class="footer-simple">{rp['footer']}</footer>
  {scripts()}
</body>
</html>
'''


def text_version(r: dict) -> str:
    tokens = resource_tokens(r)
    return '\n'.join(sc.fill(line, tokens) for line in r['text_lines']) + '\n' + tokens['date'] + '\n'


def site_config() -> str:
    service = DATA['enquiry_service']
    config = {
        'contactEmail': CONFIG['contact_email'],
        'siteUrl': BASE,
        'launchApproved': APPROVED,
        'enquiryEndpoint': service['endpoint'],
        'turnstileSiteKey': service['turnstile_site_key'],
        'enquiryServiceEnabled': service['enabled'],
        'messages': C['messages'],
    }
    # Public values only: never passwords or tokens. "<" is escaped so the JSON cannot end its script element.
    return 'window.PETER_WADE_SITE = Object.freeze(' + json.dumps(config, ensure_ascii=True).replace('<', '\\u003c') + ');'


def social_card() -> str:
    """Source for the 1200×630 social-sharing image (render with the workspace's tools/render_assets.py)."""
    card = C['social_card']
    css = (ROOT / 'tools' / 'social-card.css').read_text(encoding='utf-8')
    return (f'<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><style>{css}</style></head><body>'
            f'<p class="kicker">{card["eyebrow"]}</p><h1>{C["home"]["hero"]["title"]}</h1><p class="sub">{card["subtitle"]}</p>'
            f'<p class="foot">{T["tagline"].upper()}</p><div class="panel"><img src="../src/clarity.svg" alt=""></div></body></html>\n')


def outputs() -> dict[Path, str]:
    pages = {'index.html': home_page(), 'privacy.html': privacy_page(), '404.html': not_found_page()}
    files = {}
    for r in C['resources']:
        if r['kind'] == 'worksheet':
            pages[f'resources/{r["slug"]}.html'] = worksheet_page(r)
            files[f'resources/{r["slug"]}.txt'] = text_version(r)
        else:
            pages[f'resources/{r["slug"]}.html'] = worked_example_page(r)
    files['robots.txt'] = ('User-agent: *\nDisallow: /\n' if PREVIEW else 'User-agent: *\nAllow: /\n') + (f'\nSitemap: {BASE}sitemap.xml\n' if not PREVIEW and BASE else '')
    tools = {ROOT / 'tools' / 'social-card.html': social_card()}
    if BASE:
        files['llms.txt'] = llms_text()
        # Each sitemap entry gives the day its page's content last changed; tools/page-dates.json remembers it.
        urls = {(BASE if page == 'index.html' else BASE + page): text for page, text in sorted(pages.items()) if page != '404.html'}
        files['sitemap.xml'], tools[ROOT / 'tools' / 'page-dates.json'] = sc.dated_sitemap(urls, ROOT / 'tools' / 'page-dates.json')
        # IndexNow (Bing and others): the key file proves the site sends the change notices of tools/indexnow.py.
        files[f'{CONFIG["indexnow_key"]}.txt'] = CONFIG['indexnow_key']
    return {SITE / name: text for name, text in (pages | files).items()} | tools


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true', help='fail if any generated file is out of date')
    args = parser.parse_args()
    owned = {*SITE.glob('*.html'), *SITE.glob('*.txt'), *SITE.glob('resources/*.html'), *SITE.glob('resources/*.txt'), SITE / 'sitemap.xml'}
    owned = {path for path in owned if path.exists()}
    problems = sc.write_outputs(outputs(), args.check, owned)
    if args.check:
        if problems:
            print('\n'.join(problems), file=sys.stderr)
            sys.exit('Educational site is out of date with shared_data; run tools/build.py')
        print('Educational site is current with shared_data.')
    else:
        print(f'Built the educational site from shared_data ({len(problems)} files updated).')


if __name__ == '__main__':
    main()
