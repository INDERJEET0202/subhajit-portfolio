#!/usr/bin/env python3
"""Fetch this profile's Google Scholar publications and write data/publications.json.

Run manually:
    pip install -r scripts/requirements.txt
    python scripts/fetch_scholar.py

Run automatically by .github/workflows/update-publications.yml on a daily schedule.
Designed to fail soft: if Google Scholar rate-limits or blocks the request, the
existing data/publications.json is left untouched and the script exits non-zero
so the workflow can just retry on the next scheduled run.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHOLAR_ID = "OPXCrBcAAAAJ"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "publications.json"


def fetch_profile():
    from scholarly import scholarly

    search_query = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(search_query, sections=["basics", "indices", "publications"])
    return author


def normalize(author) -> dict:
    from scholarly import scholarly

    publications = []
    for pub in author.get("publications", []):
        # The author-level listing only has title/year/citation string;
        # fetching each publication's own page gets authors + a real link.
        try:
            pub = scholarly.fill(pub)
        except Exception as exc:  # noqa: BLE001 - keep the partial record rather than dropping the paper
            print(f"[fetch_scholar] Could not fully fetch '{pub.get('bib', {}).get('title')}': {exc}", file=sys.stderr)

        bib = pub.get("bib", {})
        pub_url = pub.get("pub_url")
        year = bib.get("pub_year")
        try:
            year = int(year)
        except (TypeError, ValueError):
            year = None

        venue_parts = [bib.get("journal"), bib.get("volume"), bib.get("number")]
        venue = ", ".join(p for p in venue_parts if p) or bib.get("citation") or ""

        publications.append({
            "title": bib.get("title"),
            "authors": bib.get("author"),
            "venue": venue,
            "year": year,
            "citations": pub.get("num_citations", 0),
            "link": pub_url if isinstance(pub_url, str) and pub_url.startswith("http") else None,
        })

    # Newest / most-cited first, unknown years last
    publications.sort(key=lambda p: (p["year"] is None, -(p["year"] or 0)))

    return {
        "scholar_id": SCHOLAR_ID,
        "name": author.get("name"),
        "affiliation": author.get("affiliation"),
        "total_citations": author.get("citedby"),
        "h_index": author.get("hindex"),
        "last_updated": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "publications": publications,
    }


def main():
    try:
        author = fetch_profile()
    except Exception as exc:  # noqa: BLE001 - fail soft, keep existing data on any scraper error
        print(f"[fetch_scholar] Failed to fetch Scholar profile: {exc}", file=sys.stderr)
        sys.exit(1)

    data = normalize(author)
    if not data["publications"]:
        print("[fetch_scholar] No publications parsed, refusing to overwrite existing data.", file=sys.stderr)
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"[fetch_scholar] Wrote {len(data['publications'])} publications to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
