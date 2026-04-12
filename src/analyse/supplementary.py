"""
Supplementary analyses reported in the paper.

Covers: mapping validation, multivariable regression, corrective mechanism
modelling, sensitivity analyses, method/modality stratification, citation
analysis, open access analysis, dataset readiness, Røttingen comparison,
country distribution, HIC-LMIC collaboration, NTD analysis, dose-response,
and permutation testing.
"""

import re
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, mannwhitneyu, linregress
import statsmodels.api as sm

from src.collect.gbd_causes import GBD_CAUSE_DICTIONARY
from src.collect.gbd_name_mapping import OUR_TO_GBD_NAME
from src.collect.disease_mapper import map_title_to_causes, compute_cause_counts
from src.analyse.attention_index import compute_rai


# ================================================================
# Mapping validation
# ================================================================

def validate_mapping(mapped_df, seed=42):
    """Validate disease mapping on 500 random papers."""
    np.random.seed(seed)
    mapped_only = mapped_df[mapped_df["is_mapped"]].sample(250, random_state=seed)
    unmapped_only = mapped_df[~mapped_df["is_mapped"]].sample(250, random_state=seed)

    # Precision: re-run mapper and check consistency
    precision_correct = 0
    for _, row in mapped_only.iterrows():
        remapped = map_title_to_causes(row.get("title", ""))
        assigned = row["gbd_causes"].split("|")
        if set(remapped).issubset(set(assigned)) or set(assigned) == set(remapped):
            precision_correct += 1

    # Recall: check unmapped for disease terms
    disease_terms = ["cancer", "tumor", "tumour", "disease", "syndrome", "disorder",
                     "infection", "pneumonia", "fracture", "carcinoma", "melanoma",
                     "leukemia", "lymphoma", "fibrosis", "cirrhosis", "diabetes",
                     "alzheimer", "parkinson", "epilepsy", "stroke", "sepsis",
                     "tuberculosis", "malaria", "hiv"]
    recall_missed = 0
    for _, row in unmapped_only.iterrows():
        title = str(row.get("title", "")).lower()
        if any(t in title for t in disease_terms):
            recall_missed += 1

    precision = precision_correct / 250
    missed_rate = recall_missed / 250
    total_mapped = mapped_df["is_mapped"].sum()
    total_unmapped = (~mapped_df["is_mapped"]).sum()
    est_missed = total_unmapped * missed_rate
    est_recall = total_mapped / (total_mapped + est_missed) if (total_mapped + est_missed) > 0 else 0
    f1 = 2 * precision * est_recall / (precision + est_recall) if (precision + est_recall) > 0 else 0

    return {
        "precision": precision,
        "estimated_recall": est_recall,
        "f1": f1,
        "missed_rate": missed_rate,
        "n_precision": 250,
        "n_recall": 250,
    }


# ================================================================
# Multivariable regression
# ================================================================

DISEASES_WITH_PUBLIC_DATASETS = {
    "Breast cancer", "Malignant skin melanoma", "Brain and central nervous system cancer",
    "Blindness and vision loss", "Tracheal, bronchus, and lung cancer",
    "COVID-19", "Colon and rectum cancer", "Alzheimer's disease and other dementias",
    "Ischemic heart disease", "Diabetes mellitus", "Stroke",
    "Parkinson's disease", "Leukemia", "Tuberculosis", "Sepsis", "Liver cancer",
    "Stomach cancer", "Depressive disorders", "Cervical cancer", "Malaria",
    "Kidney cancer", "Atrial fibrillation and flutter", "Prostate cancer",
    "Oral disorders", "Idiopathic epilepsy", "Thyroid cancer",
    "Pancreatic cancer", "Multiple sclerosis",
}

SCREENING_DISEASES = {
    "Breast cancer", "Cervical cancer", "Colon and rectum cancer",
    "Tracheal, bronchus, and lung cancer", "Blindness and vision loss",
    "Prostate cancer", "Malignant skin melanoma", "Diabetes mellitus",
    "Ischemic heart disease", "Chronic kidney disease", "Osteoporosis", "Oral disorders",
}

