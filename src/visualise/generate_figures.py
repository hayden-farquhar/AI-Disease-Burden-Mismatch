"""
Generate all publication figures for the manuscript.

Figure 1: Mismatch bubble plot (log DALYs vs log publications)
Figure 2: RAI bar chart (top/bottom 15)
Figure 3: Temporal trends (yearly ρ and key disease trajectories)
Figure 4: Method × disease heatmap
Figure 5: AI vs general medical research comparison
Figure 6: Low-SDI vs High-SDI burden alignment
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D
import seaborn as sns
from pathlib import Path

from src.visualise.style import set_lancet_style, PALETTE, LEVEL1_COLORS

set_lancet_style()
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def load_data():
    rai = pd.read_csv(ROOT / "data" / "analysis" / "rai_official_gbd_2015_2025.csv")
    yearly_corr = pd.read_csv(ROOT / "data" / "analysis" / "yearly_correlation_2015_2025.csv")
    yearly_rai = pd.read_csv(ROOT / "data" / "analysis" / "yearly_rai_2015_2025.csv")
    ai_vs_gen = pd.read_csv(ROOT / "data" / "analysis" / "ai_vs_general_medical_research.csv")
    rai_low = pd.read_csv(ROOT / "data" / "analysis" / "rai_low_sdi_burden.csv")
    rai_high = pd.read_csv(ROOT / "data" / "analysis" / "rai_high_sdi_burden.csv")
    return rai, yearly_corr, yearly_rai, ai_vs_gen, rai_low, rai_high


def figure1_bubble_plot(rai):
    """THE figure: log(DALYs) vs log(publications), coloured by GBD Level 1."""
    fig, ax = plt.subplots(figsize=(8, 6))

    for _, row in rai.iterrows():
        color = LEVEL1_COLORS.get(row.get("level1", ""), PALETTE["neutral"])
        if row["cause_name"] == "COVID-19":
            color = PALETTE["covid"]
        ax.scatter(
            np.log10(row["dalys"]),
            np.log10(row["pub_count"] + 1),
            s=max(15, min(row["pub_count"] / 8, 300)),
            c=color,
            alpha=0.65,
            edgecolors="white",
            linewidths=0.3,
            zorder=3,
        )

    # Proportionality line
    x_range = np.array([4, 9])
    total_pubs = rai["pub_count"].sum()
    total_dalys = rai["dalys"].sum()
    y_prop = x_range + np.log10(total_pubs / total_dalys)
    ax.plot(x_range, y_prop, "--", color="grey", linewidth=0.8, alpha=0.6, zorder=1)
    ax.text(8.5, y_prop[-1] + 0.1, "Proportional", fontsize=7, color="grey", ha="right")

    # Label key diseases
    labels = {
        "Malignant skin melanoma": (0.15, 0.15),
        "Breast cancer": (0.15, 0.1),
        "Brain and central nervous system cancer": (-0.15, 0.15),
        "Blindness and vision loss": (0.15, 0.1),
        "COVID-19": (0.15, -0.15),
        "Road injuries": (0.15, -0.1),
        "Diarrheal diseases": (0.15, 0.1),
        "Anxiety disorders": (-0.25, -0.15),
        "Parkinson's disease": (0.15, 0.1),
        "Ischemic heart disease": (0.15, -0.15),
        "Stroke": (-0.25, 0.1),
        "Neonatal disorders": (-0.3, -0.1),
        "Tuberculosis": (0.15, 0.1),
        "Malaria": (0.15, -0.1),
        "Dietary iron deficiency": (0.15, 0.1),
        "Diabetes mellitus": (0.15, 0.1),
        "Depressive disorders": (-0.3, -0.1),
    }
    for _, row in rai.iterrows():
        if row["cause_name"] in labels:
            dx, dy = labels[row["cause_name"]]
            name = row["cause_name"]
            if name == "Blindness and vision loss":
                name = "Blindness/vision"
            elif name == "Brain and central nervous system cancer":
                name = "Brain cancer"
            elif name == "Ischemic heart disease":
                name = "IHD"
            elif name == "Dietary iron deficiency":
                name = "Iron deficiency"
            elif name == "Depressive disorders":
                name = "Depression"
            elif name == "Diarrheal diseases":
                name = "Diarrhoea"
            elif name == "Malignant skin melanoma":
                name = "Melanoma"
            ax.annotate(
                name, (np.log10(row["dalys"]), np.log10(row["pub_count"] + 1)),
                xytext=(dx, dy), textcoords="offset fontsize",
                fontsize=6.5, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", color="grey", lw=0.4),
            )

    ax.set_xlabel("Global disease burden (log$_{10}$ DALYs, GBD 2021)")
    ax.set_ylabel("Medical AI publications (log$_{10}$, 2015–2025)")
    ax.set_title("Medical AI research attention vs global disease burden")

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=LEVEL1_COLORS["Non-communicable diseases"],
               markersize=8, label='Non-communicable diseases'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=LEVEL1_COLORS["Communicable, maternal, neonatal, and nutritional diseases"],
               markersize=8, label='Communicable/maternal/neonatal'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=LEVEL1_COLORS["Injuries"],
               markersize=8, label='Injuries'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE["covid"],
               markersize=8, label='COVID-19'),
    ]
    ax.legend(handles=legend_elements, loc="lower right", frameon=True, framealpha=0.9)

    fig.savefig(OUT / "fig1_mismatch_bubble.png")
    fig.savefig(OUT / "fig1_mismatch_bubble.pdf")
    plt.close(fig)
    print("Figure 1 saved")


def figure2_rai_bar(rai):
    """Top 15 over-studied and bottom 15 under-studied diseases."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6), gridspec_kw={"wspace": 0.6})

    # Over-studied (top 15)
    over = rai.head(15).copy()
    over["log2_rai_display"] = np.log2(over["rai"])
    over["short_name"] = over["cause_name"].str.replace(" and other dementias", "")
    over["short_name"] = over["short_name"].str.replace("and central nervous system ", "")
    over["short_name"] = over["short_name"].str.replace("Malignant skin m", "M")
    over["short_name"] = over["short_name"].str.replace("Tracheal, bronchus, and lung", "Lung")
    over["short_name"] = over["short_name"].str.replace("Inflammatory bowel disease", "IBD")
    over["short_name"] = over["short_name"].str.replace("Age-related macular degeneration", "AMD")
    over["short_name"] = over["short_name"].str.replace("Atrial fibrillation and flutter", "Atrial fibrillation")

    colors_over = [LEVEL1_COLORS.get(r["level1"], PALETTE["neutral"]) for _, r in over.iterrows()]
    ax1.barh(range(len(over)), over["log2_rai_display"], color=colors_over, edgecolor="white", linewidth=0.5)
    ax1.set_yticks(range(len(over)))
    ax1.set_yticklabels(over["short_name"], fontsize=7.5)
    ax1.set_xlabel("log$_2$(RAI)")
    ax1.set_title("Most over-studied\n(highest RAI)", fontsize=10)
    ax1.invert_yaxis()
    ax1.axvline(x=0, color="grey", linewidth=0.5, linestyle="--")

    # Under-studied (bottom 15)
    under = rai.tail(15).iloc[::-1].copy()
    under["log2_rai_display"] = np.log2(under["rai"])
    under["short_name"] = under["cause_name"].str.replace("Idiopathic developmental intellectual disability", "Intellectual disability")
    under["short_name"] = under["short_name"].str.replace("Dietary iron deficiency", "Iron deficiency")

    colors_under = [LEVEL1_COLORS.get(r["level1"], PALETTE["neutral"]) for _, r in under.iterrows()]
    ax2.barh(range(len(under)), under["log2_rai_display"], color=colors_under, edgecolor="white", linewidth=0.5)
    ax2.set_yticks(range(len(under)))
    ax2.set_yticklabels(under["short_name"], fontsize=7.5)
    ax2.set_xlabel("log$_2$(RAI)")
    ax2.set_title("Most under-studied\n(lowest RAI)", fontsize=10)
    ax2.invert_yaxis()
    ax2.axvline(x=0, color="grey", linewidth=0.5, linestyle="--")

    fig.suptitle("Research Attention Index: most over- and under-studied diseases", fontsize=11, y=1.02)
    fig.savefig(OUT / "fig2_rai_bars.png")
    fig.savefig(OUT / "fig2_rai_bars.pdf")
    plt.close(fig)
    print("Figure 2 saved")


