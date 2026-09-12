#!/usr/bin/env python3
"""Fetch this profile's Google Scholar publications and write data/publications.json.

Uses SerpApi's Google Scholar Author API rather than scraping Scholar directly:
Google blocks datacenter IPs, so a direct scrape works from a laptop but always
fails from GitHub Actions runners.

Needs a SerpApi key (free tier is 250 searches/month; a daily sync uses ~30):
    export SERPAPI_KEY=...
    python scripts/fetch_scholar.py

In CI the key comes from the SERPAPI_KEY repository secret.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

SCHOLAR_ID = "OPXCrBcAAAAJ"
API_URL = "https://serpapi.com/search.json"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "publications.json"


def fetch_profile(api_key: str) -> dict:
    response = requests.get(
        API_URL,
        params={
            "engine": "google_scholar_author",
            "author_id": SCHOLAR_ID,
            "api_key": api_key,
            "num": 100,
            "sort": "pubdate",
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(payload["error"])
    return payload


def total_citations(payload: dict):
    for row in payload.get("cited_by", {}).get("table", []):
        if "citations" in row:
            return row["citations"].get("all")
    return None


def normalize(payload: dict) -> dict:
    publications = []
    for article in payload.get("articles", []):
        year = article.get("year")
        try:
            year = int(year)
        except (TypeError, ValueError):
            year = None

        publications.append({
            "title": article.get("title"),
            "authors": article.get("authors"),
            "venue": article.get("publication") or "",
            "year": year,
            "citations": (article.get("cited_by") or {}).get("value") or 0,
            "link": article.get("link"),
        })

    publications.sort(key=lambda p: (p["year"] is None, -(p["year"] or 0)))

    author = payload.get("author", {})
    return {
        "scholar_id": SCHOLAR_ID,
        "name": author.get("name"),
        "affiliation": author.get("affiliations"),
        "total_citations": total_citations(payload),
        "last_updated": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "publications": publications,
    }


def main():
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        print("[fetch_scholar] SERPAPI_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    try:
        payload = fetch_profile(api_key)
    except Exception as exc:  # noqa: BLE001 - any failure should leave existing data alone
        print(f"[fetch_scholar] Failed to fetch Scholar profile: {exc}", file=sys.stderr)
        sys.exit(1)

    data = normalize(payload)
    if not data["publications"]:
        print("[fetch_scholar] No publications parsed, refusing to overwrite existing data.", file=sys.stderr)
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"[fetch_scholar] Wrote {len(data['publications'])} publications to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
