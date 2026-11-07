"""Writes data/research/app/*.json (hand-checked Indiana guides), data/research/michelin.json, jbf.json and closed.json from the
compact lists below. Ported from ky-eats/pipeline/build_research.py (2026-11-06).

Each entry cites the page that names it, read on 2026-11-06: an official Indiana tourism page (visitindiana.in.gov, the Indiana
Destination Development Corporation; visitelkhartcounty.com, the Elkhart County CVB; visitshipshewana.org, the LaGrange County CVB), a
page dated 2025-26 on a robots-checked host (check_sources.py), or jamesbeard.org. The address comes from the map listing we already
hold for that name in that town (site/indiana.json); a name that isn't found exactly once in its town (or at the street number given) is
left out and listed in data/research/app/LEADS.md. A place the map data doesn't show as a place to eat is added only with a street
address from its official listing or our own map data (ADDR).
Usage: ../.venv/bin/python build_research.py   (then indiana.py)"""
import json, os, re
from brands import brand_of
from common import norm_name
ROOT = os.path.join(os.path.dirname(__file__), "..")
R = os.path.join(ROOT, "data", "research")
d = json.load(open(os.path.join(ROOT, "site", "indiana.json")))
C, M = d["cols"], d["meta"]
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower().replace("'", "").replace("’", ""))).strip()

# each dated on its face, or an official tourism page (read 2026-11-06)
VI_DRIVE = "https://visitindiana.in.gov/blog/post/indiana-drive-in-restaurants/"                       # Visit Indiana, 2026-06-25
VI_PIES = "https://visitindiana.in.gov/best-of-indiana/winners/best-pies/"                            # Visit Indiana, Best Pies IN Indiana
TT_BPT = "https://www.tastingtable.com/2186805/why-indiana-locals-love-pork-tenderloin-sandwiches"     # 2026-06-05
EC_AMISH = "https://www.visitelkhartcounty.com/blog/post/top-places-for-in-home-amish-style-dining/"   # Elkhart County CVB
VS = lambda slug: f"https://visitshipshewana.org/listings/{slug}"                                     # LaGrange County CVB listing
TT_OLDREST = "https://www.tastingtable.com/1975409/oldest-restaurant-every-state-still-open/"          # 2025-09-23
TT_OLDBAR = "https://www.tastingtable.com/1786324/oldest-bar-every-state/"                          # 2025-02-17
JBF26 = "https://www.jamesbeard.org/stories/james-beard-award-semifinalists-2026"                   # 2026-01-21
JBF25 = "https://www.jamesbeard.org/stories/the-2025-james-beard-award-semifinalists"               # 2025-01-22
JBF12_SE = "https://www.jamesbeard.org/stories/americas-classics-st-elmo-steak-house-indianapolis"   # 2012 America's Classics
MI_UT = "https://guide.michelin.com/us/en"                                                         # no MICHELIN Guide covers Indiana

