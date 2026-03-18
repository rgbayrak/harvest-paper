from typing import Any
from screen import get_with_backoff_jitter
from utils import normalize_record

def fetch_crossref(query: str, limit: int) -> list[dict[str, Any]]:
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": limit,
        "select": "DOI,title,author,published-print,published-online,created,container-title,URL,abstract,is-referenced-by-count"
    }
    data = get_with_backoff_jitter(url, params=params)
    items = data.get("message", {}).get("items", [])
    results = []

    for item in items:
        authors = ", ".join(
            " ".join(filter(None, [a.get("given"), a.get("family")]))
            for a in item.get("author", [])
        ) or None

        year = None
        for key in ("published-print", "published-online", "created"):
            dp = item.get(key, {}).get("date-parts", [])
            if dp and dp[0]:
                year = dp[0][0]
                break

        title = item.get("title", [None])
        journal = item.get("container-title", [None])

        results.append(normalize_record(
            source="crossref",
            title=title[0] if title else None,
            authors=authors,
            year=year,
            doi=item.get("DOI"),
            journal=journal[0] if journal else None,
            url=item.get("URL"),
            extra={},
            citation_count=item.get("is-referenced-by-count")
        ))
    return results
