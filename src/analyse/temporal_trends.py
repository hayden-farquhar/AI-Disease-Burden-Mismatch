"""
Temporal trend analysis: how has the research-burden mismatch evolved 2015–2025?

Computes per-year RAI and summary statistics to determine whether
the mismatch is improving, worsening, or stable over time.
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def compute_yearly_rai(
    mapped_df: pd.DataFrame,
    gbd_dalys: pd.DataFrame,
    name_map: dict[str, str],
    year_range: range = range(2015, 2026),
) -> pd.DataFrame:
    """Compute RAI for each year.

    Returns a long-format DataFrame with columns:
        year, cause_name, pub_count, dalys, pub_share, daly_share, rai, log2_rai
    """
    from src.collect.disease_mapper import compute_cause_counts

    all_years = []
    for year in year_range:
        year_df = mapped_df[mapped_df["year"] == year]
        if len(year_df) == 0:
            continue

        # Get cause counts for this year
        cc = compute_cause_counts(year_df)
        cc["gbd_name"] = cc["cause_name"].map(name_map).fillna(cc["cause_name"])

        # Aggregate to GBD names
        agg = cc.groupby("gbd_name").agg(
            pub_count=("pub_count", "sum"),
            level1=("level1", "first"),
            level2=("level2", "first"),
        ).reset_index().rename(columns={"gbd_name": "cause_name"})

        # Merge with DALYs
        merged = agg.merge(gbd_dalys, on="cause_name", how="inner")
        total_pubs = merged["pub_count"].sum()
        total_dalys = merged["dalys"].sum()

        merged["pub_share"] = merged["pub_count"] / total_pubs
        merged["daly_share"] = merged["dalys"] / total_dalys
        merged["rai"] = merged["pub_share"] / merged["daly_share"]
        merged["log2_rai"] = np.log2(merged["rai"].replace(0, np.nan))
        merged["year"] = year

        all_years.append(merged)

    return pd.concat(all_years, ignore_index=True)


def compute_yearly_correlation(yearly_rai: pd.DataFrame) -> pd.DataFrame:
    """Compute Spearman correlation between pub_share and daly_share per year."""
    rows = []
    for year, group in yearly_rai.groupby("year"):
        rho, p = spearmanr(group["pub_share"], group["daly_share"])
        rows.append({
            "year": year,
            "spearman_rho": rho,
            "p_value": p,
            "n_diseases": len(group),
            "total_pubs": group["pub_count"].sum(),
            "median_rai": group["rai"].median(),
            "mean_rai": group["rai"].mean(),
            "pct_overstudied": (group["rai"] > 1).mean() * 100,
            "gini_rai": _gini(group["rai"].values),
        })
    return pd.DataFrame(rows)


def compute_disease_trajectories(
    yearly_rai: pd.DataFrame,
    diseases: list[str] | None = None,
) -> pd.DataFrame:
    """Get RAI trajectories for specific diseases over time.

    Returns wide-format: rows=diseases, columns=years, values=RAI.
    """
    pivot = yearly_rai.pivot_table(
        index="cause_name", columns="year", values="rai", aggfunc="first"
    )
    if diseases:
        pivot = pivot.loc[pivot.index.isin(diseases)]
    return pivot


def _gini(values: np.ndarray) -> float:
    """Compute Gini coefficient for RAI distribution (0=perfect equality, 1=max inequality)."""
    values = np.sort(values)
    n = len(values)
    if n == 0 or values.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * values) - (n + 1) * np.sum(values)) / (n * np.sum(values))
