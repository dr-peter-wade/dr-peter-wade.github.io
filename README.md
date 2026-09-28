# Peter Wade | Science, made clearer

A static educational website with responsive layouts, five learning-stage tabs, free study resources and a browser-only enquiry draft tool. An optional centrally routed enquiry service exists in the parent workspace, but is disabled in this preview.

**Status: public preview at https://dr-peter-wade.github.io/.** No custom domain has been registered. The contact email is intentionally blank, enquiries are disabled, and search indexing is discouraged by metadata. A public preview is not private or password protected.

## Open the website

Open `site/index.html` in a browser. For normal local preview, from this folder run:

```sh
python3 -m http.server 8000 --directory site --bind 127.0.0.1
```

Then visit `http://127.0.0.1:8000/`. On Windows, `py` may replace `python3`.

## Publish to GitHub Pages

The [organisation repository](https://github.com/dr-peter-wade/dr-peter-wade.github.io) uses GitHub Actions as its Pages source. Its workflow validates the site and uploads **only the `site/` directory**. It runs on pushes to `main` and on manual dispatch. Use [the deployment guide](docs/DEPLOYMENT.md) to update it from this shared workspace.

Before a public launch, complete [the launch checklist](docs/LAUNCH-CHECKLIST.md), then configure Peter's actual approved email and the actual HTTPS homepage URL:

```sh
python3 tools/configure.py --email "PETERS-APPROVED-EMAIL" --url "ACTUAL-HTTPS-HOMEPAGE-URL" --publish
python3 tools/check_site.py --release
```

Replace both capitalised placeholders. The script rejects invalid values. It updates the contact configuration, canonical/share metadata, sitemap and robots settings together. **It does not upload files, configure DNS or buy a domain.**

The current online review remains in preview mode. To restore preview mode after a later launch:

```sh
python3 tools/configure.py --preview
```

## Hosting suitability

GitHub Pages has restrictions on using its service to run an online business or a site primarily facilitating commercial transactions. No checkout is included, but that alone does not guarantee eligibility. Review the current policy before publishing. If this becomes primarily a paid tutoring business website, the identical `site/` folder can be hosted on a suitable commercial host; Cloudflare Pages deployment settings are included in the guide.

Official policies and instructions are linked in the deployment guide. Checked 28 September 2026; confirm again at launch.

## What is included

| Location | Purpose |
|---|---|
| `site/index.html` | Homepage and educational-support enquiries |
| `site/resources/` | Three printable HTML resources and plain-text versions |
| `site/privacy.html` | Technical privacy explanation and operator-completion reminder |
| `site/404.html` | Missing-page fallback |
| `site/assets/` | CSS, JavaScript, original SVG artwork, favicon and social-sharing PNG |
| `site/site-config.js` | Public contact and preview configuration |
| `.github/workflows/deploy.yml` | GitHub Pages deployment workflow |
| `tools/configure.py` | Metadata and launch configuration, Python standard library only |
| `tools/build.py` | Render Peter's profile and enquiry settings from `../../shared_data/peter.json` in the parent workspace |
| `tools/check_site.py` | Offline local-link, metadata and configuration checks |
| `docs/` | Deployment, domain, content and launch notes |

There is no npm install, framework, build service, database, analytics script, remote font, tracking pixel or payment integration. All runtime files are local to the site. The optional configuration and validation scripts use Python 3.10 or newer.

## Contact behaviour

The preview form **prepares a draft**; it does not send email. The optional shared Cloudflare Worker can send a verified enquiry to this site's fixed recipient after owner approval, credential setup, privacy review and live testing. See `../../email_service/README.md` in the parent workspace. With approved public contact configuration, the visitor can alternatively open their own email app and send the draft there. No automatic delivery has been tested.

The site code does not save form values in cookies or browser storage. Browsers and email apps may provide their own autofill, history or storage. Hosting providers may keep technical access logs. Never put sensitive student, health or confidential research information in an initial enquiry.

## Editing

Change site-specific text in the HTML files, shared Peter Wade profile and research data in `../../shared_data/peter.json`, colour and layout in `site/assets/styles.css`, and behaviour in `site/assets/main.js`. From the parent workspace, run `python3 education_assistance/peter-wade-website/tools/build.py` and then `python3 education_assistance/peter-wade-website/tools/check_site.py`. The public organisation repository contains generated output but not the shared JSON; use the parent workspace to regenerate it. Do not add private CVs, email archives, identity documents, credentials or confidential client research to this repository.

The visual branding and learning resources are original draft content prepared for this project. Peter must review all offers and factual claims before use. The three linked research publications/software resources remain the work of their respective authors and publishers; links do not imply endorsement. No third-party font files are included.
