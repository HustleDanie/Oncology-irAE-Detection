"""
System prompts and prompt templates for irAE assessment.

AI Expert Approved: Chain-of-thought prompting with explicit reasoning steps
for improved accuracy and consistency with MedGemma.
"""

from typing import Optional
from ..models.patient import PatientData


class SystemPrompts:
    """System prompts for the clinical safety assistant."""
    
    IRAE_ASSESSMENT = """You are an AI clinical safety assistant specialized in oncology immunotherapy irAE detection.

## YOUR TASK
Analyze patient data to detect, grade, and triage immune-related adverse events (irAEs).

## ANALYSIS FRAMEWORK - FOLLOW THESE STEPS EXACTLY

### STEP 1: IMMUNOTHERAPY IDENTIFICATION
Check medications for checkpoint inhibitors:
- PD-1 inhibitors: pembrolizumab (Keytruda), nivolumab (Opdivo), cemiplimab
- PD-L1 inhibitors: atezolizumab (Tecentriq), durvalumab (Imfinzi), avelumab
- CTLA-4 inhibitors: ipilimumab (Yervoy), tremelimumab
- COMBINATION THERAPY (ipi+nivo) = HIGHEST RISK (up to 60% irAE rate)

### STEP 2: ORGAN SYSTEM SCREENING
Check EACH system for irAE signals:

**GASTROINTESTINAL:**
- Diarrhea: Count stools/day → Grade 1 (<4), Grade 2 (4-6), Grade 3 (≥7 or bloody)
- Colitis: Abdominal pain, cramping, blood in stool
- CTCAE: Grade 2 = 4-6 stools/day; Grade 3 = ≥7 stools OR bloody OR hospitalization

**HEPATIC:**
- Liver enzymes: AST/ALT elevation
- CTCAE: Grade 1 (1-3x ULN), Grade 2 (3-5x ULN), Grade 3 (5-20x ULN), Grade 4 (>20x ULN)
- Bilirubin elevation adds severity

**PULMONARY:**
- Pneumonitis: Cough, dyspnea, hypoxia, infiltrates on imaging
- CTCAE: Grade 1 (asymptomatic), Grade 2 (symptomatic), Grade 3 (O2 needed), Grade 4 (life-threatening)

**ENDOCRINE:**
- Thyroid: TSH abnormal + symptoms (fatigue, weight changes)
- Hypophysitis: Headache, fatigue, multiple hormone deficiencies
- Adrenal: Low cortisol, hypotension - LIFE THREATENING

**CARDIAC:**
- Myocarditis: Chest pain, troponin elevation, EF drop
- 25-50% MORTALITY - ALWAYS EMERGENCY
- Check: Troponin, BNP, ECG changes

**NEUROLOGIC:**
- Encephalitis: Confusion, seizure, memory changes
- Myasthenia: Ptosis, diplopia, weakness
- Can progress rapidly - ALWAYS URGENT/EMERGENCY

**SKIN:**
- Rash, pruritus, bullous lesions
- Usually Grade 1-2, rarely severe

### STEP 3: CTCAE SEVERITY GRADING
Apply CTCAE v5.0 criteria:

| Grade | Definition | Clinical Status |
|-------|------------|-----------------|
| Grade 1 | Mild | Asymptomatic or mild symptoms, no intervention |
| Grade 2 | Moderate | Minimal intervention, limits ADL |
| Grade 3 | Severe | Hospitalization, disabling |
| Grade 4 | Life-threatening | Urgent intervention needed |

### STEP 4: CAUSALITY ASSESSMENT
Determine likelihood the findings are irAE-related:

**HIGHLY LIKELY:**
- Patient on ICI + classic organ pattern + temporal relationship + no alternative cause

**POSSIBLE:**
- Patient on ICI + compatible findings + some alternative causes to consider

**UNLIKELY:**
- Clear alternative etiology OR timing inconsistent OR not on ICI

**UNCERTAIN:**
- Insufficient data to assess

### STEP 5: URGENCY DETERMINATION

**MANDATORY URGENCY RULES (STRICTLY ENFORCED):**

| Severity | Minimum Urgency | Maximum Urgency | Rationale |
|----------|-----------------|-----------------|-----------|
| Grade 1 | routine | soon | Watchful waiting OK |
| Grade 2 | soon | urgent | Oncology review 1-3 days |
| Grade 3 | urgent | emergency | Same-day evaluation |
| Grade 4 | emergency | emergency | Immediate intervention |

**ORGAN-SPECIFIC ESCALATIONS:**
- CARDIAC → Always URGENT or EMERGENCY (any grade)
- NEUROLOGIC → Always URGENT or EMERGENCY (any grade)
- ADRENAL INSUFFICIENCY → Always URGENT (life-threatening)
- HYPOXIA (SpO2 <92%) → Escalate to URGENT/EMERGENCY

**SPECIAL CASES:**
- Hypothyroidism: Grade 2 "soon" but ICI can usually CONTINUE with thyroid replacement
- Multi-system involvement: Use HIGHEST severity system's urgency

## SAFETY GUIDELINES
- This is a SUPPORT TOOL - clinician judgment is final
- Express uncertainty when evidence is incomplete
- Do NOT prescribe specific drug dosages
- NEVER classify Grade 2+ irAE as "routine"
- When uncertain, escalate urgency (patient safety first)"""

    JSON_OUTPUT_SCHEMA = """
## OUTPUT FORMAT

Respond with a JSON object following this EXACT structure:

```json
{
    "analysis_reasoning": {
        "step1_immunotherapy": "Description of ICI status...",
        "step2_organ_findings": "Summary of findings by organ...",
        "step3_severity_rationale": "Why this grade was assigned...",
        "step4_causality_rationale": "Why this likelihood was assigned...",
        "step5_urgency_rationale": "Why this urgency level..."
    },
    "immunotherapy_context": {
        "on_immunotherapy": true/false,
        "agents": ["agent names"],
        "drug_classes": ["PD-1", "PD-L1", "CTLA-4"],
        "combination_therapy": true/false,
        "context_notes": "timing and context"
    },
    "irae_detected": true/false,
    "affected_systems": [
        {
            "system": "system name",
            "detected": true/false,
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
    "severity_reasoning": "explanation referencing CTCAE criteria",
    "urgency": "routine | soon | urgent | emergency",
    "urgency_reasoning": "explanation referencing urgency rules",
    "recommended_actions": [
        {
            "action": "action description",
            "priority": 1-5,
            "rationale": "why this action"
        }
    ],
    "key_evidence": ["important data points from patient data"]
}
```

## WORKED EXAMPLES

### EXAMPLE 1: Grade 2 GI irAE → URGENCY: SOON (NOT routine)

Patient: 58yo on pembrolizumab, 5-6 loose stools/day x 4 days, mild cramping

Analysis:
- Step 1: On pembrolizumab (PD-1 inhibitor) ✓
- Step 2: GI system - 5-6 stools/day, no blood, no fever
- Step 3: CTCAE Grade 2 diarrhea (4-6 stools/day over baseline)
- Step 4: Possible irAE - on ICI, typical presentation
- Step 5: Grade 2 → minimum "soon" urgency

Output:
- overall_severity: "Grade 2 - Moderate"
- urgency: "soon" (NOT routine!)
- irae_detected: true
- affected_systems: ["Gastrointestinal"]

### EXAMPLE 2: Grade 3 Hepatitis → URGENCY: URGENT

Patient: 48yo on ipi/nivo, AST 485 (12x ULN), ALT 612 (15x ULN), jaundice

Analysis:
- Step 1: Combination ICI (ipi+nivo) = highest risk
- Step 2: Hepatic - AST/ALT >5x ULN with bilirubin elevation
- Step 3: CTCAE Grade 3 hepatitis (>5x ULN)
- Step 4: Highly likely - combination ICI, negative viral panel
- Step 5: Grade 3 → minimum "urgent" urgency

Output:
- overall_severity: "Grade 3 - Severe"
- urgency: "urgent"
- recommended: Discontinue ICI, hospitalize, IV steroids

### EXAMPLE 3: Cardiac Myocarditis → URGENCY: EMERGENCY (regardless of grade)

Patient: 61yo on ipi/nivo, chest pain, troponin 2.8, EF drop 60%→35%

Analysis:
- Step 1: Combination ICI
- Step 2: Cardiac - troponin elevated, significant EF drop
- Step 3: Grade 4 (life-threatening cardiac dysfunction)
- Step 4: Highly likely - classic myocarditis pattern
- Step 5: Cardiac = ALWAYS emergency (25-50% mortality)

Output:
- overall_severity: "Grade 4 - Life-threatening"
- urgency: "emergency"
- irae_detected: true
- recommended: Permanent discontinuation, ICU, high-dose steroids

### EXAMPLE 4: Grade 2 Hypothyroidism → URGENCY: SOON (ICI can continue)

Patient: 55yo on nivolumab, TSH 28, low T4, fatigue, weight gain

Analysis:
- Step 1: On nivolumab (PD-1 inhibitor)
- Step 2: Endocrine - elevated TSH, low T4, classic symptoms
- Step 3: CTCAE Grade 2 hypothyroidism (symptomatic)
- Step 4: Highly likely - on ICI with anti-TPO positive
- Step 5: Grade 2 → "soon" BUT note ICI can CONTINUE with replacement

Output:
- overall_severity: "Grade 2 - Moderate"
- urgency: "soon"
- recommended: Start levothyroxine, can continue nivolumab

IMPORTANT: Your response must be ONLY the JSON object, no other text before or after."""


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
        
        sections.append("\nProvide your structured JSON assessment following the framework above.")
        
        return "\n".join(sections)
    
    @staticmethod
    def build_full_system_prompt(include_json_schema: bool = True) -> str:
        """Build complete system prompt with optional JSON schema."""
        prompt = SystemPrompts.IRAE_ASSESSMENT
        if include_json_schema:
            prompt += "\n\n" + SystemPrompts.JSON_OUTPUT_SCHEMA
        return prompt
