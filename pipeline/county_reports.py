"""Parse the county inspection PDFs (fetch_county_pdfs.py) -> data/raw/official/county_inspections.json (git-ignored, never public).

One row per inspection, as each county publishes it: the facility's name and address, the inspection date, the purpose where the county
gives one, and the number of violations the county lists for that inspection. Nothing is scored or graded here.
  - Vanderburgh: the weekly "-all" media reports (Facility Type = 'Restaurant'): Facility Name, Address, Inspection Date, Number of
    Violations, Comments. The "-viol" files repeat the same inspections one violation per row and aren't needed.
  - Porter: three layouts. 2026 monthly "Inspection Report"s list one row per citation with "Number of Citations" on each inspection's
    first row (0 for a clean one); the 2025 and early-2026 "Inspections" files list one row per inspection with "Number of Violations"
    (the matching "Violations" files aren't needed); August 2025's has text but no table (parsed by line). October 2025's has no text
    layer at all (unreadable without OCR), so that month is left out. Temporary-event inspections are dropped (event booths, not
    restaurants).
Usage: ../.venv/bin/python county_reports.py
"""
import datetime, glob, json, os, re
import pdfplumber

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAW = os.path.join(ROOT, "data", "raw", "official")
OUT = os.path.join(RAW, "county_inspections.json")
MON = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def clean(v):
    return re.sub(r"\s+", " ", (v or "").replace("\n", " ")).strip()


def iso(v):
    v = clean(v)
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})$", v)
    if m:
        y = int(m.group(3)); y = y + 2000 if y < 100 else y
        return f"{y}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    m = re.match(r"^(\d{1,2})-([A-Za-z]{3})-(\d{2})$", v)
    if m:
        return f"{2000 + int(m.group(3))}-{MON[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    try:
        return datetime.datetime.strptime(v, "%B %d, %Y").date().isoformat()
    except ValueError:
        return None


def tables(path):
    rows = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            for t in p.extract_tables():
                rows += [[c for c in r] for r in t if r]
    return rows


def vanderburgh():
    out = []
    for f in sorted(glob.glob(os.path.join(RAW, "vanderburgh", "*-all.pdf"))):
        for r in tables(f):
            if len(r) < 4 or clean(r[0]).startswith(("(Facility)", "Media Report")):
                continue
            d, n = iso(r[2]), clean(r[3])
            if not d or not re.fullmatch(r"\d+", n):
                continue
            out.append({"county": "Vanderburgh County", "name": clean(r[0]), "addr": clean(r[1]), "city": None, "zip": None, "date": d,
                        "purpose": None, "n": int(n), "file": os.path.basename(f)})
    return out


def porter():
    out, skipped = [], []
    for f in sorted(glob.glob(os.path.join(RAW, "porter", "*.pdf"))):
        b = os.path.basename(f)
        if re.search(r"(?i)violation", b):
            continue                      # per-violation lists: the inspections files carry the counts
        rows = tables(f)
        hdr = next((r for r in rows if any(clean(c).startswith("Facility Name") for c in r)), None)
        if hdr and clean(hdr[0]).startswith("Number of"):          # 2026 combined: citations on the inspection's first row
            for r in rows:
                if len(r) < 6 or not re.fullmatch(r"\d+", clean(r[0])):
                    continue
                d = iso(r[4])
                if d:
                    out.append({"county": "Porter County", "name": clean(r[1]), "addr": clean(r[2]), "city": clean(r[3]) or None, "zip": None,
                                "date": d, "purpose": clean(r[5]) or None, "n": int(clean(r[0])), "file": b})
        elif hdr:                                                  # split months: one row per inspection
            h = [clean(c).lower() for c in hdr]
            ix = {k: next((i for i, c in enumerate(h) if c.startswith(k)), None) for k in ("facility", "address", "city", "zip", "inspection date", "purpose", "number")}
            for r in rows:
                if r is hdr or len(r) < len(h):
                    continue
                n = clean(r[ix["number"]]) if ix["number"] is not None else ""
                d = iso(r[ix["inspection date"]]) if ix["inspection date"] is not None else None
                if not d or not re.fullmatch(r"\d+", n):
                    continue
                out.append({"county": "Porter County", "name": clean(r[ix["facility"]]), "addr": clean(r[ix["address"]]),
                            "city": clean(r[ix["city"]]) if ix["city"] is not None else None,
                            "zip": clean(r[ix["zip"]])[:5] if ix["zip"] is not None else None, "date": d,
                            "purpose": clean(r[ix["purpose"]]) if ix["purpose"] is not None else None, "n": int(n), "file": b})
        else:                                                      # August 2025: text lines, "name address 22-Aug-25 Purpose N inspector"
            with pdfplumber.open(f) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)
            got = 0
            for line in text.splitlines():
                m = re.match(r"^(.*?)\s+(\d{1,2}-[A-Za-z]{3}-\d{2})\s+(Routine|Follow-up|Complaint|Pre-Opening|Temporary|Other)\s+(\d+)\s", line)
                if not m:
                    continue
                head = m.group(1)
                a = re.search(r"\s(\d+[A-Z]?\s.*|PO Box.*)$", head)
                name, addr = (head[:a.start()].strip(), a.group(1).strip()) if a else (head, "")
                out.append({"county": "Porter County", "name": name, "addr": addr, "city": None, "zip": None, "date": iso(m.group(2)),
                            "purpose": m.group(3), "n": int(m.group(4)), "file": b})
                got += 1
            if not got:
                skipped.append(b)
    return [r for r in out if (r["purpose"] or "") != "Temporary"], skipped


def main():
    v = vanderburgh()
    p, skipped = porter()
    rows = v + p
    seen, uniq = set(), []
    for r in rows:      # the same inspection can sit in two weekly files
        k = (r["county"], r["name"].upper(), r["addr"].upper(), r["date"])
        if k not in seen:
            seen.add(k); uniq.append(r)
    json.dump({"parsed": datetime.date.today().isoformat(), "unreadable": skipped, "rows": uniq}, open(OUT, "w"), indent=0)
    by = {}
    for r in uniq:
        by.setdefault(r["county"], []).append(r["date"])
    print({c: (len(ds), min(ds), max(ds)) for c, ds in by.items()}, "| unreadable:", skipped)


if __name__ == "__main__":
    main()
