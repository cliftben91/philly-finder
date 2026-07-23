#!/usr/bin/env python3
"""Build all GuidePhilly pages from data files. Regenerate the whole site: python3 build_site.py"""
import json, html, pathlib
from urllib.parse import quote

BASE = pathlib.Path(__file__).parent
D = BASE / "data"

def esc(s):
    return html.escape(str(s), quote=False) if s is not None else ""

def load(name):
    return json.loads((D / name).read_text(encoding="utf-8"))

restaurants = load("best-restaurants.json")
_r = load("restaurants.json")
cheesesteaks = _r["best_cheesesteaks"]
fishtown = _r["best_fishtown"]
things = load("things-to-do.json")
parks = load("parks.json")
museums = load("museums.json")
venues = load("arts-venues.json")
daytrips = load("day-trips.json")
HEROES = load("img-heroes.json")
LANDMARKS = load("img-landmarks.json")
CUISINES = load("img-cuisines.json")

def cuisine_bucket(c):
    c = (c or "").lower()
    pairs = [
      ("cheesesteak","Cheesesteaks"),("pizza","Pizza"),("ramen","Ramen"),
      ("sushi","Japanese"),("japanese","Japanese"),("sichuan","Chinese"),("dim sum","Chinese"),
      ("chinese","Chinese"),("modern asian","Chinese"),("thai","Thai"),("vietnam","Vietnamese"),
      ("korean","Korean"),("mexican","Mexican"),("filipino","Filipino"),("cambodian","Cambodian"),
      ("israeli","Israeli"),("lebanese","Lebanese"),("mediterranean","Lebanese"),("greek","Greek"),
      ("turkish","Turkish"),("armenian","Armenian"),("french","French"),("spanish","Spanish"),
      ("cuban","Cuban"),("british","British"),("steakhouse","Steakhouse"),("steak","Steakhouse"),
      ("seafood","Seafood"),("vegan","Vegan"),("southern","Southern"),("african","Southern"),
      ("brew","Brewpub"),("beer garden","Brewpub"),("portuguese","Portuguese"),
      ("bakery","Bakery"),("new american","New American"),("brunch","American"),("diner","American"),
      ("burger","American"),("gastropub","American"),("wine bar","American"),("sandwich","American"),
      ("italian","Italian"),("american","American"),
    ]
    for k, v in pairs:
        if k in c:
            return v
    return "New American"

def item_image(item, idx):
    name = item.get("name", "")
    if LANDMARKS.get(name):
        return LANDMARKS[name]
    if item.get("cuisine"):
        pool = CUISINES.get(cuisine_bucket(item["cuisine"]))
        if pool:
            return pool[(idx - 1) % len(pool)]
    return None

WEBSITES = load("websites.json")

def website_url(item):
    u = WEBSITES.get(item.get("name", ""))
    if u:
        return u
    loc = item.get("neighborhood") or item.get("location") or "Philadelphia"
    return "https://www.google.com/search?q=" + quote(f'{item.get("name","")} {loc}')

def maps_url(item):
    name = item.get("name", "")
    if item.get("address"):
        q = f'{name} {item["address"]}'
    else:
        q = f'{name} {item.get("neighborhood") or item.get("location") or "Philadelphia"}'
    return "https://www.google.com/maps/search/?api=1&query=" + quote(q)

