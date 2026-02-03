"""Constants for the irAE detection system."""

# Common immunotherapy checkpoint inhibitor agents
IMMUNOTHERAPY_AGENTS = {
    # PD-1 inhibitors
    "pembrolizumab": {"class": "PD-1", "brand_names": ["Keytruda"]},
    "nivolumab": {"class": "PD-1", "brand_names": ["Opdivo"]},
    "cemiplimab": {"class": "PD-1", "brand_names": ["Libtayo"]},
    "dostarlimab": {"class": "PD-1", "brand_names": ["Jemperli"]},
    
    # PD-L1 inhibitors
    "atezolizumab": {"class": "PD-L1", "brand_names": ["Tecentriq"]},
    "durvalumab": {"class": "PD-L1", "brand_names": ["Imfinzi"]},
    "avelumab": {"class": "PD-L1", "brand_names": ["Bavencio"]},
    
    # CTLA-4 inhibitors
    "ipilimumab": {"class": "CTLA-4", "brand_names": ["Yervoy"]},
    "tremelimumab": {"class": "CTLA-4", "brand_names": ["Imjudo"]},
    
    # Brand name mappings
    "keytruda": {"class": "PD-1", "generic": "pembrolizumab"},
    "opdivo": {"class": "PD-1", "generic": "nivolumab"},
    "libtayo": {"class": "PD-1", "generic": "cemiplimab"},
    "jemperli": {"class": "PD-1", "generic": "dostarlimab"},
    "tecentriq": {"class": "PD-L1", "generic": "atezolizumab"},
    "imfinzi": {"class": "PD-L1", "generic": "durvalumab"},
    "bavencio": {"class": "PD-L1", "generic": "avelumab"},
    "yervoy": {"class": "CTLA-4", "generic": "ipilimumab"},
    "imjudo": {"class": "CTLA-4", "generic": "tremelimumab"},
}

# CTCAE severity grading descriptions
CTCAE_GRADES = {
    1: {
        "name": "Mild",
        "description": "Asymptomatic or mild symptoms; clinical or diagnostic observations only; intervention not indicated",
    },
    2: {
        "name": "Moderate", 
        "description": "Moderate; minimal, local or noninvasive intervention indicated; limiting age-appropriate instrumental ADL",
    },
    3: {
        "name": "Severe",
        "description": "Severe or medically significant but not immediately life-threatening; hospitalization or prolongation of hospitalization indicated; disabling; limiting self care ADL",
    },
    4: {
        "name": "Life-threatening",
        "description": "Life-threatening consequences; urgent intervention indicated",
    },
}

# Urgency triage levels
URGENCY_LEVELS = {
    "routine": {
        "emoji": "🟢",
        "name": "Routine monitoring",
        "description": "Continue current monitoring; follow up at next scheduled visit",
        "timeframe": "Days to weeks",
    },
    "soon": {
        "emoji": "🟡",
        "name": "Needs oncology review soon",
        "description": "Contact oncology team for guidance; may need earlier follow-up",
        "timeframe": "Within 1-3 days",
    },
    "urgent": {
        "emoji": "🟠",
        "name": "Urgent (same day)",
        "description": "Requires same-day oncology evaluation; consider holding immunotherapy",
        "timeframe": "Same day",
    },
    "emergency": {
        "emoji": "🔴",
        "name": "Emergency evaluation",
        "description": "Requires immediate evaluation; potential for rapid deterioration",
        "timeframe": "Immediate",
    },
}

# Organ systems for irAE detection
ORGAN_SYSTEMS = {
    "gi": {
        "name": "Gastrointestinal",
        "conditions": ["colitis", "diarrhea", "enteritis"],
        "key_symptoms": ["diarrhea", "abdominal pain", "bloody stool", "nausea", "vomiting"],
        "key_labs": [],
    },
    "liver": {
        "name": "Hepatic",
        "conditions": ["hepatitis", "liver injury"],
        "key_symptoms": ["fatigue", "jaundice", "abdominal pain", "dark urine"],
        "key_labs": ["AST", "ALT", "bilirubin", "alkaline phosphatase", "ALP", "GGT"],
    },
    "lung": {
        "name": "Pulmonary",
        "conditions": ["pneumonitis", "ILD"],
        "key_symptoms": ["cough", "dyspnea", "shortness of breath", "hypoxia", "chest pain"],
        "key_labs": [],
    },
    "endocrine": {
        "name": "Endocrine",
        "conditions": ["thyroiditis", "hypophysitis", "adrenal insufficiency", "diabetes"],
        "key_symptoms": ["fatigue", "weakness", "headache", "hypotension", "weight changes"],
        "key_labs": ["TSH", "T4", "free T4", "T3", "cortisol", "ACTH", "glucose"],
    },
    "skin": {
        "name": "Dermatologic",
        "conditions": ["rash", "dermatitis", "vitiligo", "Stevens-Johnson"],
        "key_symptoms": ["rash", "pruritus", "itching", "skin changes", "blistering"],
        "key_labs": [],
    },
    "neuro": {
        "name": "Neurologic",
        "conditions": ["neuropathy", "encephalitis", "myasthenia", "Guillain-Barre"],
        "key_symptoms": ["weakness", "numbness", "confusion", "headache", "vision changes", "ptosis"],
        "key_labs": ["CK", "creatine kinase"],
    },
    "cardiac": {
        "name": "Cardiac",
        "conditions": ["myocarditis", "pericarditis", "arrhythmia"],
        "key_symptoms": ["chest pain", "palpitations", "dyspnea", "edema", "syncope"],
        "key_labs": ["troponin", "BNP", "NT-proBNP", "CK-MB"],
    },
    "renal": {
        "name": "Renal",
        "conditions": ["nephritis", "acute kidney injury"],
        "key_symptoms": ["decreased urine output", "edema", "fatigue"],
        "key_labs": ["creatinine", "BUN", "GFR", "eGFR"],
    },
}

# Common lab reference ranges (for adults)
LAB_REFERENCE_RANGES = {
    "AST": {"low": 10, "high": 40, "unit": "U/L"},
    "ALT": {"low": 7, "high": 56, "unit": "U/L"},
    "bilirubin": {"low": 0.1, "high": 1.2, "unit": "mg/dL"},
    "alkaline phosphatase": {"low": 44, "high": 147, "unit": "U/L"},
    "ALP": {"low": 44, "high": 147, "unit": "U/L"},
    "TSH": {"low": 0.4, "high": 4.0, "unit": "mIU/L"},
    "free T4": {"low": 0.8, "high": 1.8, "unit": "ng/dL"},
    "cortisol": {"low": 6, "high": 23, "unit": "mcg/dL"},
    "troponin": {"low": 0, "high": 0.04, "unit": "ng/mL"},
    "creatinine": {"low": 0.7, "high": 1.3, "unit": "mg/dL"},
    "BUN": {"low": 7, "high": 20, "unit": "mg/dL"},
    "glucose": {"low": 70, "high": 100, "unit": "mg/dL"},
    "CK": {"low": 30, "high": 200, "unit": "U/L"},
    "BNP": {"low": 0, "high": 100, "unit": "pg/mL"},
}
