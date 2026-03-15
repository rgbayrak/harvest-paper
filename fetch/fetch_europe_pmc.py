from typing import Any
from screen import get_with_backoff_jitter
from normalize import normalize_record

def fetch_europe_pmc(query: str, limit: int) -> list[dict[str, Any]]:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": query,
        "format": "json",
        "pageSize": limit,
        "page": 1,
    }
    data = get_with_backoff_jitter(url, params=params)
    items = data.get("resultList", {}).get("result", [])
    results = []

    for item in items:
        results.append(normalize_record(
            source="europe_pmc",
            title=item.get("title"),
            authors=item.get("authorString"),
            year=item.get("pubYear"),
            doi=item.get("doi"),
            journal=item.get("journalTitle"),
            url=f"https://europepmc.org/article/{item.get('source', '')}/{item.get('id', '')}",
            extra={"id": item.get("id"), "pmid": item.get("pmid"), "pmcid": item.get("pmcid")}
        ))
    return results