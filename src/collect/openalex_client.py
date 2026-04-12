"""
OpenAlex client for collecting medical AI/ML publications (2015-2025).

Uses the OpenAlex REST API with cursor-based pagination.
Strategy: title.search for AI/ML terms (ensures AI is central to the paper)
         + concepts.id filter for Medicine (ensures medical context).

Expected yield: ~190,000 publications.
"""

import json
import time
from pathlib import Path
from typing import Iterator

import pandas as pd
import requests

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "openalex"

BASE_URL = "https://api.openalex.org/works"
MAILTO = "your.email@example.com"  # Replace with your email for OpenAlex polite pool

# AI/ML search terms for title (pipe = OR in OpenAlex)
AI_SEARCH_TERMS = (
    "machine learning|deep learning|artificial intelligence|"
    "neural network|natural language processing|computer vision|"
    "random forest|support vector|convolutional|transformer model|"
    "recurrent neural|reinforcement learning|generative adversarial"
)

# Medicine concept (OpenAlex)
MEDICINE_CONCEPT_ID = "C71924100"

# Fields to retrieve
SELECT_FIELDS = [
    "id", "doi", "title", "publication_year", "type",
    "topics", "concepts", "keywords", "authorships",
    "cited_by_count", "open_access", "primary_location",
]


def _build_params(
    year_from: int = 2015,
    year_to: int = 2025,
    per_page: int = 200,
    cursor: str = "*",
) -> dict:
    """Build query parameters for the OpenAlex API."""
    filters = ",".join([
        f"title.search:{AI_SEARCH_TERMS}",
        f"concepts.id:{MEDICINE_CONCEPT_ID}",
        "type:article",
        f"publication_year:{year_from}-{year_to}",
    ])
    params = {
        "filter": filters,
        "select": ",".join(SELECT_FIELDS),
        "per_page": per_page,
        "cursor": cursor,
        "mailto": MAILTO,
    }
    return params


def count_works(year_from: int = 2015, year_to: int = 2025) -> int:
    """Get total count of medical AI publications matching our filter."""
    params = _build_params(year_from, year_to, per_page=1)
    resp = requests.get(BASE_URL, params=params)
    resp.raise_for_status()
    return resp.json()["meta"]["count"]


def count_works_by_year(year_from: int = 2015, year_to: int = 2025) -> dict[int, int]:
    """Get publication counts by year."""
    counts = {}
    for year in range(year_from, year_to + 1):
        counts[year] = count_works(year, year)
    return counts


