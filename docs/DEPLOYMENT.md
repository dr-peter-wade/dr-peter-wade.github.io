# Deployment guide

Prepared 28 September 2026. This package is not yet online. It contains no domain registration and no verified contact email.

## 1. Review the website

Unzip the package and open `site/index.html`. Review all five learning-stage tabs, subjects, research biography, FAQs, resources and privacy page. Confirm Peter's service scope, contact address and practical teaching arrangements before opening enquiries. The draft legal/privacy text needs operator-specific completion, not merely a configuration change.

The original files intentionally start in **preview mode**. Enquiries produce draft text only, no destination is provided, and search indexing is discouraged. An online preview is still publicly accessible: `noindex` is not authentication.

## 2. Choose the right hosting route

The included workflow targets GitHub Pages. GitHub's policy restricts sites used to run an online business or primarily facilitate commercial transactions. An educational portfolio is different from a commercial tutoring storefront, but the lack of checkout is not a guarantee of eligibility. Check the actual purpose and current terms before deployment. For a main paid-tutoring business website, consider the alternative hosting route below.

Primary source: [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

## 3. Create an empty GitHub repository

Use the account that should own the site. A suggested repository name is `peter-wade`. Do not assume a particular username is available.

Public repositories can use GitHub Pages on GitHub Free. Private-repository availability depends on the plan. Never use a public repository to store personal documents or secrets.

Create an **empty** repository first, without generating a README or adding a licence. Then, inside the unzipped `peter-wade-website` folder, run:

```sh
git init -b main
git add .
git commit -m "Add Peter Wade educational website"
git remote add origin https://github.com/YOUR-USERNAME/peter-wade.git
git push -u origin main
```

Replace `YOUR-USERNAME` with the actual owner. Authenticate with GitHub's supported login, SSH or token method. Never put credentials in website files.

GitHub Desktop can publish this folder instead. Include the hidden `.github` folder. Do not upload only the ZIP: GitHub Pages needs the extracted website files and workflow.

Repository root must look like this, without an extra nesting level:

```text
.github/workflows/deploy.yml
site/index.html
site/assets/...
tools/check_site.py
tools/configure.py
README.md
docs/...
```

## 4. Enable Pages deployment

Open the repository's **Settings > Pages**. Under **Build and deployment**, select **GitHub Actions** as the source.

Then open **Actions > Deploy Peter Wade educational site > Run workflow**, selecting `main`. A first push may fail when Pages has not yet been enabled; enable it, then rerun. Future pushes to `main` trigger deployment automatically.

The workflow validates local files, uploads only `site/`, and deploys that artifact to Pages. It requires `contents: read`, `pages: write` and `id-token: write` permissions. Account or organisation policies may need an administrator's approval.

The Actions run and Pages settings show the real published URL. For a project repository, it usually follows:

```text
https://YOUR-USERNAME.github.io/peter-wade/
```

For an account site, the repository must be named `YOUR-USERNAME.github.io`; its default address is the account site's root. Relative links in this package support both forms.

Sources: [Creating a Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site), [Custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## 5. Approve contact and search indexing

Complete `docs/LAUNCH-CHECKLIST.md`, including an actual privacy notice for the operator. Once the contact email and real homepage URL are known, from the repository folder run:

```sh
python3 tools/configure.py --email "PETERS-APPROVED-EMAIL" --url "ACTUAL-HTTPS-HOMEPAGE-URL" --publish
python3 tools/check_site.py --release
```

These are placeholders, not an email address or domain to use. Example URL shape for a project: `https://YOUR-USERNAME.github.io/peter-wade/`; for an owned custom domain: `https://YOUR-ACTUAL-DOMAIN/`.

The configuration script performs no network operations. It writes public email configuration, canonical URLs, social-sharing URLs, robots metadata and a sitemap. It updates the 404 homepage link to an absolute address. It does not buy a domain, publish to GitHub, or make the privacy statement legally complete.

To deploy your approved changes:

```sh
git add site
git commit -m "Configure approved public contact and canonical domain"
git push
```

For a preview, leave `launchApproved` false. To restore preview mode use `python3 tools/configure.py --preview`, commit and push. This does not revoke copies already made by visitors or search engines.

The browser form prepares a draft and exposes a `mailto:` link only after approval. It does not submit messages to a server. Test the actual email app and mailbox delivery yourself after launch. No booking system or payment gateway is included.

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

**Enquiries do not send automatically:** this is intentional. The tool prepares a draft; the visitor sends it from their own email application. Confirm the real address, review the draft and send a test email yourself.

**Nothing appears in search:** preview mode uses `noindex`; use the configuration script only after approval. Search indexing is never guaranteed or instant.

**Custom-domain HTTPS is not ready:** verify GitHub's DNS checks, remove conflicting web records and allow DNS/certificate provisioning time. Do not remove mail records. See the current GitHub custom-domain documentation before changing an existing live domain.
