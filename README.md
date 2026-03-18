# Multi-API Literature Query (MALQ) Tool

A practical tool for running a literature search tool across **PubMed, Europe PMC, Crossref, Semantic Scholar, OpenAlex, and CORE**.

![Python](https://img.shields.io/badge/Python-3.14-blue) ![License](https://img.shields.io/badge/license-MIT-green) 
![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen)

![Domain](https://img.shields.io/badge/domain-neuroimaging-blue)
![Status](https://img.shields.io/badge/status-research%20tool-yellow)
![Purpose](https://img.shields.io/badge/purpose-literature%20mining-blueviolet)
![APIs](https://img.shields.io/badge/APIs-PubMed%20%7C%20EPMC%20%7C%20Crossref%20%7C%20OpenAlex%20%7C%20S2%20%7C%20CORE-plum)

---

## 📚 Table of Contents

- [Create a Clean Python Environment](#1--create-a-clean-python-environment)
- [API Keys — When You Need Them](#2--api-keys--when-you-need-them)
  - [How to Get Keys](#how-to-get-keys)
- [Store Keys Properly (.env)](#3--store-keys-properly-env)
- [Citation Counts](#4--citation-counts)
- [How to Form Good Queries](#5--how-to-form-good-queries)
  - [Query Design (API-Server Specific)](#-query-design-api-server-specific)
  - [Query Configuration File](#-query-configuration-file)
  - [API Query Syntax Differences](#-api-query-syntax-differences)
- [Exclusion Terms](#6--exclusion-terms)
- [Deduplication Strategy](#7--deduplication-strategy)
- [Rate Limiting Best Practice](#-rate-limiting-best-practice)
- [Pro Tips (Real-World Literature Mining Pipelines)](#-pro-tips-real-literature-mining-pipelines)

---

## 1) 📦 Create a Clean Python Environment

Always isolate dependencies.

```bash
mkdir lit_search
cd lit_search

python -m venv .lit-env
```

Activate:

```bash
# mac/linux
source .lit-env/bin/activate

# windows
.lit-env\Scripts\activate
```

Upgrade tooling:

```bash
pip install --upgrade pip setuptools wheel
```

Install common dependencies:

```bash
pip install requests pyyaml pandas tqdm python-dotenv
```

Nice optional tooling:

```bash
pip install rich typer httpx rapidfuzz
```

---

## 2) 🔑 API Keys — When You Need Them

Many scholarly APIs work without keys but rate limits will be lower.

| API              | Key Required? | Why Get One                   |
| ---------------- | ------------- | ----------------------------- |
| PubMed (NCBI)    | Optional      | Higher rate limits            |
| Europe PMC       | No            | Fully open                    |
| Crossref         | No            | Add polite email header       |
| Semantic Scholar | Recommended   | Better batching + reliability |
| OpenAlex         | No            | Email recommended             |
| CORE             | Yes           | Required                      |

### How to Get Keys

**CORE**

* https://core.ac.uk/services/api
* Create account → generate key

**Semantic Scholar**

* https://www.semanticscholar.org/product/api

**PubMed**

* https://www.ncbi.nlm.nih.gov/account/settings/

---

## 3) 🔐 Store Keys Properly (.env)

Never hardcode secrets.

Create:

```
.env
```

```env
CORE_API_KEY=xxxx
S2_API_KEY=xxxx
NCBI_API_KEY=xxxx
EMAIL=your_email@lab.edu
```

Load:

```python
from dotenv import load_dotenv
import os

load_dotenv()

CORE_KEY = os.getenv("CORE_API_KEY")
S2_KEY = os.getenv("S2_API_KEY")
EMAIL = os.getenv("EMAIL")
```

---

## 4) 📊 Citation Counts

The tool automatically extracts citation counts from APIs that provide them:

| API              | Citation Field           | Included? |
| ---------------- | ------------------------ | --------- |
| Semantic Scholar | `citationCount`          | Yes       |
| OpenAlex         | `cited_by_count`         | Yes       |
| Crossref         | `is-referenced-by-count` | Yes       |
| Europe PMC       | `citedByCount`           | Yes       |
| PubMed           | N/A                      | No        |
| CORE             | N/A                      | No        |

Results appear in the `citation_count` column of the output CSV. PubMed and CORE do not provide citation counts through their APIs, so those rows will have empty values.

---

## 5) 🧩 How to Form Good Queries

This is **information retrieval engineering**.

### 🔎 Query Design (API-Server Specific)

This tool queries multiple scholarly **API servers**, each of which supports a **different query syntax and search capability**.
Queries are therefore defined **per API** in `queries.yaml`.

---

#### 📁 Query Configuration File

All search strings live in:

```text
queries.yaml
```

Example structure:

```yaml
pubmed: |
  (
    "fMRI"[All Fields]
    OR "functional MRI"[All Fields]
    OR "BOLD"[All Fields])
    AND (respiration[All Fields] OR breathing[All Fields])
    AND (artifact*[All Fields] OR motion[All Fields] OR preprocessing[All Fields])
  )

europe_pmc: |
  ("fMRI" OR "functional MRI" OR "BOLD")
  AND (respiration OR breathing)
  AND (artifact* OR motion OR preprocessing)

openalex: >
  fMRI respiration artifact motion preprocessing
```

Each key corresponds to a **dedicated API query builder**.

**Search scope:** PubMed uses `[All Fields]` to search beyond title/abstract (MeSH terms, keywords, etc.). Europe PMC searches all fields including full text for open access articles. The remaining APIs (Crossref, Semantic Scholar, OpenAlex, CORE) search broadly by default.

---

#### 🔎 API Query Syntax Differences

<details>
<summary><strong> 👈🏼 Click to See Detailed Syntax Differences</strong></summary>

#### 🧬 PubMed (NCBI E-utilities)

Supports:

* Full Boolean logic
* Field restriction
* Wildcards (limited)
* Phrase queries

Recommended pattern:

```text
("keyword"[All Fields] OR synonym[All Fields])
AND (concept[All Fields])
NOT "excluded term"[All Fields]
```

Example:

```text
("fMRI"[All Fields] OR "BOLD"[All Fields])
AND (respiration[All Fields])
AND (artifact*[All Fields] OR motion[All Fields])
NOT "speech recognition"[All Fields]
```

**Why:**
`[All Fields]` searches title, abstract, MeSH terms, keywords, and all other indexed fields for broader recall.

---

#### 🇪🇺 Europe PMC

Supports:

* Boolean logic
* Wildcards
* Phrase queries

Without a field prefix, Europe PMC searches all fields including full text for open access articles.

Example:

```text
("fMRI" OR "BOLD")
AND (respiration)
AND (artifact*)
NOT "speech recognition"
```

---

#### 📚 Crossref

Does **not support structured Boolean queries reliably**.

Best practice:

* Use **keyword bags**
* Provide multiple concept tokens
* Let Crossref relevance ranking handle scoring

Example:

```text
fMRI respiration artifact motion denoising preprocessing
```

---

#### 🧠 Semantic Scholar

Supports:

* Keyword queries
* Limited Boolean support
* Relevance ranking strongly influences results

Recommended:

```text
fMRI BOLD respiration artifact motion denoising preprocessing
```

---

#### 🌍 OpenAlex

Uses a **semantic + keyword ranking system**.

Best practice:

* Short concept queries
* Avoid heavy Boolean nesting
* Prefer multiple independent query runs

Example:

```text
fMRI respiration physiological noise artifact
```

---

#### 📄 CORE

Supports Boolean queries but parsing can be inconsistent.

Recommended pattern:

```text
(fMRI OR "functional MRI" OR BOLD)
AND (respiration OR breathing)
AND (artifact OR motion OR preprocessing)
```

---

### 🧠 Recommended Query Strategy

Because APIs differ, the tool uses a **hybrid retrieval strategy**:

#### Tier 1 — High Recall APIs

* OpenAlex
* Semantic Scholar
* Crossref

Use **broad keyword queries**.

#### Tier 2 — High Precision APIs

* PubMed
* Europe PMC
* CORE

Use **structured Boolean + field restriction queries**.

Results are later **merged and deduplicated**.

---

### 🧩 Query Engineering Tips

* Expand synonyms:
  `respiration`, `respiratory`, `breathing`, `physiological noise`

* Expand modality:
  `fMRI`, `functional MRI`, `BOLD`

* Expand method terms:
  `artifact`, `motion`, `denoising`, `preprocessing`, `quality control`

* Avoid overly long Boolean chains for ranking-based APIs.

* Run **multiple query variants** rather than one massive query.

---

### 🔬 Reproducibility

For each search run, the tool logs: query string, API server, timestamp, and result count. This allows full reconstruction of the literature search.

</details>

---

## 6) 🚫 Exclusion Terms

`generate_queries_yaml()` supports an optional `exclude_terms` parameter to filter out irrelevant results:

```python
generate_queries_yaml(
    [
        ["foundation model", "foundation models"],
        ["fMRI", "EEG", "functional MRI"],
    ],
    exclude_terms=["speech recognition", "natural language processing", "image"],
)
```

This appends `NOT` clauses to each API query using the correct syntax:

- **PubMed:** `NOT "term"[All Fields]` per term
- **Europe PMC:** `NOT "term"` per term
- **Generic APIs:** `NOT ("term1" OR "term2")` as a single clause

---

## 7) 🧹 Deduplication Strategy

APIs overlap heavily.

Best identifiers:

* DOI (gold standard)
* Semantic Scholar CorpusID
* Title fuzzy match
* Year window ±1

Use:

```bash
pip install rapidfuzz
```

---

### 🧠 Rate Limiting Best Practice

Always be polite to literature APIs. We are using ```get_with_backoff_jitter``` to handle rate limits and transient failures. This request wrapper retries failed API calls with an increasing random delay between attempts.

It is important because literature APIs (e.g., PubMed, Semantic Scholar, CORE) enforce rate limits and temporary throttling. Retrying immediately can lead to repeated failures or IP blocking. 

Exponential backoff:
* reduces request bursts during failures
* increases the chance that the next retry succeeds
* prevents hammering external services
* improves robustness of long harvesting jobs
* helps comply with API usage policies

---

### ⭐ Pro Tips (Real Literature Mining Pipelines)

#### Save Raw JSON

Never only save processed CSV.

#### Log Query + Timestamp

Reproducibility matters.