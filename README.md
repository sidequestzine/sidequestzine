# Side Quest Zine: website

Live at https://sidequestzine.co (Cloudflare Pages, built from this repo).

## Where things live

```
sidequestzine-repo/   the website. Cloudflare only reads this folder.
  index.html          home page (the folder cabinet)
  side-quests/ comic/ thought/ photos/ spotlight/ learn/ shop/
  css/style.css       all styling
  js/site.js          theme toggle, folders, signup, checkout buttons
  functions/api/      checkout.js (Stripe: prices + shipping) and subscribe.js (Kit)
  assets/             images
tools/build.py        rewrites every page from one file of copy, prices and dates
```

## Changing something

- Prices and shipping live in `sidequestzine-repo/functions/api/checkout.js` (in cents). Change the page price in `tools/build.py` too.
- Small edits: open the file on GitHub, click the pencil, commit.
- Uploading files: they must land at the same path they replace, e.g. `sidequestzine-repo/css/style.css`. Anything outside `sidequestzine-repo/` never reaches the site.