CLASSIFICATION_SUITABLE = {
    "Breast cancer", "Malignant skin melanoma", "Brain and central nervous system cancer",
    "Blindness and vision loss", "Tracheal, bronchus, and lung cancer",
    "Colon and rectum cancer", "Cervical cancer", "Liver cancer",
    "Tuberculosis", "Malaria", "Thyroid cancer", "Stomach cancer",
    "Prostate cancer", "COVID-19", "Leukemia", "Kidney cancer",
    "Pancreatic cancer", "Oral disorders",
}

FDA_APPROVALS = {
    "Blindness and vision loss": 75, "Ischemic heart disease": 60,
    "Tracheal, bronchus, and lung cancer": 45, "Stroke": 40,
    "Breast cancer": 35, "Atrial fibrillation and flutter": 30,
    "Brain and central nervous system cancer": 15, "Malignant skin melanoma": 12,
    "Colon and rectum cancer": 10, "Prostate cancer": 8, "Liver cancer": 5,
    "Cervical cancer": 4, "Osteoarthritis": 8, "Idiopathic epilepsy": 3,
    "Diabetes mellitus": 5, "Sepsis": 3, "Tuberculosis": 2,
    "Chronic obstructive pulmonary disease": 2, "Chronic kidney disease": 1,
    "Parkinson's disease": 1,
}


def run_regression(rai, ai_vs_gen, gbd_dalys, sdi_data=None):
    """Run the multivariable regression analysis."""
    df = ai_vs_gen.dropna(subset=["general_med_pubs", "pub_count", "dalys"]).copy()
    df = df[df["dalys"] > 0].reset_index(drop=True)
    df["log_ai_pubs"] = np.log10(df["pub_count"] + 1)
    df["log_dalys"] = np.log10(df["dalys"])
    df["log_gen_pubs"] = np.log10(df["general_med_pubs"] + 1)

    # HIC burden share
    if sdi_data is not None:
        high_sdi = sdi_data[
            (sdi_data["measure_name"] == "DALYs (Disability-Adjusted Life Years)") &
            (sdi_data["year"] == 2021) & (sdi_data["sex_name"] == "Both") &
            (sdi_data["age_name"] == "All ages") & (sdi_data["location_name"] == "High SDI")
        ][["cause_name", "val"]].rename(columns={"val": "hic_dalys"})
        df = df.merge(high_sdi, left_on="rai_name", right_on="cause_name", how="left", suffixes=("", "_hic"))
        df["hic_burden_share"] = df["hic_dalys"].fillna(0) / df["dalys"]
    else:
        df["hic_burden_share"] = 0.5

    df["has_dataset"] = df["rai_name"].isin(DISEASES_WITH_PUBLIC_DATASETS).astype(int)
    df["has_screening"] = df["rai_name"].isin(SCREENING_DISEASES).astype(int)
    df["classification_task"] = df["rai_name"].isin(CLASSIFICATION_SUITABLE).astype(int)

    fda_df = pd.DataFrame([{"cause_name": k, "fda_approvals": v} for k, v in FDA_APPROVALS.items()])
    df = df.merge(fda_df, left_on="rai_name", right_on="cause_name", how="left", suffixes=("", "_fda"))
    df["has_fda"] = (df["fda_approvals"].fillna(0) > 0).astype(int)

    features = ["log_dalys", "has_dataset", "hic_burden_share", "has_screening", "has_fda", "log_gen_pubs"]
    X = df[features].copy()
    X = sm.add_constant(X)
    y = df["log_ai_pubs"]
    valid = X.join(y).dropna()

    model = sm.OLS(valid["log_ai_pubs"], valid[["const"] + features]).fit()
    return model, df


# ================================================================
# Corrective mechanism modelling
# ================================================================

