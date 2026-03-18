from config import CORE_API_KEY
from typing import Any
from screen import get_with_backoff_jitter
from utils import normalize_record

def fetch_core(query: str, limit: int) -> list[dict[str, Any]]:
    if not CORE_API_KEY:
        return []

    url = "https://api.core.ac.uk/v3/search/works"
    headers = {"Authorization": f"Bearer {CORE_API_KEY}"}
    params = {"q": query, "limit": limit}

    data = get_with_backoff_jitter(url, headers=headers, params=params)
    items = data.get("results", [])
    results = []

    for item in items:
        authors_data = item.get("authors", [])
        authors = ", ".join(
            a.get("name", "") if isinstance(a, dict) else str(a)
            for a in authors_data
        ) or None

        doi = item.get("doi")
        year = item.get("yearPublished") or item.get("year")
        journal = None
        if isinstance(item.get("publisher"), dict):
            journal = item["publisher"].get("name")

        results.append(normalize_record(
            source="core",
            title=item.get("title"),
            authors=authors,
            year=year,
            doi=doi,
            journal=journal,
            url=item.get("downloadUrl") or item.get("url"),
            extra={}
        ))
    return results
