# Indiana sources (checked 2026-11-06)

## Official data used (Nick's yes, 2026-11-07)
Indiana has no statewide inspection data and no official grade: IDOH supports 95 local health departments (the 92 counties plus Gary,
East Chicago and Fishers). Every place links the state's list (in.gov/localhealth); two counties' published reports are read:
- **Vanderburgh County** (vanderburghhealth.org/food-inspection-report/; robots.txt allows all but /wp-admin/; no stated terms): 24 weekly
  "media report" PDFs, May 3 – Oct 17, 2026. The "-all" files (Facility Type = 'Restaurant': facility, address, inspection date, number
  of violations, comments) are read with pdfplumber's table extraction (`pipeline/fetch_county_pdfs.py`, `pipeline/county_reports.py`);
  the "-viol" files aren't needed. 412 inspections.
- **Porter County** (in.gov/localhealth/portercounty/food-service-division/food-service-inspections; in.gov's robots.txt has no rules):
  monthly PDFs, Aug 2025 – Sep 2026, in three layouts (2026 combined reports with "Number of Citations" on each inspection's first row,
  2025/early-2026 inspection lists with "Number of Violations", August 2025 as text lines). October 2025's inspection list has no text
  layer (unreadable without OCR) and is left out; temporary-event inspections are dropped. 1,277 inspections.
- Shown as published: each inspection's date and the county's own count ("2 violations"), never a score or grade; the rows include
  schools and stores, so they only attach to listings they match (official.py `load_counties`, kind "inspected"). One request at a
  time, 3 seconds apart, a generic client name (EatsRankedData/1.0), no email.
- **Hamilton County** ArcGIS layer of 1,058 permitted food facilities (gis1.hamiltoncounty.in.gov): no stated terms; not used.
- **Search-only, never scraped:** Marion County (hhcwebfood.hhcorp.org), Allen County (Cloudflare), Tippecanoe; Fishers and Elkhart
  answer scripts with 403 (prompt).
- **Alcohol:** the ATC's permits sit in PLA's eVerification facility search behind a reCAPTCHA: not used, so "Serves alcohol" is unknown.

## Research sources (robots-checked with pipeline/check_sources.py)
visitindiana.in.gov (drive-ins post 2026-06-25; Best Pies IN Indiana), visitelkhartcounty.com (Amish-style dining), visitshipshewana.org
(listings), tastingtable.com (tenderloin 2026-06-05; oldest bar 2025-02-17), jamesbeard.org (St. Elmo America's Classics 2012; 2025-26
semifinalists). Blocked or unusable: indystar.com (robots), axios.com (403). Visit Indiana's tenderloin posts are 2017 (leads only); the
Indiana Foodways Alliance trails are member lists (leads only). Leads: data/research/app/LEADS.md.

## Map data and calibration
- Overture 2026-10-21.0: 27,543 eating/drinking listings with an Indiana address; 92 counties; border checks pass (Hammond, Michigan
  City, Jeffersonville, Evansville in; Calumet City, New Buffalo, Louisville, Henderson, Cincinnati out). No Google 2021 data read at all.
- App: 13,985 places, 13,476 restaurants (BLS QCEW 2025: 13,486 private NAICS 722 establishments). Keep rule: the family's (Meta 0.95,
  or 0.90 with a website, or a brand feed); nothing official to calibrate against.
