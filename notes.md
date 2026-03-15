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
├── normalize.py
├── merge_and_dedupe.py
├── screen.py
└── results/
    └── literature_results.csv