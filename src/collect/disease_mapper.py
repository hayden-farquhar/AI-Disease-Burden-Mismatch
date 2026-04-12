"""
Disease mapper: assign OpenAlex publications to GBD Level 3 causes.

Strategy:
1. Exclude non-medical papers (plant, animal, veterinary)
2. Primary: keyword matching against paper titles using the GBD cause dictionary
3. Supplementary: contextual matching for generic terms (e.g., "kidney" + "cancer")
4. Multi-disease papers get fractional credit (1/N for N matched diseases)
5. Papers not matching any cause are tagged as "unmapped"
"""

import json
import re

import pandas as pd

from src.collect.gbd_causes import GBD_CAUSE_DICTIONARY, get_all_search_terms_flat

# Titles containing these terms are excluded (not human medical research)
EXCLUSION_PATTERNS = [
    r"\bplant\b.*\bdisease\b", r"\bplant\b.*\bdetection\b",
    r"\bleaf\b.*\bdisease\b", r"\bcrop\b.*\bdisease\b",
    r"\btomato\b", r"\bwheat\b", r"\brice\b.*\bdisease\b",
    r"\bveterinar", r"\bbovine\b", r"\bcanine\b", r"\bfeline\b",
    r"\bporcine\b", r"\bpoultry\b", r"\blivestock\b",
    r"\bfish\b.*\bdisease\b", r"\baquaculture\b",
]

# Contextual rules: when a generic organ term appears with "cancer", "tumor",
# "carcinoma", or "neoplasm", map to the corresponding GBD cancer cause.
ORGAN_CANCER_MAP = {
    r"\bkidney\b|\brenal\b": "Kidney cancer",
    r"\bbladder\b|\burothelial\b": "Bladder cancer",
    r"\bpancrea": "Pancreatic cancer",
    r"\bovari": "Ovarian cancer",
    r"\buteri|\bendometri": "Uterine cancer",
    r"\bthyroid\b": "Thyroid cancer",
    r"\btesticular\b|\btestis\b": "Testicular cancer",
    r"\bnasopharyng": "Nasopharynx cancer",
    r"\blaryn": "Larynx cancer",
    r"\bgallbladder\b|\bbiliar|\bcholangiocarcinoma": "Gallbladder and biliary tract cancer",
    r"\bmesothelioma": "Mesothelioma",
    r"\bmyeloma\b": "Multiple myeloma",
    r"\besophag|\boesophag": "Oesophageal cancer",
    r"\bsalivar": "Lip and oral cavity cancer",
    r"\bhead and neck\b": "Lip and oral cavity cancer",
}

# Additional synonym rules that supplement the main dictionary.
# These catch generic terms the dictionary misses.
EXTRA_SYNONYMS = {
    "Ischaemic heart disease": [
        r"\bcardiovascular disease\b", r"\bheart disease\b",
        r"\bcardiac disease\b", r"\bcoronary\b",
    ],
    "Atrial fibrillation and flutter": [
        r"\barrhythmia\b", r"\batrial\b",
    ],
    "Falls": [
        r"\bfracture\b", r"\bosteoporotic\b.*\bfracture\b",
        r"\bhip fracture\b",
    ],
    "Colon and rectum cancer": [
        r"\bpolyp\b.*\b(?:colon|rect|colorect|bowel|colonoscop)\b",
        r"\b(?:colon|rect|colorect|bowel|colonoscop)\b.*\bpolyp\b",
        r"\bpolyp detection\b", r"\bpolyp segmentation\b",
    ],
    "Aortic aneurysm": [
        r"\baneurysm\b",
    ],
    "Chronic obstructive pulmonary disease": [
        r"\blung disease\b", r"\bpulmonary disease\b",
    ],
    "Cirrhosis and other chronic liver diseases": [
        r"\bliver disease\b",
    ],
    "Epilepsy": [
        r"\bepileptic\b",
    ],
    "Chronic kidney disease": [
        r"\bkidney disease\b", r"\brenal disease\b",
    ],
    "Malignant skin melanoma": [
        r"\bskin disease\b", r"\bskin disorder\b",
    ],
}


def _is_excluded(title_lower: str) -> bool:
    """Check if title matches non-medical exclusion patterns."""
    for pattern in EXCLUSION_PATTERNS:
        if re.search(pattern, title_lower):
            return True
    return False


def _match_organ_cancer(title_lower: str) -> set[str]:
    """Match generic cancer/tumor terms with organ context."""
    if not re.search(r"\bcancer\b|\btumor\b|\btumour\b|\bcarcinoma\b|\bneoplasm\b|\bmalignan", title_lower):
        return set()
    matched = set()
    for organ_pattern, cause in ORGAN_CANCER_MAP.items():
        if re.search(organ_pattern, title_lower):
            matched.add(cause)
    return matched


def _match_extra_synonyms(title_lower: str) -> set[str]:
    """Match additional synonym patterns."""
    matched = set()
    for cause, patterns in EXTRA_SYNONYMS.items():
        for pattern in patterns:
            if re.search(pattern, title_lower):
                matched.add(cause)
                break
    return matched


