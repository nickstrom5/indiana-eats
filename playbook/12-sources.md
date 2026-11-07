# Indiana sources (checked 2026-11-06)

## Official data: none used (Nick's calls)
Indiana has no statewide inspection data and no official grade: IDOH supports 95 local health departments (the 92 counties plus Gary,
East Chicago and Fishers). The app shows no inspection result and links the state's list (in.gov/localhealth) from every place.
- **Vanderburgh County** (vanderburghhealth.org/food-inspection-report/; robots allows it; no stated terms): weekly "media report" PDFs,
  May 3 – Oct 17, 2026, an "-all" file (facility, address, inspection date, number of violations, comments) and a "-viol" file (one row
  per violation, P/Pf/Core, no date). PDFKit text extraction wraps the columns (a name or address can spill onto two lines), so a parse
  needs character positions. Not loaded; about 25 weeks are posted. A "number of violations" isn't a grade and would be shown as such.
- **Porter County** (in.gov/localhealth/portercounty): monthly PDFs, one row per violation (from the prompt; not opened this pass).
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
