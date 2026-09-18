/**
 * POST /api/subscribe
 *
 * Takes an email from the footer form and adds it to the mailing list
 * via ConvertKit's API. The API key never reaches the browser — it lives
 * only here, as an environment variable, same pattern as checkout.js.
 *
 * Requires two things in the Cloudflare dashboard:
 *   CONVERTKIT_API_KEY = your key   (Settings → Variables and Secrets → Secret)
 *   CONVERTKIT_FORM_ID = your form's numeric ID (not secret, but easiest to
 *                        set the same way — Settings → Variables and Secrets → Text)
 *
 * Where to get both: convertkit.com → free account → Grow → Landing Pages & Forms
 *   → create a form (or use one you already have) → Settings tab shows the
 *   Form ID in the URL → Account Settings → API Keys shows your API Key.
 */

function isValidEmail(email) {
  // deliberately simple — good enough to catch typos, not trying to be a
  // full RFC 5322 validator. ConvertKit will reject anything truly malformed.
  return typeof email === "string" && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export async function onRequestPost(context) {
  const { request, env } = context;

  try {
    if (!env.CONVERTKIT_API_KEY || !env.CONVERTKIT_FORM_ID) {
      return json({ ok: false, error: "Mailing list isn't configured yet." }, 500);
    }

    const body = await request.json();
    const email = (body.email || "").trim().toLowerCase();

    if (!isValidEmail(email)) {
      return json({ ok: false, error: "That doesn't look like a real email." }, 400);
    }

    const res = await fetch(
      `https://api.convertkit.com/v3/forms/${env.CONVERTKIT_FORM_ID}/subscribe`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          api_key: env.CONVERTKIT_API_KEY,
          email: email,
        }),
      }
    );

    const data = await res.json();

    if (!res.ok) {
      return json({ ok: false, error: data.message || "Signup failed. Try again in a bit." }, 400);
    }

    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: "Something went wrong on our end." }, 500);
  }
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
