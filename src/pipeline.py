"""
Full replication pipeline for:
  "Medical artificial intelligence research is misaligned with global
   disease burden: a bibliometric analysis of 197,844 publications"

Usage:
    python -m src.pipeline           # Run everything
    python -m src.pipeline collect   # Only collect data
    python -m src.pipeline analyse   # Only run analyses (requires collected data)
    python -m src.pipeline figures   # Only generate figures (requires analysis data)
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, mannwhitneyu, linregress
import statsmodels.api as sm

# Paths
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OPENALEX_DIR = DATA_DIR / "openalex"
GBD_DIR = DATA_DIR / "gbd"
ANALYSIS_DIR = DATA_DIR / "analysis"
OUTPUT_DIR = ROOT / "outputs"
FIG_DIR = OUTPUT_DIR / "figures"

for d in [OPENALEX_DIR, GBD_DIR, ANALYSIS_DIR, OUTPUT_DIR, FIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def step_collect():
    """Step 1: Collect medical AI publications from OpenAlex."""
    from src.collect.openalex_client import collect_all_to_parquet, count_works

    merged_path = OPENALEX_DIR / "medical_ai_works_2015_2025.parquet"
    if merged_path.exists():
        df = pd.read_parquet(merged_path)
        print(f"[collect] Already collected: {len(df):,} papers. Skipping.")
        return

    print("[collect] Counting medical AI publications...")
    n = count_works()
    print(f"[collect] Total: {n:,} publications. Starting collection...")
    collect_all_to_parquet()


def step_map():
    """Step 2: Map publications to GBD diseases."""
    from src.collect.disease_mapper import map_dataframe

    merged_path = OPENALEX_DIR / "medical_ai_works_2015_2025.parquet"
    mapped_path = OPENALEX_DIR / "medical_ai_2015_2025_mapped.parquet"

    if mapped_path.exists():
        df = pd.read_parquet(mapped_path)
        print(f"[map] Already mapped: {df['is_mapped'].sum():,}/{len(df):,} papers. Skipping.")
        return

    print("[map] Loading publications...")
    df = pd.read_parquet(merged_path)
    print(f"[map] Mapping {len(df):,} papers to GBD diseases...")
    df_mapped = map_dataframe(df)
    df_mapped.to_parquet(mapped_path, index=False)
    n_mapped = df_mapped["is_mapped"].sum()
    print(f"[map] Mapped: {n_mapped:,}/{len(df_mapped):,} ({100*n_mapped/len(df_mapped):.1f}%)")


def step_analyse():
    """Step 3: Run all analyses."""
    from src.collect.disease_mapper import compute_cause_counts
    from src.collect.gbd_name_mapping import OUR_TO_GBD_NAME
    from src.analyse.attention_index import compute_rai, summarise_rai
    from src.analyse.temporal_trends import (
        compute_yearly_rai, compute_yearly_correlation, compute_disease_trajectories,
    )

    print("[analyse] Loading data...")
    mapped_df = pd.read_parquet(OPENALEX_DIR / "medical_ai_2015_2025_mapped.parquet")

    # Check GBD data exists
    gbd_path = GBD_DIR / "gbd_2023_global_dalys_number.csv"
    if not gbd_path.exists():
        print(f"[analyse] ERROR: GBD data not found at {gbd_path}")
        print("  Download from https://vizhub.healthdata.org/gbd-results/")
        print("  Settings: DALYs, Number, Global, 2021, All ages, Both, Level 3")
        sys.exit(1)

    gbd = pd.read_csv(gbd_path)
    gbd_dalys = gbd[
        (gbd["measure_name"] == "DALYs (Disability-Adjusted Life Years)") &
        (gbd["year"] == 2021) & (gbd["sex_name"] == "Both") & (gbd["age_name"] == "All ages")
    ][["cause_name", "val"]].rename(columns={"val": "dalys"})

    # --- Cause counts ---
    print("[analyse] Computing cause counts...")
    cause_counts = compute_cause_counts(mapped_df)
    cause_counts.to_csv(ANALYSIS_DIR / "cause_counts_2015_2025.csv", index=False)

    # --- RAI with official GBD DALYs ---
    print("[analyse] Computing RAI with official GBD DALYs...")
    cause_counts["gbd_name"] = cause_counts["cause_name"].map(OUR_TO_GBD_NAME).fillna(cause_counts["cause_name"])
    agg_counts = cause_counts.groupby("gbd_name").agg(
        pub_count=("pub_count", "sum"),
        level1=("level1", "first"),
        level2=("level2", "first"),
    ).reset_index().rename(columns={"gbd_name": "cause_name"})

    rai = compute_rai(agg_counts, gbd_dalys)
    rai.to_csv(ANALYSIS_DIR / "rai_official_gbd_2015_2025.csv", index=False)
    print(summarise_rai(rai))

    # --- Temporal trends ---
    print("[analyse] Computing temporal trends...")
    yearly_rai = compute_yearly_rai(mapped_df, gbd_dalys, OUR_TO_GBD_NAME)
    yearly_rai.to_csv(ANALYSIS_DIR / "yearly_rai_2015_2025.csv", index=False)

    yearly_corr = compute_yearly_correlation(yearly_rai)
    yearly_corr.to_csv(ANALYSIS_DIR / "yearly_correlation_2015_2025.csv", index=False)

    traj = compute_disease_trajectories(yearly_rai)
    traj.to_csv(ANALYSIS_DIR / "disease_rai_trajectories.csv")

    # --- Equity analysis (SDI) ---
    sdi_path = GBD_DIR / "gbd_2023_sdi_dalys_number.csv"
    if sdi_path.exists():
        print("[analyse] Computing SDI equity analysis...")
        sdi = pd.read_csv(sdi_path)
        for sdi_name, fname in [("Low SDI", "rai_low_sdi_burden.csv"),
                                 ("High SDI", "rai_high_sdi_burden.csv")]:
            sdi_dalys = sdi[
                (sdi["measure_name"] == "DALYs (Disability-Adjusted Life Years)") &
                (sdi["year"] == 2021) & (sdi["sex_name"] == "Both") &
                (sdi["age_name"] == "All ages") & (sdi["location_name"] == sdi_name)
            ][["cause_name", "val"]].rename(columns={"val": "dalys"})
            rai_sdi = compute_rai(agg_counts, sdi_dalys)
            rai_sdi.to_csv(ANALYSIS_DIR / fname, index=False)
            rho, p = spearmanr(rai_sdi["pub_share"], rai_sdi["daly_share"])
            print(f"  {sdi_name}: Spearman rho = {rho:.3f} (p = {p:.2e})")
    else:
        print("[analyse] SDI data not found — skipping equity analysis")

    # --- AI vs general medical research ---
    print("[analyse] Comparing with general medical research...")
    _compare_general_medical(mapped_df, rai, gbd_dalys)

    # --- Bootstrap CIs ---
    print("[analyse] Computing bootstrap CIs...")
    np.random.seed(42)
    n_boot = 10000
    boot_rhos = []
    for _ in range(n_boot):
        idx = np.random.choice(len(rai), size=len(rai), replace=True)
        boot_rai = rai.iloc[idx]
        r, _ = spearmanr(boot_rai["pub_share"], boot_rai["daly_share"])
        boot_rhos.append(r)
    boot_rhos = np.array(boot_rhos)
    rho_main, _ = spearmanr(rai["pub_share"], rai["daly_share"])
    print(f"  Spearman rho = {rho_main:.3f} (95% CI: {np.percentile(boot_rhos, 2.5):.3f}–{np.percentile(boot_rhos, 97.5):.3f})")

    # --- Supplementary analyses ---
    print("[analyse] Running supplementary analyses...")
    from src.analyse.supplementary import (
        validate_mapping, run_regression, corrective_modelling, permutation_test,
        sensitivity_analyses, stratify_methods_modalities, analyse_countries,
        citation_oa_analysis, ntd_analysis, dose_response_analysis,
    )

    # Mapping validation
    val = validate_mapping(mapped_df)
    print(f"  Mapping validation: precision={val['precision']:.0%}, recall={val['estimated_recall']:.1%}, F1={val['f1']:.1%}")

    # Sensitivity analyses
    sens = sensitivity_analyses(mapped_df, gbd, cause_counts)
    sens.to_csv(ANALYSIS_DIR / "sensitivity_analyses.csv", index=False)
    print(f"  Sensitivity analyses: {len(sens)} variants computed")

    # Regression
    ai_vs_gen_path = ANALYSIS_DIR / "ai_vs_general_medical_research.csv"
    if ai_vs_gen_path.exists():
        ai_vs_gen = pd.read_csv(ai_vs_gen_path)
        sdi_data = pd.read_csv(sdi_path) if sdi_path.exists() else None
        model, reg_df = run_regression(rai, ai_vs_gen, gbd_dalys, sdi_data)
        print(f"  Regression: R²={model.rsquared:.3f}, n={int(model.nobs)}")

        # Corrective modelling
        corr_results = corrective_modelling(ai_vs_gen)
        corr_results.to_csv(ANALYSIS_DIR / "corrective_scenarios.csv", index=False)
        print(f"  Corrective modelling: {len(corr_results)} scenario-share combinations")

        # Permutation test
        perm = permutation_test(ai_vs_gen)
        print(f"  Permutation test: observed rho={perm['rho_observed']:.3f}, p={perm['p_value']:.3f}")

    # Method/modality stratification
    df_strat = stratify_methods_modalities(mapped_df)
    method_counts = df_strat["primary_method"].value_counts()
    print(f"  Method stratification: {len(method_counts)} categories")
    method_by_year = pd.crosstab(df_strat["year"], df_strat["primary_method"])
    method_by_year.to_csv(ANALYSIS_DIR / "method_by_year.csv")

    mapped_strat = df_strat[df_strat["is_mapped"]]
    method_by_disease = pd.crosstab(mapped_strat["primary_cause"], mapped_strat["primary_method"])
    method_by_disease.to_csv(ANALYSIS_DIR / "method_by_disease.csv")
    modality_by_disease = pd.crosstab(mapped_strat["primary_cause"], mapped_strat["primary_modality"])
    modality_by_disease.to_csv(ANALYSIS_DIR / "modality_by_disease.csv")

    # Country/collaboration analysis
    country_counts, collab_counts, ntd_collab = analyse_countries(mapped_df)
    print(f"  Country analysis: {len(country_counts)} countries, {len(collab_counts)} collab types")
    for ct, pct in ntd_collab.items():
        print(f"    {ct}: {pct:.1f}% NTD focus")

    # Citation and OA analysis
    cite_oa = citation_oa_analysis(mapped_df, rai)
    print(f"  Citations: over-studied median={cite_oa['citation_over_median']:.0f}, under={cite_oa['citation_under_median']:.0f}, p={cite_oa['citation_p']:.3f}")
    print(f"  Open access: over-studied={cite_oa['oa_over_mean']:.1%}, under={cite_oa['oa_under_mean']:.1%}, p={cite_oa['oa_p']:.3f}")

    # NTD analysis
    ntd = ntd_analysis(cause_counts, gbd_dalys)
    print(f"  NTDs: {ntd['ntd_pubs']:.0f} papers ({ntd['ntd_pub_share']:.2f}%), attention ratio={ntd['ntd_attention_ratio']:.2f}")

    # Dose-response
    dose = dose_response_analysis(rai)
    print(f"  Dose-response: rho={dose['rho_pubs']:.3f} (p={dose['p_pubs']:.3f})")

    # --- Summary stats ---
    print(f"\n[analyse] Complete. Key results:")
    print(f"  Papers: {len(mapped_df):,}")
    print(f"  Mapped: {mapped_df['is_mapped'].sum():,} ({100*mapped_df['is_mapped'].mean():.1f}%)")
    print(f"  Diseases with RAI: {len(rai)}")
    print(f"  Median RAI: {rai['rai'].median():.3f}")
    print(f"  Outputs saved to {ANALYSIS_DIR}")


def _compare_general_medical(mapped_df, rai, gbd_dalys):
    """Compare AI research distribution with general medical research."""
    import requests

    output_path = ANALYSIS_DIR / "ai_vs_general_medical_research.csv"
    if output_path.exists():
        print("  [general] Already computed. Skipping API queries.")
        return

    DISEASE_SEARCHES = {
        "Breast cancer": "breast cancer", "Lung cancer": "lung cancer",
        "Stroke": "stroke", "Diabetes": "diabetes", "Alzheimer's": "alzheimer",
        "HIV/AIDS": "hiv", "Tuberculosis": "tuberculosis", "Malaria": "malaria",
        "Depression": "depression", "Heart failure": "heart failure",
        "Asthma": "asthma", "Chronic kidney disease": "chronic kidney",
        "Epilepsy": "epilepsy", "Parkinson's": "parkinson",
        "Colorectal cancer": "colorectal cancer", "Melanoma": "melanoma",
        "Liver cancer": "liver cancer", "Prostate cancer": "prostate cancer",
        "Stomach cancer": "gastric cancer", "Pancreatic cancer": "pancreatic cancer",
        "Sepsis": "sepsis", "COPD": "chronic obstructive pulmonary",
        "Pneumonia": "pneumonia", "Glaucoma": "glaucoma",
        "Anxiety": "anxiety disorder", "Schizophrenia": "schizophrenia",
        "Cervical cancer": "cervical cancer", "Ovarian cancer": "ovarian cancer",
        "Multiple sclerosis": "multiple sclerosis", "Osteoarthritis": "osteoarthritis",
        "IBD": "inflammatory bowel", "Thyroid cancer": "thyroid cancer",
        "Atrial fibrillation": "atrial fibrillation", "Meningitis": "meningitis",
        "Low back pain": "low back pain", "Road injuries": "road traffic",
        "Diarrhoeal diseases": "diarrhea|diarrhoea",
        "Iron deficiency": "iron deficiency", "Dengue": "dengue",
    }

    CONCEPT_TO_RAI = {
        "Breast cancer": "Breast cancer", "Lung cancer": "Tracheal, bronchus, and lung cancer",
        "Stroke": "Stroke", "Diabetes": "Diabetes mellitus",
        "Alzheimer's": "Alzheimer's disease and other dementias",
        "HIV/AIDS": "HIV/AIDS", "Tuberculosis": "Tuberculosis", "Malaria": "Malaria",
        "Depression": "Depressive disorders",
        "Heart failure": "Other cardiovascular and circulatory diseases",
        "Asthma": "Asthma", "Chronic kidney disease": "Chronic kidney disease",
        "Epilepsy": "Idiopathic epilepsy", "Parkinson's": "Parkinson's disease",
        "Colorectal cancer": "Colon and rectum cancer",
        "Melanoma": "Malignant skin melanoma", "Liver cancer": "Liver cancer",
        "Prostate cancer": "Prostate cancer", "Stomach cancer": "Stomach cancer",
        "Pancreatic cancer": "Pancreatic cancer", "Sepsis": "Sepsis",
        "COPD": "Chronic obstructive pulmonary disease",
        "Pneumonia": "Lower respiratory infections",
        "Glaucoma": "Blindness and vision loss",
        "Anxiety": "Anxiety disorders", "Schizophrenia": "Schizophrenia",
        "Cervical cancer": "Cervical cancer", "Ovarian cancer": "Ovarian cancer",
        "Multiple sclerosis": "Multiple sclerosis",
        "Osteoarthritis": "Osteoarthritis", "IBD": "Inflammatory bowel disease",
        "Thyroid cancer": "Thyroid cancer",
        "Atrial fibrillation": "Atrial fibrillation and flutter",
        "Meningitis": "Meningitis",
        "Low back pain": "Low back pain", "Road injuries": "Road injuries",
        "Diarrhoeal diseases": "Diarrheal diseases",
        "Iron deficiency": "Dietary iron deficiency", "Dengue": "Dengue",
    }

    BASE = "https://api.openalex.org/works"
    results = []
    for disease, search_term in DISEASE_SEARCHES.items():
        params = {
            "filter": f"title.search:{search_term},concepts.id:C71924100,type:article,publication_year:2015-2025",
            "per_page": 1,
            "mailto": "replication@example.com",
        }
        try:
            r = requests.get(BASE, params=params, timeout=15)
            if r.status_code == 429:
                print(f"  [general] Rate limited at {disease}. Try again later.")
                return
            data = r.json()
            count = data["meta"]["count"]
            results.append({"disease": disease, "general_med_pubs": count})
            time.sleep(0.3)
        except Exception as e:
            print(f"  [general] Error for {disease}: {e}")
            return

    gen_df = pd.DataFrame(results)
    gen_df["rai_name"] = gen_df["disease"].map(CONCEPT_TO_RAI)
    gen_df = gen_df.merge(rai[["cause_name", "pub_count", "dalys"]],
                          left_on="rai_name", right_on="cause_name", how="inner")
    gen_df.to_csv(output_path, index=False)
    print(f"  [general] Saved {len(gen_df)} disease comparisons")


def step_figures():
    """Step 4: Generate all publication figures."""
    from src.visualise.generate_figures import (
        load_data, figure1_bubble_plot, figure2_rai_bar, figure3_temporal,
        figure4_method_heatmap, figure5_ai_vs_general, figure6_sdi_comparison,
    )
    from src.visualise.style import set_lancet_style
    set_lancet_style()

    print("[figures] Loading data...")
    rai, yearly_corr, yearly_rai, ai_vs_gen, rai_low, rai_high = load_data()

    print("[figures] Generating figures...")
    figure1_bubble_plot(rai)
    figure2_rai_bar(rai)
    figure3_temporal(yearly_corr, yearly_rai)
    try:
        figure4_method_heatmap()
    except Exception as e:
        print(f"  [figures] Skipping heatmap (needs method classification): {e}")
    figure5_ai_vs_general(ai_vs_gen)
    figure6_sdi_comparison(rai, rai_low, rai_high)
    print(f"[figures] All figures saved to {FIG_DIR}")


def main():
    steps = sys.argv[1:] if len(sys.argv) > 1 else ["collect", "map", "analyse", "figures"]

    if "collect" in steps:
        step_collect()
    if "map" in steps:
        step_map()
    if "analyse" in steps:
        step_analyse()
    if "figures" in steps:
        step_figures()

    print("\n[pipeline] Complete.")


if __name__ == "__main__":
    main()