CSS = """
  :root{--ink:#1a1611;--paper:#f7f2e9;--card:#ffffff;--muted:#6f665a;--line:#e4dccd;
    --accent:#bf3c25;--accent-dark:#9a2f1c;--gold:#b6892f;
    --shadow:0 1px 2px rgba(26,22,17,.04),0 8px 30px rgba(26,22,17,.07);--radius:14px;}
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{font-family:'Inter',system-ui,sans-serif;color:var(--ink);background:var(--paper);line-height:1.6;-webkit-font-smoothing:antialiased}
  h1,h2,h3,h4{font-family:'Archivo',system-ui,sans-serif;line-height:1.1;font-weight:800;letter-spacing:-.02em}
  a{color:inherit;text-decoration:none}
  .wrap{max-width:1180px;margin:0 auto;padding:0 24px}
  .narrow{max-width:820px;margin:0 auto;padding:0 24px}
  .eyebrow{font-family:'Inter';font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}
  .ad{display:flex;flex-direction:column;align-items:center;justify-content:center;border:1px dashed #cbb9a6;border-radius:10px;
    background:repeating-linear-gradient(45deg,#f0e8da,#f0e8da 10px,#ece2d1 10px,#ece2d1 20px);
    color:#a3907a;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;text-align:center}
  .ad small{font-size:9px;letter-spacing:.1em;margin-top:3px;opacity:.7;font-weight:600}
  .ad-leaderboard{height:90px}
  .ad-inline{height:110px;margin:26px 0}
  .topbar{background:var(--ink);color:#f7f2e9;font-size:12.5px}
  .topbar .wrap{display:flex;align-items:center;justify-content:center;padding:9px 24px;text-align:center}
  .topbar strong{color:#fff;font-weight:600}
  header.site{position:sticky;top:0;z-index:50;background:rgba(247,242,233,.92);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
  .nav{display:flex;align-items:center;justify-content:space-between;height:70px;gap:20px}
  .brand{font-family:'Archivo';font-weight:900;font-size:23px;letter-spacing:-.03em;display:flex;align-items:center;gap:9px;white-space:nowrap}
  .brand .mark{width:30px;height:30px;border-radius:8px;background:var(--accent);color:#fff;display:grid;place-items:center;font-size:12px;font-weight:900;letter-spacing:-.3px;transform:rotate(-4deg)}
  .brand b{color:var(--accent)}
  nav.links{display:flex;gap:26px;align-items:center}
  nav.links a{font-size:14.5px;font-weight:600;color:var(--ink)}
  nav.links a:hover{color:var(--accent)}
  .nav-cta{background:var(--ink);color:#fff!important;padding:9px 16px;border-radius:999px;font-size:13.5px;font-weight:700}
  .nav-cta:hover{background:var(--accent)}
  .menu-btn{display:none;background:none;border:0;font-size:24px;cursor:pointer;color:var(--ink)}
  .crumbs{font-size:13px;color:var(--muted);padding:26px 0 0}
  .crumbs a:hover{color:var(--accent)}
  .art-head{padding:14px 0 8px}
  .art-head h1{font-size:46px;letter-spacing:-.03em;margin:12px 0 16px}
  .art-head .dek{font-size:19px;color:var(--muted);max-width:40em}
  .byline{display:flex;align-items:center;gap:10px;margin-top:20px;font-size:13.5px;color:var(--muted)}
  .byline .avatar{width:34px;height:34px;border-radius:50%;background:linear-gradient(150deg,#c14a34,#7c2417);color:#fff;display:grid;place-items:center;font-family:'Archivo';font-weight:800;font-size:14px}
  .byline b{color:var(--ink);font-weight:700}
  .intro{font-size:17px;color:#463f34;margin:28px 0 8px}
  .intro p{margin-bottom:16px}
  .prose{font-size:16.5px;color:#463f34}
  .prose h2{font-size:24px;margin:30px 0 12px}
  .prose p{margin-bottom:16px}
  .prose ul{margin:0 0 16px 22px}
  .prose li{margin-bottom:8px}
  .entry{padding:34px 0;border-top:1px solid var(--line)}
  .entry:first-of-type{border-top:0}
  .entry-head{display:flex;align-items:baseline;gap:14px;margin-bottom:2px}
  .entry-head .rank{font-family:'Archivo';font-weight:900;font-size:30px;color:var(--accent);line-height:1;min-width:44px}
  .entry-head h2{font-size:27px}
  .tagline{color:var(--accent-dark);font-weight:600;font-size:15px;margin:0 0 6px 58px}
  .entry-meta{display:flex;flex-wrap:wrap;gap:9px;align-items:center;font-size:13.5px;color:var(--muted);margin:6px 0 16px 58px}
  .entry-meta .tag{background:#efe6d6;color:#6a5c43;font-weight:600;padding:4px 10px;border-radius:999px;font-size:12px}
  .entry-meta .price{color:var(--gold);font-weight:700}
  .entry-photo{height:300px;border-radius:var(--radius);margin:0 0 18px;position:relative;display:grid;place-items:center;color:#fff;overflow:hidden}
  .entry-photo::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 45%,rgba(0,0,0,.32))}
  .entry-photo b{position:relative;z-index:2;font-family:'Archivo';font-weight:800;font-size:26px;text-shadow:0 1px 14px rgba(0,0,0,.35);padding:0 20px;text-align:center}
  .entry-photo .ph-note{position:absolute;bottom:10px;right:12px;z-index:2;font-size:10px;letter-spacing:.1em;text-transform:uppercase;opacity:.7}
  .entry-body{font-size:16px;color:#463f34}
  .entry-body p{margin-bottom:12px}
  .signature{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:14px;margin-top:4px}
  .signature em{font-style:normal;color:var(--accent);font-weight:700;text-transform:uppercase;font-size:11px;letter-spacing:.08em}
  .signature b{color:var(--ink)}
  .addr{font-size:13.5px;color:var(--muted);margin-top:10px}
  .addr em{font-style:normal;font-weight:700;color:#6a5c43}
  .related{background:var(--ink);color:#f7f2e9;border-radius:20px;padding:40px;text-align:center;margin:44px 0}
  .related .eyebrow{color:var(--gold)}
  .related h2{color:#fff;font-size:28px;margin:10px 0 18px}
  .btn{display:inline-flex;align-items:center;gap:8px;font-weight:700;font-size:15px;padding:13px 22px;border-radius:999px;cursor:pointer;border:0;font-family:inherit;background:var(--accent);color:#fff}
  .btn:hover{background:var(--accent-dark)}
  .hubgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin:30px 0}
  .hubcard{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;transition:transform .16s ease,box-shadow .2s ease;display:flex;flex-direction:column}
  .hubcard:hover{transform:translateY(-4px);box-shadow:var(--shadow)}
  .hubcard .top{height:120px;display:grid;place-items:center;color:#fff;font-family:'Archivo';font-weight:800;font-size:22px;text-shadow:0 1px 10px rgba(0,0,0,.25)}
  .hubcard .bot{padding:16px 18px}
  .hubcard .bot p{font-size:13.5px;color:var(--muted);margin-top:4px}
  .hubcard .bot .go{font-size:12.5px;font-weight:700;color:var(--accent);margin-top:10px;display:inline-block}
  footer{background:var(--ink);color:#c9beac;margin-top:20px}
  .foot-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:36px;padding:56px 0 34px}
  .foot-grid .brand{color:#fff;margin-bottom:12px}
  .foot-grid .brand b{color:var(--accent)}
  footer p.tag{font-size:13.5px;color:#9b917f;max-width:26em}
  footer h4{font-family:'Inter';font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#8a8072;margin-bottom:14px;font-weight:700}
  footer ul{list-style:none;display:flex;flex-direction:column;gap:9px}
  footer ul a{font-size:14px;color:#c9beac}
  footer ul a:hover{color:#fff}
  .foot-bottom{border-top:1px solid rgba(255,255,255,.09);padding:18px 0;display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;font-size:12.5px;color:#8a8072}
  @media(max-width:760px){.art-head h1{font-size:34px}nav.links{display:none}.menu-btn{display:block}
    .entry-head h2{font-size:22px}.entry-head .rank{font-size:24px;min-width:34px}
    .entry-meta,.tagline{margin-left:0}.entry-photo{height:210px}
    .hubgrid{grid-template-columns:1fr 1fr}.foot-grid{grid-template-columns:1fr 1fr}}
"""

