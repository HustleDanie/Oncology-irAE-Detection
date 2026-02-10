"""
Training data generator for MedGemma fine-tuning.

Creates instruction-tuning pairs from sample cases with expected outcomes.
Format: (clinical_input, expected_json_output)
"""

import json
from typing import List, Dict, Any

# Training examples based on our validated sample cases
TRAINING_EXAMPLES = [
    {
        "id": "GI-001",
        "input": {
            "patient_id": "GI-001",
            "age": 58,
            "cancer_type": "Melanoma",
            "medications": "Pembrolizumab 200mg IV q3weeks, Ondansetron 8mg PRN, Lisinopril 10mg daily",
            "labs": "WBC: 11.2 x10^9/L (H), CRP: 2.8 mg/dL (H), Albumin: 3.2 g/dL (L), Hemoglobin: 12.5 g/dL",
            "symptoms": "Diarrhea - 5-6 loose stools daily for 4 days, Abdominal cramping - mild, No blood in stool, No fever",
            "notes": "Patient on cycle 4 of pembrolizumab for stage IIIC melanoma. Reports onset of loose stools 4 days ago, now having 5-6 episodes daily. Mild periumbilical cramping. No mucus or blood. Appetite slightly decreased. No recent antibiotic use. No sick contacts."
        },
        "expected_output": {
            "irae_detected": True,
            "overall_severity": "Grade 2 - Moderate",
            "urgency": "soon",
            "affected_systems": ["Gastrointestinal"],
            "causality": {
                "likelihood": "Possible",
                "reasoning": "Patient on PD-1 inhibitor (pembrolizumab) with new onset diarrhea 5-6 stools/day consistent with CTCAE Grade 2 colitis. Timing during cycle 4 is typical for immune-related colitis. No infectious etiology identified.",
                "temporal_relationship": "Onset during active immunotherapy treatment",
                "supporting_factors": ["On checkpoint inhibitor", "Classic Grade 2 diarrhea pattern", "No alternative cause identified"],
                "against_factors": ["No blood in stool", "No fever"]
            },
            "severity_reasoning": "CTCAE Grade 2 Diarrhea: 4-6 stools/day over baseline. Patient reports 5-6 loose stools daily which meets Grade 2 criteria.",
            "urgency_reasoning": "Grade 2 GI toxicity requires oncology review within 1-3 days to assess need for immunotherapy hold and corticosteroid initiation.",
            "recommended_actions": [
                {"action": "Hold pembrolizumab pending evaluation", "priority": 1, "rationale": "Grade 2 colitis typically requires treatment hold"},
                {"action": "Start oral prednisone 1mg/kg daily", "priority": 1, "rationale": "Standard first-line treatment for Grade 2 colitis"},
                {"action": "Obtain stool studies to rule out infectious etiology", "priority": 2, "rationale": "Must exclude C. diff and other infections"}
            ],
            "key_evidence": ["5-6 loose stools daily", "On pembrolizumab", "Elevated CRP", "Low albumin"]
        }
    },
    {
        "id": "GI-002", 
        "input": {
            "patient_id": "GI-002",
            "age": 65,
            "cancer_type": "Non-small cell lung cancer",
            "medications": "Nivolumab 480mg IV q4weeks, Prednisone 10mg daily (started 2 days ago), Loperamide 2mg PRN",
            "labs": "WBC: 14.5 x10^9/L (H), CRP: 8.5 mg/dL (H), Albumin: 2.8 g/dL (L), Potassium: 3.2 mEq/L (L), Creatinine: 1.4 mg/dL (H)",
            "symptoms": "Diarrhea - 8-10 watery stools daily, Blood in stool - present, Severe abdominal pain, Fever - 38.2°C, Dehydration signs",
            "notes": "Patient on nivolumab for metastatic NSCLC. Severe watery diarrhea started 1 week ago, now with visible blood. Diffuse abdominal tenderness on exam. Signs of dehydration. Started low-dose prednisone 2 days ago without improvement."
        },
        "expected_output": {
            "irae_detected": True,
            "overall_severity": "Grade 3 - Severe",
            "urgency": "urgent",
            "affected_systems": ["Gastrointestinal"],
            "causality": {
                "likelihood": "Highly likely",
                "reasoning": "Patient on PD-1 inhibitor with severe bloody diarrhea (8-10 stools/day), fever, and dehydration consistent with Grade 3 immune-related colitis. Failed low-dose steroids indicating need for escalation.",
                "temporal_relationship": "During active immunotherapy",
                "supporting_factors": ["On checkpoint inhibitor", "Bloody diarrhea", "Failed low-dose steroids", "Fever and dehydration"],
                "against_factors": []
            },
            "severity_reasoning": "CTCAE Grade 3 Diarrhea: ≥7 stools/day over baseline OR bloody diarrhea. Patient has 8-10 stools with blood, meeting Grade 3 criteria.",
            "urgency_reasoning": "Grade 3 colitis requires same-day evaluation and hospitalization for IV corticosteroids.",
            "recommended_actions": [
                {"action": "Hospitalize for IV methylprednisolone 1-2mg/kg", "priority": 1, "rationale": "Grade 3 colitis requires IV steroids"},
                {"action": "Discontinue nivolumab", "priority": 1, "rationale": "Grade 3 toxicity requires treatment discontinuation"},
                {"action": "GI consultation for colonoscopy", "priority": 1, "rationale": "Confirm diagnosis and assess severity"},
                {"action": "IV fluid resuscitation", "priority": 1, "rationale": "Patient is dehydrated"}
            ],
            "key_evidence": ["8-10 bloody stools daily", "Failed low-dose steroids", "Fever", "Dehydration", "Elevated CRP"]
        }
    },
    {
        "id": "HEP-001",
        "input": {
            "patient_id": "HEP-001",
            "age": 52,
            "cancer_type": "Urothelial carcinoma",
            "medications": "Atezolizumab 1200mg IV q3weeks, Metformin 1000mg BID, Omeprazole 20mg daily",
            "labs": "AST: 156 U/L (H) - baseline 28, ALT: 189 U/L (H) - baseline 32, ALP: 145 U/L (H), Total Bilirubin: 1.8 mg/dL (H), INR: 1.1",
            "symptoms": "Fatigue - moderate, Mild nausea, No jaundice, No abdominal pain",
            "notes": "Routine labs show AST/ALT elevation >3x ULN. Patient asymptomatic except for mild fatigue. No alcohol use. No new medications. Viral hepatitis panel pending."
        },
        "expected_output": {
            "irae_detected": True,
            "overall_severity": "Grade 2 - Moderate",
            "urgency": "soon",
            "affected_systems": ["Hepatic"],
            "causality": {
                "likelihood": "Possible",
                "reasoning": "Patient on PD-L1 inhibitor with AST/ALT elevation 3-5x ULN consistent with Grade 2 immune-related hepatitis. Need to rule out viral hepatitis and drug-induced causes.",
                "temporal_relationship": "During active immunotherapy",
                "supporting_factors": ["On checkpoint inhibitor", "AST/ALT >3x ULN", "No other hepatotoxic medications"],
                "against_factors": ["Viral hepatitis panel pending", "Could be other etiology"]
            },
            "severity_reasoning": "CTCAE Grade 2 Hepatitis: AST/ALT >3-5x ULN. AST 156 (~4x ULN) and ALT 189 (~4.7x ULN) meet Grade 2 criteria.",
            "urgency_reasoning": "Grade 2 hepatitis requires oncology review to determine need for treatment hold and corticosteroid initiation.",
            "recommended_actions": [
                {"action": "Hold atezolizumab pending evaluation", "priority": 1, "rationale": "Grade 2 hepatitis requires treatment hold"},
                {"action": "Rule out viral hepatitis (HAV, HBV, HCV)", "priority": 1, "rationale": "Must exclude infectious causes"},
                {"action": "Consider prednisone 0.5-1mg/kg if viral negative", "priority": 2, "rationale": "Standard treatment for immune-related hepatitis"},
                {"action": "Recheck LFTs in 3-5 days", "priority": 2, "rationale": "Monitor for progression"}
            ],
            "key_evidence": ["AST 156 U/L (>3x ULN)", "ALT 189 U/L (>3x ULN)", "On atezolizumab", "Mildly elevated bilirubin"]
        }
    },
    {
        "id": "HEP-002",
        "input": {
            "patient_id": "HEP-002",
            "age": 48,
            "cancer_type": "Melanoma",
            "medications": "Ipilimumab 3mg/kg + Nivolumab 1mg/kg IV q3weeks, Acetaminophen 500mg PRN",
            "labs": "AST: 485 U/L (H), ALT: 612 U/L (H), ALP: 210 U/L (H), Total Bilirubin: 3.2 mg/dL (H), Direct Bilirubin: 2.1 mg/dL (H), INR: 1.4 (H), Albumin: 3.0 g/dL (L)",
            "symptoms": "Jaundice - visible scleral icterus, Fatigue - severe, Nausea and anorexia, Dark urine, Right upper quadrant discomfort",
            "notes": "Patient on combination immunotherapy for metastatic melanoma. Developed jaundice over past week. AST/ALT >10x ULN. Hepatitis panel negative. No hepatotoxic medications. Ultrasound shows no biliary obstruction."
        },
        "expected_output": {
            "irae_detected": True,
            "overall_severity": "Grade 3 - Severe",
            "urgency": "urgent",
            "affected_systems": ["Hepatic"],
            "causality": {
                "likelihood": "Highly likely",
                "reasoning": "Patient on combination ICI (ipi/nivo) with severe transaminitis >10x ULN, jaundice, and elevated INR. Viral hepatitis ruled out. Classic presentation of Grade 3 immune-related hepatitis.",
                "temporal_relationship": "During combination immunotherapy",
                "supporting_factors": ["Combination ICI (highest hepatitis risk)", "AST/ALT >10x ULN", "Jaundice with elevated bilirubin", "Negative viral panel", "No biliary obstruction"],
                "against_factors": []
            },
            "severity_reasoning": "CTCAE Grade 3 Hepatitis: AST/ALT >5-20x ULN. AST 485 (~12x ULN) and ALT 612 (~15x ULN) with elevated bilirubin and INR indicate severe hepatitis.",
            "urgency_reasoning": "Grade 3 hepatitis requires same-day hospitalization for IV corticosteroids and close monitoring of synthetic function.",
            "recommended_actions": [
                {"action": "Permanently discontinue immunotherapy", "priority": 1, "rationale": "Grade 3 hepatitis typically requires permanent discontinuation"},
                {"action": "Hospitalize for IV methylprednisolone 1-2mg/kg", "priority": 1, "rationale": "Grade 3 hepatitis requires IV steroids"},
                {"action": "Hepatology consultation", "priority": 1, "rationale": "Severe hepatitis needs specialist input"},
                {"action": "Monitor INR daily", "priority": 1, "rationale": "Elevated INR indicates synthetic dysfunction - monitor for acute liver failure"}
            ],
            "key_evidence": ["AST 485, ALT 612 (>10x ULN)", "Jaundice", "Elevated INR 1.4", "Combination ICI", "Negative viral panel"]
        }
    },
    {
        "id": "LUNG-001",
        "input": {
            "patient_id": "LUNG-001",
            "age": 67,
            "cancer_type": "Non-small cell lung cancer",
            "medications": "Durvalumab 10mg/kg IV q2weeks, Albuterol inhaler PRN, Lisinopril 20mg daily",
            "labs": "WBC: 9.8 x10^9/L, LDH: 280 U/L (H), CRP: 3.2 mg/dL (H), Procalcitonin: 0.15 ng/mL",
            "symptoms": "Dry cough - new onset, 2 weeks, Dyspnea on exertion - moderate, No fever, O2 saturation: 94% on room air",
            "notes": "Post-chemoradiation consolidation durvalumab. New dry cough and exertional dyspnea x 2 weeks. CT chest shows new bilateral ground-glass opacities. No infectious symptoms. Sputum culture negative."
        },
        "expected_output": {
            "irae_detected": True,
            "overall_severity": "Grade 2 - Moderate",
            "urgency": "soon",
            "affected_systems": ["Pulmonary"],
            "causality": {
                "likelihood": "Highly likely",
                "reasoning": "Patient on durvalumab post-chemoradiation (high pneumonitis risk setting) with new cough, dyspnea, and bilateral GGO on CT. Low procalcitonin and negative cultures argue against infection.",
                "temporal_relationship": "During consolidation durvalumab after chemoradiation",
                "supporting_factors": ["Post-CRT durvalumab (10-15% pneumonitis rate)", "New bilateral GGO on CT", "Negative infection workup", "Classic symptom pattern"],
                "against_factors": ["O2 sat 94% - borderline"]
            },
            "severity_reasoning": "CTCAE Grade 2 Pneumonitis: Symptomatic, medical intervention indicated, limiting instrumental ADL. Patient has moderate dyspnea on exertion with O2 sat 94%.",
            "urgency_reasoning": "Grade 2 pneumonitis requires oncology review to initiate corticosteroids and determine need for treatment hold.",
            "recommended_actions": [
                {"action": "Hold durvalumab", "priority": 1, "rationale": "Grade 2 pneumonitis requires treatment hold"},
                {"action": "Start prednisone 1-2mg/kg daily", "priority": 1, "rationale": "Standard treatment for Grade 2 pneumonitis"},
                {"action": "Bronchoscopy with BAL if diagnostic uncertainty", "priority": 2, "rationale": "Can confirm diagnosis and rule out infection"},
                {"action": "Follow-up CT in 3-4 weeks", "priority": 2, "rationale": "Assess response to steroids"}
            ],
            "key_evidence": ["New bilateral GGO on CT", "Dry cough and dyspnea", "O2 sat 94%", "Low procalcitonin", "Negative cultures"]
        }
    },
    {
        "id": "LUNG-002",
        "input": {
            "patient_id": "LUNG-002",
            "age": 71,
            "cancer_type": "Non-small cell lung cancer",
            "medications": "Pembrolizumab 200mg IV q3weeks, Oxygen 4L NC, Azithromycin 500mg daily (started empirically)",
            "labs": "WBC: 11.5 x10^9/L, LDH: 450 U/L (H), CRP: 12.5 mg/dL (H), PaO2: 58 mmHg on 4L NC, Procalcitonin: 0.2 ng/mL",
            "symptoms": "Severe dyspnea at rest, Persistent dry cough, Hypoxia requiring supplemental O2, Tachypnea - RR 28, No fever",
            "notes": "Patient on pembrolizumab for stage IV NSCLC. Progressive dyspnea over 1 week, now requiring 4L O2. CT shows extensive bilateral GGO and consolidation. BAL cultures negative. Considering ICU transfer."
        },
        "expected_output": {
            "irae_detected": True,
            "overall_severity": "Grade 3 - Severe",
            "urgency": "emergency",
            "affected_systems": ["Pulmonary"],
            "causality": {
                "likelihood": "Highly likely",
                "reasoning": "Patient on pembrolizumab with severe hypoxemia (PaO2 58) requiring supplemental O2, extensive bilateral GGO/consolidation on CT, and negative infection workup. Classic severe immune-related pneumonitis.",
                "temporal_relationship": "During active immunotherapy",
                "supporting_factors": ["On checkpoint inhibitor", "Severe hypoxemia requiring O2", "Extensive bilateral infiltrates", "Negative BAL cultures", "Low procalcitonin"],
                "against_factors": []
            },
            "severity_reasoning": "CTCAE Grade 3 Pneumonitis: Severe symptoms, oxygen indicated, limiting self-care ADL. PaO2 58 on 4L O2 with tachypnea indicates severe respiratory compromise.",
            "urgency_reasoning": "Grade 3 pneumonitis with significant hypoxemia requires emergency evaluation and ICU admission for high-dose IV steroids.",
            "recommended_actions": [
                {"action": "Permanently discontinue pembrolizumab", "priority": 1, "rationale": "Grade 3 pneumonitis requires permanent discontinuation"},
                {"action": "IV methylprednisolone 2-4mg/kg/day", "priority": 1, "rationale": "High-dose IV steroids for severe pneumonitis"},
                {"action": "ICU admission for monitoring", "priority": 1, "rationale": "Severe hypoxemia requires close monitoring"},
                {"action": "Pulmonology consultation", "priority": 1, "rationale": "Specialist input for severe pneumonitis"},
                {"action": "Consider infliximab if no response in 48h", "priority": 2, "rationale": "Steroid-refractory pneumonitis may need additional immunosuppression"}
            ],
            "key_evidence": ["PaO2 58 on 4L O2", "Extensive bilateral GGO", "Tachypnea RR 28", "Negative BAL cultures"]
        }
    },
    {
        "id": "ENDO-001",
        "input": {
            "patient_id": "ENDO-001",
            "age": 55,
            "cancer_type": "Renal cell carcinoma",
            "medications": "Nivolumab 240mg IV q2weeks, Amlodipine 5mg daily",
            "labs": "TSH: 28.5 mIU/L (H) - baseline 2.1, Free T4: 0.4 ng/dL (L), Free T3: 1.8 pg/mL (L), Anti-TPO: positive",
            "symptoms": "Fatigue - progressive over 4 weeks, Weight gain - 8 lbs in 1 month, Cold intolerance, Constipation, Dry skin",
            "notes": "Patient on nivolumab for metastatic RCC. Progressive fatigue and weight gain over past month. TSH markedly elevated with low free T4. Classic hypothyroid symptoms present."
        },
        "expected_output": {
            "irae_detected": True,
            "overall_severity": "Grade 2 - Moderate",
            "urgency": "soon",
            "affected_systems": ["Endocrine"],
            "causality": {
                "likelihood": "Highly likely",
                "reasoning": "Patient on PD-1 inhibitor with markedly elevated TSH, low free T4, positive anti-TPO antibodies, and classic hypothyroid symptoms. This is immune-related thyroiditis causing hypothyroidism.",
                "temporal_relationship": "During active immunotherapy",
                "supporting_factors": ["On checkpoint inhibitor", "TSH 28.5 (very elevated)", "Low free T4", "Anti-TPO positive", "Classic symptoms"],
                "against_factors": []
            },
            "severity_reasoning": "CTCAE Grade 2 Hypothyroidism: Symptomatic, thyroid replacement indicated. Patient has overt hypothyroidism with classic symptoms.",
            "urgency_reasoning": "Hypothyroidism requires oncology review but is not urgent. Importantly, immunotherapy can typically be CONTINUED with thyroid hormone replacement.",
            "recommended_actions": [
                {"action": "Start levothyroxine replacement", "priority": 1, "rationale": "Overt hypothyroidism requires hormone replacement"},
                {"action": "Can continue nivolumab", "priority": 2, "rationale": "Unlike other irAEs, hypothyroidism does not require ICI discontinuation"},
                {"action": "Recheck TSH in 6-8 weeks", "priority": 2, "rationale": "Monitor response to replacement therapy"},
                {"action": "Endocrinology referral if needed", "priority": 3, "rationale": "For dose adjustment and long-term management"}
            ],
            "key_evidence": ["TSH 28.5 mIU/L", "Free T4 0.4 ng/dL", "Anti-TPO positive", "Classic hypothyroid symptoms"]
        }
    },
    {
        "id": "ENDO-002",
        "input": {
            "patient_id": "ENDO-002",
            "age": 62,
            "cancer_type": "Melanoma",
            "medications": "Ipilimumab 3mg/kg IV q3weeks (4th dose), Hydrochlorothiazide 25mg daily",
            "labs": "ACTH: 5 pg/mL (L), Cortisol (AM): 2.1 ug/dL (L), TSH: 0.5 mIU/L (L), Free T4: 0.6 ng/dL (L), LH: 1.2 mIU/mL (L), FSH: 2.0 mIU/mL (L), Testosterone: 85 ng/dL (L), Prolactin: 45 ng/mL (H)",
            "symptoms": "Severe headache - frontal, Profound fatigue, Nausea, Visual disturbance - none, Dizziness on standing",
            "notes": "Patient after 4th dose of ipilimumab for melanoma. New severe headache and fatigue over past week. Labs show panhypopituitarism pattern. MRI pituitary shows enlarged gland with heterogeneous enhancement."
        },
        "expected_output": {
            "irae_detected": True,
            "overall_severity": "Grade 3 - Severe",
            "urgency": "urgent",
            "affected_systems": ["Endocrine"],
            "causality": {
                "likelihood": "Highly likely",
                "reasoning": "Patient on ipilimumab (CTLA-4 inhibitor with 5-10% hypophysitis rate) with panhypopituitarism pattern (low ACTH, cortisol, TSH, gonadotropins) and MRI showing enlarged pituitary. Classic immune-related hypophysitis.",
                "temporal_relationship": "After 4th dose of ipilimumab",
                "supporting_factors": ["Ipilimumab (highest hypophysitis risk)", "Panhypopituitarism labs", "MRI showing enlarged pituitary", "Classic headache presentation"],
                "against_factors": []
            },
            "severity_reasoning": "CTCAE Grade 3: Severe symptoms with adrenal insufficiency (cortisol 2.1). Low cortisol is life-threatening and requires immediate treatment.",
            "urgency_reasoning": "Adrenal insufficiency is life-threatening. Patient needs immediate stress-dose hydrocortisone to prevent adrenal crisis.",
            "recommended_actions": [
                {"action": "IMMEDIATE stress-dose hydrocortisone 100mg IV", "priority": 1, "rationale": "Adrenal insufficiency is life-threatening - cortisol replacement is critical"},
                {"action": "Hold ipilimumab", "priority": 1, "rationale": "Grade 3 hypophysitis requires treatment hold"},
                {"action": "Endocrinology consultation urgent", "priority": 1, "rationale": "Specialist input for hormone replacement"},
                {"action": "Start thyroid replacement AFTER cortisol", "priority": 2, "rationale": "CRITICAL: Starting levothyroxine before cortisol can precipitate adrenal crisis"}
            ],
            "key_evidence": ["Cortisol 2.1 ug/dL (critically low)", "ACTH 5 pg/mL (low)", "Panhypopituitarism pattern", "MRI shows enlarged pituitary"]
        }
    },
    {
        "id": "CARD-001",
        "input": {
            "patient_id": "CARD-001",
            "age": 61,
            "cancer_type": "Melanoma",
            "medications": "Ipilimumab 3mg/kg + Nivolumab 1mg/kg IV q3weeks, Metoprolol 25mg BID, Lisinopril 10mg daily",
            "labs": "Troponin I: 2.8 ng/mL (H), CK-MB: 45 ng/mL (H), BNP: 850 pg/mL (H), CRP: 8.5 mg/dL (H), CK: 1200 U/L (H)",
            "symptoms": "Chest pain - substernal, worse with exertion, Dyspnea - progressive, Palpitations, Fatigue - severe, Orthopnea",
            "notes": "Patient on combination ipilimumab/nivolumab for melanoma. Chest pain and dyspnea started 5 days ago. ECG shows diffuse ST changes and low voltage. Echo shows EF 35% (baseline 60%). Troponin elevated. Urgent cardiology consult for suspected ICI myocarditis."
        },
        "expected_output": {
            "irae_detected": True,
            "overall_severity": "Grade 4 - Life-threatening",
            "urgency": "emergency",
            "affected_systems": ["Cardiac"],
            "causality": {
                "likelihood": "Highly likely",
                "reasoning": "Patient on combination ICI with elevated troponin, significantly reduced EF (60% to 35%), elevated BNP, ECG changes, and classic symptoms. This is immune-related myocarditis which has 25-50% mortality.",
                "temporal_relationship": "During combination immunotherapy",
                "supporting_factors": ["Combination ICI (highest myocarditis risk)", "Troponin 2.8 ng/mL", "EF drop from 60% to 35%", "ECG changes", "Elevated CK (possible concurrent myositis)"],
                "against_factors": []
            },
            "severity_reasoning": "CTCAE Grade 4: Life-threatening cardiac dysfunction. Troponin elevation with significant EF reduction indicates severe myocardial injury with high mortality risk.",
            "urgency_reasoning": "ICI myocarditis has 25-50% mortality rate. This is a MEDICAL EMERGENCY requiring immediate ICU admission and high-dose steroids.",
            "recommended_actions": [
                {"action": "IMMEDIATE permanent discontinuation of all ICIs", "priority": 1, "rationale": "Myocarditis requires permanent discontinuation"},
                {"action": "ICU admission with continuous telemetry", "priority": 1, "rationale": "High risk of arrhythmia and hemodynamic collapse"},
                {"action": "IV methylprednisolone 1g daily", "priority": 1, "rationale": "High-dose steroids for life-threatening myocarditis"},
                {"action": "Emergent cardiology consultation", "priority": 1, "rationale": "Specialist input critical for management"},
                {"action": "Serial troponin and telemetry monitoring", "priority": 1, "rationale": "Monitor for progression"},
                {"action": "Have IVIG and plasmapheresis available", "priority": 2, "rationale": "May need escalation if steroid-refractory"}
            ],
            "key_evidence": ["Troponin I 2.8 ng/mL", "EF 35% (baseline 60%)", "BNP 850", "ECG changes", "Combination ICI"]
        }
    },
    {
        "id": "NEURO-001",
        "input": {
            "patient_id": "NEURO-001",
            "age": 68,
            "cancer_type": "Small cell lung cancer",
            "medications": "Nivolumab 240mg IV q2weeks, Pyridostigmine 60mg TID (started 2 days ago)",
            "labs": "CK: 180 U/L, Acetylcholine receptor antibodies: positive, Anti-striated muscle antibodies: positive, Troponin: 0.08 ng/mL (slightly elevated)",
            "symptoms": "Bilateral ptosis, Diplopia, Dysphagia - mild, Proximal muscle weakness, Fatigue worse with activity",
            "notes": "Patient on nivolumab for extensive stage SCLC. Developed ptosis and diplopia over 1 week. Fatigable weakness on exam. Ice pack test positive. AChR antibodies positive. Concerned for irAE MG. Monitor for respiratory involvement."
        },
        "expected_output": {
            "irae_detected": True,
            "overall_severity": "Grade 2 - Moderate",
            "urgency": "urgent",
            "affected_systems": ["Neurologic"],
            "causality": {
                "likelihood": "Highly likely",
                "reasoning": "Patient on PD-1 inhibitor with positive AChR antibodies, positive anti-striated muscle antibodies, and classic MG symptoms (ptosis, diplopia, fatigable weakness). The anti-striated muscle antibodies indicate 20-40% risk of concurrent myocarditis.",
                "temporal_relationship": "During active immunotherapy",
                "supporting_factors": ["On checkpoint inhibitor", "AChR antibodies positive", "Anti-striated muscle antibodies positive", "Classic MG symptoms", "Slightly elevated troponin"],
                "against_factors": []
            },
            "severity_reasoning": "CTCAE Grade 2 but URGENT due to MG crisis risk and concurrent myocarditis concern. Dysphagia indicates bulbar involvement.",
            "urgency_reasoning": "ICI-related MG can progress rapidly to respiratory failure. Anti-striated muscle antibodies + elevated troponin suggest possible concurrent myocarditis. Requires urgent evaluation.",
            "recommended_actions": [
                {"action": "Permanently discontinue nivolumab", "priority": 1, "rationale": "ICI-related MG requires permanent discontinuation"},
                {"action": "Neurology consultation urgent", "priority": 1, "rationale": "Specialist input for MG management"},
                {"action": "Serial FVC monitoring q4-6h", "priority": 1, "rationale": "Monitor for MG crisis and respiratory failure"},
                {"action": "Check troponin daily and get cardiac workup", "priority": 1, "rationale": "Anti-striated muscle antibodies indicate myocarditis risk"},
                {"action": "Start prednisone 1mg/kg", "priority": 1, "rationale": "Steroids for immune-related MG"}
            ],
            "key_evidence": ["AChR antibodies positive", "Anti-striated muscle antibodies positive", "Troponin 0.08", "Ptosis and diplopia", "Dysphagia"]
        }
    },
    {
        "id": "NEURO-002",
        "input": {
            "patient_id": "NEURO-002",
            "age": 54,
            "cancer_type": "Non-small cell lung cancer",
            "medications": "Pembrolizumab 200mg IV q3weeks, Levetiracetam 1000mg BID (started after seizure), Methylprednisolone 1g IV daily",
            "labs": "CSF: WBC 45 (lymphocyte predominant), CSF protein: 85 mg/dL (H), CSF glucose: 55 mg/dL (normal), MRI brain: bilateral medial temporal lobe hyperintensity",
            "symptoms": "Confusion - acute onset, Memory impairment, Seizure - witnessed generalized tonic-clonic, Headache, Personality change",
            "notes": "Patient on pembrolizumab for NSCLC. Acute confusion and witnessed seizure 3 days ago. MRI shows bilateral medial temporal lobe T2 hyperintensity. LP shows lymphocytic pleocytosis. Autoimmune encephalitis workup sent. Started high-dose steroids."
        },
        "expected_output": {
            "irae_detected": True,
            "overall_severity": "Grade 3 - Severe",
            "urgency": "emergency",
            "affected_systems": ["Neurologic"],
            "causality": {
                "likelihood": "Highly likely",
                "reasoning": "Patient on pembrolizumab with acute encephalopathy, seizure, bilateral medial temporal lobe MRI findings (limbic encephalitis pattern), and inflammatory CSF (lymphocytic pleocytosis with elevated protein). Classic immune-related encephalitis.",
                "temporal_relationship": "During active immunotherapy",
                "supporting_factors": ["On checkpoint inhibitor", "Limbic encephalitis pattern on MRI", "Inflammatory CSF", "Seizure", "Acute confusion"],
                "against_factors": ["Normal CSF glucose argues against infectious meningitis"]
            },
            "severity_reasoning": "CTCAE Grade 3-4: Seizure and significant encephalopathy indicate severe neurologic toxicity requiring ICU-level monitoring.",
            "urgency_reasoning": "Immune-related encephalitis with seizure is a neurologic emergency requiring ICU admission, high-dose steroids, and close monitoring.",
            "recommended_actions": [
                {"action": "Permanently discontinue pembrolizumab", "priority": 1, "rationale": "Severe neurologic toxicity requires permanent discontinuation"},
                {"action": "Continue IV methylprednisolone 1g daily x 3-5 days", "priority": 1, "rationale": "High-dose steroids for encephalitis"},
                {"action": "Neurology consultation urgent", "priority": 1, "rationale": "Specialist input critical"},
                {"action": "EEG monitoring", "priority": 1, "rationale": "Monitor for subclinical seizures"},
                {"action": "ICU admission for neuro monitoring", "priority": 1, "rationale": "Encephalitis with seizure requires close monitoring"},
                {"action": "Consider IVIG if steroid-refractory", "priority": 2, "rationale": "May need additional immunosuppression"}
            ],
            "key_evidence": ["Bilateral medial temporal hyperintensity", "CSF WBC 45 (lymphocytic)", "CSF protein 85", "Witnessed seizure", "Acute confusion"]
        }
    }
]