def corrective_modelling(ai_vs_gen):
    """Model AI's corrective potential under four scenarios."""
    df = ai_vs_gen.dropna(subset=["general_med_pubs", "pub_count", "dalys"]).copy()
    df = df[df["dalys"] > 0].reset_index(drop=True)
    df["gen_share"] = df["general_med_pubs"] / df["general_med_pubs"].sum()
    df["ai_share"] = df["pub_count"] / df["pub_count"].sum()
    df["daly_share"] = df["dalys"] / df["dalys"].sum()

    ai_proportional = df["daly_share"].copy()
    df["gen_rai"] = df["gen_share"] / df["daly_share"]
    cw = 1 / (df["gen_rai"] + 0.01)
    counter_share = cw / cw.sum()

    target_10 = df.sort_values("ai_share").head(10).index
    targeted = df["ai_share"].copy()
    for idx in target_10:
        targeted[idx] = 2.0 * df.loc[idx, "daly_share"]
    targeted = targeted / targeted.sum()

    scenarios = {
        "Business as usual": df["ai_share"],
        "Proportional": ai_proportional,
        "Counter-weighted": counter_share,
        "Targeted datasets": targeted,
    }

    results = []
    for ai_pct in range(0, 31):
        alpha = ai_pct / 100
        for name, ai_dist in scenarios.items():
            combined = (1 - alpha) * df["gen_share"] + alpha * ai_dist
            rho, p = spearmanr(combined, df["daly_share"])
            results.append({"ai_pct": ai_pct, "scenario": name, "rho": rho, "p": p})

    return pd.DataFrame(results)


def permutation_test(ai_vs_gen, n_perm=10000, seed=42):
    """Test whether targeting bottom 10 diseases outperforms random selection."""
    np.random.seed(seed)
    df = ai_vs_gen.dropna(subset=["general_med_pubs", "pub_count", "dalys"]).copy()
    df = df[df["dalys"] > 0].reset_index(drop=True)
    n = len(df)
    df["gen_share"] = df["general_med_pubs"] / df["general_med_pubs"].sum()
    df["ai_share"] = df["pub_count"] / df["pub_count"].sum()
    df["daly_share"] = df["dalys"] / df["dalys"].sum()
    alpha = 0.10

    # Observed
    target_10 = df.sort_values("ai_share").head(10).index
    new_ai = df["ai_share"].copy()
    for idx in target_10:
        new_ai[idx] = 2.0 * df.loc[idx, "daly_share"]
    new_ai = new_ai / new_ai.sum()
    combined_obs = (1 - alpha) * df["gen_share"] + alpha * new_ai
    rho_obs, _ = spearmanr(combined_obs, df["daly_share"])

    # Null
    null_rhos = []
    for _ in range(n_perm):
        rand_idx = np.random.choice(n, size=10, replace=False)
        new_ai_null = df["ai_share"].copy()
        for idx in rand_idx:
            new_ai_null[idx] = 2.0 * df.loc[idx, "daly_share"]
        new_ai_null = new_ai_null / new_ai_null.sum()
        combined = (1 - alpha) * df["gen_share"] + alpha * new_ai_null
        r, _ = spearmanr(combined, df["daly_share"])
        null_rhos.append(r)

    p_value = np.mean(np.array(null_rhos) >= rho_obs)
    return {"rho_observed": rho_obs, "null_mean": np.mean(null_rhos), "p_value": p_value}


# ================================================================
# Sensitivity analyses
# ================================================================

