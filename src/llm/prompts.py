"""System prompts and prompt templates for irAE assessment."""

from typing import Optional
from ..models.patient import PatientData


class SystemPrompts:
    """System prompts for the clinical safety assistant."""
    
    IRAE_ASSESSMENT = """You are an AI clinical safety assistant specialized in oncology immunotherapy.
Your task is to identify, classify, and triage immune-related adverse events (irAEs) from clinical data.

You assist clinicians by:
- Detecting possible irAEs
- Estimating likelihood the event is immunotherapy-related
- Grading severity (CTCAE-style)
- Recommending urgency and next action
- Citing supporting evidence from the patient data

You do not replace clinical judgment. You act as an early warning and structured reasoning system.

🧬 DOMAIN CONTEXT

Immune checkpoint inhibitors (ICIs) such as PD-1, PD-L1, and CTLA-4 therapies can cause immune-related adverse events (irAEs) affecting:
- Skin
- GI tract (colitis, diarrhea)
- Liver (hepatitis, ↑AST/ALT)
- Lungs (pneumonitis)
- Endocrine (thyroiditis, hypophysitis, adrenal insufficiency)
- Neurologic, cardiac, renal (rare but severe)

irAEs are often:
- Subtle early
- Buried in notes, labs, vitals, or patient messages
- Missed until severe

Your job is pattern recognition across multimodal clinical text and structured data.

🧠 TASK LOGIC

When reviewing a case:

Step 1 — Confirm Immunotherapy Context
Determine if the patient is receiving or recently received:
- PD-1 / PD-L1 inhibitors
- CTLA-4 inhibitors
- Combination immunotherapy
If not present → still analyze but lower irAE likelihood.

Step 2 — Detect Possible Toxicity Signals
Look for patterns like:
- GI: Diarrhea, abdominal pain, blood in stool
- Liver: ↑AST/ALT, ↑bilirubin, fatigue
- Lung: Cough, dyspnea, hypoxia, new infiltrates
- Endocrine: Fatigue, hypotension, headache, hyponatremia, low TSH, cortisol
- Skin: Rash, pruritus
- Neuro: Weakness, confusion, neuropathy
- Cardiac: Chest pain, troponin ↑

Step 3 — Causality Reasoning
Estimate whether this is likely:
- Highly likely irAE
- Possible irAE
- Unlikely irAE
- More consistent with infection, progression, or other cause

Use:
- Temporal relation to immunotherapy
- Multi-system involvement
- Lab patterns typical of autoimmunity
- Absence of clear alternative cause

Step 4 — Severity Assessment
Map to a CTCAE-style severity level:
- Grade 1 – Mild
- Grade 2 – Moderate
- Grade 3 – Severe
- Grade 4 – Life-threatening

Step 5 — Clinical Triage
Classify urgency:
- 🟢 Routine monitoring
- 🟡 Needs oncology review soon
- 🟠 Urgent (same day)
- 🔴 Emergency evaluation

🚫 SAFETY RULES
- Do not prescribe drugs or dosages
- Do not give definitive diagnoses
- Always express uncertainty when evidence is incomplete
- Emphasize clinician confirmation"""

    JSON_OUTPUT_SCHEMA = """
Respond with a JSON object following this exact structure:
{
    "immunotherapy_context": {
        "on_immunotherapy": boolean,
        "agents": ["list of agent names"],
        "drug_classes": ["PD-1", "PD-L1", "CTLA-4"],
        "combination_therapy": boolean,
        "context_notes": "string describing timing and context"
    },
    "irae_detected": boolean,
    "affected_systems": [
        {
            "system": "system name",
            "detected": boolean,
            "findings": ["list of findings"],
            "evidence": ["supporting evidence"],
            "severity": "Grade 1-4 or Unknown"
        }
    ],
    "causality": {
        "likelihood": "Highly likely | Possible | Unlikely | Uncertain",
        "reasoning": "explanation",
        "temporal_relationship": "timing description",
        "alternative_causes": ["other possible causes"],
        "supporting_factors": ["factors supporting irAE"],
        "against_factors": ["factors against irAE"]
    },
    "overall_severity": "Grade 1 - Mild | Grade 2 - Moderate | Grade 3 - Severe | Grade 4 - Life-threatening | Unknown",
    "severity_reasoning": "explanation",
    "urgency": "routine | soon | urgent | emergency",
    "urgency_reasoning": "explanation",
    "recommended_actions": [
        {
            "action": "action description",
            "priority": 1-5,
            "rationale": "why this action"
        }
    ],
    "key_evidence": ["important data points"]
}"""


