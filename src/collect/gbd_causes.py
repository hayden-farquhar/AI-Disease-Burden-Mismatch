"""
GBD Level 3 cause-term dictionary for mapping publications to diseases.

Each entry maps a GBD cause name to:
  - search_terms: keywords to match in paper titles/concepts (case-insensitive)
  - level2: GBD Level 2 parent category
  - level1: GBD Level 1 parent (Communicable/NCD/Injuries)

This dictionary covers the ~170 most important GBD Level 3 causes
(those contributing ≥0.01% of global DALYs). Terms are designed to be
specific enough to avoid false positives while catching common synonyms
used in the AI/ML literature.
"""

# Level 1 categories
COMMUNICABLE = "Communicable, maternal, neonatal, and nutritional diseases"
NCD = "Non-communicable diseases"
INJURIES = "Injuries"

GBD_CAUSE_DICTIONARY = {
    # =========================================================================
    # COMMUNICABLE, MATERNAL, NEONATAL, AND NUTRITIONAL DISEASES
    # =========================================================================

    # --- HIV/AIDS and STIs ---
    "HIV/AIDS": {
        "search_terms": ["hiv", "human immunodeficiency virus", "aids", "antiretroviral"],
        "level2": "HIV/AIDS and sexually transmitted infections",
        "level1": COMMUNICABLE,
    },
    "Sexually transmitted infections excluding HIV": {
        "search_terms": ["sexually transmitted", "syphilis", "gonorrhea", "gonorrhoea",
                         "chlamydia", "herpes simplex", "trichomoniasis"],
        "level2": "HIV/AIDS and sexually transmitted infections",
        "level1": COMMUNICABLE,
    },

    # --- Respiratory infections ---
    "Tuberculosis": {
        "search_terms": ["tuberculosis", "mycobacterium tuberculosis", "tb screening",
                         "tb detection", "tb diagnosis"],
        "level2": "Respiratory infections and tuberculosis",
        "level1": COMMUNICABLE,
    },
    "Lower respiratory infections": {
        "search_terms": ["pneumonia", "lower respiratory infection", "bronchiolitis",
                         "respiratory syncytial virus", "rsv"],
        "level2": "Respiratory infections and tuberculosis",
        "level1": COMMUNICABLE,
    },
    "Upper respiratory infections": {
        "search_terms": ["upper respiratory infection", "pharyngitis", "sinusitis",
                         "common cold"],
        "level2": "Respiratory infections and tuberculosis",
        "level1": COMMUNICABLE,
    },
    "COVID-19": {
        "search_terms": ["covid", "sars-cov-2", "coronavirus disease 2019",
                         "covid-19", "coronavirus pandemic"],
        "level2": "Respiratory infections and tuberculosis",
        "level1": COMMUNICABLE,
    },

    # --- Enteric infections ---
    "Diarrhoeal diseases": {
        "search_terms": ["diarrhea", "diarrhoea", "diarrhoeal", "rotavirus",
                         "cholera", "shigella", "gastroenteritis"],
        "level2": "Enteric infections",
        "level1": COMMUNICABLE,
    },
    "Typhoid and paratyphoid": {
        "search_terms": ["typhoid", "paratyphoid", "salmonella typhi"],
        "level2": "Enteric infections",
        "level1": COMMUNICABLE,
    },

    # --- Neglected tropical diseases ---
    "Malaria": {
        "search_terms": ["malaria", "plasmodium", "falciparum", "anopheles"],
        "level2": "Neglected tropical diseases and malaria",
        "level1": COMMUNICABLE,
    },
    "Chagas disease": {
        "search_terms": ["chagas", "trypanosoma cruzi"],
        "level2": "Neglected tropical diseases and malaria",
        "level1": COMMUNICABLE,
    },
    "Leishmaniasis": {
        "search_terms": ["leishmaniasis", "leishmania", "kala-azar"],
        "level2": "Neglected tropical diseases and malaria",
        "level1": COMMUNICABLE,
    },
    "Schistosomiasis": {
        "search_terms": ["schistosomiasis", "schistosoma", "bilharzia"],
        "level2": "Neglected tropical diseases and malaria",
        "level1": COMMUNICABLE,
    },
    "Dengue": {
        "search_terms": ["dengue"],
        "level2": "Neglected tropical diseases and malaria",
        "level1": COMMUNICABLE,
    },
    "Rabies": {
        "search_terms": ["rabies"],
        "level2": "Neglected tropical diseases and malaria",
        "level1": COMMUNICABLE,
    },
    "Intestinal nematode infections": {
        "search_terms": ["hookworm", "ascariasis", "trichuriasis", "intestinal nematode",
                         "soil-transmitted helminth"],
        "level2": "Neglected tropical diseases and malaria",
        "level1": COMMUNICABLE,
    },
    "Lymphatic filariasis": {
        "search_terms": ["lymphatic filariasis", "elephantiasis"],
        "level2": "Neglected tropical diseases and malaria",
        "level1": COMMUNICABLE,
    },
    "Onchocerciasis": {
        "search_terms": ["onchocerciasis", "river blindness"],
        "level2": "Neglected tropical diseases and malaria",
        "level1": COMMUNICABLE,
    },
    "Trachoma": {
        "search_terms": ["trachoma"],
        "level2": "Neglected tropical diseases and malaria",
        "level1": COMMUNICABLE,
    },
    "Leprosy": {
        "search_terms": ["leprosy", "hansen disease", "mycobacterium leprae"],
        "level2": "Neglected tropical diseases and malaria",
        "level1": COMMUNICABLE,
    },

    # --- Other infectious diseases ---
    "Meningitis": {
        "search_terms": ["meningitis", "meningococcal"],
        "level2": "Other infectious diseases",
        "level1": COMMUNICABLE,
    },
    "Encephalitis": {
        "search_terms": ["encephalitis"],
        "level2": "Other infectious diseases",
        "level1": COMMUNICABLE,
    },
    "Hepatitis B": {
        "search_terms": ["hepatitis b", "hbv"],
        "level2": "Other infectious diseases",
        "level1": COMMUNICABLE,
    },
    "Hepatitis C": {
        "search_terms": ["hepatitis c", "hcv"],
        "level2": "Other infectious diseases",
        "level1": COMMUNICABLE,
    },

    # --- Maternal and neonatal ---
    "Maternal disorders": {
        "search_terms": ["maternal mortality", "maternal health", "preeclampsia",
                         "eclampsia", "obstetric", "postpartum hemorrhage",
                         "maternal sepsis"],
        "level2": "Maternal and neonatal disorders",
        "level1": COMMUNICABLE,
    },
    "Neonatal disorders": {
        "search_terms": ["neonatal", "preterm birth", "birth asphyxia",
                         "neonatal sepsis", "neonatal encephalopathy",
                         "low birth weight", "newborn"],
        "level2": "Maternal and neonatal disorders",
        "level1": COMMUNICABLE,
    },

    # --- Nutritional deficiencies ---
    "Protein-energy malnutrition": {
        "search_terms": ["malnutrition", "wasting", "stunting", "kwashiorkor",
                         "marasmus", "undernutrition"],
        "level2": "Nutritional deficiencies",
        "level1": COMMUNICABLE,
    },
    "Iron-deficiency anaemia": {
        "search_terms": ["iron deficiency", "iron-deficiency anaemia",
                         "iron-deficiency anemia"],
        "level2": "Nutritional deficiencies",
        "level1": COMMUNICABLE,
    },
    "Vitamin A deficiency": {
        "search_terms": ["vitamin a deficiency"],
        "level2": "Nutritional deficiencies",
        "level1": COMMUNICABLE,
    },

    # =========================================================================
    # NON-COMMUNICABLE DISEASES
    # =========================================================================

    # --- Neoplasms ---
    "Breast cancer": {
        "search_terms": ["breast cancer", "breast neoplasm", "breast tumor",
                         "breast tumour", "mammograph", "breast mass",
                         "breast lesion", "breast carcinoma"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Tracheal, bronchus, and lung cancer": {
        "search_terms": ["lung cancer", "lung nodule", "lung tumor", "lung tumour",
                         "pulmonary nodule", "lung carcinoma", "lung neoplasm",
                         "non-small cell lung", "small cell lung"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Colon and rectum cancer": {
        "search_terms": ["colorectal cancer", "colon cancer", "rectal cancer",
                         "colorectal polyp", "colorectal neoplasm", "bowel cancer"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Stomach cancer": {
        "search_terms": ["gastric cancer", "stomach cancer", "gastric carcinoma"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Liver cancer": {
        "search_terms": ["liver cancer", "hepatocellular carcinoma", "liver tumor",
                         "liver tumour", "hcc"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Cervical cancer": {
        "search_terms": ["cervical cancer", "cervix cancer", "cervical neoplasm",
                         "cervical carcinoma"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Prostate cancer": {
        "search_terms": ["prostate cancer", "prostate neoplasm", "prostate carcinoma",
                         "prostatic cancer"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Oesophageal cancer": {
        "search_terms": ["esophageal cancer", "oesophageal cancer",
                         "esophageal carcinoma"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Pancreatic cancer": {
        "search_terms": ["pancreatic cancer", "pancreas cancer",
                         "pancreatic carcinoma", "pancreatic adenocarcinoma"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Kidney cancer": {
        "search_terms": ["kidney cancer", "renal cell carcinoma", "renal cancer"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Bladder cancer": {
        "search_terms": ["bladder cancer", "bladder carcinoma", "urothelial"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Brain and central nervous system cancer": {
        "search_terms": ["brain tumor", "brain tumour", "brain cancer", "glioma",
                         "glioblastoma", "brain neoplasm", "meningioma",
                         "brain metastas"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Non-Hodgkin lymphoma": {
        "search_terms": ["non-hodgkin lymphoma", "non-hodgkin's lymphoma", "nhl",
                         "diffuse large b-cell"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Leukaemia": {
        "search_terms": ["leukemia", "leukaemia", "acute lymphoblastic",
                         "acute myeloid", "chronic lymphocytic",
                         "chronic myeloid"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Ovarian cancer": {
        "search_terms": ["ovarian cancer", "ovary cancer", "ovarian carcinoma"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Thyroid cancer": {
        "search_terms": ["thyroid cancer", "thyroid nodule", "thyroid carcinoma"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Malignant skin melanoma": {
        "search_terms": ["melanoma", "skin cancer", "skin lesion", "dermoscop",
                         "pigmented lesion"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Lip and oral cavity cancer": {
        "search_terms": ["oral cancer", "oral cavity cancer", "mouth cancer",
                         "oral squamous cell"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Larynx cancer": {
        "search_terms": ["laryngeal cancer", "larynx cancer"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Nasopharynx cancer": {
        "search_terms": ["nasopharyngeal cancer", "nasopharyngeal carcinoma"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Multiple myeloma": {
        "search_terms": ["multiple myeloma"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Hodgkin lymphoma": {
        "search_terms": ["hodgkin lymphoma", "hodgkin's lymphoma", "hodgkin disease"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Uterine cancer": {
        "search_terms": ["endometrial cancer", "uterine cancer", "uterus cancer"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Gallbladder and biliary tract cancer": {
        "search_terms": ["gallbladder cancer", "biliary tract cancer",
                         "cholangiocarcinoma"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Mesothelioma": {
        "search_terms": ["mesothelioma"],
        "level2": "Neoplasms",
        "level1": NCD,
    },
    "Testicular cancer": {
        "search_terms": ["testicular cancer"],
        "level2": "Neoplasms",
        "level1": NCD,
    },

    # --- Cardiovascular diseases ---
    "Ischaemic heart disease": {
        "search_terms": ["ischemic heart disease", "ischaemic heart disease",
                         "coronary artery disease", "myocardial infarction",
                         "heart attack", "coronary heart disease", "angina",
                         "acute coronary syndrome"],
        "level2": "Cardiovascular diseases",
        "level1": NCD,
    },
    "Stroke": {
        "search_terms": ["stroke", "cerebrovascular", "cerebral infarction",
                         "intracerebral hemorrhage", "intracranial hemorrhage",
                         "ischemic stroke", "haemorrhagic stroke"],
        "level2": "Cardiovascular diseases",
        "level1": NCD,
    },
    "Hypertensive heart disease": {
        "search_terms": ["hypertension", "hypertensive", "blood pressure",
                         "antihypertensive"],
        "level2": "Cardiovascular diseases",
        "level1": NCD,
    },
    "Cardiomyopathy and myocarditis": {
        "search_terms": ["cardiomyopathy", "myocarditis", "dilated cardiomyopathy",
                         "hypertrophic cardiomyopathy"],
        "level2": "Cardiovascular diseases",
        "level1": NCD,
    },
    "Atrial fibrillation and flutter": {
        "search_terms": ["atrial fibrillation", "atrial flutter", "afib"],
        "level2": "Cardiovascular diseases",
        "level1": NCD,
    },
    "Aortic aneurysm": {
        "search_terms": ["aortic aneurysm"],
        "level2": "Cardiovascular diseases",
        "level1": NCD,
    },
    "Peripheral artery disease": {
        "search_terms": ["peripheral artery disease", "peripheral arterial disease",
                         "peripheral vascular disease"],
        "level2": "Cardiovascular diseases",
        "level1": NCD,
    },
    "Endocarditis": {
        "search_terms": ["endocarditis"],
        "level2": "Cardiovascular diseases",
        "level1": NCD,
    },
    "Rheumatic heart disease": {
        "search_terms": ["rheumatic heart disease", "rheumatic fever"],
        "level2": "Cardiovascular diseases",
        "level1": NCD,
    },
    "Heart failure": {
        "search_terms": ["heart failure", "cardiac failure", "congestive heart"],
        "level2": "Cardiovascular diseases",
        "level1": NCD,
    },

    # --- Chronic respiratory diseases ---
    "Chronic obstructive pulmonary disease": {
        "search_terms": ["copd", "chronic obstructive pulmonary",
                         "chronic obstructive lung", "emphysema"],
        "level2": "Chronic respiratory diseases",
        "level1": NCD,
    },
    "Asthma": {
        "search_terms": ["asthma"],
        "level2": "Chronic respiratory diseases",
        "level1": NCD,
    },
    "Interstitial lung disease": {
        "search_terms": ["interstitial lung disease", "pulmonary fibrosis",
                         "idiopathic pulmonary fibrosis"],
        "level2": "Chronic respiratory diseases",
        "level1": NCD,
    },

    # --- Digestive diseases ---
    "Cirrhosis and other chronic liver diseases": {
        "search_terms": ["liver cirrhosis", "cirrhosis", "chronic liver disease",
                         "liver fibrosis", "fatty liver", "nafld", "nash"],
        "level2": "Digestive diseases",
        "level1": NCD,
    },
    "Inflammatory bowel disease": {
        "search_terms": ["inflammatory bowel disease", "crohn", "ulcerative colitis",
                         "ibd"],
        "level2": "Digestive diseases",
        "level1": NCD,
    },
    "Peptic ulcer disease": {
        "search_terms": ["peptic ulcer", "gastric ulcer", "duodenal ulcer",
                         "helicobacter pylori"],
        "level2": "Digestive diseases",
        "level1": NCD,
    },
    "Pancreatitis": {
        "search_terms": ["pancreatitis"],
        "level2": "Digestive diseases",
        "level1": NCD,
    },
    "Appendicitis": {
        "search_terms": ["appendicitis"],
        "level2": "Digestive diseases",
        "level1": NCD,
    },
    "Gallbladder and biliary diseases": {
        "search_terms": ["gallstone", "cholelithiasis", "cholecystitis"],
        "level2": "Digestive diseases",
        "level1": NCD,
    },

    # --- Neurological disorders ---
    "Alzheimer's disease and other dementias": {
        "search_terms": ["alzheimer", "dementia", "cognitive decline",
                         "cognitive impairment", "neurodegenerat"],
        "level2": "Neurological disorders",
        "level1": NCD,
    },
    "Parkinson's disease": {
        "search_terms": ["parkinson"],
        "level2": "Neurological disorders",
        "level1": NCD,
    },
    "Epilepsy": {
        "search_terms": ["epilepsy", "seizure", "epileptic"],
        "level2": "Neurological disorders",
        "level1": NCD,
    },
    "Multiple sclerosis": {
        "search_terms": ["multiple sclerosis"],
        "level2": "Neurological disorders",
        "level1": NCD,
    },
    "Motor neuron disease": {
        "search_terms": ["motor neuron disease", "amyotrophic lateral sclerosis",
                         "als"],
        "level2": "Neurological disorders",
        "level1": NCD,
    },
    "Migraine": {
        "search_terms": ["migraine"],
        "level2": "Neurological disorders",
        "level1": NCD,
    },
    "Tension-type headache": {
        "search_terms": ["tension headache", "tension-type headache"],
        "level2": "Neurological disorders",
        "level1": NCD,
    },

    # --- Mental disorders ---
    "Major depressive disorder": {
        "search_terms": ["depression", "depressive disorder", "major depression",
                         "antidepressant"],
        "level2": "Mental disorders",
        "level1": NCD,
    },
    "Anxiety disorders": {
        "search_terms": ["anxiety disorder", "generalized anxiety",
                         "panic disorder", "social anxiety"],
        "level2": "Mental disorders",
        "level1": NCD,
    },
    "Bipolar disorder": {
        "search_terms": ["bipolar disorder", "bipolar affective"],
        "level2": "Mental disorders",
        "level1": NCD,
    },
    "Schizophrenia": {
        "search_terms": ["schizophrenia", "psychosis", "psychotic disorder"],
        "level2": "Mental disorders",
        "level1": NCD,
    },
    "Eating disorders": {
        "search_terms": ["eating disorder", "anorexia nervosa", "bulimia"],
        "level2": "Mental disorders",
        "level1": NCD,
    },
    "Autism spectrum disorders": {
        "search_terms": ["autism", "autistic", "autism spectrum"],
        "level2": "Mental disorders",
        "level1": NCD,
    },
    "Attention-deficit/hyperactivity disorder": {
        "search_terms": ["adhd", "attention deficit", "attention-deficit"],
        "level2": "Mental disorders",
        "level1": NCD,
    },
    "Conduct disorder": {
        "search_terms": ["conduct disorder"],
        "level2": "Mental disorders",
        "level1": NCD,
    },
    "Idiopathic developmental intellectual disability": {
        "search_terms": ["intellectual disability", "mental retardation"],
        "level2": "Mental disorders",
        "level1": NCD,
    },
    "Alcohol use disorders": {
        "search_terms": ["alcohol use disorder", "alcoholism", "alcohol dependence",
                         "alcohol abuse"],
        "level2": "Substance use disorders",
        "level1": NCD,
    },
    "Drug use disorders": {
        "search_terms": ["drug use disorder", "substance use disorder", "opioid use",
                         "drug addiction", "substance abuse"],
        "level2": "Substance use disorders",
        "level1": NCD,
    },

    # --- Diabetes and kidney diseases ---
    "Diabetes mellitus type 1": {
        "search_terms": ["type 1 diabetes", "type i diabetes", "juvenile diabetes",
                         "insulin-dependent diabetes"],
        "level2": "Diabetes and kidney diseases",
        "level1": NCD,
    },
    "Diabetes mellitus type 2": {
        "search_terms": ["type 2 diabetes", "type ii diabetes", "diabetes mellitus",
                         "diabetic", "glucose", "glycemic", "hba1c",
                         "insulin resistance"],
        "level2": "Diabetes and kidney diseases",
        "level1": NCD,
    },
    "Chronic kidney disease": {
        "search_terms": ["chronic kidney disease", "chronic renal", "ckd",
                         "end-stage renal", "hemodialysis", "haemodialysis",
                         "dialysis", "kidney failure"],
        "level2": "Diabetes and kidney diseases",
        "level1": NCD,
    },

    # --- Musculoskeletal disorders ---
    "Low back pain": {
        "search_terms": ["low back pain", "lower back pain", "lumbar pain",
                         "lumbar spine"],
        "level2": "Musculoskeletal disorders",
        "level1": NCD,
    },
    "Neck pain": {
        "search_terms": ["neck pain", "cervical pain", "cervical spine"],
        "level2": "Musculoskeletal disorders",
        "level1": NCD,
    },
    "Osteoarthritis": {
        "search_terms": ["osteoarthritis", "knee arthritis", "hip arthritis",
                         "joint degeneration"],
        "level2": "Musculoskeletal disorders",
        "level1": NCD,
    },
    "Rheumatoid arthritis": {
        "search_terms": ["rheumatoid arthritis"],
        "level2": "Musculoskeletal disorders",
        "level1": NCD,
    },
    "Gout": {
        "search_terms": ["gout", "hyperuricemia"],
        "level2": "Musculoskeletal disorders",
        "level1": NCD,
    },
    "Osteoporosis": {
        "search_terms": ["osteoporosis", "bone density", "bone mineral density",
                         "osteoporotic fracture"],
        "level2": "Musculoskeletal disorders",
        "level1": NCD,
    },

    # --- Skin and subcutaneous diseases ---
    "Dermatitis": {
        "search_terms": ["dermatitis", "eczema", "atopic dermatitis"],
        "level2": "Skin and subcutaneous diseases",
        "level1": NCD,
    },
    "Psoriasis": {
        "search_terms": ["psoriasis"],
        "level2": "Skin and subcutaneous diseases",
        "level1": NCD,
    },
    "Acne vulgaris": {
        "search_terms": ["acne"],
        "level2": "Skin and subcutaneous diseases",
        "level1": NCD,
    },

    # --- Sense organ diseases ---
    "Glaucoma": {
        "search_terms": ["glaucoma", "intraocular pressure"],
        "level2": "Sense organ diseases",
        "level1": NCD,
    },
    "Cataracts": {
        "search_terms": ["cataract"],
        "level2": "Sense organ diseases",
        "level1": NCD,
    },
    "Age-related macular degeneration": {
        "search_terms": ["macular degeneration", "age-related macular",
                         "amd"],
        "level2": "Sense organ diseases",
        "level1": NCD,
    },
    "Diabetic retinopathy": {
        "search_terms": ["diabetic retinopathy", "retinal"],
        "level2": "Sense organ diseases",
        "level1": NCD,
    },
    "Hearing loss": {
        "search_terms": ["hearing loss", "deafness", "hearing impairment"],
        "level2": "Sense organ diseases",
        "level1": NCD,
    },

    # --- Oral disorders ---
    "Dental caries": {
        "search_terms": ["dental caries", "tooth decay", "dental cavity"],
        "level2": "Oral disorders",
        "level1": NCD,
    },
    "Periodontal diseases": {
        "search_terms": ["periodontal", "periodontitis", "gingivitis",
                         "gum disease"],
        "level2": "Oral disorders",
        "level1": NCD,
    },

    # --- Other NCDs ---
    "Congenital heart anomalies": {
        "search_terms": ["congenital heart", "congenital cardiac"],
        "level2": "Other non-communicable diseases",
        "level1": NCD,
    },
    "Sickle cell disorders": {
        "search_terms": ["sickle cell"],
        "level2": "Other non-communicable diseases",
        "level1": NCD,
    },
    "Urinary diseases and male infertility": {
        "search_terms": ["urinary tract infection", "kidney stone",
                         "nephrolithiasis", "benign prostatic"],
        "level2": "Other non-communicable diseases",
        "level1": NCD,
    },
    "Endocrine, metabolic, blood, and immune disorders": {
        "search_terms": ["thyroid disorder", "hypothyroidism", "hyperthyroidism",
                         "adrenal", "pituitary"],
        "level2": "Other non-communicable diseases",
        "level1": NCD,
    },
    "Gynecological diseases": {
        "search_terms": ["endometriosis", "uterine fibroid", "polycystic ovary",
                         "pcos"],
        "level2": "Other non-communicable diseases",
        "level1": NCD,
    },

    # =========================================================================
    # INJURIES
    # =========================================================================
    "Road injuries": {
        "search_terms": ["road traffic", "traffic accident", "road injury",
                         "traffic injury", "vehicle crash", "motor vehicle accident"],
        "level2": "Transport injuries",
        "level1": INJURIES,
    },
    "Falls": {
        "search_terms": ["fall detection", "fall prevention", "fall risk",
                         "accidental fall"],
        "level2": "Unintentional injuries",
        "level1": INJURIES,
    },
    "Drowning": {
        "search_terms": ["drowning"],
        "level2": "Unintentional injuries",
        "level1": INJURIES,
    },
    "Fire, heat, and hot substances": {
        "search_terms": ["burn injury", "burn wound", "thermal injury"],
        "level2": "Unintentional injuries",
        "level1": INJURIES,
    },
    "Poisonings": {
        "search_terms": ["poisoning", "toxic exposure"],
        "level2": "Unintentional injuries",
        "level1": INJURIES,
    },
    "Self-harm": {
        "search_terms": ["suicide", "self-harm", "self-injury", "suicidal"],
        "level2": "Self-harm and interpersonal violence",
        "level1": INJURIES,
    },
    "Interpersonal violence": {
        "search_terms": ["interpersonal violence", "homicide", "assault",
                         "domestic violence", "intimate partner violence"],
        "level2": "Self-harm and interpersonal violence",
        "level1": INJURIES,
    },
    "Conflict and terrorism": {
        "search_terms": ["conflict", "war injury", "terrorism", "blast injury"],
        "level2": "Self-harm and interpersonal violence",
        "level1": INJURIES,
    },

    # --- Sepsis (cross-cutting) ---
    "Sepsis": {
        "search_terms": ["sepsis", "septic shock", "bacteremia", "bloodstream infection"],
        "level2": "Other infectious diseases",
        "level1": COMMUNICABLE,
    },
}


def get_cause_names() -> list[str]:
    """Return all GBD cause names in the dictionary."""
    return list(GBD_CAUSE_DICTIONARY.keys())


def get_search_terms(cause_name: str) -> list[str]:
    """Return search terms for a given GBD cause."""
    return GBD_CAUSE_DICTIONARY[cause_name]["search_terms"]


def get_all_search_terms_flat() -> dict[str, str]:
    """Return a flat mapping of search_term -> cause_name for fast lookup."""
    mapping = {}
    for cause, info in GBD_CAUSE_DICTIONARY.items():
        for term in info["search_terms"]:
            mapping[term.lower()] = cause
    return mapping


def get_cause_hierarchy():
    import pandas as pd
    """Return the cause dictionary as a DataFrame with hierarchy info."""  # noqa: D205
    rows = []
    for cause, info in GBD_CAUSE_DICTIONARY.items():
        rows.append({
            "cause_name": cause,
            "level2": info["level2"],
            "level1": info["level1"],
            "n_search_terms": len(info["search_terms"]),
            "search_terms": "; ".join(info["search_terms"]),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    hierarchy = get_cause_hierarchy()
    print(f"Total GBD causes in dictionary: {len(hierarchy)}")
    print(f"\nBy Level 1:")
    print(hierarchy["level1"].value_counts())
    print(f"\nBy Level 2:")
    print(hierarchy["level2"].value_counts().head(10))
    print(f"\nTotal unique search terms: {sum(hierarchy['n_search_terms'])}")