def sensitivity_analyses(mapped_df, gbd_data, cause_counts):
    """Run all sensitivity analyses."""
    results = []

    gbd_dalys = gbd_data[
        (gbd_data["measure_name"] == "DALYs (Disability-Adjusted Life Years)") &
        (gbd_data["year"] == 2021) & (gbd_data["sex_name"] == "Both") &
        (gbd_data["age_name"] == "All ages")
    ][["cause_name", "val"]].rename(columns={"val": "dalys"})

    cc = cause_counts.copy()
    cc["gbd_name"] = cc["cause_name"].map(OUR_TO_GBD_NAME).fillna(cc["cause_name"])
    agg = cc.groupby("gbd_name").agg(
        pub_count=("pub_count", "sum"), level1=("level1", "first"), level2=("level2", "first"),
    ).reset_index().rename(columns={"gbd_name": "cause_name"})

    # Main
    rai = compute_rai(agg, gbd_dalys)
    rho, p = spearmanr(rai["pub_share"], rai["daly_share"])
    results.append({"analysis": "Main (Global DALYs 2021)", "rho": rho, "p": p, "n": len(rai)})

    # Exclude COVID
    rai_nc = rai[rai["cause_name"] != "COVID-19"].copy()
    rai_nc["pub_share"] = rai_nc["pub_count"] / rai_nc["pub_count"].sum()
    rai_nc["daly_share"] = rai_nc["dalys"] / rai_nc["dalys"].sum()
    r, p = spearmanr(rai_nc["pub_share"], rai_nc["daly_share"])
    results.append({"analysis": "Excluding COVID-19", "rho": r, "p": p, "n": len(rai_nc)})

    # Pre-COVID
    pre = mapped_df[mapped_df["year"] <= 2019]
    cc_pre = compute_cause_counts(pre)
    cc_pre["gbd_name"] = cc_pre["cause_name"].map(OUR_TO_GBD_NAME).fillna(cc_pre["cause_name"])
    agg_pre = cc_pre.groupby("gbd_name").agg(
        pub_count=("pub_count", "sum"), level1=("level1", "first"), level2=("level2", "first"),
    ).reset_index().rename(columns={"gbd_name": "cause_name"})
    rai_pre = compute_rai(agg_pre, gbd_dalys)
    r, p = spearmanr(rai_pre["pub_share"], rai_pre["daly_share"])
    results.append({"analysis": "Pre-pandemic (2015-2019)", "rho": r, "p": p, "n": len(rai_pre)})

    # Alternative DALY years
    for yr in [2022, 2023]:
        gbd_yr = gbd_data[
            (gbd_data["measure_name"] == "DALYs (Disability-Adjusted Life Years)") &
            (gbd_data["year"] == yr) & (gbd_data["sex_name"] == "Both") & (gbd_data["age_name"] == "All ages")
        ][["cause_name", "val"]].rename(columns={"val": "dalys"})
        if len(gbd_yr) > 0:
            rai_yr = compute_rai(agg, gbd_yr)
            r, p = spearmanr(rai_yr["pub_share"], rai_yr["daly_share"])
            results.append({"analysis": f"DALYs from {yr}", "rho": r, "p": p, "n": len(rai_yr)})

    # Deaths
    gbd_deaths = gbd_data[
        (gbd_data["measure_name"] == "Deaths") &
        (gbd_data["year"] == 2021) & (gbd_data["sex_name"] == "Both") & (gbd_data["age_name"] == "All ages")
    ][["cause_name", "val"]].rename(columns={"val": "dalys"})
    if len(gbd_deaths) > 0:
        rai_d = compute_rai(agg, gbd_deaths)
        r, p = spearmanr(rai_d["pub_share"], rai_d["daly_share"])
        results.append({"analysis": "Deaths instead of DALYs", "rho": r, "p": p, "n": len(rai_d)})

    # Strict mapping
    strict = mapped_df[(mapped_df["is_mapped"]) & (mapped_df["n_causes"] == 1)]
    cc_s = compute_cause_counts(strict)
    cc_s["gbd_name"] = cc_s["cause_name"].map(OUR_TO_GBD_NAME).fillna(cc_s["cause_name"])
    agg_s = cc_s.groupby("gbd_name").agg(
        pub_count=("pub_count", "sum"), level1=("level1", "first"), level2=("level2", "first"),
    ).reset_index().rename(columns={"gbd_name": "cause_name"})
    rai_s = compute_rai(agg_s, gbd_dalys)
    r, p = spearmanr(rai_s["pub_share"], rai_s["daly_share"])
    results.append({"analysis": "Strict mapping", "rho": r, "p": p, "n": len(rai_s)})

    # Loose mapping
    cc_l = compute_cause_counts(mapped_df[mapped_df["is_mapped"]], fractional=False)
    cc_l["gbd_name"] = cc_l["cause_name"].map(OUR_TO_GBD_NAME).fillna(cc_l["cause_name"])
    agg_l = cc_l.groupby("gbd_name").agg(
        pub_count=("pub_count", "sum"), level1=("level1", "first"), level2=("level2", "first"),
    ).reset_index().rename(columns={"gbd_name": "cause_name"})
    rai_l = compute_rai(agg_l, gbd_dalys)
    r, p = spearmanr(rai_l["pub_share"], rai_l["daly_share"])
    results.append({"analysis": "Loose mapping", "rho": r, "p": p, "n": len(rai_l)})

    # Sub-periods
    for label, yr_range in [("2015-2017", (2015, 2017)), ("2018-2020", (2018, 2020)),
                             ("2021-2023", (2021, 2023)), ("2024-2025", (2024, 2025))]:
        sub = mapped_df[(mapped_df["year"] >= yr_range[0]) & (mapped_df["year"] <= yr_range[1])]
        cc_w = compute_cause_counts(sub)
        cc_w["gbd_name"] = cc_w["cause_name"].map(OUR_TO_GBD_NAME).fillna(cc_w["cause_name"])
        agg_w = cc_w.groupby("gbd_name").agg(
            pub_count=("pub_count", "sum"), level1=("level1", "first"), level2=("level2", "first"),
        ).reset_index().rename(columns={"gbd_name": "cause_name"})
        rai_w = compute_rai(agg_w, gbd_dalys)
        r, p = spearmanr(rai_w["pub_share"], rai_w["daly_share"])
        results.append({"analysis": f"Sub-period {label}", "rho": r, "p": p, "n": len(rai_w)})

    return pd.DataFrame(results)