def fetch_page(
    year_from: int = 2015,
    year_to: int = 2025,
    per_page: int = 200,
    cursor: str = "*",
    max_retries: int = 10,
) -> tuple[list[dict], str | None]:
    """Fetch a single page of results with retry logic. Returns (works, next_cursor)."""
    params = _build_params(year_from, year_to, per_page, cursor)
    for attempt in range(max_retries):
        try:
            resp = requests.get(BASE_URL, params=params, timeout=30)
            if resp.status_code == 429:
                wait = min(60 * (attempt + 1), 300)
                print(f"  Rate limited (429), waiting {wait}s (attempt {attempt + 1}/{max_retries})", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            next_cursor = data["meta"].get("next_cursor")
            return data["results"], next_cursor
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            wait = min(10 * (attempt + 1), 120)
            if attempt < max_retries - 1:
                print(f"  Retry {attempt + 1}/{max_retries} after {wait}s ({e.__class__.__name__})", flush=True)
                time.sleep(wait)
            else:
                raise
    raise requests.exceptions.HTTPError("Max retries exceeded after repeated 429 responses")


def iter_all_works(
    year_from: int = 2015,
    year_to: int = 2025,
    per_page: int = 200,
    max_pages: int | None = None,
) -> Iterator[dict]:
    """Iterate over all matching works using cursor pagination."""
    cursor = "*"
    page = 0
    while cursor:
        works, cursor = fetch_page(year_from, year_to, per_page, cursor)
        for w in works:
            yield w
        page += 1
        if max_pages and page >= max_pages:
            break
        time.sleep(0.25)  # Respect rate limits


def fetch_sample(n: int = 100, year_from: int = 2015, year_to: int = 2025) -> pd.DataFrame:
    """Fetch a small sample of works and return as DataFrame."""
    works, _ = fetch_page(year_from, year_to, per_page=min(n, 200))
    return works_to_dataframe(works[:n])


def works_to_dataframe(works: list[dict]) -> pd.DataFrame:
    """Convert raw OpenAlex work records to a flat DataFrame."""
    rows = []
    for w in works:
        # Extract first author country
        first_author_country = None
        if w.get("authorships"):
            for inst in w["authorships"][0].get("institutions", []):
                if inst.get("country_code"):
                    first_author_country = inst["country_code"]
                    break

        # Extract all author countries
        author_countries = set()
        for auth in w.get("authorships", []):
            for inst in auth.get("institutions", []):
                if inst.get("country_code"):
                    author_countries.add(inst["country_code"])

        # Extract topic names
        topic_names = [t.get("display_name", "") for t in w.get("topics", [])]

        # Extract concept names and IDs
        concepts = [
            {"id": c.get("id", ""), "name": c.get("display_name", ""), "score": c.get("score", 0)}
            for c in w.get("concepts", [])
        ]

        # Journal name
        journal = None
        if w.get("primary_location") and w["primary_location"].get("source"):
            journal = w["primary_location"]["source"].get("display_name")

        rows.append({
            "openalex_id": w.get("id", ""),
            "doi": w.get("doi", ""),
            "title": w.get("title", ""),
            "year": w.get("publication_year"),
            "journal": journal,
            "cited_by_count": w.get("cited_by_count", 0),
            "is_oa": w.get("open_access", {}).get("is_oa", False),
            "first_author_country": first_author_country,
            "author_countries": "|".join(sorted(author_countries)),
            "n_authors": len(w.get("authorships", [])),
            "topics": "|".join(topic_names),
            "concepts_json": json.dumps(concepts),
        })
    return pd.DataFrame(rows)


def collect_year_to_parquet(year: int) -> Path:
    """Collect all works for a single year and save to parquet."""
    output_path = DATA_DIR / f"medical_ai_works_{year}.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        existing = pd.read_parquet(output_path)
        print(f"  {year}: already collected ({len(existing):,} works), skipping")
        return output_path

    all_rows = []
    buffer = []
    total = 0

    for work in iter_all_works(year, year):
        buffer.append(work)
        total += 1
        if len(buffer) >= 5000:
            all_rows.append(works_to_dataframe(buffer))
            buffer = []
            print(f"  {year}: {total:,} works...", flush=True)

    if buffer:
        all_rows.append(works_to_dataframe(buffer))

    if all_rows:
        df = pd.concat(all_rows, ignore_index=True)
    else:
        df = pd.DataFrame()

    df.to_parquet(output_path, index=False)
    print(f"  {year}: saved {len(df):,} works")
    return output_path


def collect_all_to_parquet(
    year_from: int = 2015,
    year_to: int = 2025,
) -> Path:
    """Collect all works year-by-year (resumable). Merges into single parquet."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for year in range(year_from, year_to + 1):
        collect_year_to_parquet(year)

    # Merge all year files into one
    parts = []
    for year in range(year_from, year_to + 1):
        p = DATA_DIR / f"medical_ai_works_{year}.parquet"
        if p.exists():
            parts.append(pd.read_parquet(p))

    merged = pd.concat(parts, ignore_index=True)
    output_path = DATA_DIR / f"medical_ai_works_{year_from}_{year_to}.parquet"
    merged.to_parquet(output_path, index=False)
    print(f"\nMerged: {len(merged):,} total works → {output_path}")
    return output_path


if __name__ == "__main__":
    print("Counting medical AI publications (2015-2025)...")
    n = count_works()
    print(f"Total works: {n:,}")

    print("\nYear-by-year counts:")
    for year, count in count_works_by_year().items():
        print(f"  {year}: {count:,}")

    print("\nFetching 100-paper sample...")
    df = fetch_sample(100)
    print(f"Retrieved {len(df)} papers")
    print(f"\nYear distribution:\n{df['year'].value_counts().sort_index()}")
    print(f"\nTop 5 journals:\n{df['journal'].value_counts().head()}")
    print(f"\nSample titles:")
    for t in df["title"].head(10):
        print(f"  - {t}")
