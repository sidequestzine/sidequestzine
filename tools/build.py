"""
SIDE QUEST site builder (v2, "the cabinet").

Change content here, run `python3 tools/build.py` from the top of the repo, and every
page is rewritten with the same header, folders, footer and theme toggle.
Tutorial pages under /learn/<name>/ are standalone and are not touched.

The <head> of each page (titles, descriptions, search tags) is kept from the
page that is already on disk, so search work is never overwritten.
"""
import os, re, html

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sidequestzine-repo")

# ------------------------------------------------------------------ settings
SHIP = {
    "window_closes": "Sun, Dec 13, 2026",
    "ships_by": "Thu, Jan 7, 2027",
}

# the folders, in drawer order. c = colour, x / xm = tab position desktop / phone
FOLDERS = [
    dict(id="side-quests", what="The detours, written up", label="Side Quests", href="/side-quests/", c="#E15A2C", x="2%",  xm="5%",
         body="t-classic", badge="/assets/badges/1_classic.svg",
         kicker="THE SIDE QUESTS", status_line="in progress",
         title="The stuff that wasn't the mission.",
         blurb="Bowling with your cousin. Running a cabaret club instead of avenging anyone. The detours, written up.",
         empty=("Out touching grass.", "Quests unlock when Issue 01 lands. Currently gathering material the hard way.")),
    dict(id="comic", what="The side quest, drawn", label="Comic", href="/comic/", c="#5B6B79", x="48%", xm="40%",
         body="t-mono-line", badge="/assets/badges/6_mono_line.svg",
         kicker="THE COMIC", status_line="panels in progress",
         title="The side quest, drawn.",
         blurb="Feelings included, (un¿)fortunately.",
         empty=("Artist is on a side quest.", "Panels in progress. He said he'd be back by dark. He was not back by dark.")),
    dict(id="thought", what="Thinking out loud, on purpose", label="Thought", href="/thought/", c="#2C6E9E", x="14%", xm="8%",
         body="t-deep-sea", badge="/assets/badges/2_deep_sea.svg",
         kicker="THE THOUGHT", status_line="still forming",
         title="Thinking out loud, on purpose.",
         blurb="The reflective beat. The part of the issue that slows down.",
         empty=("Thinking outside right now.", "Issue 01 in progress. Back once the thought finishes forming.")),
    dict(id="photos", what="The ordinary, made worth noticing", label="Photos", href="/photos/", c="#E8337F", x="60%", xm="40%",
         body="t-glitch-rave", badge="/assets/badges/B_glitch_rave.svg",
         kicker="THE PHOTOS", status_line="developing",
         title="Proof it happened.",
         blurb="The ordinary, made worth noticing.",
         empty=("Photos or it didn't happen, amirite?", "Issue 01 in progress. Camera roll currently full of things that seemed profound at 2am.")),
    dict(id="spotlight", what="Flowers, on the record", label="Spotlight", href="/spotlight/", c="#5F8578", x="28%", xm="4%",
         body="t-flat-minimal", badge="/assets/badges/5_flat_minimal.svg",
         kicker="THE SPOTLIGHT", status_line="flowers incoming",
         title="Somebody's getting their flowers.",
         blurb="<b>spot·light·ing</b> <i>(v.)</i> to shower a person with unabashed love, support and encouragement, on the record.",
         empty=("Spotlight 4 spotlight?", "Issue 01 in progress. Somebody's getting their flowers. On the record.")),
    dict(id="learn", what="Free tutorials on how this got built", label="Learn", href="/learn/", c="#A6501E", x="68%", xm="40%",
         body="t-grunge", badge="/assets/badges/C_grunge_stencil.svg",
         kicker="THE LEARN", status_line="5 tutorials, free",
         title="When you learn, teach.",
         blurb="Free tutorials. Everything it took to build Side Quest, written down so you can build yours.",
         empty=None),
    dict(id="shop", what="Caps, pins and $3 stickers", label="Creative Arts Dept.", href="/shop/", c="#EAAC44", x="6%", xm="5%",
         body="t-shop", badge="/assets/thumbs/prjct_pin.png",
         kicker="THE CREATIVE ARTS DEPT.", status_line="founding run open",
         title="prjct.sidequest.",
         blurb="The part of Side Quest that actually makes things. The founding run: one cap, one pin, and stickers. Never re-run.",
         empty=None),
]
BY_ID = {f["id"]: f for f in FOLDERS}