def figure3_temporal(yearly_corr, yearly_rai):
    """Panel A: yearly Spearman ρ. Panel B: RAI trajectories for key diseases."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), gridspec_kw={"wspace": 0.35})

    # Panel A: yearly correlation
    ax1.plot(yearly_corr["year"], yearly_corr["spearman_rho"], "o-", color=PALETTE["communicable"],
             markersize=5, linewidth=1.5)
    ax1.fill_between(yearly_corr["year"], 0, yearly_corr["spearman_rho"], alpha=0.1,
                     color=PALETTE["communicable"])
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Spearman ρ\n(publication share vs DALY share)")
    ax1.set_title("A  Alignment trend (2015–2025)", loc="left", fontweight="bold")
    ax1.set_ylim(0, 0.6)
    ax1.axhline(y=0, color="grey", linewidth=0.5)

    from scipy.stats import linregress
    slope, intercept, _, p, _ = linregress(yearly_corr["year"], yearly_corr["spearman_rho"])
    ax1.text(0.05, 0.95, f"Trend: +{slope:.3f}/year\n(p = {p:.3f})",
             transform=ax1.transAxes, fontsize=7.5, va="top",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="lightgrey"))

    # Panel B: disease trajectories
    key_diseases = [
        ("Breast cancer", PALETTE["ncd"]),
        ("Malignant skin melanoma", "#D6604D"),
        ("Ischemic heart disease", "#F4A582"),
        ("Stroke", "#92C5DE"),
        ("Tuberculosis", PALETTE["communicable"]),
        ("Road injuries", PALETTE["injuries"]),
        ("Depressive disorders", "#756BB1"),
        ("COVID-19", PALETTE["covid"]),
    ]
    for disease, color in key_diseases:
        traj = yearly_rai[yearly_rai["cause_name"] == disease].sort_values("year")
        if len(traj) > 0:
            ax2.plot(traj["year"], np.log2(traj["rai"]), "o-", color=color,
                     markersize=3, linewidth=1.2, label=disease.replace("Ischemic heart disease", "IHD")
                     .replace("Depressive disorders", "Depression")
                     .replace("Malignant skin melanoma", "Melanoma"))

    ax2.axhline(y=0, color="grey", linewidth=0.8, linestyle="--")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("log$_2$(RAI)")
    ax2.set_title("B  Disease RAI trajectories", loc="left", fontweight="bold")
    ax2.legend(fontsize=6.5, loc="upper left", frameon=True, framealpha=0.9, ncol=2)

    # Annotations
    ax2.text(2025.3, 0.3, "Over-studied", fontsize=6.5, color="grey", rotation=90, va="bottom")
    ax2.text(2025.3, -0.3, "Under-studied", fontsize=6.5, color="grey", rotation=90, va="top")

    fig.savefig(OUT / "fig3_temporal_trends.png")
    fig.savefig(OUT / "fig3_temporal_trends.pdf")
    plt.close(fig)
    print("Figure 3 saved")


def figure4_method_heatmap():
    """Heatmap of AI method × disease (top diseases)."""
    method_by_disease = pd.read_csv(ROOT / "data" / "analysis" / "method_by_disease.csv", index_col=0)

    # Top 20 diseases by total across methods
    method_by_disease["total"] = method_by_disease.sum(axis=1)
    top20 = method_by_disease.nlargest(20, "total").drop(columns=["total"])

    # Normalise by row (percentage within disease)
    top20_pct = top20.div(top20.sum(axis=1), axis=0) * 100

    # Rename for display
    rename_map = {
        "Alzheimer's disease and other dementias": "Alzheimer's",
        "Brain and central nervous system cancer": "Brain cancer",
        "Tracheal, bronchus, and lung cancer": "Lung cancer",
        "Diabetes mellitus type 2": "Diabetes",
        "Ischaemic heart disease": "IHD",
        "Atrial fibrillation and flutter": "Atrial fibrillation",
        "Colon and rectum cancer": "Colorectal cancer",
        "Chronic kidney disease": "CKD",
        "Cirrhosis and other chronic liver diseases": "Liver disease",
        "Malignant skin melanoma": "Melanoma",
        "Hypertensive heart disease": "Hypertension",
    }
    top20_pct.index = [rename_map.get(d, d) for d in top20_pct.index]

    # Keep most interesting method columns
    cols = ["Deep learning (CNN)", "Deep learning (other)", "Traditional ML",
            "NLP", "Transformer / LLM", "Reinforcement learning"]
    cols = [c for c in cols if c in top20_pct.columns]
    top20_pct = top20_pct[cols]

    fig, ax = plt.subplots(figsize=(7, 7))
    sns.heatmap(top20_pct, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, linecolor="white", ax=ax,
                cbar_kws={"label": "% of disease papers", "shrink": 0.6})
    ax.set_title("AI method distribution by disease (%)", fontsize=11)
    ax.set_ylabel("")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right", fontsize=7.5)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=7.5)

    fig.savefig(OUT / "fig4_method_heatmap.png")
    fig.savefig(OUT / "fig4_method_heatmap.pdf")
    plt.close(fig)
    print("Figure 4 saved")


def figure5_ai_vs_general(ai_vs_gen):
    """AI vs general medical research: scatter of RAI ratios."""
    fig, ax = plt.subplots(figsize=(8, 6.5))

    df = ai_vs_gen.dropna(subset=["ai_rai", "gen_rai"]).copy()
    df = df[(df["gen_rai"] > 0) & (df["ai_rai"] > 0)]
    df["log_ai"] = np.log2(df["ai_rai"])
    df["log_gen"] = np.log2(df["gen_rai"])

    ax.scatter(df["log_gen"], df["log_ai"], s=45, c=PALETTE["communicable"],
               alpha=0.7, edgecolors="white", linewidths=0.5, zorder=3)

    # Identity line
    lim = max(abs(df["log_gen"]).max(), abs(df["log_ai"]).max()) + 0.5
    ax.plot([-lim, lim], [-lim, lim], "--", color="grey", linewidth=0.8, zorder=1)

    # Label selection: only label points far from the diagonal or with large |RAI|
    # Use adjustText to avoid overlaps
    from adjustText import adjust_text
    texts = []
    for _, row in df.iterrows():
        dist_from_diag = abs(row["log_ai"] - row["log_gen"])
        magnitude = max(abs(row["log_ai"]), abs(row["log_gen"]))
        if dist_from_diag > 1.0 or magnitude > 2.5:
            name = row["disease"]
            texts.append(ax.text(row["log_gen"], row["log_ai"], name, fontsize=6))

    adjust_text(texts, ax=ax,
                arrowprops=dict(arrowstyle="-", color="grey", lw=0.4),
                force_points=(0.5, 0.5),
                force_text=(0.8, 0.8),
                expand_points=(1.5, 1.5),
                expand_text=(1.2, 1.2))

    ax.set_xlabel("General medical research: log$_2$(RAI)")
    ax.set_ylabel("Medical AI research: log$_2$(RAI)")
    ax.set_title("AI vs general medical research alignment with disease burden")

    # Quadrant labels
    ax.text(0.97, 0.97, "AI & general\nboth over-study", transform=ax.transAxes,
            fontsize=7, ha="right", va="top", color="grey", style="italic")
    ax.text(0.03, 0.03, "AI & general\nboth under-study", transform=ax.transAxes,
            fontsize=7, ha="left", va="bottom", color="grey", style="italic")
    ax.text(0.03, 0.97, "AI over-studies\nmore than general", transform=ax.transAxes,
            fontsize=7, ha="left", va="top", color=PALETTE["over"], style="italic")
    ax.text(0.97, 0.03, "AI under-studies\nmore than general", transform=ax.transAxes,
            fontsize=7, ha="right", va="bottom", color=PALETTE["under"], style="italic")

    ax.axhline(0, color="lightgrey", linewidth=0.5, zorder=0)
    ax.axvline(0, color="lightgrey", linewidth=0.5, zorder=0)

    fig.savefig(OUT / "fig5_ai_vs_general.png")
    fig.savefig(OUT / "fig5_ai_vs_general.pdf")
    plt.close(fig)
    print("Figure 5 saved")


def figure6_sdi_comparison(rai, rai_low, rai_high):
    """Scatter: AI research vs Low-SDI burden (left) and High-SDI burden (right)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), gridspec_kw={"wspace": 0.35})

    from scipy.stats import spearmanr

    for ax, sdi_rai, label, sdi_label in [
        (ax1, rai_low, "A  vs Low SDI burden", "Low SDI"),
        (ax2, rai_high, "B  vs High SDI burden", "High SDI"),
    ]:
        df = sdi_rai.dropna(subset=["dalys", "pub_count"])
        df = df[df["dalys"] > 0]

        colors = [LEVEL1_COLORS.get(r.get("level1", ""), PALETTE["neutral"]) for _, r in df.iterrows()]
        ax.scatter(np.log10(df["dalys"]), np.log10(df["pub_count"] + 1),
                   s=25, c=colors, alpha=0.6, edgecolors="white", linewidths=0.3)

        # Proportionality line
        x_range = np.array([3, 9])
        total_pubs = df["pub_count"].sum()
        total_dalys = df["dalys"].sum()
        y_prop = x_range + np.log10(total_pubs / total_dalys)
        ax.plot(x_range, y_prop, "--", color="grey", linewidth=0.8, alpha=0.5)

        rho, p = spearmanr(df["pub_share"], df["daly_share"])
        ax.set_title(f"{label}\n(ρ = {rho:.3f})", loc="left", fontweight="bold", fontsize=9)
        ax.set_xlabel(f"Disease burden ({sdi_label}, log$_{{10}}$ DALYs)")
        ax.set_ylabel("AI publications (log$_{10}$)")

    # Shared legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=LEVEL1_COLORS["Non-communicable diseases"],
               markersize=7, label='Non-communicable diseases'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=LEVEL1_COLORS["Communicable, maternal, neonatal, and nutritional diseases"],
               markersize=7, label='Communicable/maternal/neonatal'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=LEVEL1_COLORS["Injuries"],
               markersize=7, label='Injuries'),
        Line2D([0], [0], linestyle='--', color='grey', linewidth=0.8, label='Proportional'),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=4, frameon=True,
               framealpha=0.9, fontsize=7.5, bbox_to_anchor=(0.5, -0.05))

    fig.suptitle("AI research alignment with disease burden by income group", fontsize=11, y=1.02)
    fig.savefig(OUT / "fig6_sdi_comparison.png")
    fig.savefig(OUT / "fig6_sdi_comparison.pdf")
    plt.close(fig)
    print("Figure 6 saved")


if __name__ == "__main__":
    print("Loading data...")
    rai, yearly_corr, yearly_rai, ai_vs_gen, rai_low, rai_high = load_data()

    print("Generating figures...")
    figure1_bubble_plot(rai)
    figure2_rai_bar(rai)
    figure3_temporal(yearly_corr, yearly_rai)
    figure4_method_heatmap()
    figure5_ai_vs_general(ai_vs_gen)
    figure6_sdi_comparison(rai, rai_low, rai_high)

    print(f"\nAll figures saved to {OUT}/")
