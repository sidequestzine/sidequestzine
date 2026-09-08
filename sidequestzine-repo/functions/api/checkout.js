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

const CATALOG = {
  cap: {
    name: "prjct.sidequest. — Creative Arts Dept. Cap",
    description: "Embroidered, navy. Creative Arts Dept. design.",
    amount: 2800,            // cents
    image: "/assets/thumbs/patch.png",
  },
  stickers: {
    name: "prjct.sidequest. — 3-Icon Sticker Set",
    description: "OG Side Quest logo, Classic icon, Keep Going.",
    amount: 1000,
    image: "/assets/thumbs/classic.png",
  },
  prjct_pin: {
    name: "prjct.sidequest. — Pin",
    description: "Gold enamel, unnumbered, off-system. Never reissued.",
    amount: 1200,
    image: "/assets/thumbs/prjct_pin.png",
  },
};

export async function onRequestPost(context) {
  const { request, env } = context;

  try {
    if (!env.STRIPE_SECRET_KEY) {
      return json({ error: "Payments aren't configured yet." }, 500);
    }

    const body = await request.json();
    const item = CATALOG[body.item];
    const qty = Math.min(Math.max(parseInt(body.qty, 10) || 1, 1), 5);

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
    // product image, shown on Stripe's checkout page.
    // built from the request origin so it works on both the .pages.dev
    // address and the custom domain without editing this file.
    if (item.image) {
      form.append("line_items[0][price_data][product_data][images][0]", origin + item.image);
    }
    // collect a shipping address — you're mailing a physical object
    form.append("shipping_address_collection[allowed_countries][0]", "US");
    form.append("shipping_address_collection[allowed_countries][1]", "CA");
    form.append("shipping_address_collection[allowed_countries][2]", "GB");

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