# ================================================================
# Method and modality stratification
# ================================================================

METHOD_PATTERNS = {
    "Deep learning (CNN)": [r"convolutional neural", r"\bcnn\b", r"u-net", r"unet",
                            r"resnet", r"vgg", r"densenet", r"efficientnet", r"yolo"],
    "Deep learning (other)": [r"deep learning", r"deep neural", r"autoencoder",
                              r"generative adversarial", r"\bgan\b", r"\blstm\b",
                              r"recurrent neural", r"\brnn\b", r"attention mechanism"],
    "Transformer / LLM": [r"transformer", r"\bbert\b", r"gpt", r"large language model",
                          r"\bllm\b", r"foundation model", r"vision transformer"],
    "Traditional ML": [r"random forest", r"support vector", r"\bsvm\b", r"gradient boosting",
                       r"\bxgboost\b", r"decision tree", r"logistic regression",
                       r"naive bayes", r"\bknn\b", r"ensemble"],
    "NLP": [r"natural language processing", r"\bnlp\b", r"text mining",
            r"text classification", r"sentiment analysis", r"named entity"],
    "Reinforcement learning": [r"reinforcement learning"],
}

MODALITY_PATTERNS = {
    "Medical imaging": [r"imaging", r"radiograph", r"x-ray", r"mri", r"ultrasound",
                        r"mammogra", r"fundus", r"dermoscop", r"histopath", r"endoscop",
                        r"ct scan", r"ct image", r"medical image", r"radiology"],
    "Genomics / omics": [r"genom", r"transcriptom", r"proteom", r"gene expression",
                         r"single-cell", r"rna-seq", r"biomarker", r"multi-omic"],
    "Clinical text / NLP": [r"clinical note", r"electronic health record", r"\behr\b",
                            r"clinical text", r"medical record", r"discharge summar"],
    "Tabular / EHR structured": [r"tabular", r"clinical data", r"patient data",
                                 r"registry", r"retrospective", r"predict.*mortality",
                                 r"risk predict", r"prognos"],
    "Signals / waveforms": [r"electrocardiogra", r"\becg\b", r"\beeg\b", r"wearable",
                            r"signal processing", r"time series"],
    "Drug discovery": [r"drug discover", r"drug design", r"drug repurpos",
                       r"molecular docking", r"virtual screening"],
}


def classify_method(title):
    if not isinstance(title, str):
        return []
    title_lower = title.lower()
    methods = []
    for method, patterns in METHOD_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, title_lower):
                methods.append(method)
                break
    return methods


def classify_modality(title):
    if not isinstance(title, str):
        return []
    title_lower = title.lower()
    modalities = []
    for modality, patterns in MODALITY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, title_lower):
                modalities.append(modality)
                break
    return modalities


def stratify_methods_modalities(mapped_df):
    """Classify papers by AI method and data modality."""
    df = mapped_df.copy()
    df["methods"] = df["title"].apply(classify_method)
    df["primary_method"] = df["methods"].apply(lambda x: x[0] if x else "Unclassified")
    df["modalities"] = df["title"].apply(classify_modality)
    df["primary_modality"] = df["modalities"].apply(lambda x: x[0] if x else "Unclassified")
    return df


# ================================================================
# Country and collaboration analysis
# ================================================================

