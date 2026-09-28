# Owner approval before launch

The site is built, but these business and operational decisions cannot be inferred from a CV.

- [ ] Peter approves use of his name/title, biography, research summary and publication links.
- [ ] Peter approves each advertised learning stage and specific topic. Remove topics he does not wish to teach.
- [ ] Confirm the real public contact email and who monitors it. No email is currently connected.
- [ ] Agree format, availability, fees, preparation time, cancellations, refunds and terms before accepting any paid booking. Do not promise instant availability.
- [ ] Decide whether under-18 support will be offered; complete appropriate safeguarding arrangements and verify any credentials before making claims about them. A parent tick-box is not a safeguarding system.
- [ ] Complete the actual operator's privacy notice: identity/contact, purposes, applicable lawful basis, retention, service providers, any international transfers, rights and complaint route. Confirm the wording reflects the real email and hosting arrangements. Obtain appropriate advice where needed.
- [ ] Confirm the intended use is permitted by the selected host. In particular, review GitHub Pages restrictions on business and commercial-transaction sites.
- [ ] Register the chosen domain in the correct owner's account, or obtain verified permission to use the parent domain for a subdomain. Check renewal price and protect account access.
- [ ] Run `tools/configure.py` with the real email/URL and `--publish` only after the above approvals.
- [ ] Run `python3 tools/check_site.py --release`, then deploy.
- [ ] Check actual live links, 404 behaviour, both desktop and mobile browsers, browser print output, contact draft, email-app opening and real mailbox delivery. These hosted/email checks remain outstanding.
- [ ] Set up domain verification and HTTPS; keep credentials and private research out of the repository.

Noindex metadata and robots instructions are not access control. Do not put confidential content in an online preview.
