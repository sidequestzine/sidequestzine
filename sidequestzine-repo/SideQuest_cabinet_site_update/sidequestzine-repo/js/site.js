/* SIDE QUEST — site behaviour: theme toggle, the cabinet, signup, shop */
(function () {
  var root = document.documentElement;

  /* ---------- light / dark toggle ---------- */
  var mq = window.matchMedia('(prefers-color-scheme: dark)');
  function current() { return root.dataset.theme || (mq.matches ? 'dark' : 'light'); }
  function sync() {
    var dark = current() === 'dark';
    document.querySelectorAll('.theme-toggle').forEach(function (b) {
      b.setAttribute('aria-pressed', dark ? 'true' : 'false');
      b.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
      b.title = dark ? 'Light mode' : 'Dark mode';
    });
  }
  document.querySelectorAll('.theme-toggle').forEach(function (b) {
    b.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('sq-theme', next); } catch (e) {}
      sync();
    });
  });
  if (mq.addEventListener) mq.addEventListener('change', sync);
  sync();

  /* ---------- header tabs: fade when more tabs are off to the right ---------- */
  var tw = document.querySelector('.tabs-wrap'), tl = tw && tw.querySelector('.tabs');
  if (tl) {
    var on = tl.querySelector('a.on');
    if (on && tl.scrollWidth > tl.clientWidth) tl.scrollLeft = on.offsetLeft - 24;
    var fade = function () { tw.classList.toggle('more', tl.scrollLeft + tl.clientWidth < tl.scrollWidth - 4); };
    tl.addEventListener('scroll', fade, { passive: true });
    window.addEventListener('resize', fade);
    fade();
  }

  /* ---------- the cabinet (home page folders) ---------- */
  var folders = Array.prototype.slice.call(document.querySelectorAll('.cabinet .folder'));
  function setOpen(f, open) {
    f.classList.toggle('open', open);
    var btn = f.querySelector('.tab button');
    if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  // how long each folder's "pop" plays before it opens
  var REVEAL = { 'side-quests': 720, comic: 760, thought: 820, photos: 620, spotlight: 760, learn: 720, shop: 760 };
  function openFolder(f, opts) {
    opts = opts || {};
    if (f.classList.contains('revealing')) return;
    var opening = !f.classList.contains('open');
    if (opening && !opts.instant && !opts.force && !calm.matches) {
      f.classList.add('revealing');
      setTimeout(function () {
        f.classList.remove('revealing', 'peeking');
        doOpen(f, opts);
      }, REVEAL[f.id] || 720);
      return;
    }
    doOpen(f, opts);
  }
  function doOpen(f, opts) {
    var wasOpen = f.classList.contains('open');
    folders.forEach(function (x) { if (x !== f) setOpen(x, false); });
    setOpen(f, !wasOpen || opts.force);
    var nowOpen = f.classList.contains('open');
    try { history.replaceState(null, '', nowOpen ? '#' + f.id : location.pathname); } catch (e) {}
    if (nowOpen) bringIntoView(f, opts.instant);
  }
  function bringIntoView(f, instant) {
    // wait for the other folders to finish closing, then line this one up under the header
    setTimeout(function () {
      var tab = f.querySelector('.tab') || f;
      var top = tab.getBoundingClientRect().top;
      var head = document.querySelector('.site-head');
      var offset = (head ? head.offsetHeight : 0) + 16;
      if (top < offset || top > window.innerHeight * 0.5) {
        window.scrollTo({ top: window.scrollY + top - offset, behavior: instant ? 'auto' : 'smooth' });
      }
    }, instant ? 0 : 540);
  }
  folders.forEach(function (f) {
    var btn = f.querySelector('.tab button');
    if (btn) btn.addEventListener('click', function () { openFolder(f); });
    var strip = f.querySelector('.strip');
    if (strip) strip.addEventListener('click', function () { openFolder(f); });
  });
  function fromHash(instant) {
    var id = decodeURIComponent(location.hash.slice(1));
    var f = id && document.getElementById(id);
    if (f && folders.indexOf(f) > -1) openFolder(f, { force: true, instant: instant });
  }
  if (folders.length) {
    // phones have no hover: tease each folder as it scrolls through the middle of the screen
    if (window.matchMedia('(hover: none)').matches && 'IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { e.target.classList.toggle('peeking', e.isIntersecting); });
      }, { rootMargin: '-38% 0px -48% 0px' });
      folders.forEach(function (f) { io.observe(f); });
    }
    // spotlight folder: the light follows the cursor
    var spot = document.querySelector('.k-spotlight .sheet');
    if (spot) spot.addEventListener('pointermove', function (e) {
      var r = spot.getBoundingClientRect();
      spot.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      spot.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
    // first visit this session, no folder asked for: deal the folders in
    var cab = document.getElementById('cabinet');
    var seen = false;
    try { seen = sessionStorage.getItem('sq-dealt') === '1'; sessionStorage.setItem('sq-dealt', '1'); } catch (e) {}
    if (cab && !seen && !location.hash && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      cab.classList.add('deal');
      setTimeout(function () { cab.classList.remove('deal'); }, 2400);
    }
    fromHash(true);
    // fonts and images can shift the layout after load; line the open folder up again
    window.addEventListener('load', function () {
      var f = document.querySelector('.cabinet .folder.open');
      if (f) bringIntoView(f, true);
    });
    window.addEventListener('hashchange', function () { fromHash(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var f = document.querySelector('.cabinet .folder.open');
      if (!f) return;
      openFolder(f);
      var b = f.querySelector('.tab button'); if (b) b.focus();
    });
  }

  /* ---------- email signup ---------- */
  var form = document.getElementById('signup-form');
  if (form) {
    var msg = document.getElementById('signup-msg');
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      var email = form.email.value.trim();
      var btn = form.querySelector('button');
      var original = btn.textContent;
      btn.disabled = true; btn.textContent = 'Sending...'; msg.hidden = true;
      try {
        var res = await fetch('/api/subscribe', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email })
        });
        var data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Something went wrong.');
        form.hidden = true;
        msg.textContent = "You're on the list. That's it, that's the whole thing.";
        msg.className = 'signup-msg ok'; msg.hidden = false;
      } catch (err) {
        msg.textContent = err.message; msg.className = 'signup-msg err'; msg.hidden = false;
        btn.disabled = false; btn.textContent = original;
      }
    });
  }

  /* ---------- shop: send an item id to Stripe checkout ---------- */
  document.querySelectorAll('.buy').forEach(function (btn) {
    btn.addEventListener('click', async function () {
      var errBox = document.getElementById('shop-error');
      if (errBox) errBox.hidden = true;
      btn.disabled = true;
      var original = btn.textContent;
      btn.textContent = 'Loading...';
      try {
        var res = await fetch('/api/checkout', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ item: btn.dataset.item, qty: 1 })
        });
        var data = await res.json();
        if (!data.url) throw new Error(data.error || 'Checkout failed.');
        window.location.href = data.url;
      } catch (e) {
        if (errBox) { errBox.textContent = e.message; errBox.hidden = false; }
        btn.disabled = false; btn.textContent = original;
      }
    });
  });
})();