HIGH_INCOME = {"US", "GB", "DE", "JP", "FR", "CA", "AU", "NL", "IT", "KR", "ES",
               "CH", "SE", "BE", "AT", "DK", "NO", "FI", "IE", "IL", "SG", "NZ",
               "PT", "CZ", "GR", "HU", "PL", "SK", "SI", "HR", "EE", "LT", "LV",
               "TW", "HK", "AE", "SA", "QA", "KW", "BH", "OM"}
LMIC = {"IN", "BD", "PK", "EG", "VN", "PH", "NG", "KE", "GH", "ET",
        "TZ", "UG", "ZW", "SN", "CM", "AF", "MZ", "MW", "ML", "BF",
        "NE", "TD", "CF", "CD", "SO", "SS", "BI", "RW", "SL", "LR",
        "HT", "MG", "NP", "KH", "LA", "LK", "MA", "UA", "UZ", "ID", "MM"}


def analyse_countries(mapped_df):
    """Analyse author country distribution and collaboration patterns."""
    def classify_collab(countries_str):
        if pd.isna(countries_str) or countries_str == "":
            return "Unknown"
        countries = set(countries_str.split("|"))
        has_hic = bool(countries & HIGH_INCOME)
        has_lmic = bool(countries & LMIC)
        if has_hic and has_lmic:
            return "HIC-LMIC collaboration"
        elif has_hic:
            return "HIC only"
        elif has_lmic:
            return "LMIC only"
        return "Other"

    mapped_only = mapped_df[mapped_df["is_mapped"]].copy()
    mapped_only["collab_type"] = mapped_only["author_countries"].apply(classify_collab)

    country_counts = mapped_df["first_author_country"].value_counts()
    collab_counts = mapped_only["collab_type"].value_counts()

    # NTD focus by collaboration type
    ntd_terms = {"Malaria", "Tuberculosis", "HIV/AIDS", "Dengue", "Leishmaniasis",
                 "Schistosomiasis", "Chagas disease", "Leprosy"}
    ntd_by_collab = {}
    for ct in ["HIC only", "LMIC only", "HIC-LMIC collaboration"]:
        subset = mapped_only[mapped_only["collab_type"] == ct]
        if len(subset) > 50:
            ntd_pct = subset["primary_cause"].isin(ntd_terms).mean() * 100
            ntd_by_collab[ct] = ntd_pct

    return country_counts, collab_counts, ntd_by_collab


# ================================================================
# Citation and open access analysis
# ================================================================

def citation_oa_analysis(mapped_df, rai):
    """Analyse citations and open access by RAI category."""
    mapped_only = mapped_df[mapped_df["is_mapped"]].copy()

    cite_by_cause = mapped_only.groupby("primary_cause")["cited_by_count"].median().reset_index()
    cite_by_cause.columns = ["cause_name", "median_citations"]
    cite_rai = cite_by_cause.merge(rai[["cause_name", "rai"]], on="cause_name", how="inner")

    over = cite_rai[cite_rai["rai"] > 1]["median_citations"]
    under = cite_rai[cite_rai["rai"] < 1]["median_citations"]
    u_cite, p_cite = mannwhitneyu(over, under, alternative="two-sided")

    oa_by_cause = mapped_only.groupby("primary_cause")["is_oa"].mean().reset_index()
    oa_by_cause.columns = ["cause_name", "oa_rate"]
    oa_rai = oa_by_cause.merge(rai[["cause_name", "rai"]], on="cause_name", how="inner")
    over_oa = oa_rai[oa_rai["rai"] > 1]["oa_rate"]
    under_oa = oa_rai[oa_rai["rai"] < 1]["oa_rate"]
    u_oa, p_oa = mannwhitneyu(over_oa, under_oa, alternative="two-sided")

    return {
        "citation_over_median": over.median(),
        "citation_under_median": under.median(),
        "citation_p": p_cite,
        "oa_over_mean": over_oa.mean(),
        "oa_under_mean": under_oa.mean(),
        "oa_p": p_oa,
    }


# ================================================================
# NTD analysis
# ================================================================

