# GTA VI Question Gap

Single-page landing site for a daily digest that lists the GTA VI questions players are asking right now that no good video answers yet. Plain HTML + CSS + a few lines of JS, no framework, no build step needed to serve.

Live: https://navidemad.github.io/vicecity-gaps/

## Files

| Path | Role |
| --- | --- |
| `docs/index.html` | The whole site (inline CSS and JS). GitHub Pages serves `docs/`. |
| `docs/favicon.svg` | Favicon. |
| `sample-digest.md` | Sample digest shown in the "Sample from Digest #1" section. |
| `build.py` | Renders `sample-digest.md` into `docs/index.html` between `<!-- digest:start -->` and `<!-- digest:end -->`. Python 3 standard library only. |
| `test_build.py` | Tests for the renderer: `python3 -m unittest test_build.py`. |

## Update the sample digest

1. Edit `sample-digest.md`. Supported: headings, paragraphs, lists, pipe tables, blockquotes, `---`, **bold**, *italic*, `code`, links. Raw HTML is escaped.
   In a table, a cell reading `No good video yet`, `Small video only`, `Conflicting answers` or `Covered` becomes a coloured badge.
2. Run `python3 build.py`.
3. Commit `docs/index.html` together with `sample-digest.md`.

## Deploy

GitHub Pages is set to **branch `main`, folder `/docs`**. Every push to `main` redeploys in about a minute.

```bash
python3 -m unittest test_build.py
python3 build.py
git add -A && git commit -m "Update landing" && git push origin main
```

Local preview: `python3 -m http.server 8765 --directory docs`, then open http://127.0.0.1:8765/?utm_source=test&utm_campaign=check.

## Tracking

- **GoatCounter** (cookie-free, no consent banner): page views, plus two events:
  - `click-stripe-founder`: click on either founder-price link.
  - `signup-submit`: submit of either sign-up form.
  Each event's referrer is `source/campaign` from the UTM parameters (`direct` when there are none).
- **UTM passthrough**: `utm_*` parameters on the landing URL are kept for the session and:
  - appended to the Stripe Payment Link, along with `client_reference_id=<source>__<campaign>` (shows on the Checkout Session in Stripe);
  - added as Buttondown tags `src:<source>` and `camp:<campaign>` on sign-up (plus `free`).

Ad link format: `https://navidemad.github.io/vicecity-gaps/?utm_source=x&utm_medium=cpc&utm_campaign=launch_a`

## Manual configuration checklist

- [ ] **GoatCounter**: create a free account at https://www.goatcounter.com/signup with the site code **`vicecitygaps`**. If that code is taken, change it in the `data-goatcounter` script tag in `docs/index.html`. Optionally, in its settings, enable the Campaign parameters so `utm_campaign` shows in the Campaigns widget.
- [ ] **Stripe live Payment Link**: the page currently points to the **test-mode** link (`https://buy.stripe.com/test_…`), which charges nothing. Before running ads: activate the live account, create the €9/month product and Payment Link in live mode, then replace both `data-stripe-link` URLs in `docs/index.html`. Optional: set the link's confirmation to redirect back to the site.
- [ ] **Stripe refund promise**: the FAQ promises a full refund within 14 days of any payment and an automatic refund if the daily digest doesn't launch. Refunds are manual (Dashboard → Payments → Refund).
- [ ] **Buttondown**: rename the newsletter to "GTA VI Question Gap" if you want the name in confirmation emails (Settings → General), and write the welcome email. Double opt-in is on by default.
- [ ] **Legal**: fill in the highlighted placeholders in the footer (SIREN, address, contact email).
- [ ] **Test end to end** from the live URL with `?utm_source=test&utm_campaign=check`: sign up (tags in Buttondown), click the founder button (event in GoatCounter, `client_reference_id` on the Stripe checkout).
- [ ] **Name and trademark**: "GTA VI" is a Take-Two trademark. Using it in the product name increases the risk of a takedown or ad rejection; consider a name that doesn't start with the mark.