TUTORIALS = [
    ("01", "/learn/code-your-badge/", "Code Your Own Badge",
     "Design a real logo with SVG. A text editor and a browser, nothing else. No experience needed."),
    ("02", "/learn/build-a-brand/", "Build a Brand From Scratch",
     "Nine steps, sketch to product. The whole arc, including the parts that got scrapped."),
    ("03", "/learn/build-the-machine/", "Build the Machine",
     "The deep one. Write a generator that writes your site, so changing one line updates every page. Plus the SVG bug nobody warns you about."),
    ("04", "/learn/receive-real-money/", "Receive Real Money",
     "Build a preorder shop with Stripe and one server function. No Shopify, no monthly fee."),
    ("05", "/learn/own-the-list/", "Own the List",
     "Build a real email signup, server-side, so an audience you actually own doesn't depend on any algorithm's mood."),
]

# shop items: id must match functions/api/checkout.js
SINGLES = [
    ("sticker_og", "OG Side Quest Logo", "/assets/thumbs/wide.png", "The original. 3 inches wide."),
    ("sticker_classic", "Classic Icon", "/assets/thumbs/classic.png", "The stop sign badge."),
    ("sticker_keepgoing", "Keep Going", "/assets/thumbs/keepgoing.png", "For the long days."),
    ("sticker_prjct", "prjct.sidequest.", "/assets/thumbs/sticker_prjct_white.png", "The white run. Founding edition."),
]
SINGLE_PRICE = "$3"
LETTERING = '<span class="lettering"><img class="lt-l" src="/assets/thumbs/prjct_lettering_light.png" alt="" width="1100" height="288"><img class="lt-d" src="/assets/thumbs/prjct_lettering_dark.png" alt="" width="1100" height="288"><span class="sr">prjct.sidequest.</span></span>'
SET_PRICE, SET_WAS = "$8", "$9"

# ------------------------------------------------------------------ pieces
THEME_INIT = """<meta name="color-scheme" content="light dark">
<script>try{var t=localStorage.getItem('sq-theme');if(t)document.documentElement.dataset.theme=t;}catch(e){}</script>
<link rel="stylesheet" href="/css/style.css?v=2">"""

SUN = '<svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></svg>'
MOON = '<svg class="i-moon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.5 14.6A8.6 8.6 0 0 1 9.4 3.5a8.6 8.6 0 1 0 11.1 11.1z"/></svg>'


def header(active=None):
    on = ' class="on" aria-current="page"'
    tabs = "\n".join(
        f'      <a href="{f["href"]}" class="t-{f["id"]}{" on" if f["id"] == active else ""}" style="--c:{f["c"]}"{" aria-current=" + chr(34) + "page" + chr(34) if f["id"] == active else ""}>{f["label"]}</a>'
        for f in FOLDERS)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap bar">
    <a class="brand" href="/">
      <img src="/assets/thumbs/mark_1_classic.png" alt="" width="44" height="44">
      <span>SIDE<br>QUEST</span>
    </a>
    <nav class="tabs-wrap" aria-label="Sections"><div class="tabs">
{tabs}
    </div></nav>
    <a class="shop-pin" href="/shop/"{' aria-current="page"' if active == "shop" else ""}>Shop</a>
    <button class="theme-toggle" type="button" aria-pressed="false" aria-label="Switch to dark mode">{SUN}{MOON}<span class="knob"></span></button>
  </div>
