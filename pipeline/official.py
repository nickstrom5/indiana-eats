"""Official records for Indiana -> one table of inspected food businesses (playbook/12-sources.md).

Indiana has no statewide inspection data and no official grade: IDOH supports 95 local health departments (the 92 counties plus Gary,
East Chicago and Fishers), and none found publishes a score, grade or placard. Marion County's portal (hhcwebfood.hhcorp.org), Allen
County's (Cloudflare), Tippecanoe's and Hamilton County's are search-only: linked, never read. With Nick's yes (2026-11-07) two
counties' published reports are read (fetch_county_pdfs.py, county_reports.py): Vanderburgh County's weekly "media report" PDFs and
Porter County's monthly ones, each inspection with its date, purpose and the number of violations the county lists, shown as published
(never a score or grade). Hamilton County's ArcGIS layer of 1,058
permitted facilities states no terms: not used. The ATC's alcohol permits sit behind a reCAPTCHA search: not used, so "Serves alcohol" is
unknown everywhere.

load() returns: jur, lic (our id), name, keys (name keys), addr, city, zip, num, street, lat, lon, kind, active, ltype, insp, biz.
"""
import os, re, json, datetime
import numpy as np, pandas as pd
from common import norm_name, RAW, name_sim, _stems, GENERIC, canon_city

OFF = os.path.join(RAW, "official")
DIRS = {"N": "N", "S": "S", "E": "E", "W": "W", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
TYPES = set("ST STREET AVE AV AVENUE BLVD BOULEVARD RD ROAD DR DRIVE LN LANE CT COURT PL PLACE PKWY PARKWAY TER TRL TRAIL WAY HWY CIR "
            "CIRCLE PLZ SQ MALL BND PASS XING RUN ROW WALK RDG LOOP FWY FREEWAY EXPY EXPRESSWAY PIKE PK PKE".split())


def road(a):
    """One spelling for numbered roads. Indiana writes one road as 'Route 100', 'US 7', 'Rt 2', 'IN 100' or 'IN Route 100', so every
    numbered US or state route is 'SH n' (as in ri-eats); 'N INTERSTATE 95' = 'I-95'; 'COUNTY ROAD 5' = 'CR 5'."""
    a = re.sub(r"(\d)\s*&\s*(\d)", r"\1-\2", a.upper())
    a = re.sub(r"\b(US|IN|SR|SH|CR|I|IH|RT|RTE)-(\w)", r"\1 \2", a)
    a = re.sub(r"\b(?:INTERSTATE(?: HIGHWAY| HWY)?|IH|I H)\s*(?=\d)", "I ", a)
    a = re.sub(r"\b(?:US|U S)\s+(?:HIGHWAY|HWY)\b", "US", a)
    a = re.sub(r"\b(?:FARM[- ]TO[- ]MARKET(?: ROAD| RD)?|FARM (?:ROAD|RD)|F M)\b", "FM", a)
    a = re.sub(r"\b(?:RANCH[- ]TO[- ]MARKET(?: ROAD| RD)?|RANCH (?:ROAD|RD)|RR|RM)\b(?=\s*\d)", "RM", a)
    a = re.sub(r"\b(?:STATE (?:HIGHWAY|HWY|ROAD|RD|ROUTE|RTE)|SR|SH|VERMONT (?:ROUTE|RTE|HIGHWAY|HWY)|IN (?:ROUTE|RTE|RT|HIGHWAY|HWY)|IN|"
               r"US (?:ROUTE|RTE|RT)|US|ROUTE|RTE|RT|HWY)\b\.?(?=\s*\d)", "SH", a)
    a = re.sub(r"\b(?:COUNTY (?:HIGHWAY|HWY|ROAD|RD)|CO RD|CTY (?:HWY|RD)|CR)\b", "CR", a)
    a = re.sub(r"\bHIGHWAY\b", "HWY", a)
    return re.sub(r"\b(US|SH|CR|HWY|FM|RM|I) (\w+)\s*-\s*\w+", r"\1 \2", a)


ORD = {"FIRST": "1ST", "SECOND": "2ND", "THIRD": "3RD", "FOURTH": "4TH", "FIFTH": "5TH", "SIXTH": "6TH", "SEVENTH": "7TH",
       "EIGHTH": "8TH", "NINTH": "9TH", "TENTH": "10TH", "ELEVENTH": "11TH", "TWELFTH": "12TH"}


def street_key(a):
    """'2505 Monroe St' -> ('2505', 'MONROE'); '1000 OSAGE STREET' -> ('1000', 'OSAGE'); 'E Colfax Ave' keeps 'COLFAX'."""
    if not isinstance(a, str):
        return None, None
    a = re.sub(r"[.,#]", " ", road(a))
    # "20940-A North Frederick Ave": a hyphenated unit letter is part of the number (Maryland's Montgomery County wrote them so)
    m = re.match(r"^\s*(\d+)(?:-?[A-Z])?(?:\s*-\s*\d+[A-Z]?)?\s+(.*)$", a)
    if not m:
        return None, None
    words = [w for w in m.group(2).split() if w]
    if len(words) > 1 and words[0] in DIRS:
        words = words[1:]
    core = []
    for w in words:
        if w in TYPES and core:
            break
        core.append(w)
    core = [ORD.get(w, w) for w in core]
    return m.group(1), " ".join(core[:3]) or None


def street_compat(a, b):
    """Same street, or one is a whole-word prefix of the other: Boulder's 2025 set sometimes truncates ("1206 CENTAUR" = Centaur Village Dr)."""
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return False
    return a == b or a.startswith(b + " ") or b.startswith(a + " ")


def street_nums(a):
    """'157-159 W Main St' -> {'157', '159'}; '2505 Monroe St' -> {'2505'}."""
    if not isinstance(a, str):
        return set()
    a = road(a)
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*(\d+)[A-Z]?)?\s", a.upper() + " ")
    if not m:
        return set()
    lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
    if hi < lo:   # "1500-02"
        hi = int(str(lo)[: len(str(lo)) - len(m.group(2))] + m.group(2)) if m.group(2) else lo
    return {str(x) for x in range(lo, hi + 1, 2 if (hi - lo) % 2 == 0 else 1)} if 0 <= hi - lo <= 12 else {str(lo)}


