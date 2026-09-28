# Getting a domain close to peter.wade

Checked 28 September 2026. **No candidate below has been confirmed available, reserved or purchased.** Registrar checkout/RDAP verification was not accessible during this task. These are search candidates, not availability results.

## Recommended shortlist

| Candidate | Reason to check it |
|---|---|
| `peterwade.uk` | First choice for a short UK-facing personal address |
| `peterwade.co.uk` | Familiar UK alternative |
| `peterwade.me` | Personal brand without a UK-specific ending |
| `peterwade.com` | International option, availability and price unverified |
| `peter-wade.uk` | Readable fallback when the unhyphenated version is taken |
| `drpeterwade.uk` | Another fallback consistent with the supplied professional title |

The exact `peter.wade` cannot currently be registered in the normal public DNS because `.wade` is not a delegated top-level domain in the IANA root database. Do not confuse a similarly marketed alternative-root/blockchain name with a universally resolvable website domain.

Primary source: [IANA root-zone database](https://www.iana.org/domains/root/db).

## Keeping the dot between first name and surname

`peter.wade.uk`, `peter.wade.me` or `peter.wade.com` would preserve that dot. They are subdomains of `wade.uk`, `wade.me` or `wade.com`. You would need to control the respective parent domain, or obtain the existing owner's permission and DNS configuration. You cannot independently register such a subdomain through an ordinary registrar simply because it does not show a website.

If a parent domain is owned by somebody else, negotiating for it may be expensive or unsuccessful. Check this route only if preserving the dot is important enough to justify the effort. A simple `peterwade.uk` is my practical first choice, subject to availability.

Do not build a new long-term plan around the old registry-operated third-level `.name` registration scheme such as `peter.wade.name`: ICANN approved discontinuation of that specific service in 2026. This is not a claim that every `.name` domain or ordinary owner-created subdomain is being discontinued.

Primary source: [ICANN's 28 July 2026 approval letter](https://itp.cdn.icann.org/en/files/consensus-policies/fessenden-to-kane-2-28-07-2026-en.pdf).

## Buy the domain

Use a registrar account controlled by Peter or the intended long-term owner. Search the exact candidates above and compare both first-year and renewal prices. If the checkout reports a premium or aftermarket domain, the standard extension price is not the price of that name.

Current example advertised prices from Porkbun, in **USD**:

| Extension | Advertised first year | Advertised annual renewal |
|---|---:|---:|
| `.uk` | $4.32 sale | $5.66 |
| `.co.uk` | $4.32 sale | $5.66 |
| `.me` | $17.27 | $17.27 |
| `.com` | $11.08 | $11.08 |

These are extension-level, standard-registration prices, not quotes for any specific Peter Wade name. Checkout determines actual availability, tax, promotions, currency conversion and any premium pricing. Recheck before payment.

Official price/search pages: [Porkbun .uk](https://porkbun.com/tld/uk), [.co.uk](https://porkbun.com/tld/co.uk), [.me](https://porkbun.com/tld/me), [.com](https://porkbun.com/tld/com).

Register with correct owner details, enable two-factor authentication, keep recovery details accessible, and record the renewal date. I recommend automatic renewal backed by a current payment method. Domain ownership, DNS, website hosting and email service are separate things. You do not need to buy an additional hosting package to use GitHub Pages; a domain registration alone does not create an email inbox.

## Connect an apex domain to GitHub Pages

Example: after legitimately obtaining a domain such as `peterwade.uk`.

1. In GitHub's **account Settings > Pages**, verify the domain using the exact TXT record GitHub supplies. This helps protect against domain takeover. Follow the account or organisation instructions that match the actual owner.
2. In the repository's **Settings > Pages > Custom domain**, enter the owned hostname without `https://` or a path. Save it before pointing DNS at GitHub.
3. At the registrar or active DNS provider, configure the following web records. These values apply to GitHub Pages, not Cloudflare Pages.

| Type | Name / host | Target |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `YOUR-USERNAME.github.io` |

`@` normally means the root/apex domain. Your DNS provider may instead use a blank name or the full hostname. Replace `YOUR-USERNAME` with the actual GitHub account/organisation owner. Use no `https://` and no repository path in the CNAME target.

Remove conflicting **web** A/AAAA/CNAME records only after checking what currently uses the domain. **Preserve mail-related MX, SPF, DKIM and DMARC records and the GitHub verification TXT record.** Do not add a wildcard record.

For a subdomain such as `peter.wade.uk`, after obtaining control of `wade.uk`, set a CNAME named `peter` to `YOUR-USERNAME.github.io` instead of configuring apex A records for a domain you do not own. Set that full subdomain as the custom domain in Pages.

4. Allow DNS verification and HTTPS certificate provisioning, then enable **Enforce HTTPS** when GitHub makes it available. Test both the chosen hostname and the `www` route if configured. GitHub notes DNS propagation can take up to 24 hours; certificates may not be immediately ready.
5. Run `tools/configure.py` with the final HTTPS homepage URL, validate and redeploy. GitHub Actions deployments use the custom domain stored in Pages settings, not a `CNAME` file.

Official instructions: [Managing a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site), [Verifying domain ownership](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages).
