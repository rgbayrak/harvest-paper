from typing import Any, Optional

def normalize_record(source: str, title: Optional[str], authors: Optional[str],
                    year: Optional[Any], doi: Optional[str],
                    journal: Optional[str], url: Optional[str],
                    extra: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return {
        "source": source,
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi.lower().strip() if isinstance(doi, str) and doi.strip() else None,
        "journal": journal,
        "url": url,
        "extra": extra or {}
    }