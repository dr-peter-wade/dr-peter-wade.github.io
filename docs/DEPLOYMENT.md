# Deployment guide

Public preview deployed 28 September 2026 at https://dr-peter-wade.github.io/ from https://github.com/dr-peter-wade/dr-peter-wade.github.io. It has no custom domain or verified public contact email.

## 1. Review the website

Unzip the package and open `site/index.html`. Review all five learning-stage tabs, subjects, research biography, FAQs, resources and privacy page. Confirm Peter's service scope, contact address and practical teaching arrangements before opening enquiries. The draft legal/privacy text needs operator-specific completion, not merely a configuration change.

The original files intentionally start in **preview mode**. Enquiries produce draft text only, no destination is provided, and search indexing is discouraged. An online preview is still publicly accessible: `noindex` is not authentication.

## 2. Choose the right hosting route

The included workflow targets GitHub Pages. GitHub's policy restricts sites used to run an online business or primarily facilitate commercial transactions. An educational portfolio is different from a commercial tutoring storefront, but the lack of checkout is not a guarantee of eligibility. Check the actual purpose and current terms before deployment. For a main paid-tutoring business website, consider the alternative hosting route below.

Primary source: [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

## 3. Update the organisation repository

The public repository `dr-peter-wade/dr-peter-wade.github.io` already exists. Never add personal documents or secrets to it. The website also lives under `education_assistance/peter-wade-website/` in the shared `peterwade` workspace. To push changes from that workspace, commit the relevant website files on its `main` branch, then split and push only this directory:

```sh
cd /path/to/peterwade
python3 education_assistance/peter-wade-website/tools/build.py --check
python3 education_assistance/peter-wade-website/tools/check_site.py
git add education_assistance/peter-wade-website
git commit -m "Update Peter Wade educational website"
site_commit=$(git subtree split --prefix=education_assistance/peter-wade-website HEAD)
git push git@github.com:dr-peter-wade/dr-peter-wade.github.io.git "${site_commit}:refs/heads/main"
```

Use SSH authentication with access to the organisation. The split excludes the geochemical consulting project and the source ZIP. The published repository root must look like this, without an extra nesting level:

```text
.github/workflows/deploy.yml
site/index.html
site/assets/...
tools/check_site.py
tools/configure.py
README.md
docs/...
```

## 4. Verify Pages deployment

The repository's **Settings > Pages > Build and deployment > Source** is set to **GitHub Actions**. Check this setting if deployment stops working.

After pushing, open **Actions > Deploy Peter Wade educational site** and confirm the run succeeds. You can also use **Run workflow** on `main` to retry. Future pushes to `main` trigger deployment automatically.

The workflow validates local files, uploads only `site/`, and deploys that artifact to Pages. It requires `contents: read`, `pages: write` and `id-token: write` permissions. Account or organisation policies may need an administrator's approval.

The Actions run and Pages settings show the published URL: `https://dr-peter-wade.github.io/`. The repository is an organisation site, so the address has no project path.

Sources: [Creating a Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site), [Custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## 5. Approve contact and search indexing

Complete `docs/LAUNCH-CHECKLIST.md`, including an actual privacy notice for the operator. Once the contact email and real homepage URL are known, from the repository folder run:

```sh
python3 tools/configure.py --email "PETERS-APPROVED-EMAIL" --url "ACTUAL-HTTPS-HOMEPAGE-URL" --publish
python3 tools/check_site.py --release
```

These are placeholders, not an email address or domain to use. Example URL shape for a project: `https://YOUR-USERNAME.github.io/peter-wade/`; for an owned custom domain: `https://YOUR-ACTUAL-DOMAIN/`.

The configuration script performs no network operations. It writes public email configuration, canonical URLs, social-sharing URLs, robots metadata and a sitemap. It updates the 404 homepage link to an absolute address. It does not buy a domain, publish to GitHub, or make the privacy statement legally complete.

To deploy approved changes from the shared workspace, use the commit, subtree split and push commands in section 3.

For a preview, leave `launchApproved` false. To restore preview mode use `python3 tools/configure.py --preview`, commit and push. This does not revoke copies already made by visitors or search engines.

The browser form currently prepares a draft and exposes a `mailto:` link only after approval. A separate, disabled Cloudflare Worker in the parent workspace can optionally send verified enquiries after sender credentials, a Turnstile widget, privacy wording and real delivery tests are complete. See `email_service/README.md` in the parent workspace. No booking system or payment gateway is included.

## 6. Connect an owned domain

Use `docs/DOMAIN-GUIDE.md`. Verify ownership in GitHub account settings, add the custom domain under the repository's Pages settings, then set DNS at the provider. Preserve existing email DNS records.

The supplied deployment is **Actions-based**, so a `CNAME` file is not required and is not used to set the custom domain. Enter the domain in GitHub Pages settings. Rerun the configuration script with the new homepage URL so canonical links and sitemap point to the new domain, then commit and push.

## Alternative: Cloudflare Pages using the same GitHub repository

The same static files require no redesign. In Cloudflare, create a Pages application and import the GitHub repository. Use:

| Setting | Value |
|---|---|
| Framework preset | None |
| Production branch | `main` |
| Build command | `exit 0` |
| Build output directory | `site` |
| Repository root | Leave at repository root |

Cloudflare's official static HTML guide describes this route. Follow that host's custom-domain process rather than using GitHub's IP addresses. Update the configuration URL and hosting references in the privacy notice. Do not deploy the same domain to two competing hosts.

Disable/remove `.github/workflows/deploy.yml` if GitHub Pages should no longer deploy. Review Cloudflare's own plan limits and terms before launch; this package does not assert blanket policy approval.

Source: [Cloudflare static HTML deployment](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/).

## Troubleshooting

**Workflow cannot find `tools/check_site.py`:** files were nested inside an extra folder, or `tools/` was not committed.

**Workflow cannot deploy Pages:** enable Pages with the GitHub Actions source, check allowed Actions and repository plan, then rerun.

**Styles or resources missing:** publish the entire `site/` folder, not only `index.html`.

**Enquiries do not send automatically:** the central Worker and frontend switch are disabled in this preview. The draft flow needs the visitor's email application. Confirm the approved address and test delivery before changing either mode.

**Nothing appears in search:** preview mode uses `noindex`; use the configuration script only after approval. Search indexing is never guaranteed or instant.

**Custom-domain HTTPS is not ready:** verify GitHub's DNS checks, remove conflicting web records and allow DNS/certificate provisioning time. Do not remove mail records. See the current GitHub custom-domain documentation before changing an existing live domain.