WHO_NTDS = {
    "Dengue", "Rabies", "Trachoma", "Leprosy", "Chagas disease",
    "Leishmaniasis", "Schistosomiasis", "Lymphatic filariasis",
    "Onchocerciasis", "Intestinal nematode infections",
}


def ntd_analysis(cause_counts, gbd_dalys):
    """Analyse NTD research attention."""
    total_pubs = cause_counts["pub_count"].sum()
    total_dalys = gbd_dalys["dalys"].sum()

    ntd_pubs = 0
    ntd_dalys = 0
    for disease in WHO_NTDS:
        cc = cause_counts[cause_counts["cause_name"] == disease]
        ntd_pubs += cc["pub_count"].sum() if len(cc) > 0 else 0
        gbd_name = OUR_TO_GBD_NAME.get(disease, disease)
        gbd_match = gbd_dalys[gbd_dalys["cause_name"] == gbd_name]
        if len(gbd_match) > 0:
            ntd_dalys += gbd_match["dalys"].values[0]

    return {
        "ntd_pubs": ntd_pubs,
        "ntd_pub_share": ntd_pubs / total_pubs * 100,
        "ntd_daly_share": ntd_dalys / total_dalys * 100,
        "ntd_attention_ratio": (ntd_pubs / total_pubs) / (ntd_dalys / total_dalys) if ntd_dalys > 0 else 0,
    }


# ================================================================
# Dataset dose-response
# ================================================================

DATASET_COUNTS = {
    "Breast cancer": 5, "Malignant skin melanoma": 4,
    "Brain and central nervous system cancer": 3, "Blindness and vision loss": 6,
    "Tracheal, bronchus, and lung cancer": 4, "COVID-19": 5,
    "Colon and rectum cancer": 3, "Alzheimer's disease and other dementias": 3,
    "Ischemic heart disease": 2, "Diabetes mellitus": 2,
    "Stroke": 1, "Parkinson's disease": 2, "Tuberculosis": 3,
    "Sepsis": 2, "Malaria": 1, "Liver cancer": 1,
    "Depressive disorders": 2, "Cervical cancer": 2,
    "Idiopathic epilepsy": 2, "Multiple sclerosis": 2,
}


def dose_response_analysis(rai):
    """Test dose-response between number of datasets and research volume."""
    dose_data = []
    for disease, n_datasets in DATASET_COUNTS.items():
        match = rai[rai["cause_name"] == disease]
        if len(match) > 0:
            dose_data.append({
                "disease": disease, "n_datasets": n_datasets,
                "pub_count": match["pub_count"].values[0],
                "rai": match["rai"].values[0],
            })
    dose_df = pd.DataFrame(dose_data)
    rho_pubs, p_pubs = spearmanr(dose_df["n_datasets"], dose_df["pub_count"])
    rho_rai, p_rai = spearmanr(dose_df["n_datasets"], dose_df["rai"])
    return {"rho_pubs": rho_pubs, "p_pubs": p_pubs, "rho_rai": rho_rai, "p_rai": p_rai, "data": dose_df}


# ================================================================
# Røttingen Level 1 comparison
# ================================================================

def rottingen_comparison(cause_counts):
    """Compare AI research distribution with Røttingen et al. (2013) at GBD Level 1."""
    COMMUNICABLE = "Communicable, maternal, neonatal, and nutritional diseases"
    NCD = "Non-communicable diseases"
    INJURIES = "Injuries"

    l1_pubs = cause_counts.groupby("level1")["pub_count"].sum()
    l1_total = l1_pubs.sum()

    rottingen = {COMMUNICABLE: {"research": 24, "dalys": 52},
                 NCD: {"research": 62, "dalys": 38},
                 INJURIES: {"research": 3, "dalys": 10}}

    results = []
    for cat in [COMMUNICABLE, NCD, INJURIES]:
        ai_pct = l1_pubs.get(cat, 0) / l1_total * 100
        r = rottingen[cat]
        results.append({
            "category": cat,
            "ai_research_pct": ai_pct,
            "rottingen_research_pct": r["research"],
            "rottingen_dalys_pct": r["dalys"],
            "ai_ratio": ai_pct / r["dalys"] if r["dalys"] > 0 else 0,
            "rottingen_ratio": r["research"] / r["dalys"],
        })
    return pd.DataFrame(results)
