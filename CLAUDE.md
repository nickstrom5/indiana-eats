# Indiana Eats (in-eats) — notes for Claude Code sessions

Built 2026-11-06 by a side session for Nick's "build the 17 states left" (group: Kentucky, Indiana, Missouri, Kansas), ported from
`../ky-eats/` (itself from `../va-eats/`) with every fix through 2026-11-05 (delivery-only brands hidden, the website blocklist and
`link_blocklist.py`, the Share link `Links.site + explore/#p=<id>`, over-the-air data, the adult-venue rules, the Denny's check,
`playbook/app-store/listing.json`). Local only: git-ignored data, no repo, no remote, nothing published. Sources: `playbook/12-sources.md`.
Brand: `playbook/05-naming.md` — **provisional**, every choice waits for Nick ("Indiana Eats: Restaurants", subtitle "Tenderloins, Pie &
Drive-Ins", Home Screen "Indiana Eats"; a breaded tenderloin sandwich on flag blue #000F5D, brick red #8E2A1E cards, flag gold
#D59F0F fill only; a checkered stripe header).

## Indiana is different
- **No official data used.** 95 local health departments, none posting grades or results as data; Vanderburgh's weekly PDFs, Porter's
  monthly PDFs and Hamilton's ArcGIS layer post no terms and are Nick's call (playbook/12-sources.md). The ATC's alcohol permits sit
  behind a reCAPTCHA search. So no place is "official", no inspection result shows, and "Serves alcohol" is unknown everywhere.
  Every place links in.gov/localhealth.
- **No Google data at all** (the UCSD snapshot isn't downloaded; `listings.py` and `indiana.py` run without it).
- **ZIPs** 460xx-479xx. **One region** ("Indiana", one detail file); the site groups lists by county.
- **Guides** (tags in `indiana.py` TAGS; bits 1..16): tenderloin 4, driveins 15, pie 6, amish 5, oldest 6 (Knickerbocker Saloon 1835,
  Triple XXX 1929, Kunkel's 1954, Dog n Suds Lafayette 1956, The Suds 1957, Bo-Mac's 1960). Honors: James Beard only (no MICHELIN Guide
  covers Indiana): St. Elmo Steak House (America's Classics 2012) and the 2025-26 semifinalists (Red Yeti, Macizo, Lone Pine, Vida,
  Beholder; J'adore Pastry isn't in the map data). Only Indianapolis has a city page (four or more listed places).
- **Venues:** IND (7800 Col. H. Weir Cook Memorial Dr and the terminal box), FWA, SBN, EVV, Lucas Oil Stadium, Gainbridge Fieldhouse,
  the Motor Speedway, Notre Dame/Purdue/IU venues, the State Fairgrounds, Camp Atterbury, NSA Crane, the prisons.

## Rebuild
```bash
cd pipeline
../.venv/bin/python fetch_overture.py && ../.venv/bin/python fetch_extras.py && ../.venv/bin/python fetch_official.py
../.venv/bin/python geocode_official.py && ../.venv/bin/python geocode_census.py && ../.venv/bin/python listings.py
../.venv/bin/python calibrate.py && ../.venv/bin/python indiana.py && ../.venv/bin/python build_research.py && ../.venv/bin/python indiana.py
IN_APP=1 ../.venv/bin/python indiana.py && cd .. && cp data/app/places.json data/app/detail-*.json IndianaEats/Resources/
.venv/bin/python pipeline/check_websites.py && .venv/bin/python pipeline/check_websites.py --retry-transient   # then re-export
.venv/bin/python scripts/make-site.py && .venv/bin/python scripts/publish_app_data.py && .venv/bin/python scripts/publish_app_data.py --check
.venv/bin/python scripts/qa-site.py --static
```
The `.venv` is a copy of va-eats' (python.org framework 3.12). Run `xcodegen generate` when the set of `Resources/*.json` changes.

## App, site, screenshots
- App: `IndianaEats/` (bundle `com.indianaeats.ios`), tests in `IndianaEatsTests/` (fixture, outline with Hammond, Evansville and
  Jeffersonville in and Calumet City, Louisville and Cincinnati out, bundled-data guards) and `IndianaEatsUITests/`. Archive only with
  Xcode 1.app (27.2, 27B52).
- Site: `scripts/make-site.py` (14 pages; nickstrom5.github.io/indiana-eats until a CNAME exists), `scripts/explore.js`, `scripts/qa-site.py`
  (its other-state check allows Michigan City, East Chicago and Nashville, all Indiana towns).
- Screenshots: `scripts/capture-screenshots.sh` (ScreenshotMode: downtown Indianapolis; West Lafayette for drive-ins, Shipshewana for
  Amish country; detail = Triple XXX), then `scripts/site-images.sh`, `scripts/appstore-screenshots.py`.

## Status (2026-11-06, ready to publish; nothing public)
- Pipeline: app 13,985 places / 13,476 restaurants in 507 towns; research 33/34 matched; websites link-checked (check_websites.py +
  `--retry-transient`). **No official data used** (no statewide inspections; county sources and the ATC's reCAPTCHA-gated permits are
  Nick's call, playbook/12-sources.md).
- Tests (Xcode 1.app, iOS 27.0): unit 49/49 on iPhone 17 Pro Max and iPad Pro 13" M5; UI 5/6 on iPhone (testLaunchIsQuick skipped itself: load 73, not judged) and 6/6 on
  iPad. testTourEveryScreen now searches "indianapolis" (a one-result search shows "1 place ·", not "places ·").
- Site: 14 pages, `qa-site.py --static` OK; OTA 2026-11-06.3 `--check` OK (local only). Screens: docs/screenshots (11), App Store frames
  playbook/app-store/iphone (8) and ipad (6). Icon A passes check.swift. `playbook/app-store/listing.json` (support/privacy URLs on
  nickstrom5.github.io/indiana-eats/, 404 until Pages is on).
- **Nick decides:** name, icon and palette (playbook/05-naming.md); a county inspection source (Vanderburgh PDFs first); the repo, Pages,
  App Store Connect record and upload.

## Rules
No commits, pushes, public repos, App Store Connect or DNS changes without Nick's yes each time; never submit for review or accept
agreements; never publish Google-derived data. Support email nick@eatsranked.com. Commit author "Nick Soderstrom"
<329204362+nickstrom5@users.noreply.github.com> via `-c user.name -c user.email`.