GRADS = ["g1","g2","g3","g4","g5","g6"]
GRAD_CSS = """
  .g1{background:linear-gradient(150deg,#c14a34,#7c2417)}
  .g2{background:linear-gradient(150deg,#2f4b52,#16292e)}
  .g3{background:linear-gradient(150deg,#b6892f,#6f4f14)}
  .g4{background:linear-gradient(150deg,#6b5b95,#3a2f54)}
  .g5{background:linear-gradient(150deg,#3f7360,#1f3a30)}
  .g6{background:linear-gradient(150deg,#a34760,#5e2436)}
  .entry-photo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0}
  .entry-photo::after{z-index:1}
  .pagehero{position:relative;background-color:var(--ink);background-size:cover;background-position:center;color:#fff;border-bottom:1px solid var(--line)}
  .pagehero .narrow{padding:22px 24px 42px}
  .pagehero .crumbs{color:rgba(255,255,255,.8);padding:0}
  .pagehero .crumbs a{color:rgba(255,255,255,.85)}
  .pagehero .crumbs a:hover{color:#fff}
  .pagehero .eyebrow{color:#fff}
  .pagehero .art-head{padding:12px 0 0}
  .pagehero .art-head h1{color:#fff;text-shadow:0 2px 24px rgba(0,0,0,.45)}
  .pagehero .art-head .dek{color:rgba(255,255,255,.92)}
  .pagehero .byline{color:rgba(255,255,255,.82)}
  .pagehero .byline b{color:#fff}
  .hubcard .top{position:relative;overflow:hidden}
  .hubcard .top img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0}
  .hubcard .top::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.15),rgba(0,0,0,.5));z-index:1}
  .hubcard .top span{position:relative;z-index:2}
  .entry-head h2 a{color:inherit}
  .entry-head h2 a:hover{color:var(--accent)}
  a.entry-photo{cursor:pointer;text-decoration:none}
  .addr a{color:var(--accent-dark);text-decoration:underline;text-underline-offset:2px}
  .addr a:hover{color:var(--accent)}
  .actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
  .actions .act{font-size:13px;font-weight:700;color:var(--accent);border:1px solid var(--line);border-radius:999px;padding:8px 15px;background:#fff;transition:all .16s ease}
  .actions .act:hover{background:var(--accent);color:#fff;border-color:var(--accent)}
"""

NAV = """
<div class="topbar"><div class="wrap"><span>Updated for 2026 &mdash; <strong>the definitive local guide to eating and exploring in Philadelphia</strong></span></div></div>
<header class="site">
  <div class="wrap nav">
    <a class="brand" href="/"><span class="mark">GP</span>Guide<b>Philly</b></a>
    <nav class="links">
      <a href="/restaurants/best-restaurants-philadelphia.html">Restaurants</a>
      <a href="/things-to-do/best-things-to-do-philadelphia.html">Things to Do</a>
      <a href="/arts-culture/best-museums-philadelphia.html">Arts &amp; Culture</a>
      <a href="/neighborhoods/">Neighborhoods</a>
      <a href="/day-trips/best-day-trips-from-philadelphia.html">Day Trips</a>
      <a class="nav-cta" href="/restaurants/best-restaurants-philadelphia.html">Explore Philly</a>
    </nav>
    <button class="menu-btn" aria-label="Menu">&#9776;</button>
  </div>
</header>
"""

