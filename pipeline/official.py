"""Official records for Indiana -> one table of licensed food businesses (playbook/12-sources.md). Empty for now.

Indiana has no statewide inspection data and no official grade: IDOH supports 95 local health departments (the 92 counties plus Gary,
East Chicago and Fishers), and none found publishes a score, grade or placard. Marion County's portal (hhcwebfood.hhcorp.org), Allen
County's (Cloudflare), Tippecanoe's and Hamilton County's are search-only: linked, never read. Vanderburgh County posts weekly "media
report" PDFs (name, address, date, number of violations) and Porter County monthly PDFs (one row per violation); neither states terms,
and their wrapped columns need a positional parse: not loaded in this pass (a lead for Nick). Hamilton County's ArcGIS layer of 1,058
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


def load():
    """No official list a script may read in Indiana yet (see the docstring): an empty table of the right shape."""
    df = pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})
    df["lat"] = df["lat"].astype(float); df["lon"] = df["lon"].astype(float); df["active"] = df["active"].astype(bool)
    df["biz"] = np.arange(len(df))
    return df
