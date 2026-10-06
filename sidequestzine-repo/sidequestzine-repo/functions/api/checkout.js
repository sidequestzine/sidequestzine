/**
 * POST /api/checkout
 *
 * Creates a Stripe Checkout Session and returns the URL to redirect to.
 *
 * SECURITY NOTE — the important one:
 * Prices live HERE, on the server, never in the page. If the browser sent us a
 * price we'd have to trust it, and anyone could edit it to $0.01 before hitting
 * buy. The page only ever sends an item id. We look up what that costs.
 *
 * Requires an environment variable in the Cloudflare dashboard:
 *   STRIPE_SECRET_KEY = sk_live_...  (or sk_test_... while testing)
 */

// Prices and shipping live here, on the server. Edit these numbers, not the page.
// amount and ship are in cents. ship = flat shipping for the whole order.
const STICKER_SHIP = 150;   // stamped envelope
const CATALOG = {
  cap: {
    name: "prjct.sidequest. Creative Arts Dept. Cap",
    description: "Creative Arts Dept. design, embroidered. Preorder, ships by Jan 7, 2027.",
    amount: 2800, ship: 600, shipLabel: "USPS Ground Advantage",
    image: "/assets/thumbs/patch.png",
  },
  prjct_pin: {
    name: "prjct.sidequest. Pin",
    description: "Gold enamel, unnumbered, off-system. Never reissued. Preorder, ships by Jan 7, 2027.",
    amount: 1200, ship: 300, shipLabel: "Padded envelope",
    image: "/assets/thumbs/prjct_pin.png",
  },
  stickers: {
    name: "3-Icon Sticker Set",
    description: "Classic icon, Keep Going, prjct.sidequest. white. Matte vinyl.",
    amount: 800, ship: STICKER_SHIP, shipLabel: "Stamped envelope",
    image: "/assets/thumbs/classic.png",
  },
  sticker_classic: {
    name: "Sticker: Classic Icon",
    description: "Matte die-cut vinyl.",
    amount: 300, ship: STICKER_SHIP, shipLabel: "Stamped envelope",
    image: "/assets/thumbs/classic.png",
  },
  sticker_keepgoing: {
    name: "Sticker: Keep Going",
    description: "Matte die-cut vinyl.",
    amount: 300, ship: STICKER_SHIP, shipLabel: "Stamped envelope",
    image: "/assets/thumbs/keepgoing.png",
  },
  sticker_prjct: {
    name: "Sticker: prjct.sidequest. (white)",
    description: "Matte die-cut vinyl. Founding edition.",
    amount: 300, ship: STICKER_SHIP, shipLabel: "Stamped envelope",
    image: "/assets/thumbs/sticker_prjct_white.png",
  },
};

// Where you ship. Flat rates above are US prices, so US only for now.
// To reopen Canada/UK, add them here AND raise the ship amounts for them.
const COUNTRIES = ["US"];

export async function onRequestPost(context) {
  const { request, env } = context;

  try {
    if (!env.STRIPE_SECRET_KEY) {
      return json({ error: "Payments aren't configured yet." }, 500);
    }

    const body = await request.json();
    const item = CATALOG[body.item];
    const qty = Math.min(Math.max(parseInt(body.qty, 10) || 1, 1), 10);

    if (!item) return json({ error: "Unknown item." }, 400);

    const origin = new URL(request.url).origin;

    // Stripe's API takes form-encoded data, not JSON.
    const form = new URLSearchParams();
    form.append("mode", "payment");
    form.append("success_url", `${origin}/shop/thanks/`);
    form.append("cancel_url", `${origin}/shop/`);
    form.append("line_items[0][quantity]", String(qty));
    form.append("line_items[0][price_data][currency]", "usd");
    form.append("line_items[0][price_data][unit_amount]", String(item.amount));
    form.append("line_items[0][price_data][product_data][name]", item.name);
    form.append("line_items[0][price_data][product_data][description]", item.description);
    // let buyers change the quantity on Stripe's page (1 to 10)
    form.append("line_items[0][adjustable_quantity][enabled]", "true");
    form.append("line_items[0][adjustable_quantity][minimum]", "1");
    form.append("line_items[0][adjustable_quantity][maximum]", "10");
    // product image, shown on Stripe's checkout page.
    // built from the request origin so it works on both the .pages.dev
    // address and the custom domain without editing this file.
    if (item.image) {
      form.append("line_items[0][price_data][product_data][images][0]", origin + item.image);
    }
    // collect a shipping address and charge flat shipping
    COUNTRIES.forEach((c, i) => form.append(`shipping_address_collection[allowed_countries][${i}]`, c));
    form.append("shipping_options[0][shipping_rate_data][type]", "fixed_amount");
    form.append("shipping_options[0][shipping_rate_data][fixed_amount][amount]", String(item.ship));
    form.append("shipping_options[0][shipping_rate_data][fixed_amount][currency]", "usd");
    form.append("shipping_options[0][shipping_rate_data][display_name]", item.shipLabel);

    const res = await fetch("https://api.stripe.com/v1/checkout/sessions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.STRIPE_SECRET_KEY}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: form,
    });

    const session = await res.json();

    if (!res.ok) {
      return json({ error: session.error?.message || "Stripe rejected that." }, 400);
    }

    return json({ url: session.url });
  } catch (err) {
    return json({ error: "Something went wrong creating checkout." }, 500);
  }
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
