TO DO: 
add google scholar > Google Scholar has no official API. scholarly library, Free Python library that scrapes Google Scholar directly. Works but is unreliable — frequently blocked by Google CAPTCHAs/rate limits, especially in automated pipelines.

remove redundant old code
exclude review papers
check the main text not only abstract

Recommended stack:
requests
beautifulsoup4
pandas
biopython for PubMed
tenacity for retries
rapidfuzz for fuzzy dedupe
sqlite3 or duckdb for storage

literature_review/
├── queries.yaml
├── harvest-paper.py
├── fetch
│   ├── fetch_pubmed.py
│   └── ...
├── config.py
├── utils.py
├── screen.py
└── results/
    └── literature_results.csv