</header>
"""


FOOTER = """
<footer>
  <div class="wrap">
    <div class="signup" id="signup">
      <div class="signup-inner">
        <div class="signup-copy">
          <div class="signup-tag">GET IN BEFORE ISSUE 01</div>
          <p>No spam, no daily nonsense. Just the Prologue, Issue 01 dropping, and the founding capsule opening. That's it.</p>
        </div>
        <form class="signup-form" id="signup-form">
          <input type="email" name="email" placeholder="you@wherever.com" required autocomplete="email" aria-label="Email address">
          <button type="submit">Keep me posted</button>
        </form>
      </div>
      <div class="signup-msg" id="signup-msg" role="status" hidden></div>
    </div>

    <img src="/assets/thumbs/mark_1_classic.png" alt="Side Quest badge">
    <div class="tag">The stop sign says SIDE. Keep going.</div>
    <div class="links">
      LINKS
    </div>
    <div class="socials"><a href="https://www.instagram.com/sidequest.zine" target="_blank" rel="noopener">Instagram</a><a href="https://www.threads.com/@sidequest.zine" target="_blank" rel="noopener">Threads</a><a href="https://www.tiktok.com/@sidequestzine" target="_blank" rel="noopener">TikTok</a><a href="https://www.patreon.com/user?u=225603240" target="_blank" rel="noopener">Patreon</a><a href="https://discord.gg/Ufu7aw9aT" target="_blank" rel="noopener">Discord</a></div>
    <div class="small">&copy; Side Quest, with Rodrius &middot; Seattle</div>
  </div>
</footer>

