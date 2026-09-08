# SIDE QUEST — Website

Static site. No build step, no dependencies, no framework. Plain HTML and CSS.

---

## What's here

```
index.html            home
report/               ─┐
comic/                 │
thought/               ├─ the five beats
photos/                │
spotlight/            ─┘
learn/                 tutorials (both already live)
  code-your-badge/
  build-a-brand/
shop/                  capsules — needs checkout, see below
404.html
css/style.css          all styling, one file
assets/                badge + favicon
```

---

## Deploy to Cloudflare Pages

**Option A — drag and drop (fastest, no GitHub needed)**

1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** → **Upload assets**
2. Drag this entire folder in
3. Name the project `sidequest`
4. Deploy

Live in about a minute on `sidequest.pages.dev`.

**Option B — connect GitHub (better long-term)**

1. Push this folder to a GitHub repo
2. Cloudflare → Workers & Pages → Create → Pages → **Connect to Git**
3. Build settings:
   - Framework preset: **None**
   - Build command: *leave empty*
   - Build output directory: `/`
4. Deploy

Now every push to `main` updates the site automatically.

---

## Connect your domain

Since the domain is already registered in Cloudflare, this is quick:

1. Open the Pages project → **Custom domains** → **Set up a custom domain**
2. Enter your domain
3. Cloudflare adds the DNS records and issues SSL itself — nothing manual

Takes a few minutes to go live. HTTPS is automatic and free.

---

## Editing pages

Every page has an empty-state block that looks like this:

```html
<div class="empty">
  <h2>Nothing here yet.</h2>
  ...
  <div class="note">&lt;!-- replace this block with real content --&gt;</div>
</div>
```

Delete that whole block and write normal HTML in its place. The header, nav,
and footer are already handled on every page.

**Adding a nav item?** It has to be added in two places per page: the `<nav class="tabs">`
block in the header, and the `.links` block in the footer. That's the tradeoff of
having no build step — worth it at this size.

---

## The Shop tab

**Now live**, wired to Stripe. Not a placeholder anymore.

Cloudflare Pages serves files. It doesn't process payments on its own — but Pages
Functions (a feature already built into the platform you're deploying on) can talk
to Stripe on the server side. That's what powers this: `functions/api/checkout.js`
creates a real Stripe Checkout session when someone clicks Preorder.

**One thing that never changes, on any platform:** you can't handle raw card
numbers yourself — that's a legal requirement (PCI compliance), not a Shopify
thing. Stripe's own hosted checkout screen is what actually takes the card. Your
site never sees it.

### Set this up before it goes live

1. **Create a Stripe account** at stripe.com, verify your business details
2. **Get your secret key** — Dashboard → Developers → API keys → copy the one starting `sk_live_...`
   (use the `sk_test_...` one while you're testing so no real charges happen)
3. **Add it to Cloudflare**, not to any file in this repo:
   Pages project → Settings → Environment variables → add
   `STRIPE_SECRET_KEY` = your key → redeploy
4. **Edit the prices** in `functions/api/checkout.js` — they're in the `CATALOG`
   object near the top, in cents. This is the *only* place prices live; the page
   itself never sends a price, only an item id, so nobody can tamper with what
   they're charged from the browser.
5. **Test with a real test card**: `4242 4242 4242 4242`, any future date, any CVC
6. **Check the order lands** in Stripe Dashboard → Payments

### How the preorder floor actually gets enforced

Stripe's dashboard already tracks how many of each item sold — that's just the
order list, filterable by product name. When the window closes:

- Count orders for each item in the Stripe dashboard
- Below the supplier's MOQ (50 for pins) → **Refunds** tab → refund those orders,
  one click each
- At or above → place the bulk order with your supplier, funded by the money
  already sitting in your Stripe balance

No extra software. This is genuinely the whole system.

---

## Notes

- Fonts load from Google Fonts. Nothing to install.
- The badge PNG is used for the logo, favicon, and social share image.
- `css/style.css` holds every colour as a CSS variable at the top. Change the palette
  there and it updates the whole site.

---

*The stop sign says SIDE. Keep going.*
