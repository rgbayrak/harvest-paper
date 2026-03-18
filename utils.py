from pathlib import Path
from typing import Any, Optional
import yaml
import pandas as pd


def generate_queries_yaml(
    keyword_groups: list[list[str]],
    exclude_terms: list[str] | None = None,
    output_path: str | Path = "queries.yaml",
) -> None:
    """Generate a queries.yaml with correct syntax for all 6 API servers.

    Args:
        keyword_groups: List of keyword groups. Each group is a list of
            alternative terms (OR'd together). Groups are AND'd together.
        exclude_terms: Optional list of terms to exclude (NOT'd).
        output_path: Path to write the YAML file.

    Example::

        generate_queries_yaml(
            [
                ["foundation model", "foundation models"],
                ["SOTA", "state of the art"],
                ["pretraining", "pre-training", "pretrained", "pre-trained"],
                ["PPG", "physiological signals", "photoplethysmography"],
            ],
            exclude_terms=["speech recognition", "natural language processing"],
        )
    """
    output_path = Path(output_path)
    exclude_terms = exclude_terms or []

    def _q(term: str) -> str:
        """Wrap in quotes if the term contains spaces, hyphens, etc."""
        return f'"{term}"' if not term.isalnum() else term

    # ── PubMed ──────────────────────────────────────────────────────
    pm_parts = []
    for group in keyword_groups:
        inner = "\n    OR ".join(f"{_q(t)}[All Fields]" for t in group)
        pm_parts.append(f"({inner})")
    pm_body = "\n    AND\n    ".join(pm_parts)
    pm_not = "".join(f"\n    NOT {_q(t)}[All Fields]" for t in exclude_terms)
    pubmed_query = f"  (\n    {pm_body}{pm_not}\n  )\n"

    # ── Europe PMC ──────────────────────────────────────────────────
    epmc_parts = []
    for group in keyword_groups:
        inner = "\n    OR ".join(f"{_q(t)}" for t in group)
        epmc_parts.append(f"(\n    {inner}\n  )")
    epmc_body = "\n  AND\n  ".join(epmc_parts)
    epmc_not = "".join(f"\n  NOT {_q(t)}" for t in exclude_terms)
    epmc_query = f"  {epmc_body}{epmc_not}\n"

    # ── Generic (crossref, semantic_scholar, openalex, core) ────────
    gen_parts = []
    for group in keyword_groups:
        inner = " OR ".join(_q(t) for t in group)
        gen_parts.append(f"({inner})")
    generic_query = f"  {gen_parts[0]}\n"
    for part in gen_parts[1:]:
        generic_query += f"  AND {part}\n"
    if exclude_terms:
        not_inner = " OR ".join(_q(t) for t in exclude_terms)
        generic_query += f"  NOT ({not_inner})\n"

    # ── Write YAML ──────────────────────────────────────────────────
    with output_path.open("w", encoding="utf-8") as f:
        f.write(f"pubmed: |\n{pubmed_query}\n")
        f.write(f"europe_pmc: |\n{epmc_query}\n")
        for api in ("crossref", "semantic_scholar", "openalex", "core"):
            f.write(f"{api}: >\n{generic_query}\n")

    print(f"Wrote queries for 6 APIs to {output_path}")


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


def normalize_record(source: str, title: Optional[str], authors: Optional[str],
                    year: Optional[Any], doi: Optional[str],
                    journal: Optional[str], url: Optional[str],
                    extra: Optional[dict[str, Any]] = None,
                    citation_count: Optional[int] = None) -> dict[str, Any]:
    return {
        "citation_count": citation_count,
        "year": year,
        "title": title,
        "authors": authors,
        "doi": doi.lower().strip() if isinstance(doi, str) and doi.strip() else None,
        "url": url,
        "journal": journal,
        "source": source,
        "extra": extra or {}
    }


def dedupe_records(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["title_norm"] = (
        df["title"]
        .fillna("")
        .str.lower()
        .str.replace(r"[^a-z0-9 ]", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Prefer DOI dedupe first
    with_doi = df[df["doi"].notna()].drop_duplicates(subset=["doi"], keep="first")
    without_doi = df[df["doi"].isna()].drop_duplicates(subset=["title_norm"], keep="first")

    merged = pd.concat([with_doi, without_doi], ignore_index=True)
    merged = merged.drop_duplicates(subset=["title_norm"], keep="first")

    return merged.drop(columns=["title_norm"], errors="ignore")