def map_title_to_causes(title: str) -> list[str]:
    """Map a paper title to GBD cause(s) via keyword matching.

    Returns list of matched GBD cause names (may be empty).
    """
    if not title:
        return []

    title_lower = title.lower()

    # Exclude non-medical papers
    if _is_excluded(title_lower):
        return []

    matched_causes = set()

    # Primary: dictionary-based matching
    for cause_name, info in GBD_CAUSE_DICTIONARY.items():
        for term in info["search_terms"]:
            if len(term) <= 3:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, title_lower):
                    matched_causes.add(cause_name)
                    break
            else:
                if term.lower() in title_lower:
                    matched_causes.add(cause_name)
                    break

    # Supplementary: organ-cancer contextual matching
    matched_causes |= _match_organ_cancer(title_lower)

    # Supplementary: extra synonym matching
    matched_causes |= _match_extra_synonyms(title_lower)

    return sorted(matched_causes)


def map_concepts_to_causes(concepts_json: str) -> list[str]:
    """Map OpenAlex concept tags to GBD causes.

    Uses concept display_names matched against the cause dictionary.
    Only considers concepts with score >= 0.3 (reasonably confident).
    """
    try:
        concepts = json.loads(concepts_json) if isinstance(concepts_json, str) else concepts_json
    except (json.JSONDecodeError, TypeError):
        return []

    matched_causes = set()
    term_to_cause = get_all_search_terms_flat()

    for concept in concepts:
        score = concept.get("score", 0)
        if score < 0.3:
            continue
        name = concept.get("name", "").lower()
        # Check if concept name matches any search term
        for term, cause in term_to_cause.items():
            if term in name or name in term:
                matched_causes.add(cause)

    return sorted(matched_causes)


def map_paper_to_causes(row: pd.Series) -> list[str]:
    """Map a single paper (DataFrame row) to GBD causes.

    Uses title-based matching only. Concept-based matching was found to
    produce excessive false positives due to substring matching issues
    (e.g., "uti" in "convolutional", "cancer" matching all cancer types).
    Title-based matching is more defensible: if a disease appears in the
    title, it is almost certainly a focus of the paper.
    """
    return map_title_to_causes(row.get("title", ""))


def map_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add disease mapping columns to a publications DataFrame.

    Adds columns:
    - gbd_causes: pipe-separated list of matched GBD causes
    - n_causes: number of matched causes
    - fractional_weight: 1/n_causes (for fractional counting)
    - is_mapped: whether at least one cause was matched
    - primary_cause: first matched cause (for single-assignment analyses)
    """
    results = []
    for _, row in df.iterrows():
        causes = map_paper_to_causes(row)
        results.append({
            "gbd_causes": "|".join(causes) if causes else "",
            "n_causes": len(causes),
            "fractional_weight": 1.0 / len(causes) if causes else 0.0,
            "is_mapped": len(causes) > 0,
            "primary_cause": causes[0] if causes else "",
        })

    mapping_df = pd.DataFrame(results)
    return pd.concat([df.reset_index(drop=True), mapping_df], axis=1)


def compute_cause_counts(df: pd.DataFrame, fractional: bool = True) -> pd.DataFrame:
    """Compute publication counts by GBD cause.

    Args:
        df: DataFrame with disease mapping columns (from map_dataframe)
        fractional: if True, use fractional weights for multi-disease papers

    Returns:
        DataFrame with cause_name, pub_count, and hierarchy info
    """
    mapped = df[df["is_mapped"]].copy()

    cause_counts = {}
    for _, row in mapped.iterrows():
        causes = row["gbd_causes"].split("|")
        weight = row["fractional_weight"] if fractional else 1.0
        for cause in causes:
            if cause:
                cause_counts[cause] = cause_counts.get(cause, 0) + weight

    rows = []
    for cause_name, count in cause_counts.items():
        info = GBD_CAUSE_DICTIONARY.get(cause_name, {})
        rows.append({
            "cause_name": cause_name,
            "pub_count": count,
            "level2": info.get("level2", ""),
            "level1": info.get("level1", ""),
        })

    result = pd.DataFrame(rows).sort_values("pub_count", ascending=False)
    result["pub_share"] = result["pub_count"] / result["pub_count"].sum()
    return result.reset_index(drop=True)


if __name__ == "__main__":
    # Quick test with some example titles
    test_titles = [
        "Deep learning for breast cancer detection in mammography",
        "Machine learning prediction of sepsis in the ICU",
        "Neural network-based diagnosis of diabetic retinopathy and glaucoma",
        "AI-driven drug discovery using random forest models",
        "Convolutional neural network for COVID-19 detection from chest CT",
        "Natural language processing for clinical depression screening",
        "Deep learning for malaria parasite detection in blood smears",
        "Machine learning approach to Alzheimer's disease classification using MRI",
        "Support vector machine for tuberculosis screening in chest X-rays",
        "Transformer model for protein structure prediction",
    ]

    print("Disease mapping test:")
    print("=" * 80)
    for title in test_titles:
        causes = map_title_to_causes(title)
        status = ", ".join(causes) if causes else "[UNMAPPED]"
        print(f"  {title[:65]:<65} → {status}")
