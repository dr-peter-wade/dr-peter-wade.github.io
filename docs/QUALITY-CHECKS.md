# Quality checks

Checked 28 September 2026.

Chromium, locally inlined copies of the delivered HTML/CSS/JS/SVG. Browser URL navigation was restricted in the environment, so local link targets are checked separately by tools/check_site.py.

- No horizontal page overflow at 320, 375, 390, 720, 768, 900, 1024, 1440 and 1920px.
- Mobile menu opens, closes on Escape, and closes after navigation selection.
- All five level tabs render, select one panel, and support arrow/Home/End keys.
- Level CTA prefills the enquiry; FAQ disclosures expand.
- Invalid forms do not create drafts. Preview contact stays disabled; generated text is not executed; copy fallback does not imply delivery.
- With mock approved email config, the correctly encoded mailto draft is exposed. No email link was activated and no message was sent.
- All six HTML pages render without horizontal overflow at 320, 390 and 1440px.
- Without JavaScript, all level panels remain readable and form fields remain disabled to prevent accidental URL submission.
- No uncaught JavaScript errors during these tests.

The standard-library local-file validator also passes. Browser tests used Chromium only, not a complete cross-browser or accessibility certification. Live GitHub deployment, DNS, certificate provisioning, real email-app launching and mailbox delivery were not performed.

The configuration tool was separately checked in a temporary copy: publish and preview modes, HTTPS URL validation, email validation, subdirectory canonical URLs, repeated configuration without duplicate metadata, and release-check failure in preview mode. The delivery copy remains unconfigured and in preview mode.
