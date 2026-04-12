"""
GBD 2023 data loader.

Loads and processes DALY data from the IHME Global Burden of Disease 2023 study.
The user must download CSV data from https://vizhub.healthdata.org/gbd-results/
with these settings:
  - Measure: DALYs
  - Location: Global (and optionally by World Bank income group)
  - Year: 2021 (latest available in GBD 2023)
  - Age: All ages
  - Sex: Both
  - Cause: Level 3
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "gbd"


def load_gbd_dalys(filepath: Path | str | None = None) -> pd.DataFrame:
    """Load GBD DALY data from CSV.

    Expected columns from IHME download:
    - cause_name: GBD cause name
    - val: central estimate (DALYs)
    - upper: upper uncertainty interval
    - lower: lower uncertainty interval
    - year: year
    - location_name: location
    """
    if filepath is None:
        # Try to find a CSV in the data directory
        csvs = list(DATA_DIR.glob("*.csv"))
        if not csvs:
            raise FileNotFoundError(
                f"No GBD CSV files found in {DATA_DIR}. "
                "Download from https://vizhub.healthdata.org/gbd-results/"
            )
        filepath = csvs[0]

    df = pd.read_csv(filepath)

    # Standardise column names (IHME exports vary slightly)
    col_map = {}
    for col in df.columns:
        cl = col.lower().strip()
        if cl in ("cause_name", "cause"):
            col_map[col] = "cause_name"
        elif cl in ("val", "value"):
            col_map[col] = "dalys"
        elif cl in ("upper",):
            col_map[col] = "dalys_upper"
        elif cl in ("lower",):
            col_map[col] = "dalys_lower"
        elif cl in ("year", "year_id"):
            col_map[col] = "year"
        elif cl in ("location_name", "location"):
            col_map[col] = "location"
        elif cl in ("measure_name", "measure"):
            col_map[col] = "measure"
        elif cl in ("sex_name", "sex"):
            col_map[col] = "sex"
        elif cl in ("age_name", "age"):
            col_map[col] = "age"
        elif cl in ("cause_id",):
            col_map[col] = "cause_id"

    df = df.rename(columns=col_map)
    return df


def get_global_dalys(filepath: Path | str | None = None) -> pd.DataFrame:
    """Get global DALYs by cause (Level 3), most recent year.

    Returns DataFrame with columns: cause_name, dalys, dalys_share
    """
    df = load_gbd_dalys(filepath)

    # Filter to global, both sexes, all ages if those columns exist
    if "location" in df.columns:
        df = df[df["location"] == "Global"]
    if "sex" in df.columns:
        df = df[df["sex"] == "Both"]
    if "age" in df.columns:
        df = df[df["age"].str.contains("All", case=False, na=False)]
    if "measure" in df.columns:
        df = df[df["measure"].str.contains("DALY", case=False, na=False)]

    # Take most recent year
    if "year" in df.columns:
        df = df[df["year"] == df["year"].max()]

    # Keep essential columns
    result = df[["cause_name", "dalys"]].copy()
    result = result.sort_values("dalys", ascending=False).reset_index(drop=True)
    result["dalys_share"] = result["dalys"] / result["dalys"].sum()
    return result