# (name as the source writes it or as our listing spells it, town as our listing has it, street number to pick the location (or
# None), note, founded, founded_note, [sources])
IND = "Indianapolis"
GUIDES = {
 "tenderloin": [   # the breaded pork tenderloin, bigger than the bun
  ("Nick's Kitchen", "Huntington", None, "Claims the breaded pork tenderloin: Nick Freienstein swapped veal for pork in a schnitzel-style sandwich and opened here in 1908.", None, None, [TT_BPT]),
  ("Steer-In Indianapolis", IND, "5130", "An east-side diner with a spicy take on the tenderloin, and omelets, fried chicken and pies.", None, None, [TT_BPT, VI_DRIVE]),
  ("Mug-n-Bun", IND, "5211", "Tenderloins and homemade root beer for more than 50 years; flip your lights for car service.", None, None, [VI_DRIVE]),
  ("Ray's Drive-In", "Kokomo", None, "Carhop service only, known for its large King Tenderloin.", None, None, [VI_DRIVE]),
 ],
 "drive in": [   # Visit Indiana's drive-ins and carhops (June 2026)
  ("Triple XXX Family Restaurant", "West Lafayette", None, "Indiana's first drive-in, opened in 1929, per Visit Indiana; root beer on tap.", None, None, [VI_DRIVE]),
  ("Bo-Mac's Drive-In", "Shoals", None, "Carhop service since 1960: onion rings, shakes and sundaes.", None, None, [VI_DRIVE]),
  ("Mug-n-Bun", IND, "5211", "Tenderloins and homemade root beer for more than 50 years.", None, None, [VI_DRIVE]),
  ("Gene's Root Beer and Hot Dogs", "Anderson", None, "Homemade root beer, fried food and ice cream.", None, None, [VI_DRIVE]),
  ("Kunkel's Drive-In", "Connersville", None, "Open since 1954: daily specials and homemade pies.", None, None, [VI_DRIVE]),
  ("The Suds", "Greenwood", None, "Opened as a Dog n Suds in 1957: burgers, shakes and classic cars.", None, None, [VI_DRIVE]),
  ("Steer-In Indianapolis", IND, "5130", "An east-side diner and drive-in with omelets, fried chicken, pizza and pies.", None, None, [VI_DRIVE]),
  ("Tasty Freeze", "Montezuma", None, "Hamburgers and ice cream for about 25 years.", None, None, [VI_DRIVE]),
  ("Ray's Drive-In", "Kokomo", None, "Carhop service only, with the large King Tenderloin.", None, None, [VI_DRIVE]),
  ("Frazier's Dairy Maid", "Anderson", None, "Ice cream treats since 1954.", None, None, [VI_DRIVE]),
  ("Dog n Suds", "Lafayette", None, "Locally owned since 1956: the Coney Dog, the Boilermaker and root beer.", None, None, [VI_DRIVE]),
  ("The Port Drive-In", "Chesterton", None, "Chili dogs, creamy root beer and fried \"mouse ears\", with carhops.", None, None, [VI_DRIVE]),
  ("Bonnie Doon Drive-In", "Mishawaka", None, "Classic drive-in food ordered by intercom, now in its 88th year.", None, None, [VI_DRIVE]),
  ("Carlson's Drive-In", "Michigan City", None, "Homemade root beer, all-beef hot dogs and carhop trays.", None, None, [VI_DRIVE]),
  ("Mr. Weenie", "Peru", None, "A hot dog stand known for its Chicago dog; turn on your lights for carhop service.", None, None, [VI_DRIVE]),
 ],
 "hoosier pie": [   # Visit Indiana's Best Pies IN Indiana (the dining rooms; Wick's Pie's shop is a bakery)
  ("Clifty Inn", "Madison", "1650", "Sugar cream pie, Indiana's state pie, in the inn at Clifty Falls State Park.", None, None, [VI_PIES]),
  ("Old Richmond Inn", "Richmond", "138", "Peanut butter pie in a historic downtown dining room.", None, None, [VI_PIES]),
  ("Fort Harrison State Park Inn", IND, "5830", "Pecan pie at the inn in Fort Harrison State Park.", None, None, [VI_PIES]),
  ("Das Dutchman Essenhaus", "Middlebury", "240", "Berry pie at Indiana's big Amish-country family restaurant.", None, None, [VI_PIES, EC_AMISH]),
  ("Stone Hearth Cafe", "Centerville", "2131", "Cobblers and pies by the hearth.", None, None, [VI_PIES]),
  ("Abe Martin Lodge", "Nashville", "1405", "Mini peanut butter pies at the lodge in Brown County State Park.", None, None, [VI_PIES]),
 ],
 "amish country": [   # Elkhart County and LaGrange County visitors bureaus
  ("Das Dutchman Essenhaus", "Middlebury", "240", "A family-style Amish restaurant, the Elkhart County visitors bureau's first pick.", None, None, [EC_AMISH]),
  ("Village Inn Restaurant", "Middlebury", "107", "A small-town café on Main Street in Middlebury.", None, None, [EC_AMISH]),
  ("Blue Gate Restaurant", "Shipshewana", "195", "Amish home-style meals and a bakery in Shipshewana.", None, None, [EC_AMISH]),
  ("Shipshewana Auction Restaurant", "Shipshewana", "345", "A sit-down restaurant at the auction: chicken and noodles and homemade pies.", None, None, [VS("shipshewana-auction-restaurant")]),
  ("Country Corral Restaurant", "Shipshewana", None, "Comfort food in Shipshewana: meatloaf and pot roast.", None, None, [VS("country-corral-restaurant")]),
 ],
 "oldest": [
  ("Knickerbocker Saloon", "Lafayette", "113", "A saloon on North 5th Street in Lafayette since 1835.", 1835,
   "Tasting Table's oldest bar in every state (February 2025): Indiana's is the Knickerbocker Saloon, operating since 1835.", [TT_OLDBAR]),
  ("Triple XXX Family Restaurant", "West Lafayette", None, "Indiana's first drive-in.", 1929, "Visit Indiana (June 2026): opened in West Lafayette in 1929 as Indiana's first drive-in.", [VI_DRIVE]),
  ("Kunkel's Drive-In", "Connersville", None, "A drive-in with daily specials and homemade pies.", 1954, "Visit Indiana (June 2026): open since 1954.", [VI_DRIVE]),
  ("Dog n Suds", "Lafayette", None, "The Lafayette Dog n Suds.", 1956, "Visit Indiana (June 2026): the Lafayette location, locally owned since 1956.", [VI_DRIVE]),
  ("The Suds", "Greenwood", None, "Opened as a Dog n Suds.", 1957, "Visit Indiana (June 2026): opened as a Dog n Suds in 1957.", [VI_DRIVE]),
  ("Bo-Mac's Drive-In", "Shoals", None, "A carhop drive-in.", 1960, "Visit Indiana (June 2026): run by the Ragsdale family from 1960.", [VI_DRIVE]),
 ],
}
# street addresses for places the map data doesn't show as a place to eat: from the official listing, or our own map listing for it
ADDR = {("Clifty Inn", "Madison"): "1650 Clifty Hollow Rd", ("Das Dutchman Essenhaus", "Middlebury"): "240 US-20", ("Abe Martin Lodge", "Nashville"): "1405 State Road 46 W",
        ("Fort Harrison State Park Inn", IND): "5830 N Post Rd", ("Knickerbocker Saloon", "Lafayette"): "113 N 5th St",
        ("Shipshewana Auction Restaurant", "Shipshewana"): "345 S Van Buren St"}
