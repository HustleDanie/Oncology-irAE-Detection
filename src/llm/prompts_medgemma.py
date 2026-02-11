"""
Optimized prompts for MedGemma 4B model.

MedGemma has limited context window, so prompts must be concise.
The model is already trained on medical knowledge, so we don't need
extensive clinical guidelines - just clear task instructions.
"""

from typing import Optional
from ..models.patient import PatientData


class MedGemmaPrompts:
    """Concise prompts optimized for MedGemma 4B context limits."""
    
    SYSTEM_PROMPT = """You are MedGemma, a clinical AI assistant for oncology immunotherapy safety.

TASK: Analyze patient data for immune-related adverse events (irAEs) from checkpoint inhibitors.

CHECKPOINT INHIBITORS:
- PD-1: pembrolizumab, nivolumab, cemiplimab
- PD-L1: atezolizumab, durvalumab, avelumab  
- CTLA-4: ipilimumab, tremelimumab

ORGAN SYSTEMS TO CHECK:
- GI: diarrhea, colitis (count stools/day)
- Hepatic: elevated AST/ALT (grade by x ULN)
- Pulmonary: pneumonitis, hypoxia
- Endocrine: thyroid dysfunction, adrenal insufficiency
- Cardiac: myocarditis (ALWAYS EMERGENCY)
- Neurologic: encephalitis, myasthenia (ALWAYS URGENT)
- Skin: rash, pruritus
- Renal: nephritis
- Hematologic: cytopenias

CTCAE GRADING:
- Grade 1: Mild, asymptomatic
- Grade 2: Moderate, limiting daily activities  
- Grade 3: Severe, hospitalization needed
- Grade 4: Life-threatening

URGENCY RULES:
- Grade 1 → routine
- Grade 2 → soon (1-3 days)
- Grade 3 → urgent (same day)
- Grade 4 → emergency
- Cardiac/Neuro → always urgent minimum

OUTPUT: Respond with a JSON object only, no other text."""

    JSON_SCHEMA = """{
  "irae_detected": true/false,
  "affected_systems": [{"system": "name", "detected": true/false, "severity": "Grade 1-4"}],
  "overall_severity": "Grade 1-4 or Unknown",
  "urgency": "routine|soon|urgent|emergency",
  "causality": {"likelihood": "Highly likely|Possible|Unlikely|Uncertain", "reasoning": "..."},
  "severity_reasoning": "brief CTCAE rationale",
  "urgency_reasoning": "brief urgency rationale", 
  "recommended_actions": [{"action": "...", "priority": 1-5}],
  "key_evidence": ["evidence1", "evidence2"]
}"""


class MedGemmaPromptBuilder:
    """Build concise prompts for MedGemma."""
    
    @staticmethod
    def build_system_prompt() -> str:
        """Build the complete system prompt."""
        return f"{MedGemmaPrompts.SYSTEM_PROMPT}\n\nJSON FORMAT:\n{MedGemmaPrompts.JSON_SCHEMA}"
    
    @staticmethod
    def build_user_prompt(patient_data: PatientData) -> str:
        """Build a concise user prompt with patient data."""
        parts = ["PATIENT DATA:\n"]
        
        # Basic info
        if patient_data.age:
            parts.append(f"Age: {patient_data.age}")
        if patient_data.cancer_type:
            parts.append(f"Cancer: {patient_data.cancer_type}")
        
        # Medications (critical for ICI detection)
        meds = []
        if patient_data.medications:
            meds = [m.name for m in patient_data.medications]
        if patient_data.raw_medications:
            meds.append(patient_data.raw_medications)
        if meds:
            parts.append(f"\nMedications: {', '.join(meds)}")
        
        # Labs (keep concise)
        labs = []
        if patient_data.labs:
            for lab in patient_data.labs:
                flag = "*" if lab.is_abnormal else ""
                labs.append(f"{lab.name}: {lab.value}{flag}")
        if patient_data.raw_labs:
            labs.append(patient_data.raw_labs)
        if labs:
            parts.append(f"\nLabs: {', '.join(labs[:10])}")  # Limit to 10 labs
        
        # Symptoms
        symptoms = []
        if patient_data.symptoms:
            symptoms = [s.symptom for s in patient_data.symptoms]
        if patient_data.raw_symptoms:
            symptoms.append(patient_data.raw_symptoms)
        if symptoms:
            parts.append(f"\nSymptoms: {', '.join(symptoms)}")
        
        # Notes (truncate if too long)
        notes = []
        if patient_data.notes:
            notes = [n.content[:200] for n in patient_data.notes]  # Truncate each note
        if patient_data.raw_notes:
            notes.append(patient_data.raw_notes[:500])  # Truncate raw notes
        if notes:
            parts.append(f"\nClinical Notes: {' '.join(notes)}")
        
        parts.append("\n\nAnalyze for irAEs and respond with JSON only:")
        
        return "\n".join(parts)
