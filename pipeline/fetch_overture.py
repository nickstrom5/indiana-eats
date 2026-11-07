"""Download the Overture Maps extracts that indiana.py reads -> data/in/

- overture_in_bbox.parquet     every place in Indiana's bounding box (name, category, address, point)
- overture_in_sources.parquet  which datasets each Indiana eating/drinking listing came from (Meta, Foursquare, ...)
- in_shapes.json               simplified state and county outlines for the map
- in_state_detail.geojson      the state outline at full detail, for the in-state test

Reads the public Overture bucket over S3 with DuckDB (no account needed). Ported from ky-eats/pipeline/fetch_overture.py (2026-11-06).
Indiana: 92 counties from Overture's land division areas (Indianapolis-Marion County is a consolidated government, still one county).
The script checks the towns on the lines with Illinois, Michigan, Ohio and Kentucky (Hammond is in, Calumet City out; Jeffersonville in,
Louisville out; Michigan City in, New Buffalo out).
"""
import os, re, json, time
import duckdb
from shapely import wkb
from shapely.geometry import mapping, Polygon

RELEASE = "2026-10-21.0"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "in")
# Indiana (37.77°N–41.76°N, 84.78°W–88.10°W) plus a margin for the border towns (the Region, the Ohio River towns)
BBOX = "bbox.xmin BETWEEN -88.2 AND -84.7 AND bbox.ymin BETWEEN 37.7 AND 41.8"
EAT = "('restaurant','casual_eatery','bar','fast_food_restaurant','coffee_shop','cafe','smoothie_juice_bar','brewery','food_court')"
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2';")
places = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*.parquet"

t = time.time()
if not os.path.exists(f"{OUT}/overture_in_bbox.parquet"):
    con.execute(f"""
COPY (
  SELECT id, names.primary AS name, basic_category AS cat, taxonomy.primary AS tax, taxonomy.hierarchy AS hier, confidence,
         operating_status AS status, brand.names.primary AS brand, addresses[1].freeform AS street, addresses[1].locality AS city,
         addresses[1].postcode AS zip, addresses[1].region AS region, ST_Y(geometry) AS lat, ST_X(geometry) AS lon, websites[1] AS web,
         phones[1] AS phone
  FROM read_parquet('{places}', hive_partitioning=1) WHERE {BBOX}
) TO '{OUT}/overture_in_bbox.parquet' (FORMAT PARQUET)""")
    print("places in bbox", round(time.time() - t), "s", flush=True)
if not os.path.exists(f"{OUT}/overture_in_sources.parquet"):
    con.execute(f"""
COPY (
  SELECT id, list_transform(sources, lambda x: x.dataset) AS ds, list_transform(sources, lambda x: x.update_time) AS ut,
         list_transform(sources, lambda x: x.record_id) AS rid,
         len(socials) AS n_soc, len(websites) AS n_web, len(phones) AS n_ph
  FROM read_parquet('{places}', hive_partitioning=1)
  WHERE {BBOX} AND basic_category IN {EAT}
) TO '{OUT}/overture_in_sources.parquet' (FORMAT PARQUET)""")
    print("sources", round(time.time() - t), "s", flush=True)