FOOTER = """
<footer>
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="/">Guide<b>Philly</b></a>
        <p class="tag">Your independent, locally-curated guide to the best restaurants, things to do, and neighborhoods in Philadelphia.</p>
      </div>
      <div><h4>Eat</h4><ul>
        <li><a href="/restaurants/best-restaurants-philadelphia.html">Best Restaurants</a></li>
        <li><a href="/restaurants/best-cheesesteaks-philadelphia.html">Best Cheesesteaks</a></li>
        <li><a href="/neighborhoods/best-restaurants-fishtown.html">Restaurants in Fishtown</a></li>
        <li><a href="/neighborhoods/">Neighborhoods</a></li></ul></div>
      <div><h4>Explore</h4><ul>
        <li><a href="/things-to-do/best-things-to-do-philadelphia.html">Things to Do</a></li>
        <li><a href="/things-to-do/best-parks-philadelphia.html">Best Parks</a></li>
        <li><a href="/arts-culture/best-museums-philadelphia.html">Museums</a></li>
        <li><a href="/arts-culture/theater-and-live-music-philadelphia.html">Theater &amp; Music</a></li>
        <li><a href="/day-trips/best-day-trips-from-philadelphia.html">Day Trips</a></li></ul></div>
      <div><h4>About</h4><ul>
        <li><a href="/about.html">Our Story</a></li>
        <li><a href="/contact.html">Contact</a></li>
        <li><a href="/advertise.html">Advertise</a></li>
        <li><a href="/privacy.html">Privacy</a></li></ul></div>
    </div>
    <div class="foot-bottom">
      <span>&copy; 2026 GuidePhilly. Made in Philadelphia.</span>
      <span>Photos via Unsplash, Pexels &amp; Wikimedia Commons.</span>
      <span>Not affiliated with the City of Philadelphia or Visit Philadelphia.</span>
    </div>
  </div>
</footer>
"""

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{meta}">
<link rel="canonical" href="{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
"""

AD_INLINE = '<div class="ad ad-inline">Advertisement<small>Responsive &middot; Monetag native / display zone</small></div>'
AD_LEAD = '<div class="wrap" style="padding-top:14px"><div class="ad ad-leaderboard">Advertisement<small>728 &times; 90 &middot; Monetag zone</small></div></div>'

def crumbs_html(crumbs):
    parts = []
    for label, href in crumbs:
        if href:
            parts.append(f'<a href="{href}">{esc(label)}</a>')
        else:
            parts.append(esc(label))
    return '<div class="crumbs">' + " / ".join(parts) + "</div>"

def entry_html(i, item):
    g = GRADS[(i - 1) % len(GRADS)]
    tag = item.get("tag") or item.get("cuisine")
    location = item.get("location") or item.get("neighborhood")
    price = item.get("price") or item.get("price_range")
    highlight = item.get("highlight")
    signature = item.get("signature_dish")
    meta = []
    if tag: meta.append(f'<span class="tag">{esc(tag)}</span>')
    if location: meta.append(f'<span>{esc(location)}</span>')
    if price: meta.append(f'<span class="price">{esc(price)}</span>')
    tagline = f'<p class="tagline">{esc(highlight)}</p>' if highlight else ""
    sig = f'<div class="signature"><em>Signature</em>&nbsp; <b>{esc(signature)}</b></div>' if signature else ""
    site = website_url(item)
    maps = maps_url(item)
    addr = f'<div class="addr"><em>Address:</em> <a href="{maps}" target="_blank" rel="noopener noreferrer">{esc(item["address"])}</a></div>' if item.get("address") else ""
    img = item_image(item, i)
    imgtag = f'<img src="{img}" alt="{esc(item["name"])}" loading="lazy" onerror="this.style.display=&#39;none&#39;">' if img else ""
    phnote = "" if img else '<span class="ph-note">Photo</span>'
    actions = f'<div class="actions"><a class="act" href="{site}" target="_blank" rel="noopener noreferrer">Visit website &#8599;</a><a class="act" href="{maps}" target="_blank" rel="noopener noreferrer">Get directions &#8599;</a></div>'
    return f'''  <div class="entry">
    <div class="entry-head"><span class="rank">{i}</span><h2><a href="{site}" target="_blank" rel="noopener noreferrer">{esc(item["name"])}</a></h2></div>
    {tagline}
    <div class="entry-meta">{"".join(meta)}</div>
    <a class="entry-photo {g}" href="{site}" target="_blank" rel="noopener noreferrer">{imgtag}<b>{esc(item["name"])}</b>{phnote}</a>
    <div class="entry-body"><p>{esc(item["description"])}</p>{sig}{addr}{actions}</div>
  </div>'''

def render_listicle(cfg, items):
    entries = []
    for i, it in enumerate(items, start=1):
        entries.append(entry_html(i, it))
        if i % 5 == 0 and i != len(items):
            entries.append("  " + AD_INLINE)
    intro = "".join(f"<p>{esc(p)}</p>" for p in cfg["intro"])
    rel = cfg["related"]
    css = CSS + GRAD_CSS
    hero_url = HEROES.get(cfg.get("hero") or "")
    hero_style = (f"background-image:linear-gradient(rgba(20,16,12,.58),rgba(20,16,12,.72)), url('{hero_url}')"
                  if hero_url else "")
    return HEAD.format(title=esc(cfg["title"]), meta=esc(cfg["meta"]), css=css, canonical=cfg.get("canonical", "https://guidephilly.com/")) + f'''{NAV}
<div class="pagehero" style="{hero_style}">
  <div class="narrow">
    {crumbs_html(cfg["crumbs"])}
    <div class="art-head">
      <span class="eyebrow">{esc(cfg["eyebrow"])}</span>
      <h1>{esc(cfg["h1"])}</h1>
      <p class="dek">{esc(cfg["dek"])}</p>
      <div class="byline"><span class="avatar">GP</span><span>By the <b>GuidePhilly</b> team &middot; Updated July 2026</span></div>
    </div>
  </div>
</div>
{AD_LEAD}
<div class="narrow">
  <div class="intro">{intro}</div>
  {AD_INLINE}
{chr(10).join(entries)}
  <div class="related">
    <span class="eyebrow">Keep exploring</span>
    <h2>{esc(rel[0])}</h2>
    <a class="btn" href="{rel[1]}">{esc(rel[2])} &rarr;</a>
  </div>
</div>
{FOOTER}
</body>
</html>
'''

def render_static(title, meta, eyebrow, h1, crumbs, body, canonical="https://guidephilly.com/"):
    return HEAD.format(title=esc(title), meta=esc(meta), css=CSS, canonical=canonical) + f'''{NAV}
{AD_LEAD}
<div class="narrow" style="padding-bottom:40px">
  {crumbs_html(crumbs)}
  <div class="art-head"><span class="eyebrow">{esc(eyebrow)}</span><h1>{esc(h1)}</h1></div>
  <div class="prose">{body}</div>
</div>
{FOOTER}
</body>
</html>
'''

def write(rel, content):
    p = BASE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {rel} ({len(content)} bytes)")

def canon(out):
    p = out
    if p.endswith("index.html"):
        p = p[:-len("index.html")]
    elif p.endswith(".html"):
        p = p[:-5]
    return "https://guidephilly.com/" + p

# ---- Listicle pages ----
PAGES = [
  (restaurants, "restaurants/best-restaurants-philadelphia.html", {
    "title":"The 25 Best Restaurants in Philadelphia (2026) — GuidePhilly",
    "meta":"From James Beard winners to tiny BYOs, our ranked guide to the 25 best restaurants in Philadelphia right now, updated for 2026.",
    "eyebrow":"Where to eat","h1":"The 25 Best Restaurants in Philadelphia",
    "dek":"From James Beard winners and Michelin stars to tiny BYOs, these are the tables defining Philadelphia dining right now.",
    "intro":["Philadelphia's dining scene has never been better. Over the past few years the city has racked up James Beard Awards, a growing list of Michelin stars, and a wave of ambitious BYOs that punch far above their size.","We pulled together the restaurants worth building a night, or a whole trip, around. From Southern Thai fireworks to fine-dining Italian and hidden sushi counters, here are the 25 best restaurants in Philadelphia right now."],
    "crumbs":[("Home","/"),("Restaurants",None)],
    "related":("The 10 Best Cheesesteaks in Philadelphia","/restaurants/best-cheesesteaks-philadelphia.html","See the ranking")}),
  (cheesesteaks, "restaurants/best-cheesesteaks-philadelphia.html", {
    "title":"The 10 Best Cheesesteaks in Philadelphia (2026) — GuidePhilly",
    "meta":"From John's Roast Pork to Pat's, Geno's and Tony Luke's, our ranked guide to the best cheesesteaks in Philadelphia, updated for 2026.",
    "eyebrow":"The Philly essential","h1":"The 10 Best Cheesesteaks in Philadelphia",
    "dek":"Whiz or provolone, wit or witout — here's where to get the city's greatest cheesesteak, from old-school legends to modern upstarts.",
    "intro":["No sandwich is more Philadelphia than the cheesesteak: thin-sliced beef griddled with onions, piled onto a long roll, and blanketed in Cheez Whiz or melted provolone. Everyone here has an opinion, and the best one depends on whether you're after tourist spectacle, connoisseur craft, or a late-night classic.","A quick primer on ordering like a local: 'whiz wit' means Cheez Whiz with onions; 'provolone witout' swaps the cheese and skips them. Now, the ten that matter most."],
    "crumbs":[("Home","/"),("Restaurants","/restaurants/best-restaurants-philadelphia.html"),("Best Cheesesteaks",None)],
    "related":("The 25 Best Restaurants in Philadelphia","/restaurants/best-restaurants-philadelphia.html","See the full guide")}),
  (fishtown, "neighborhoods/best-restaurants-fishtown.html", {
    "title":"The Best Restaurants in Fishtown, Philadelphia (2026) — GuidePhilly",
    "meta":"Kalaya, Laser Wolf, Suraya and more — the best restaurants in Philadelphia's Fishtown neighborhood, updated for 2026.",
    "eyebrow":"Neighborhood guide","h1":"The Best Restaurants in Fishtown",
    "dek":"Philadelphia's buzziest food neighborhood, from a James Beard-winning Thai flagship to live-fire grills and destination pizza.",
    "intro":["Once a working-class fishing district, Fishtown has become the single most exciting place to eat in Philadelphia. Its blocks of converted factories and rowhomes now hold some of the city's most acclaimed restaurants, side by side with great bars and coffee.","Here are the Fishtown tables worth crossing town for."],
    "crumbs":[("Home","/"),("Neighborhoods","/neighborhoods/"),("Fishtown",None)],
    "related":("The 25 Best Restaurants in Philadelphia","/restaurants/best-restaurants-philadelphia.html","See the citywide guide")}),
  (things, "things-to-do/best-things-to-do-philadelphia.html", {
    "title":"The Best Things to Do in Philadelphia (2026) — GuidePhilly",
    "meta":"Liberty Bell, Reading Terminal Market, the Rocky Steps and more — the best things to do and top attractions in Philadelphia, updated for 2026.",
    "eyebrow":"What to do","h1":"The Best Things to Do in Philadelphia",
    "dek":"Founding-era history, world-class museums, great markets and one-of-a-kind experiences — the essential Philadelphia checklist.",
    "intro":["Philadelphia rewards curiosity. It's the birthplace of American democracy, a serious arts and food town, and a city of distinct, walkable neighborhoods all packed into a compact core.","Whether you have a day or a long weekend, these are the attractions and experiences worth your time."],
    "crumbs":[("Home","/"),("Things to Do",None)],
    "related":("The Best Parks in Philadelphia","/things-to-do/best-parks-philadelphia.html","Explore the parks")}),
  (parks, "things-to-do/best-parks-philadelphia.html", {
    "title":"The Best Parks in Philadelphia (2026) — GuidePhilly",
    "meta":"Fairmount Park, the Wissahickon, Spruce Street Harbor Park and more — the best parks and green spaces in Philadelphia.",
    "eyebrow":"Get outside","h1":"The Best Parks in Philadelphia",
    "dek":"From a 2,000-acre riverside wilderness to hammock-strung waterfront pop-ups, Philly's green spaces are some of the best in any big city.",
    "intro":["For a dense East Coast city, Philadelphia is remarkably green, ringed and threaded by one of the largest urban park systems in the country.","Here are the parks, trails and gardens locals actually use, whether you want a rugged hike or a hammock by the river."],
    "crumbs":[("Home","/"),("Things to Do","/things-to-do/best-things-to-do-philadelphia.html"),("Best Parks",None)],
    "related":("The Best Things to Do in Philadelphia","/things-to-do/best-things-to-do-philadelphia.html","See all attractions")}),
  (museums, "arts-culture/best-museums-philadelphia.html", {
    "title":"The Best Museums in Philadelphia (2026) — GuidePhilly",
    "meta":"The Philadelphia Museum of Art, Barnes Foundation, Franklin Institute, Mutter Museum and more — the best museums in Philadelphia.",
    "eyebrow":"Arts & culture","h1":"The Best Museums in Philadelphia",
    "dek":"World-class art, hands-on science, medical oddities and founding-era history — Philadelphia is one of America's great museum cities.",
    "intro":["Few American cities pack as many great museums into as small a footprint as Philadelphia. The Benjamin Franklin Parkway alone strings together several world-class institutions in an easy walk.","From Impressionist masterpieces to a walk-through human heart, here are the museums worth planning a day around."],
    "crumbs":[("Home","/"),("Arts & Culture",None)],
    "related":("Theater & Live Music in Philadelphia","/arts-culture/theater-and-live-music-philadelphia.html","See music & theater")}),
  (venues, "arts-culture/theater-and-live-music-philadelphia.html", {
    "title":"The Best Theater & Live Music Venues in Philadelphia (2026) — GuidePhilly",
    "meta":"The Kimmel Center, Academy of Music, Union Transfer, the Fillmore and more — the best concert halls, theaters and live music venues in Philadelphia.",
    "eyebrow":"Arts & culture","h1":"Theater & Live Music in Philadelphia",
    "dek":"From the home of the Philadelphia Orchestra to intimate Fishtown clubs, here's where to catch a show in Philly.",
    "intro":["Philadelphia's performing-arts scene runs from grand historic opera houses to sweaty indie clubs, much of it clustered along the Avenue of the Arts and in Fishtown.","Here are the concert halls, theaters and live-music rooms worth building a night out around."],
    "crumbs":[("Home","/"),("Arts & Culture","/arts-culture/best-museums-philadelphia.html"),("Theater & Live Music",None)],
    "related":("The Best Museums in Philadelphia","/arts-culture/best-museums-philadelphia.html","See the museums")}),
  (daytrips, "day-trips/best-day-trips-from-philadelphia.html", {
    "title":"The Best Day Trips from Philadelphia (2026) — GuidePhilly",
    "meta":"New Hope, Longwood Gardens, Cape May, Lancaster and more — the best day trips within two hours of Philadelphia.",
    "eyebrow":"Get out of town","h1":"The Best Day Trips from Philadelphia",
    "dek":"Beaches, gardens, mountains and Amish country — all within about two hours of the city.",
    "intro":["One of the underrated perks of living in or visiting Philadelphia is how much sits within an easy drive: the Jersey Shore, world-class gardens, historic towns and mountain trails are all day-trip distance.","Here are the best places to escape for the day, no overnight bag required."],
    "crumbs":[("Home","/"),("Day Trips",None)],
    "related":("The Best Things to Do in Philadelphia","/things-to-do/best-things-to-do-philadelphia.html","Back to the city")}),
]

HERO_MAP = {
  "restaurants/best-restaurants-philadelphia.html":"restaurants",
  "restaurants/best-cheesesteaks-philadelphia.html":"cheesesteaks",
  "neighborhoods/best-restaurants-fishtown.html":"hood-fishtown",
  "things-to-do/best-things-to-do-philadelphia.html":"things-to-do",
  "things-to-do/best-parks-philadelphia.html":"parks",
  "arts-culture/best-museums-philadelphia.html":"museums",
  "arts-culture/theater-and-live-music-philadelphia.html":"theater-music",
  "day-trips/best-day-trips-from-philadelphia.html":"day-trips",
}
print("Building listicle pages...")
for items, out, cfg in PAGES:
    cfg["hero"] = HERO_MAP.get(out)
    cfg["canonical"] = canon(out)
    write(out, render_listicle(cfg, items))

NEIGHBORHOODS = [
  ("Rittenhouse","rittenhouse","hood-rittenhouse.json",
   "Philadelphia's most elegant square, ringed by brasseries, fine dining, and buzzy hotel restaurants.",
   "Rittenhouse Square sits at the center of Philadelphia's most polished dining district, where sidewalk brasseries, hotel dining rooms, and several of the city's best fine-dining tables cluster within a few blocks."),
  ("East Passyunk","east-passyunk","hood-east-passyunk.json",
   "South Philly's foodie playground: a restaurant row of Filipino, Italian, and inventive BYOs.",
   "Few streets in Philadelphia pack more great restaurants per block than East Passyunk Avenue, a South Philly strip that runs from century-old Italian to award-winning Filipino and Vietnamese."),
  ("Old City","old-city","hood-old-city.json",
   "Historic cobblestone blocks packed with tapas, sushi, and Stephen Starr landmarks.",
   "Philadelphia's most historic quarter is also a serious dining destination, where founding-era cobblestones lead to buzzy tapas houses, omakase counters, and theatrical Stephen Starr rooms."),
  ("Northern Liberties","northern-liberties","hood-northern-liberties.json",
   "A trendy, walkable district of vegan fine dining, brunch spots, and global flavors.",
   "Once industrial and now one of the city's trendiest neighborhoods, Northern Liberties has become a magnet for ambitious restaurants, from nationally praised vegan cooking to packed brunch spots and global BYOs."),
  ("Manayunk","manayunk","hood-manayunk.json",
   "Main Street's hillside strip of gastropubs, breweries, and easygoing neighborhood spots.",
   "Manayunk's Main Street hugs the Schuylkill with a walkable strip of gastropubs, a riverside brewery, and easygoing neighborhood restaurants that are perfect after a day on the towpath."),
  ("Fairmount","fairmount","hood-fairmount.json",
   "The Art Museum area's mix of Italian standouts, cozy BYOs, and neighborhood gems.",
   "Just behind the Art Museum, Fairmount pairs a laid-back residential feel with a surprisingly deep dining bench, from destination Italian to cozy BYOs and reliable neighborhood taverns."),
  ("University City","university-city","hood-university-city.json",
   "Eclectic dining around Penn and Drexel, from farm-to-table to standout dumplings.",
   "Anchored by Penn and Drexel, University City serves a global, student-and-professor-friendly mix, from a pioneering farm-to-table cafe to some of the city's best dumplings and ramen."),
  ("Bella Vista","bella-vista","hood-bella-vista.json",
   "The Italian Market's home turf of century-old red-sauce icons and modern Mexican.",
   "Home to the 9th Street Italian Market, Bella Vista is where Philadelphia's red-sauce heritage lives on, alongside a new wave of acclaimed Mexican kitchens and a Vetri pasta bar."),
]
print("Building neighborhood pages...")
for name, slug, dfile, dek, introline in NEIGHBORHOODS:
    n_items = load(dfile)
    n_cfg = {
      "hero": f"hood-{slug}",
      "canonical": canon(f"neighborhoods/best-restaurants-{slug}.html"),
      "title": f"The Best Restaurants in {name}, Philadelphia (2026) - GuidePhilly",
      "meta": f"A curated, updated 2026 guide to the best restaurants in {name}, Philadelphia - where to eat and what to order.",
      "eyebrow": "Neighborhood guide",
      "h1": f"The Best Restaurants in {name}",
      "dek": dek,
      "intro": [introline, f"Here are the best restaurants in {name} right now."],
      "crumbs": [("Home","/"),("Neighborhoods","/neighborhoods/"),(name,None)],
      "related": ("The 25 Best Restaurants in Philadelphia","/restaurants/best-restaurants-philadelphia.html","See the citywide guide"),
    }
    write(f"neighborhoods/best-restaurants-{slug}.html", render_listicle(n_cfg, n_items))

# ---- Neighborhoods hub ----
HOODS = [
  ("Fishtown","g1","Buzzy converted factories and the city's most exciting new restaurants.","/neighborhoods/best-restaurants-fishtown.html"),
  ("Rittenhouse","g4","Elegant square ringed by brasseries and fine dining.","/neighborhoods/best-restaurants-rittenhouse.html"),
  ("East Passyunk","g2","South Philly's foodie playground and restaurant row.","/neighborhoods/best-restaurants-east-passyunk.html"),
  ("Old City","g5","Historic cobblestones, tapas, sushi, and landmarks.","/neighborhoods/best-restaurants-old-city.html"),
  ("Northern Liberties","g6","Trendy, walkable global dining and brunch.","/neighborhoods/best-restaurants-northern-liberties.html"),
  ("Manayunk","g3","Main Street gastropubs, breweries, and river views.","/neighborhoods/best-restaurants-manayunk.html"),
  ("Fairmount","g1","Art Museum-area Italian, BYOs, and gems.","/neighborhoods/best-restaurants-fairmount.html"),
  ("University City","g5","Eclectic dining around Penn and Drexel.","/neighborhoods/best-restaurants-university-city.html"),
  ("Bella Vista","g2","Italian Market icons and modern Mexican.","/neighborhoods/best-restaurants-bella-vista.html"),
]
def _hub_card(name, g, desc, href):
    slug = href.split("best-restaurants-")[1].replace(".html", "") if "best-restaurants-" in href else ""
    himg = HEROES.get("hood-" + slug)
    imgtag = f'<img src="{himg}" alt="{esc(name)}" loading="lazy" onerror="this.style.display=&#39;none&#39;">' if himg else ""
    return f'''<a class="hubcard" href="{href}"><div class="top {g}">{imgtag}<span>{esc(name)}</span></div><div class="bot"><p>{esc(desc)}</p><span class="go">Explore &rarr;</span></div></a>'''
hub_cards = "".join(_hub_card(*h) for h in HOODS)
hub_hero = HEROES.get("neighborhoods")
hub_hero_style = (f"background-image:linear-gradient(rgba(20,16,12,.58),rgba(20,16,12,.72)), url('{hub_hero}')"
                  if hub_hero else "")
hub_body = HEAD.format(
    title="Philadelphia Neighborhoods Guide - GuidePhilly",
    meta="A guide to Philadelphia's neighborhoods, from buzzy Fishtown to historic Old City and the Italian Market of South Philly.",
    css=CSS + GRAD_CSS, canonical="https://guidephilly.com/neighborhoods/") + f'''{NAV}
<div class="pagehero" style="{hub_hero_style}">
  <div class="narrow">
    {crumbs_html([("Home","/"),("Neighborhoods",None)])}
    <div class="art-head"><span class="eyebrow">Explore by area</span><h1>Philadelphia Neighborhoods</h1>
    <p class="dek">Every neighborhood has its own personality, and its own best places to eat and explore. Start here.</p></div>
  </div>
</div>
{AD_LEAD}
<div class="wrap">
  <div class="hubgrid">{hub_cards}</div>
  {AD_INLINE}
</div>
{FOOTER}
</body>
</html>
'''
print("Building neighborhoods hub...")
write("neighborhoods/index.html", hub_body)

# ---- Static pages ----
print("Building info pages...")
about_body = """
<p>GuidePhilly is an independent, locally-minded guide to the best of Philadelphia &mdash; the restaurants worth crossing town for, the museums and attractions worth your afternoon, the parks locals actually use, and the neighborhoods that give the city its character.</p>
<h2>What we do</h2>
<p>We cut through the noise. Instead of endless listings, we publish focused, ranked guides to the things that matter most: where to eat, what to see, and how to spend a great day in Philadelphia. Every guide is researched, curated, and kept up to date.</p>
<h2>How we choose</h2>
<p>Our picks draw on local knowledge and a wide read of trusted sources &mdash; James Beard recognition, critical acclaim, and the places Philadelphians genuinely love. We update our guides regularly as new spots open and the city changes.</p>
<h2>Get in touch</h2>
<p>Spot something out of date, or think we missed a gem? We'd love to hear it &mdash; head to our <a href="/contact.html">contact page</a> and let us know.</p>
"""
write("about.html", render_static(
    "About GuidePhilly","About GuidePhilly, an independent local guide to the best restaurants and things to do in Philadelphia.",
    "About","About GuidePhilly",[("Home","/"),("About",None)], about_body, canon("about.html")))

contact_body = """
<p>We'd love to hear from you &mdash; whether you have a correction, a suggestion for a spot we should cover, or a question about the site.</p>
<h2>Suggest a place or send a correction</h2>
<p>Restaurants open and close, and details change. If you notice something out of date or want to nominate a favorite, drop us a note using the form below.</p>
<form onsubmit="return false" style="margin-top:18px;display:flex;flex-direction:column;gap:12px;max-width:520px">
  <input type="text" placeholder="Your name" aria-label="Your name" style="padding:12px 14px;border:1.5px solid var(--line);border-radius:10px;font-family:inherit;font-size:15px">
  <input type="email" placeholder="Your email" aria-label="Your email" style="padding:12px 14px;border:1.5px solid var(--line);border-radius:10px;font-family:inherit;font-size:15px">
  <textarea placeholder="Your message" aria-label="Your message" rows="5" style="padding:12px 14px;border:1.5px solid var(--line);border-radius:10px;font-family:inherit;font-size:15px"></textarea>
  <button class="btn" type="submit" style="align-self:flex-start">Send message</button>