<script src="/js/site.js?v=2" defer></script>
</body>
</html>
""".replace("LINKS", "".join(f'<a href="{f["href"]}">{f["label"]}</a>' for f in FOLDERS))


def read_head(rel):
    """Keep the existing <head> (search tags), swap the stylesheet line for theme + css v2."""
    src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    m = re.search(r"<head>(.*?)</head>", src, re.S)
    head = m.group(1)
    head = re.sub(r'\s*<meta name="color-scheme"[^>]*>', "", head)
    head = re.sub(r"\s*<script>try\{var t=localStorage.*?</script>", "", head, flags=re.S)
    head = re.sub(r'<link rel="stylesheet" href="/css/style\.css[^"]*">', THEME_INIT, head)
    return "<!DOCTYPE html>\n<html lang=\"en\">\n<head>" + head + "</head>\n"


def write(rel, body_class, main, active=None):
    out = read_head(rel) + f'<body class="{body_class}">\n' + header(active) + main + FOOTER
    open(os.path.join(ROOT, rel), "w", encoding="utf-8").write(out)
    print("wrote", rel)


def vt(f):  # cross-page morph name
    return f'view-transition-name:folder-{f["id"]}'



# ------------------------------------------------------------------ folder peeks (hover tease + click reveal)
# Each folder hides a little object behind its front sheet. Hover (or scroll it into view on a
# phone) and the object peeks out; click and it pops fully out before the folder opens.
PEEKS = {
    "side-quests": """<div class="pk pk-map"><svg viewBox="0 0 240 108" aria-hidden="true">
        <rect x="2" y="2" width="236" height="104" rx="6" class="map-paper"/>
        <path d="M80 2V106M160 2V106" class="map-fold"/>
        <path d="M8 84H232" class="map-road"/>
        <path d="M54 84C70 30 110 18 140 40S176 80 196 84" class="map-detour"/>
        <g class="map-sign" transform="translate(120 30)"><polygon points="13,-6 13,6 6,13 -6,13 -13,6 -13,-6 -6,-13 6,-13" fill="#C8102E" stroke="#F8F2E6" stroke-width="2.5"/><text y="3.5" text-anchor="middle">SIDE</text></g>
      </svg><span class="map-dot"></span><span class="map-stamp">DETOUR</span></div>""",
    "comic": """<div class="pk pk-comic">
        <span class="cp cp1"><i class="cp-dots"></i><i class="cp-guy"></i></span>
        <span class="cp cp2"><i class="cp-bub">&hellip;</i></span>
        <span class="cp cp3"><i class="cp-burst">?!</i></span>
      </div>""",
    "thought": """<div class="pk pk-mag">
        <div class="pg-under">Thinking out loud, on purpose.</div>
        <div class="pg-turn"><div class="pg pg-front"><span class="pg-k">THE THOUGHT</span><span class="pg-h">Out loud.</span><span class="pg-cols"><i></i><i></i></span></div><div class="pg pg-back"></div></div>
      </div>""",
    "photos": """<div class="pk pk-pola">
        <span class="pol p1"><i></i></span><span class="pol p2"><i></i></span><span class="pol p3"><i></i></span>
      </div>""",
    "spotlight": """<div class="pk pk-flow">
        <span class="fl f1"><i></i></span><span class="fl f2"><i></i></span><span class="fl f3"><i></i></span>
        <span class="pt t1"></span><span class="pt t2"></span><span class="pt t3"></span><span class="pt t4"></span><span class="pt t5"></span><span class="pt t6"></span>
      </div>""",
    "learn": """<div class="pk pk-cards">
        <span class="ic c1">01</span><span class="ic c2">02</span><span class="ic c3">03</span><span class="ic c4">04</span><span class="ic c5">05</span>
      </div>""",
    "shop": """<div class="pk pk-patch"><div class="patch-in">
        <svg class="stitch" viewBox="0 0 150 108" preserveAspectRatio="none" aria-hidden="true"><rect x="5" y="5" width="140" height="98" rx="12"/></svg>
        <img src="/assets/thumbs/patch_trim.png" alt="" width="900" height="714">
      </div></div>""",
}

# ------------------------------------------------------------------ home
def doc_content(f):
    parts = [f'<img class="sticker" src="{f["badge"]}" alt="" loading="lazy">',
             f'<div class="kicker">{f["kicker"]}</div>',
             f'<h3>{LETTERING if f["id"] == "shop" else f["title"]}</h3>',
             f'<p>{f["blurb"]}</p>']
    if f["empty"]:
        parts.append(f'<div class="status"><div class="ach">&#9670; SIDE QUEST IN PROGRESS</div>'
                     f'<b>{f["empty"][0]}</b><span>{f["empty"][1]}</span></div>')
    if f["id"] == "learn":
        parts.append('<ul class="mini">' + "".join(
            f'<li><a href="{h}"><span class="k">{n}</span><span><span class="t">{t}</span></span></a></li>'
            for n, h, t, _ in sorted(TUTORIALS)) + "</ul>")
    if f["id"] == "shop":
        figs = [("/assets/thumbs/patch_trim.png", "$28", "On the cap"),
                ("/assets/thumbs/prjct_pin.png", "$12", "The pin"),
                ("/assets/thumbs/classic.png", SET_PRICE, "3-icon sticker set"),
                ("/assets/thumbs/keepgoing.png", SINGLE_PRICE, "Single stickers")]
        parts.append('<div class="prices">' + "".join(
            f'<figure{" class=" + chr(34) + "swatch" + chr(34) if "patch" in i else ""}><img src="{i}" alt="" loading="lazy"><figcaption><b>{p}</b>{c}</figcaption></figure>'
            for i, p, c in figs) + "</div>")
    verb = {"shop": "Open the Creative Arts Dept.", "learn": "Open all tutorials"}.get(f["id"], f"Open {f['label']}")
    parts.append(f'<a class="open-link" href="{f["href"]}">{verb} <span class="arr" aria-hidden="true">&rarr;</span></a>')
    return "\n          ".join(parts)


def home():
    folders = []
    for i, f in enumerate(FOLDERS, 1):
        folders.append(f"""
    <section class="folder k-{f['id']} pk-{'right' if float(f['x'].rstrip('%')) < 40 else 'left'}" id="{f['id']}" style="--c:{f['c']};--x:{f['x']};--xm:{f['xm']};--i:{i - 1};{vt(f)}">
      <div class="peek" aria-hidden="true">{PEEKS[f['id']]}</div>
      <h2 class="tab"><span class="sheen" aria-hidden="true"></span><button type="button" aria-expanded="false" aria-controls="{f['id']}-body" aria-describedby="{f['id']}-what"><span class="tab-n">{i:02d}</span>{f['label']}</button></h2>
      <div class="sheet">
        <span class="fx" aria-hidden="true"></span>
        <div class="strip"><span class="what" id="{f['id']}-what">{f['what']}</span><span class="status-pill"><span class="dot" aria-hidden="true"></span>{f['status_line']}</span><span class="chev" aria-hidden="true"><svg viewBox="0 0 16 16" width="14" height="14"><path d="M3.5 6l4.5 4.5L12.5 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span></div>
        <div class="body" id="{f['id']}-body" role="region" aria-label="{f['label']}"><div class="body-in"><div class="doc">
          {doc_content(f)}
        </div></div></div>
      </div>
    </section>""")
    main = f"""