CUISINE = {("Clifty Inn", "Madison"): "American & Other", ("Das Dutchman Essenhaus", "Middlebury"): "American & Other", ("Abe Martin Lodge", "Nashville"): "American & Other",
           ("Fort Harrison State Park Inn", IND): "American & Other", ("Knickerbocker Saloon", "Lafayette"): "Bar & Pub",
           ("Shipshewana Auction Restaurant", "Shipshewana"): "American & Other"}
KINDS = {k: [k] for k in ("tenderloin", "drive in", "hoosier pie", "amish country", "oldest")}

# MICHELIN: no guide covers Indiana
MICHELIN = []
MI_MATCH = {}
# James Beard (facts with sources): St. Elmo (America's Classics 2012) and Indiana's 2025-26 semifinalists; no Indiana finalist or winner
GL = "Best Chef: Great Lakes"
JBF = [{"name": "St. Elmo Steak House", "city": IND, "address": "127 S Illinois St", "honors": ["America's Classics 2012"], "sources": [JBF12_SE]},
       {"name": "Red Yeti", "city": "Jeffersonville", "honors": [f"{GL} semifinalist 2026 (Michael Bowe)"], "sources": [JBF26]},
       {"name": "Macizo Restaurant", "city": IND, "honors": [f"{GL} semifinalist 2026 (Omar Muñoz and Luz Gonza)"], "sources": [JBF26], "match_names": ["MACIZO"]},
       {"name": "Lone Pine", "city": "Carmel", "honors": [f"{GL} semifinalist 2026 (Aaron Hansen)"], "sources": [JBF26]},
       {"name": "J'adore Pastry", "city": IND, "honors": ["Outstanding Pastry Chef or Baker semifinalist 2026 (Youssef Boudarine)"], "sources": [JBF26], "match_names": ["JADORE"]},
       {"name": "Vida", "city": IND, "honors": ["Outstanding Professional in Beverage Service semifinalist 2026 (Jared May)"], "sources": [JBF26]},
       {"name": "Beholder", "city": IND, "honors": [f"{GL} semifinalist 2025 (Jonathan Brooks)"], "sources": [JBF25]}]
# closed, each with a source (none verified this pass)
CLOSED = []


def key(s):
    """The name key without a leading "the": "Varsity" is our "The Varsity"."""
    return re.sub(r"^the ", "", norm(s))


def find(name, town, num):
    k = key(name)
    hits = [i for i, n in enumerate(C["name"]) if C["city"][i] is not None and M["cities"][C["city"][i]] == town
            and (key(n) == k or key(n).startswith(k + " ") or k.startswith(key(n) + " ") or key(n).replace(" ", "") == k.replace(" ", "")
                 or (key(n).split()[:2] == k.split()[:2] and len(k.split()) >= 2))]
    if num:
        hits = [i for i in hits if (C["addr"][i] or "").split(" ")[0] == num]
    return hits