</form>
<p style="margin-top:18px;font-size:14px;color:var(--muted)">For advertising and partnership inquiries, see our <a href="/advertise.html">advertise page</a>.</p>
"""
write("contact.html", render_static(
    "Contact GuidePhilly","Get in touch with GuidePhilly to suggest a place, send a correction, or ask about advertising.",
    "Contact","Contact Us",[("Home","/"),("Contact",None)], contact_body, canon("contact.html")))

advertise_body = """
<p>GuidePhilly reaches people at the exact moment they're deciding where to eat, what to see, and how to spend their time in Philadelphia &mdash; a high-intent local and visitor audience.</p>
<h2>Partner with us</h2>
<p>We offer a limited number of tasteful advertising and sponsorship placements across the site. If you're a restaurant, attraction, or brand looking to reach engaged Philadelphia audiences, we'd like to talk.</p>
<h2>What we offer</h2>
<ul>
  <li>Display advertising across our most-read guides</li>
  <li>Sponsored placements and featured listings</li>
  <li>Custom local campaigns</li>
</ul>
<p>To start a conversation, reach out through our <a href="/contact.html">contact page</a> and mention advertising.</p>
"""
write("advertise.html", render_static(
    "Advertise with GuidePhilly","Advertise with GuidePhilly and reach a high-intent Philadelphia local and visitor audience.",
    "Advertise","Advertise With Us",[("Home","/"),("Advertise",None)], advertise_body, canon("advertise.html")))

privacy_body = """
<p><em>Last updated: July 2026.</em></p>
<p>This Privacy Policy explains how GuidePhilly ("we", "us") handles information when you visit our website. By using the site, you agree to the practices described here.</p>
<h2>Information we collect</h2>
<p>We do not require you to create an account or provide personal information to read our guides. If you contact us or submit a form, we collect only the information you choose to share, such as your name, email, and message.</p>
<h2>Cookies and analytics</h2>
<p>We use cookies and similar technologies to understand how visitors use the site and to improve it. We may use third-party analytics services that set their own cookies to measure traffic and usage.</p>
<h2>Advertising</h2>
<p>This site is supported by advertising. Third-party advertising partners may use cookies, web beacons, and similar technologies to serve ads and measure their performance, and may collect information such as your device type, browser, and general location to show more relevant advertising. You can typically manage ad personalization through your browser or device settings.</p>
<h2>Third-party links</h2>
<p>Our guides link to restaurants, venues, and other websites we don't control. We aren't responsible for the privacy practices of those third-party sites.</p>
<h2>Your choices</h2>
<p>Most browsers let you refuse or delete cookies. Doing so may affect how some parts of the site function. You can also opt out of personalized advertising through industry tools offered by advertising networks.</p>
<h2>Contact</h2>
<p>Questions about this policy? Reach us through our <a href="/contact.html">contact page</a>.</p>
"""
write("privacy.html", render_static(
    "Privacy Policy — GuidePhilly","GuidePhilly's privacy policy: how we handle cookies, analytics, and third-party advertising.",
    "Legal","Privacy Policy",[("Home","/"),("Privacy",None)], privacy_body, canon("privacy.html")))

print("Done.")
