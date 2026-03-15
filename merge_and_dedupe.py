import pandas as pd

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