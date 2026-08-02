"""
fetch_jobs.py (v2 - multi-role)
Fetches postings for MULTIPLE roles in India from the Adzuna Job Search API
and saves them all to one CSV, with a "role" column to tell them apart.

Setup:
1. Get a free API key: https://developer.adzuna.com/
2. Set ADZUNA_APP_ID and ADZUNA_APP_KEY as environment variables.
3. Run: python fetch_jobs.py

Output: jobs_raw.csv (one row per job posting, across all roles)
"""

import os
import time
import csv
import urllib.request
import urllib.parse
import json

# ---- Config ----
APP_ID = os.environ.get("ADZUNA_APP_ID", "PASTE_YOUR_APP_ID_HERE")
APP_KEY = os.environ.get("ADZUNA_APP_KEY", "PASTE_YOUR_APP_KEY_HERE")
COUNTRY = "in"                 # India
ROLES = ["data analyst", "business analyst", "data scientist"]
RESULTS_PER_PAGE = 50
MAX_PAGES = 6                  # per role - up to 300 postings each, ~900 total
OUTPUT_FILE = "jobs_raw.csv"


def fetch_page(query: str, page: int) -> dict:
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": query,
        "content-type": "application/json",
    }
    url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{page}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=20) as resp:
        return json.loads(resp.read().decode())


def main():
    if "PASTE_YOUR" in APP_ID or "PASTE_YOUR" in APP_KEY:
        print("Set ADZUNA_APP_ID and ADZUNA_APP_KEY (env vars) before running.")
        return

    rows = []
    seen_urls = set()  # avoid double-counting a job that shows up under 2 role searches

    for role in ROLES:
        print(f"\n=== Fetching role: {role} ===")
        for page in range(1, MAX_PAGES + 1):
            print(f"Fetching page {page}...")
            data = fetch_page(role, page)
            results = data.get("results", [])
            if not results:
                break
            for job in results:
                url = job.get("redirect_url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                rows.append({
                    "role": role,
                    "title": job.get("title", "").strip(),
                    "company": (job.get("company") or {}).get("display_name", ""),
                    "city": (job.get("location") or {}).get("display_name", ""),
                    "salary_min": job.get("salary_min", ""),
                    "salary_max": job.get("salary_max", ""),
                    "created": job.get("created", ""),
                    "description": job.get("description", "").replace("\n", " ").strip(),
                    "redirect_url": url,
                })
            time.sleep(1)  # be polite to the API

    if not rows:
        print("No results fetched.")
        return

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} postings across {len(ROLES)} roles to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
