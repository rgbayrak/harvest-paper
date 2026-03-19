# Multi-API Literature Query (MALQ) Tool

A tool for running literature searches across **PubMed, Europe PMC, Crossref, Semantic Scholar, OpenAlex, CORE, and arXiv**.

![Python](https://img.shields.io/badge/Python-3.14-blue) ![License](https://img.shields.io/badge/license-MIT-green)
![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen)

![Domain](https://img.shields.io/badge/domain-neuroimaging-blue)
![Status](https://img.shields.io/badge/status-research%20tool-yellow)
![Purpose](https://img.shields.io/badge/purpose-literature%20mining-blueviolet)
![APIs](https://img.shields.io/badge/APIs-PubMed%20%7C%20EPMC%20%7C%20Crossref%20%7C%20OpenAlex%20%7C%20S2%20%7C%20CORE%20%7C%20arXiv-plum)

---

## Table of Contents

- [Setup](#1--setup)
- [API Keys](#2--api-keys)
- [Citation Counts](#3--citation-counts)
- [Query Configuration](#4--query-configuration)
  - [Query Syntax by API](#query-syntax-by-api)
- [Exclusion Terms](#5--exclusion-terms)
- [Deduplication](#6--deduplication)
- [Rate Limiting](#7--rate-limiting)

---

## 1) Setup

```bash
python -m venv .lit-env
source .lit-env/bin/activate   # mac/linux
pip install -r requirements.txt
```

---

## 2) API Keys

Many APIs work without keys but rate limits will be lower.

| API              | Key Required? | Why Get One                   |
| ---------------- | ------------- | ----------------------------- |
| PubMed (NCBI)    | Optional      | Higher rate limits            |
| Europe PMC       | No            | Fully open                    |
| Crossref         | No            | Add polite email header       |
| Semantic Scholar | Recommended   | Better batching + reliability |
| OpenAlex         | No            | Email recommended             |
| CORE             | Yes           | Required                      |
| arXiv            | No            | Fully open                    |

Store keys in a `.env` file (see `config.py` for which variables are loaded):

```env
CORE_API_KEY=xxxx
S2_API_KEY=xxxx
NCBI_API_KEY=xxxx
EMAIL=your_email@lab.edu
```

Key registration links:
- **CORE:** https://core.ac.uk/services/api
- **Semantic Scholar:** https://www.semanticscholar.org/product/api
- **PubMed:** https://www.ncbi.nlm.nih.gov/account/settings/

---

## 3) Citation Counts

The tool extracts citation counts from APIs that provide them:

| API              | Citation Field           | Included? |
| ---------------- | ------------------------ | --------- |
| Semantic Scholar | `citationCount`          | Yes       |
| OpenAlex         | `cited_by_count`         | Yes       |
| Crossref         | `is-referenced-by-count` | Yes       |
| Europe PMC       | `citedByCount`           | Yes       |
| PubMed           | N/A                      | No        |
| CORE             | N/A                      | No        |
| arXiv            | N/A                      | No        |

Results appear in the `citation_count` column of the output CSV.

---

## 4) Query Configuration

All search strings live in `queries.yaml`, with one entry per API. You can write this file manually or generate it with `generate_queries_yaml()`:

```python
generate_queries_yaml(
    [
        ["foundation model", "foundation models"],
        ["fMRI", "EEG", "functional MRI"],
        ["multimodal"],
    ],
    exclude_terms=["image", "survey"],
)
```

This generates API-specific query syntax for all 7 APIs. See `queries-example.yaml` for a full example.

**Search scope:**
- **PubMed** uses `[All Fields]` — searches title, abstract, MeSH terms, keywords, and all other indexed fields.
- **Europe PMC** searches all fields including full text for open access articles.
- **arXiv** uses `all:` prefix — searches title, abstract, comments, and full text.
- **Crossref, Semantic Scholar, OpenAlex, CORE** search broadly by default.

### Query Syntax by API

<details>
<summary>Click to expand syntax details</summary>

#### PubMed (NCBI E-utilities)

Full Boolean logic, field restriction, wildcards, phrase queries.

```text
("fMRI"[All Fields] OR "BOLD"[All Fields])
AND (respiration[All Fields])
NOT "speech recognition"[All Fields]
```

#### Europe PMC

Boolean logic, wildcards, phrase queries. No field prefix = full-text search for open access.

```text
("fMRI" OR "BOLD")
AND (respiration)
NOT "speech recognition"
```

#### Crossref

Limited Boolean support. Best with keyword bags — let relevance ranking handle scoring.

```text
fMRI respiration artifact motion denoising preprocessing
```

#### Semantic Scholar

Keyword queries with limited Boolean support.

```text
fMRI BOLD respiration artifact motion denoising preprocessing
```

#### OpenAlex

Semantic + keyword ranking system. Keep queries short.

```text
fMRI respiration physiological noise artifact
```

#### CORE

Supports Boolean queries but parsing can be inconsistent.

```text
(fMRI OR "functional MRI" OR BOLD)
AND (respiration OR breathing)
```

#### arXiv

Uses `all:` field prefix and `ANDNOT` instead of `NOT`.

```text
(all:"fMRI" OR all:"BOLD")
AND (all:respiration)
ANDNOT all:"speech recognition"
```

</details>

---

## 5) Exclusion Terms

`generate_queries_yaml()` supports an optional `exclude_terms` parameter:

```python
generate_queries_yaml(
    [["foundation model", "foundation models"]],
    exclude_terms=["speech recognition", "natural language processing"],
)
```

This appends exclusion clauses using API-specific syntax:

- **PubMed:** `NOT "term"[All Fields]` per term
- **Europe PMC:** `NOT "term"` per term
- **arXiv:** `ANDNOT all:"term"` per term
- **Generic APIs:** `NOT ("term1" OR "term2")` as a single clause

---

## 6) Deduplication

Results from all APIs are merged and deduplicated in two passes:

1. **DOI match** — exact match on normalized DOI (lowercased, stripped)
2. **Title match** — normalized title comparison (lowercase, alphanumeric only)

Records with DOIs are deduplicated first, then DOI-less records are deduplicated by title. A final pass removes any cross-group title duplicates.

---

## 7) Rate Limiting

All API requests use `get_with_backoff_jitter` which retries failed calls with exponential backoff and random jitter. This prevents IP blocking and complies with API usage policies.
