# PhillyFinder

An independent, locally-curated guide to the best restaurants, things to do, museums, parks, neighborhoods, and day trips in Philadelphia. Static site, deployed on Cloudflare Pages.

## Structure

- `index.html` — homepage / hub
- `restaurants/` — best restaurants, best cheesesteaks
- `things-to-do/` — top attractions, best parks
- `arts-culture/` — best museums, theater & live music
- `day-trips/` — best day trips from Philadelphia
- `neighborhoods/` — neighborhoods hub + Fishtown guide
- `about.html`, `contact.html`, `advertise.html`, `privacy.html` — info pages
- `data/` — JSON data files that drive the guide pages
- `build_site.py` — regenerates all guide + info pages from `data/`

## Rebuilding

Edit the JSON in `data/`, then run:

```
python3 build_site.py
```

Every guide page (restaurants, cheesesteaks, things to do, parks, museums, theater & music, day trips, Fishtown), the neighborhoods hub, and the info pages are regenerated from the data files and templates. Commit and push to `main`; Cloudflare Pages auto-deploys.

## Ads

Ad slots are marked in place (leaderboard + in-content units). Replace the placeholder `.ad` blocks with real Monetag zone code once the live site is verified.
