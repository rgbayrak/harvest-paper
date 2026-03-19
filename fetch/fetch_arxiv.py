import requests
import random
import time
import xml.etree.ElementTree as ET
from typing import Any
from utils import normalize_record

ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


def fetch_arxiv(query: str, limit: int) -> list[dict[str, Any]]:
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "start": 0,
        "max_results": limit,
    }

    # arXiv returns Atom XML, so we handle retries inline
    for attempt in range(5):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            break
        except Exception as e:
            wait = random.uniform(0, 1 * (2 ** attempt))
            print(f"  Retrying in {wait:.2f}s due to {e}")
            time.sleep(wait)
    else:
        raise RuntimeError("arXiv: failed after retries")

    root = ET.fromstring(r.text)
    results = []

    for entry in root.findall("atom:entry", ARXIV_NS):
        title = entry.findtext("atom:title", namespaces=ARXIV_NS)
        if title:
            title = " ".join(title.split())

        authors = ", ".join(
            a.findtext("atom:name", namespaces=ARXIV_NS) or ""
            for a in entry.findall("atom:author", ARXIV_NS)
        ) or None

        published = entry.findtext("atom:published", namespaces=ARXIV_NS)
        year = int(published[:4]) if published else None

        doi = entry.findtext("{http://arxiv.org/schemas/atom}doi")

        link = entry.findtext("atom:id", namespaces=ARXIV_NS)

        results.append(normalize_record(
            source="arxiv",
            title=title,
            authors=authors,
            year=year,
            doi=doi,
            journal="arXiv",
            url=link,
        ))

    return results