class PromptBuilder:
    """Build prompts for irAE assessment."""
    
    @staticmethod
    def build_assessment_prompt(patient_data: PatientData) -> str:
        """
        Build the user prompt for irAE assessment.
        
        Args:
            patient_data: Patient clinical data
            
        Returns:
            Formatted prompt string
        """
        sections = ["Analyze the following oncology patient data for possible immune-related adverse events.\n"]
        
        # Patient context
        if patient_data.patient_id or patient_data.age or patient_data.cancer_type:
            sections.append("## Patient Context")
            if patient_data.patient_id:
                sections.append(f"Patient ID: {patient_data.patient_id}")
            if patient_data.age:
                sections.append(f"Age: {patient_data.age}")
            if patient_data.cancer_type:
                sections.append(f"Cancer Type: {patient_data.cancer_type}")
            sections.append("")
        
        # Medications
        if patient_data.medications or patient_data.raw_medications:
            sections.append("## Medications")
            if patient_data.medications:
                for med in patient_data.medications:
                    med_str = f"- {med.name}"
                    if med.dose:
                        med_str += f" {med.dose}"
                    if med.frequency:
                        med_str += f" {med.frequency}"
                    if med.is_immunotherapy:
                        med_str += " [IMMUNOTHERAPY]"
                    sections.append(med_str)
            if patient_data.raw_medications:
                sections.append(patient_data.raw_medications)
            sections.append("")
        
        # Labs
        if patient_data.labs or patient_data.raw_labs:
            sections.append("## Laboratory Results")
            if patient_data.labs:
                for lab in patient_data.labs:
                    flag = " [ABNORMAL]" if lab.is_abnormal else ""
                    sections.append(
                        f"- {lab.name}: {lab.value} {lab.unit}{flag} "
                        f"(ref: {lab.reference_low}-{lab.reference_high})"
                    )
            if patient_data.raw_labs:
                sections.append(patient_data.raw_labs)
            sections.append("")
        
        # Vitals
        if patient_data.vitals:
            sections.append("## Vital Signs")
            for vital in patient_data.vitals:
                vital_parts = []
                if vital.temperature:
                    vital_parts.append(f"Temp: {vital.temperature}°C")
                if vital.heart_rate:
                    vital_parts.append(f"HR: {vital.heart_rate}")
                if vital.blood_pressure_systolic:
                    vital_parts.append(
                        f"BP: {vital.blood_pressure_systolic}/{vital.blood_pressure_diastolic or '?'}"
                    )
                if vital.respiratory_rate:
                    vital_parts.append(f"RR: {vital.respiratory_rate}")
                if vital.oxygen_saturation:
                    vital_parts.append(f"SpO2: {vital.oxygen_saturation}%")
                if vital_parts:
                    sections.append(f"- {vital.date.strftime('%Y-%m-%d')}: {', '.join(vital_parts)}")
            sections.append("")
        
        # Symptoms
        if patient_data.symptoms or patient_data.raw_symptoms:
            sections.append("## Patient Symptoms")
            if patient_data.symptoms:
                for symptom in patient_data.symptoms:
                    sev = f" ({symptom.severity})" if symptom.severity else ""
                    sections.append(f"- {symptom.symptom}{sev}")
            if patient_data.raw_symptoms:
                sections.append(patient_data.raw_symptoms)
            sections.append("")
        
        # Clinical Notes
        if patient_data.notes or patient_data.raw_notes:
            sections.append("## Clinical Notes")
            if patient_data.notes:
                for note in patient_data.notes:
                    sections.append(f"### {note.note_type.title()} ({note.date.strftime('%Y-%m-%d')})")
                    sections.append(note.content)
                    sections.append("")
            if patient_data.raw_notes:
                sections.append("### Additional Notes")
                sections.append(patient_data.raw_notes)
            sections.append("")
        
        # Imaging
        if patient_data.imaging:
            sections.append("## Imaging Studies")
            for img in patient_data.imaging:
                sections.append(f"### {img.modality} - {img.body_region} ({img.date.strftime('%Y-%m-%d')})")
                sections.append(f"Findings: {img.findings}")
                if img.impression:
                    sections.append(f"Impression: {img.impression}")
                sections.append("")
        
        return "\n".join(sections)
    
    @staticmethod
    def build_full_system_prompt(include_json_schema: bool = True) -> str:
        """Build complete system prompt with optional JSON schema."""
        prompt = SystemPrompts.IRAE_ASSESSMENT
        if include_json_schema:
            prompt += "\n\n" + SystemPrompts.JSON_OUTPUT_SCHEMA
        return prompt
