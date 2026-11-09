"""Indiana county food-inspection reports (PDF) -> data/raw/official/<county>/*.pdf (git-ignored, never public).

Nick's yes, 2026-11-07: script two county health departments' published inspection reports.
  - Vanderburgh County Health Department (vanderburghhealth.org/food-inspection-report/): weekly "media report" PDFs, an "-all" file
    (one row per inspection) and a "-viol"/"-vio" file (one row per violation). robots.txt allows everything but /wp-admin/.
  - Porter County Health Department (in.gov/localhealth/portercounty/food-service-division/food-service-inspections): monthly
    inspection reports (some months with a separate violations file). in.gov's robots.txt has no rules.
The index pages are read for their PDF links; each PDF is downloaded once (a file already on disk is kept). One request at a time with
a 3-second pause, a generic client name, no email address. pipeline/county_reports.py parses them.
Usage: ../.venv/bin/python fetch_county_pdfs.py
"""
import datetime, json, os, re, time, urllib.parse
import requests

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAW = os.path.join(ROOT, "data", "raw", "official")
SOURCES = {
    "vanderburgh": "https://vanderburghhealth.org/food-inspection-report/",
    "porter": "https://www.in.gov/localhealth/portercounty/food-service-division/food-service-inspections",
}
SKIP = re.compile(r"beach|water-sample", re.I)
PAUSE = 3.0
S = requests.Session()
S.headers["User-Agent"] = "EatsRankedData/1.0"


def get(url):
    for attempt in range(4):
        try:
            r = S.get(url, timeout=120)
            if r.status_code == 200:
                return r
            print(f"  HTTP {r.status_code} {url}; retrying", flush=True)
        except requests.RequestException as e:
            print(f"  {type(e).__name__} {url}; retrying", flush=True)
        time.sleep(PAUSE * 5 * (attempt + 1))
    raise RuntimeError(f"failed: {url}")


def main():
    log = {}
    for county, index in SOURCES.items():
        out = os.path.join(RAW, county)
        os.makedirs(out, exist_ok=True)
        page = get(index).text
        time.sleep(PAUSE)
        links = sorted({urllib.parse.urljoin(index, h).replace("http://", "https://", 1)
                        for h in re.findall(r'href="([^"]+\.pdf)"', page, re.I)})
        links = [u for u in links if not SKIP.search(u)]
        got = 0
        for u in links:
            path = os.path.join(out, os.path.basename(urllib.parse.urlparse(u).path))
            if os.path.exists(path) and os.path.getsize(path) > 0:
                continue
            r = get(u)
            if not r.content.startswith(b"%PDF"):
                raise RuntimeError(f"not a PDF: {u}")
            open(path, "wb").write(r.content)
            got += 1
            print(f"{county}: {os.path.basename(path)} ({len(r.content) // 1024} KB)", flush=True)
            time.sleep(PAUSE)
        log[county] = {"index": index, "links": len(links), "new": got}
    json.dump({"fetched": datetime.date.today().isoformat(), "sources": log}, open(os.path.join(RAW, "county_pdfs.json"), "w"), indent=1)
    print("done", log)


if __name__ == "__main__":
    main()
