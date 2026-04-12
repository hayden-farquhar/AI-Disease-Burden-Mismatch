"""
Mapping between our GBD cause dictionary names and official GBD 2023 cause names.

Some causes differ in spelling (UK vs US), aggregation level, or naming convention.
This mapping allows us to link our publication counts to official DALY data.
"""

# Our dictionary name -> GBD 2023 official name
OUR_TO_GBD_NAME = {
    # Spelling differences (UK vs US)
    "Ischaemic heart disease": "Ischemic heart disease",
    "Diarrhoeal diseases": "Diarrheal diseases",
    "Leukaemia": "Leukemia",
    "Oesophageal cancer": "Esophageal cancer",

    # Different naming conventions
    "Iron-deficiency anaemia": "Dietary iron deficiency",
    "Major depressive disorder": "Depressive disorders",
    "Hearing loss": "Age-related and other hearing loss",
    "Epilepsy": "Idiopathic epilepsy",
    "Sickle cell disorders": "Hemoglobinopathies and hemolytic anemias",

    # Our sub-causes -> GBD parent categories
    "Migraine": "Headache disorders",
    "Tension-type headache": "Headache disorders",
    "Peptic ulcer disease": "Upper digestive system diseases",
    "Dental caries": "Oral disorders",
    "Periodontal diseases": "Oral disorders",
    "Congenital heart anomalies": "Congenital birth defects",
    "Osteoporosis": "Other musculoskeletal disorders",
    "Glaucoma": "Blindness and vision loss",
    "Diabetic retinopathy": "Blindness and vision loss",
    "Age-related macular degeneration": "Blindness and vision loss",
    "Cataracts": "Blindness and vision loss",
    "Heart failure": "Other cardiovascular and circulatory diseases",
    "Peripheral artery disease": "Other cardiovascular and circulatory diseases",
    "Hepatitis B": "Acute hepatitis",
    "Hepatitis C": "Acute hepatitis",
    "Diabetes mellitus type 1": "Diabetes mellitus",
    "Diabetes mellitus type 2": "Diabetes mellitus",
    "Interstitial lung disease": "Other chronic respiratory diseases",
}


def map_to_gbd_name(our_name: str) -> str:
    """Map our cause dictionary name to the official GBD 2023 name."""
    return OUR_TO_GBD_NAME.get(our_name, our_name)