def generate_training_prompt(example: Dict[str, Any]) -> str:
    """Generate the instruction prompt for training."""
    input_data = example["input"]
    
    prompt = f"""You are a clinical oncology AI assistant specializing in detecting immune-related adverse events (irAEs) in patients on checkpoint inhibitor immunotherapy.

Analyze the following patient data and provide a structured assessment:

Patient ID: {input_data['patient_id']}
Age: {input_data['age']}
Cancer Type: {input_data['cancer_type']}

MEDICATIONS:
{input_data['medications']}

LABORATORY VALUES:
{input_data['labs']}

SYMPTOMS:
{input_data['symptoms']}

CLINICAL NOTES:
{input_data['notes']}

Based on CTCAE v5.0 grading criteria and ASCO irAE management guidelines, provide your assessment in JSON format with the following structure:
- irae_detected (boolean)
- overall_severity (Grade 1-4 or Unknown)
- urgency (routine/soon/urgent/emergency)
- affected_systems (list of organ systems)
- causality (likelihood, reasoning, temporal_relationship, supporting_factors, against_factors)
- severity_reasoning (explanation of CTCAE grade)
- urgency_reasoning (explanation of triage level)
- recommended_actions (list with action, priority, rationale)
- key_evidence (list of key findings)

IMPORTANT RULES:
1. Grade 2 irAEs require at minimum "soon" urgency (oncology review needed)
2. Grade 3 irAEs require at minimum "urgent" urgency
3. Grade 4 irAEs or cardiac/neuro involvement require "emergency" urgency
4. Always err on the side of higher urgency for patient safety"""
    
    return prompt


def generate_training_response(example: Dict[str, Any]) -> str:
    """Generate the expected response for training."""
    return json.dumps(example["expected_output"], indent=2)


def create_training_dataset() -> List[Dict[str, str]]:
    """Create the full training dataset."""
    dataset = []
    
    for example in TRAINING_EXAMPLES:
        dataset.append({
            "id": example["id"],
            "prompt": generate_training_prompt(example),
            "response": generate_training_response(example),
        })
    
    return dataset


def save_training_data(output_path: str = "training_data.jsonl"):
    """Save training data in JSONL format for fine-tuning."""
    dataset = create_training_dataset()
    
    with open(output_path, 'w') as f:
        for item in dataset:
            # Format for instruction tuning
            training_item = {
                "messages": [
                    {"role": "user", "content": item["prompt"]},
                    {"role": "assistant", "content": item["response"]}
                ]
            }
            f.write(json.dumps(training_item) + '\n')
    
    print(f"Saved {len(dataset)} training examples to {output_path}")
    return output_path


if __name__ == "__main__":
    import os
    # Save in current directory
    output_file = os.path.join(os.path.dirname(__file__), "training_data.jsonl")
    save_training_data(output_file)