areas = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=divisions/type=division_area/*.parquet"
rows = con.execute(f"""
  SELECT subtype, names.primary AS name, ST_AsWKB(geometry) AS g
  FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region = 'US-IN' AND subtype IN ('region', 'county') AND class = 'land'
    AND bbox.xmin > -88.3 AND bbox.xmax < -84.6 AND bbox.ymin > 37.6 AND bbox.ymax < 41.9""").fetchall()
# Indiana has no independent cities; a merged government's area keeps its county name ("Louisville/Jefferson County Metro" ->
# "Jefferson County")
def _cname(sub, name):
    if sub == "region" or name.endswith(" County"):
        return name
    m = re.search(r"\b([A-Z][a-z]+) County\b", name)
    return m.group(1) + " County" if m else name + " County"
rows = [(sub, _cname(sub, name), g) for sub, name, g in rows]


def rings(geom, tol, min_area):
    geom = geom.simplify(tol, preserve_topology=True)
    polys = [p for p in getattr(geom, "geoms", [geom]) if p.geom_type == "Polygon" and p.area >= min_area]
    return [[[round(x, 3), round(y, 3)] for x, y in p.exterior.coords] for p in polys]


out = {"state": None, "counties": []}
for sub, name, g in rows:
    geom = wkb.loads(bytes(g)).buffer(0)
    if sub == "region":
        json.dump(mapping(geom.simplify(0.0005, preserve_topology=True)), open(f"{OUT}/in_state_detail.geojson", "w"))
        out["state"] = [[r] for r in rings(geom, 0.002, 0.000005)]
    else:
        out["counties"].append({"name": name, "c": rings(geom, 0.004, 0.00002)})
# full-detail county polygons for assigning each place to a county (not shipped)
json.dump({name: mapping(wkb.loads(bytes(g)).buffer(0).simplify(0.0003, preserve_topology=True))
           for sub, name, g in rows if sub == "county"}, open(f"{OUT}/in_counties_detail.geojson", "w"))
json.dump(out, open(f"{OUT}/in_shapes.json", "w"), separators=(",", ":"))
print("outlines: state", len(out["state"] or []), "rings +", len(out["counties"]), "counties;", round(time.time() - t), "s total")
# islands, shores and border towns: each must fall on the right side of the detailed state outline
from shapely.geometry import shape, Point
st = shape(json.load(open(f"{OUT}/in_state_detail.geojson")))
for nm, lon, lat, want in [("Indianapolis", -86.1581, 39.7684, True), ("Hammond", -87.5000, 41.5834, True), ("Calumet City, IL", -87.5295, 41.6156, False),
                           ("Gary", -87.3464, 41.5934, True), ("Michigan City", -86.8950, 41.7075, True), ("New Buffalo, MI", -86.7439, 41.7939, False),
                           ("Elkhart", -85.9767, 41.6820, True), ("Angola", -84.9994, 41.6345, True), ("Fort Wayne", -85.1394, 41.0793, True),
                           ("Richmond, IN", -84.8903, 39.8289, True), ("Lawrenceburg", -84.8497, 39.0909, True), ("Cincinnati, OH", -84.5120, 39.1031, False),
                           ("Jeffersonville", -85.7372, 38.2776, True), ("Louisville, KY", -85.7585, 38.2527, False), ("Evansville", -87.5558, 37.9748, True),
                           ("Henderson, KY", -87.5900, 37.8362, False), ("Vincennes", -87.5286, 38.6773, True), ("Lawrenceville, IL", -87.6814, 38.7292, False),
                           ("Terre Haute", -87.4139, 39.4667, True), ("Danville, IL", -87.6300, 40.1245, False), ("Mount Vernon, IN", -87.8950, 37.9323, True)]:
    ok = st.contains(Point(lon, lat))
    print(f"  {nm}: {'inside' if ok else 'outside'}{'' if ok == want else '  <-- WRONG'}")
print("counties:", len(out["counties"]), sorted(c["name"] for c in out["counties"]))

# the neighbours' land (Indiana, Ohio, West Virginia, Virginia, Tennessee, Missouri, Illinois): listings.py widens Indiana's outline
# ~300 m for river shores, but only where no neighbour's land is, so a Cincinnati or Jeffersonville listing across the Ohio stays out
nb = con.execute(f"""
  SELECT region, ST_AsWKB(geometry) FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region IN ('US-IL', 'US-MI', 'US-OH', 'US-KY') AND subtype = 'region' AND class = 'land'""").fetchall()
from shapely.ops import unary_union
from shapely.geometry import box
near = box(-88.3, 37.6, -84.6, 41.9)
nbg = unary_union([wkb.loads(bytes(g)).buffer(0).intersection(near) for _, g in nb])
json.dump(mapping(nbg.simplify(0.0002, preserve_topology=True)), open(f"{OUT}/in_neighbors.geojson", "w"))
print("neighbours:", sorted(r for r, _ in nb))