def _names(*vals):
    out = []
    for v in vals:
        if not isinstance(v, str):
            continue
        v = re.sub(r"\s*\((?:MOBILE|MOBILE UNIT|COMMISSARY|CATERING|SPECIAL EVENT|SPEC EVENT|TEMP(?:ORARY)? EVENT|CP|INSIDE [^)]*)\)\s*$", "", v, flags=re.I)
        for part in re.split(r"\s*/\s*|\s+\bdba\b\s+|\s+&\s+(?=[A-Z][a-z])", v, flags=re.I):
            k = norm_name(re.sub(r"\b(?:LLC|INC|CORP|CORPORATION|LTD|CO)\b\.?", "", part, flags=re.I))
            if k and k not in out:
                out.append(k)
    return out


META = {}
LIST_DATE = None
FETCHED = None
# the state's list of local health departments, each with its own inspection page (linked from every place)
MONT_PAGE = "https://www.in.gov/localhealth/"
INSPECTIONS_URL = "https://www.in.gov/localhealth/"
RESULTS = ()
ONPREM_T = ()      # no alcohol permit list (the ATC's permits sit behind a reCAPTCHA search)


def liq_kind(t):
    """A license type as shown -> on-premises or retail."""
    if not isinstance(t, str):
        return None
    return "onprem" if t in ONPREM_T else "retail" if "package" in t else None


COLUMNS = ["jur", "lic", "name", "dba", "holder", "keys", "addr", "city", "zip", "num", "street", "lat", "lon", "kind", "active", "ltype",
           "insp", "issued", "biz", "drinks", "county"]


def _zip(z):
    z = re.sub(r"\D", "", str(z or ""))
    return z[:5] if len(z) >= 5 else ""


def _addr(a):
    """'2790 VETERANS MEMORIAL BLVD STE 130' -> '2790 Veterans Memorial Blvd Ste 130'."""
    a = re.sub(r"\s+", " ", a or "").strip()
    return re.sub(r"\b([A-Z]{2,})\b", lambda m: m.group(1).title(), a)


def _city(c):
    return canon_city(" ".join(w.capitalize() for w in str(c or "").split())) if isinstance(c, str) and c.strip() else None


def _ms(v):
    """An ArcGIS date (epoch milliseconds, UTC) -> YYYY-MM-DD in Louisville's time (the inspector's own day)."""
    if not isinstance(v, (int, float)):
        return None
    d = datetime.datetime.fromtimestamp(v / 1000, datetime.timezone.utc) - datetime.timedelta(hours=5)
    return d.date().isoformat()


COUNTY_FILE = os.path.join(OFF, "county_inspections.json")
COUNTY_JUR = {"Vanderburgh County": "vanderburgh", "Porter County": "porter"}
COUNTY_HD = {"vanderburgh": "Vanderburgh County Health Department", "porter": "Porter County Health Department"}


def violations(n):
    """The county's own count, in words: '0 violations', '1 violation', '3 violations'."""
    return f"{n} violation" + ("" if n == 1 else "s")


def load_counties():
    """One record per facility and address, with each of its inspections: [date, 'N violations', purpose, id], latest first. The
    reports cover schools, stores and clubs too, so these rows only ever attach to a listing they match (kind "inspected")."""
    if not os.path.exists(COUNTY_FILE):
        return []
    by = {}
    for i, r in enumerate(json.load(open(COUNTY_FILE))["rows"]):
        jur = COUNTY_JUR[r["county"]]
        name = re.sub(r"\s+", " ", r["name"]).strip()
        addr = _addr(r["addr"])
        if not name or not addr:
            continue
        k = (jur, name.upper(), addr.upper())
        rec = by.setdefault(k, {"jur": jur, "name": name, "addr": addr, "city": _city(r.get("city")), "zip": _zip(r.get("zip")),
                                "county": r["county"], "insp": []})
        rec["city"] = rec["city"] or _city(r.get("city")); rec["zip"] = rec["zip"] or _zip(r.get("zip"))
        rec["insp"].append([r["date"], violations(r["n"]), r.get("purpose") or "Inspection", f"{jur}-{i}"])
    rows = []
    for n_, ((jur, _, _), r) in enumerate(sorted(by.items())):
        num, st = street_key(r["addr"])
        rows.append({"jur": jur, "lic": f"{jur}-{n_}", "name": r["name"], "dba": r["name"], "holder": None, "keys": _names(r["name"]),
                     "addr": r["addr"], "city": r["city"], "zip": r["zip"], "num": num, "street": st, "lat": None, "lon": None,
                     "kind": "inspected", "active": True, "ltype": COUNTY_HD[jur] + " inspection report", "issued": None, "drinks": None,
                     "county": r["county"], "insp": sorted(r["insp"], key=lambda v: v[0], reverse=True)})
    return rows


def load():
    """Vanderburgh and Porter counties' inspections (see the docstring)."""
    rows = load_counties()
    df = pd.DataFrame(rows) if rows else pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})
    for c_ in COLUMNS:
        if c_ not in df.columns:
            df[c_] = None
    df["lat"] = df["lat"].astype(float); df["lon"] = df["lon"].astype(float); df["active"] = df["active"].astype(bool)
    df["biz"] = np.arange(len(df))
    return df