leads, n_out = [], {}
for kind, rows in GUIDES.items():
    out = []
    for name, town, num, note, founded, fnote, srcs in rows:
        hits = find(name, town, num)
        if not hits and (name, town) in ADDR:
            out.append({"name": name, "address": ADDR[(name, town)], "city": town, "zip": None, "kinds": KINDS[kind], "dishes": [], "note": note,
                        "founded": founded, "founded_note": fnote, "website": None, "open": True, "evidence_date": "2026-10",
                        "sources": srcs, "match_names": []} | ({"cuisine": CUISINE[(name, town)]} if (name, town) in CUISINE else {}))
            continue
        if len(hits) != 1:
            leads.append(f"- {kind}: {name} ({town}{', ' + num if num else ''}) — {len(hits)} matches in our data; not added"); continue
        i = hits[0]
        out.append({"name": C["name"][i], "address": C["addr"][i], "city": town, "zip": str(C["zip"][i]) if C["zip"][i] else None,
                    "kinds": KINDS[kind], "dishes": [], "note": note, "founded": founded, "founded_note": fnote, "website": None, "open": True,
                    "evidence_date": "2026-10", "sources": srcs, "match_names": [name.upper()] if norm(name) != norm(C["name"][i]) else []})
        if brand_of(norm_name(name)):   # a chain shows under its own spelling at every branch, whatever the listing says
            out[-1]["display"] = name
        if (name, town) in CUISINE:
            out[-1]["cuisine"] = CUISINE[(name, town)]
    fn = re.sub(r"[^a-z]+", "_", kind).strip("_")
    json.dump(out, open(f"{R}/app/{fn}.json", "w"), indent=1, ensure_ascii=False)
    n_out[kind] = len(out)

MI_ADDR = {}
json.dump({"restaurants": [{"name": n, "address": MI_ADDR.get(n), "city": t, "zip": None, "distinction": dist, "cuisine": cu, "green_star": False,
                             "michelin_url": MI_UT, "sources": [MI_UT], "match_names": [x.upper() for x in MI_MATCH.get(n, [])], "open": True}
                            for n, t, dist, cu in MICHELIN]}, open(f"{R}/michelin.json", "w"), indent=1, ensure_ascii=False)
json.dump([dict({"address": None}, **j, zip=None, open=True) for j in JBF], open(f"{R}/jbf.json", "w"), indent=1, ensure_ascii=False)
json.dump(CLOSED, open(f"{R}/closed.json", "w"), indent=1, ensure_ascii=False)
open(f"{R}/app/LEADS.md", "w").write("# Indiana research leads (not yet verified)\n\nWritten by pipeline/build_research.py.\n\n" + "\n".join(leads) + """

## Waiting for a source we may use, or for the map data
- Drive-ins: Fry's A&W (Greensburg) isn't in the map data; Johnsen's Blue Top Drive-In (Highland) is listed as \"Johns' Blue Top Drive In\"
  at 8801 Indianapolis Blvd: the name needs checking before it's added.
- Tenderloins: Visit Indiana's tenderloin posts are from 2017 (Dooley O'Toole's, The Willard); the Indiana Foodways Alliance's Tenderloin
  Lovers Trail is a member list (leads only); indystar.com disallows Claude's fetcher; axios.com answers 403.
- Sugar cream pie: Wick's Pie's shop (217 SE Greenville Ave, Winchester) is a bakery; Mrs. Wick's Restaurant needs its own 2025-26 source.
- Coney dogs: Fort Wayne's Famous Coney Island (since 1914 per its own site) needs a 2025-26 source.
- Southern Indiana: fried biscuits and apple butter (Brown County), persimmon pudding, Evansville's brain sandwich: no 2025-26 source yet.
- Oldest: The Log Inn, Haubstadt (Tasting Table, Sept 2025) dates its building to 1825, not its opening; St. Elmo (1902) needs a source
  that ties the year to 127 S Illinois St.
- Honors: Tom Main (Freeland's and Tinker Street, Outstanding Restaurateur semifinalist 2026) is a group honor.
- Official data: Vanderburgh County's weekly media-report PDFs and Porter County's monthly PDFs (no stated terms; wrapped columns need a
  positional parse); Hamilton County's ArcGIS facility layer (no stated terms); the ATC's alcohol permits (reCAPTCHA search): Nick's call.
""")
print(n_out, "| leads:", len(leads))
for l in leads: print(l)
