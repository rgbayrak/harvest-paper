from typing import Any
from screen import get_with_backoff_jitter
from utils import normalize_record


def fetch_openalex(query: str, limit: int) -> list[dict[str, Any]]:
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": limit,
    }
    data = get_with_backoff_jitter(url, params=params)
    items = data.get("results", [])
    results = []

    for item in items:
        authors = ", ".join(
            a.get("author", {}).get("display_name", "")
            for a in item.get("authorships", [])
            if a.get("author", {}).get("display_name")
        ) or None

        doi = item.get("doi")
        if isinstance(doi, str) and doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")

        primary_location = item.get("primary_location") or {}
        source = primary_location.get("source") or {}

        results.append(normalize_record(
            source="openalex",
            title=item.get("title"),
            authors=authors,
            year=item.get("publication_year"),
            doi=doi,
            journal=source.get("display_name"),
            url=item.get("id"),
            extra={"type": item.get("type")},
            citation_count=item.get("cited_by_count")
        ))
    return results