<main id="main" class="wrap">
  <section class="hero">
    <div>
      <span class="eyebrow">&#9679; a zine about the detours</span>
      <h1>Nobody remembers the plan. <em>They remember the detour.</em></h1>
      <p>A small, stubborn magazine that happens to also draw, record, and touch grass. Every issue has five beats, and each beat has its own folder.</p>
    </div>
    <img class="hero-badge" src="/assets/badge.png" alt="Side Quest gold badge" width="300" height="300">
  </section>

  <div class="pick">Pick a folder</div>
  <div class="cabinet" id="cabinet">{''.join(folders)}
  </div>
</main>
"""
    write("index.html", "t-home", main)


# ------------------------------------------------------------------ section pages
def page(f, inner, rel=None, label=None):
    rel = rel or f["href"].strip("/") + "/index.html"
    main = f"""
<main id="main" class="wrap page">
  <section class="folder" style="--c:{f['c']};{vt(f)}">
    <div class="tab"><a href="/#{f['id']}" aria-label="Back to the {f['label']} folder on the home page">{label or f['label']}</a></div>
    <div class="sheet">
      <a class="back" href="/#{f['id']}">&larr; back to the cabinet</a>
{inner}
{folder_nav(f) if not label else ""}
    </div>
  </section>
</main>
"""
    write(rel, f["body"], main, active=f["id"])


def folder_nav(f):
    i = [x["id"] for x in FOLDERS].index(f["id"])
    prev, nxt = FOLDERS[i - 1], FOLDERS[(i + 1) % len(FOLDERS)]
    return f"""      <nav class="folder-nav" aria-label="More folders">
        <a class="fn-prev" href="{prev['href']}" style="--c:{prev['c']}"><span class="fn-k">Previous folder</span><span class="fn-t">&larr; {prev['label']}</span></a>
        <a class="fn-next" href="{nxt['href']}" style="--c:{nxt['c']}"><span class="fn-k">Next folder</span><span class="fn-t">{nxt['label']} &rarr;</span></a>
      </nav>"""


def phead(eyebrow, h1, p):
    return f"""      <div class="phead">
        <span class="eyebrow">&#9679; {eyebrow}</span>
        <h1>{h1}</h1>
        <p>{p}</p>
      </div>"""


def beat_pages():
    for fid in ["side-quests", "comic", "thought", "photos", "spotlight"]:
        f = BY_ID[fid]
        t, p = f["empty"]
        inner = phead(f["kicker"].lower(), f["label"], f["blurb"]) + f"""
      <div class="empty">
        <div class="ach">&#9670; SIDE QUEST IN PROGRESS</div>
        <h2>{t}</h2>
        <p>{p}</p>
      </div>"""
        page(f, inner)


def learn_page():
    f = BY_ID["learn"]
    cards = "\n".join(f"""        <a class="beat" href="{h}">
          <div class="n">TUTORIAL {n}</div>
          <h3>{t}</h3>
          <p>{d}</p>
        </a>""" for n, h, t, d in sorted(TUTORIALS))
    inner = phead("the learn", "Learn",
                  "Free tutorials. &ldquo;When you learn, teach. When you get, give.&rdquo; Maya Angelou said that, and this folder is us taking her up on it.") + f"""
      <div class="beats">
{cards}
      </div>"""
    page(f, inner)


def shop_page():
    f = BY_ID["shop"]
    singles = "\n".join(f"""        <div class="item small">
          <div class="item-img"><img src="{img}" alt="{name} sticker" loading="lazy"></div>
          <h3>{name}</h3>
          <p>{desc}</p>
          <div class="price">{SINGLE_PRICE}</div>
          <button class="btn buy" data-item="{iid}">Get one</button>
        </div>""" for iid, name, img, desc in SINGLES)
    pins = [("1_classic", "CLASSIC", None, False), ("6_mono_line", "BLUEPRINT", "/comic/", True),
            ("2_deep_sea", "??????????", "/thought/", True), ("B_glitch_rave", "???????", "/photos/", True),
            ("5_flat_minimal", "?????????", "/spotlight/", True), ("C_grunge_stencil", "????????", "/learn/", True),
            ("3_sunset_pop", "?????", None, True), ("4_night_mode", "??????", None, True)]
    lineup = ""
    for key, name, href, locked in pins:
        tag, end = (f'<a class="pin locked" href="{href}">', "</a>") if href else (f'<div class="pin{" locked" if locked else ""}">', "</div>")
        lock = '<div class="lockbar">LOCKED</div>' if locked else ""
        lineup += f'{tag}<img src="/assets/thumbs/pin_{key}.png" alt="{name} emblem" loading="lazy"><span>{name}</span>{lock}{end}'

    inner = phead("the creative arts dept.", "Creative Arts Dept.",
                  "The part of Side Quest that actually makes things. Capsules for the collectors, one drop per issue. Will you be there?") + f"""

      <section class="capsule">
        <div class="cap-tag">FOUNDING EDITION &middot; ONE TIME ONLY</div>
        <h2 class="cap-lettering">{LETTERING}</h2>
        <p>The Creative Arts Dept. is the heart of Side Quest. It's the part that takes an idea and turns it into something you can hold. This is the first run it ever made, and it's what funds the numbered capsule that follows.</p>
        <p>Buying in here means you were here before the system existed.</p>
        <div class="cap-shots">
          <figure class="shot half swatch">
            <img src="/assets/thumbs/patch_trim.png" alt="Creative Arts Dept. embroidery design">
            <figcaption>The cap &middot; this design, embroidered on navy</figcaption>
          </figure>
          <figure class="shot half">
            <img class="pin-shot" src="/assets/thumbs/prjct_pin.png" alt="prjct.sidequest. gold enamel pin">
            <figcaption>The pin &middot; prjct.sidequest.</figcaption>
          </figure>
          <figure class="shot"><img src="/assets/thumbs/wide.png" alt="OG Side Quest logo sticker"><figcaption>OG Side Quest logo</figcaption></figure>
          <figure class="shot"><img src="/assets/thumbs/classic.png" alt="Classic icon sticker"><figcaption>Classic icon</figcaption></figure>
          <figure class="shot"><img src="/assets/thumbs/keepgoing.png" alt="Keep Going sticker"><figcaption>Keep Going</figcaption></figure>
        </div>
        <p class="cap-pin-note">The prjct. pin isn't one of the nine emblems. No number, no unlock, no reissue. It only exists because this run happened.</p>
        <div class="cap-note">Never re-run. When it closes, it closes.</div>
      </section>

      <h2 class="sec-h">The founding run</h2>
      <p class="sec-p">The cap and the pin are made to order. The stickers are the easy way in.</p>
      <div class="shop-grid">
        <div class="item">
          <div class="item-img swatch"><img src="/assets/thumbs/patch_trim.png" alt="Creative Arts Dept. embroidery design, as it will be stitched on the cap" loading="lazy"></div>
          <div class="item-badge">THE CAP &middot; PREORDER</div>
          <h3>Creative Arts Dept. Cap</h3>
          <p>Navy cap with this Creative Arts Dept. design embroidered on the front.</p>
          <div class="price">$28</div>
          <button class="btn buy" data-item="cap">Preorder</button>
        </div>
        <div class="item">
          <div class="item-img no-zoom"><img src="/assets/thumbs/prjct_pin.png" alt="prjct.sidequest. pin" loading="lazy"></div>
          <div class="item-badge">THE PIN &middot; PREORDER</div>
          <h3>prjct.sidequest. Pin</h3>
          <p>Gold enamel, unnumbered. Not one of the nine. Never reissued.</p>
          <div class="price">$12</div>
          <button class="btn buy" data-item="prjct_pin">Preorder</button>
        </div>
        <div class="item">
          <div class="item-img"><img src="/assets/thumbs/classic.png" alt="3-icon sticker set" loading="lazy"></div>
          <div class="item-badge save">THE SET &middot; SAVE $1</div>
          <h3>3-Icon Sticker Set</h3>
          <p>OG Side Quest logo, Classic icon, and Keep Going. Matte vinyl, water-bottle tough.</p>
          <div class="price">{SET_PRICE}<s>{SET_WAS}</s></div>
          <button class="btn buy" data-item="stickers">Get the set</button>
        </div>
      </div>

      <h2 class="sec-h">Singles</h2>
      <p class="sec-p">Any sticker on its own, {SINGLE_PRICE} each. Matte die-cut vinyl.</p>
      <div class="shop-grid four">
{singles}
      </div>

      <div class="ship">
        <div><b>Preorder window</b>Closes {SHIP['window_closes']}.</div>
        <div><b>Ships by</b>{SHIP['ships_by']}, everything in one go.</div>
        <div><b>Shipping</b>Stickers $1.50 &middot; pin $3 &middot; cap $6. US only for now.</div>
      </div>
      <p class="shop-note"><b>This is a preorder, not a store.</b> If an item doesn't clear its minimum, that item is refunded in full and the rest still ships. You can change the quantity at checkout. No card details ever touch this site; checkout runs through Stripe.</p>
      <div id="shop-error" class="shop-error" role="alert" hidden></div>

      <h2 class="sec-h">Pin emblems</h2>
      <p class="sec-p">Nine emblems. One unlocks with each issue, then the window shuts on it forever. Eight are still sealed.</p>
      <div class="lineup">{lineup}</div>
      <p class="sec-p" style="margin-top:14px;">Gold-plated editions exist. You'll know when.</p>"""
    page(f, inner)


def thanks_page():
    f = BY_ID["shop"]
    inner = phead("order confirmed", "You're in.",
                  f"Your order is confirmed and a receipt is on its way to your email. The preorder window closes {SHIP['window_closes']} and everything ships by {SHIP['ships_by']}. You'll hear from us either way.") + """
      <a class="btn" href="/">Back to Side Quest</a>"""
    page(f, inner, rel="shop/thanks/index.html", label="Order confirmed")


def not_found():
    f = dict(BY_ID["side-quests"])
    f["id"] = "side-quests"
    inner = """      <div class="empty" style="margin-top:6px;">
        <div class="ach">&#9670; QUEST FAILED</div>
        <h2>You took a wrong turn.</h2>
        <p>Which is extremely on brand. That page doesn't exist though.</p>
        <a class="btn" href="/">Back to the cabinet</a>
      </div>"""
    main = f"""
<main id="main" class="wrap page">
  <section class="folder" style="--c:{f['c']}">
    <div class="tab"><a href="/">Lost &amp; found</a></div>
    <div class="sheet">
{inner}
    </div>
  </section>
</main>
"""
    write("404.html", "t-home", main)


if __name__ == "__main__":
    home(); beat_pages(); learn_page(); shop_page(); thanks_page(); not_found()
