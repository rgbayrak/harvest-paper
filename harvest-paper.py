import time
from typing import Optional, Any
import yaml
from pathlib import Path
import pandas as pd

from fetch import *
from merge_and_dedupe import dedupe_records


MAX_RESULTS_PER_SOURCE = 100
REQUEST_TIMEOUT = 30
SLEEP_SECONDS = 0.5


def load_queries_from_yaml(path: str | Path) -> dict[str, str]:
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping in {path}, got {type(data).__name__}")

    queries: dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError(f"Query key must be a string, got {type(key).__name__}")
        if not isinstance(value, str):
            raise ValueError(f"Query for '{key}' must be a string, got {type(value).__name__}")

        queries[key] = value.strip()

    return queries


API_REGISTRY = {
    "pubmed": fetch_pubmed,
    "europe_pmc": fetch_europe_pmc,
    "crossref": fetch_crossref,
    "semantic_scholar": fetch_semantic_scholar,
    "openalex": fetch_openalex,
    "core": fetch_core,
}


def harvest_all(queries: dict[str, str], limit_per_source: int) -> pd.DataFrame:
    all_records = []

    for name, fetcher in API_REGISTRY.items():
        query = queries.get(name)
        if query is None:
            print(f"Skipping {name} (no query defined)")
            continue
        try:
            print(f"Fetching from {name} ...")
            records = fetcher(query, limit_per_source)
            print(f"  got {len(records)} records")
            all_records.extend(records)
        except Exception as e:
            print(f"  failed: {e}")
        time.sleep(SLEEP_SECONDS)

    df = pd.DataFrame(all_records)
    if df.empty:
        return df

    return dedupe_records(df)

# TODO: compute recall diagnostics per API


if __name__ == "__main__":
    queries = load_queries_from_yaml("queries.yaml")
    df = harvest_all(queries, MAX_RESULTS_PER_SOURCE)
    # TODO: df.to_json("results/literature_results_merged.json", orient='table', index=False)
    df.to_csv("results/literature_results_merged.csv", index=False)
    print(f"Saved {len(df)} deduplicated records to literature_results.ext")
    print(df[["source", "year", "title", "doi", "url"]].head(20).to_string(index=False))