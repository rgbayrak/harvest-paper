import time
import pandas as pd
from fetch import *
from utils import dedupe_records, generate_queries_yaml, load_queries_from_yaml


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

MAX_RESULTS_PER_SOURCE = 100
SLEEP_SECONDS = 0.5

API_REGISTRY = {
    "europe_pmc": fetch_europe_pmc,
    "crossref": fetch_crossref,
    "semantic_scholar": fetch_semantic_scholar,
    "openalex": fetch_openalex,
    "core": fetch_core,
    "pubmed": fetch_pubmed,
    "arxiv": fetch_arxiv,
}

if __name__ == "__main__":
    generate_queries_yaml(
        [
            ["pretraining", "pre-training", "pretrained", "pre-trained"],
            ["foundation"],
            ["time series", "timeseries", "time-series"],
        ],
        exclude_terms=["survey"],
    )
    
    queries = load_queries_from_yaml("queries.yaml")
    df = harvest_all(queries, MAX_RESULTS_PER_SOURCE)
    # TODO: df.to_json("results/literature_results.json", orient='table', index=False)
    df.to_csv("results/literature_review_results.csv", index=False)
    print(f"Saved {len(df)} deduplicated records to literature_review_results.csv")
    # print(df[["year", "title", "url"]].head(20).to_string(index=False))