"""
Research Attention Index (RAI) computation.

RAI = (Publications for disease X / Total publications) /
      (DALYs for disease X / Total global DALYs)

RAI > 1 = over-studied relative to burden
RAI < 1 = under-studied relative to burden
RAI = 1 = perfectly proportional

log2(RAI) is used for visualization (symmetric around 0).
"""

import numpy as np
import pandas as pd


def compute_rai(
    pub_counts: pd.DataFrame,
    daly_data: pd.DataFrame,
    cause_col: str = "cause_name",
    pub_col: str = "pub_count",
    daly_col: str = "dalys",
) -> pd.DataFrame:
    """Compute the Research Attention Index for each disease.

    Args:
        pub_counts: DataFrame with cause_name and pub_count columns
        daly_data: DataFrame with cause_name and dalys columns
        cause_col: column name for disease/cause
        pub_col: column name for publication counts
        daly_col: column name for DALY values

    Returns:
        DataFrame with RAI values, sorted by RAI descending
    """
    # Merge publications with DALYs
    merged = pub_counts.merge(daly_data, on=cause_col, how="inner")

    total_pubs = merged[pub_col].sum()
    total_dalys = merged[daly_col].sum()

    # Compute RAI
    merged["pub_share"] = merged[pub_col] / total_pubs
    merged["daly_share"] = merged[daly_col] / total_dalys
    merged["rai"] = merged["pub_share"] / merged["daly_share"]
    merged["log2_rai"] = np.log2(merged["rai"].replace(0, np.nan))

    # Rank
    merged = merged.sort_values("rai", ascending=False).reset_index(drop=True)
    merged["rank_overstudied"] = range(1, len(merged) + 1)

    return merged


def top_overstudied(rai_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the top N most over-studied diseases (highest RAI)."""
    return rai_df.head(n)


def top_understudied(rai_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the top N most under-studied diseases (lowest RAI)."""
    return rai_df.tail(n).iloc[::-1]


def summarise_rai(rai_df: pd.DataFrame) -> str:
    """Print a formatted summary of the RAI analysis."""
    lines = []
    lines.append(f"Research Attention Index — {len(rai_df)} diseases analysed")
    lines.append("=" * 70)

    lines.append(f"\nMedian RAI: {rai_df['rai'].median():.2f}")
    lines.append(f"Mean RAI:   {rai_df['rai'].mean():.2f}")
    lines.append(f"Diseases with RAI > 1 (over-studied): {(rai_df['rai'] > 1).sum()}")
    lines.append(f"Diseases with RAI < 1 (under-studied): {(rai_df['rai'] < 1).sum()}")

    lines.append("\nTop 10 OVER-studied (highest RAI):")
    lines.append("-" * 70)
    for _, row in top_overstudied(rai_df).iterrows():
        lines.append(
            f"  {row['cause_name']:<45} RAI={row['rai']:>8.1f}  "
            f"pubs={row['pub_count']:>6.0f}  DALYs={row['dalys']:>12,.0f}"
        )

    lines.append("\nTop 10 UNDER-studied (lowest RAI):")
    lines.append("-" * 70)
    for _, row in top_understudied(rai_df).iterrows():
        lines.append(
            f"  {row['cause_name']:<45} RAI={row['rai']:>8.3f}  "
            f"pubs={row['pub_count']:>6.0f}  DALYs={row['dalys']:>12,.0f}"
        )

    return "\n".join(lines)
