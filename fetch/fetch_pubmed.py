from config import NCBI_API_KEY, USER_EMAIL
from typing import Any
from screen import get_with_backoff_jitter
from normalize import normalize_record

def fetch_pubmed(query: str, limit: int) -> list[dict[str, Any]]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": limit,
        "email": USER_EMAIL,
        "tool": "lit_review_harvester",
    }
    if NCBI_API_KEY:
        search_params["api_key"] = NCBI_API_KEY

    search_data = get_with_backoff_jitter(base + "esearch.fcgi", params=search_params)
    ids = search_data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    summary_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json",
        "email": USER_EMAIL,
        "tool": "lit_review_harvester",
    }
    if NCBI_API_KEY:
        summary_params["api_key"] = NCBI_API_KEY

    summary_data = get_with_backoff_jitter(base + "esummary.fcgi", params=summary_params)
    results = []
    result_block = summary_data.get("result", {})

    for pmid in ids:
        item = result_block.get(pmid, {})
        authors = ", ".join(a.get("name", "") for a in item.get("authors", []))
        article_ids = item.get("articleids", [])
        doi = None
        for aid in article_ids:
            if aid.get("idtype") == "doi":
                doi = aid.get("value")
                break

        results.append(normalize_record(
            source="pubmed",
            title=item.get("title"),
            authors=authors or None,
            year=item.get("pubdate"),
            doi=doi,
            journal=item.get("fulljournalname"),
            url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            extra={"pmid": pmid}
        ))
    return results