"""Endocrine irAE analyzer for thyroid/adrenal/pituitary toxicity detection."""

from typing import Optional

from ..models.patient import PatientData, LabResult
from ..models.assessment import OrganSystemFinding, OrganSystem, Severity
from .base import BaseAnalyzer


class EndocrineAnalyzer(BaseAnalyzer):
    """Analyzer for endocrine immune-related adverse events."""
    
    def __init__(self):
        super().__init__()
        self.organ_system = OrganSystem.ENDOCRINE
        self.key_symptoms = [
            "fatigue", "weakness", "lethargy",
            "weight gain", "weight loss",
            "cold intolerance", "heat intolerance",
            "headache", "vision changes", "visual field",
            "hypotension", "low blood pressure", "orthostatic",
            "nausea", "vomiting", "anorexia",
            "polyuria", "polydipsia", "increased thirst",
            "constipation", "hair loss", "dry skin",
            "bradycardia", "tachycardia",
        ]
        self.key_labs = [
            "TSH", "T4", "free T4", "T3", "free T3",
            "cortisol", "ACTH",
            "glucose", "HbA1c",
            "sodium", "potassium",
            "LH", "FSH", "testosterone", "estradiol",
        ]
        self.conditions = [
            "thyroiditis", "hypothyroidism", "hyperthyroidism",
            "hypophysitis", "adrenal insufficiency", "adrenalitis",
            "diabetes", "hyperglycemia", "diabetic ketoacidosis", "dka",
            "hyponatremia",
        ]
    
    def analyze(self, patient_data: PatientData) -> OrganSystemFinding:
        """Analyze patient data for endocrine irAE signals."""
        findings = []
        evidence = []
        detected = False
        severity = None
        confidence = 0.0
        
        # Check endocrine labs
        relevant_labs = self._find_relevant_labs(patient_data.labs, self.key_labs)
        abnormal_labs = self._get_abnormal_labs(relevant_labs)
        
        # Specific endocrine pattern detection
        thyroid_pattern = self._detect_thyroid_dysfunction(relevant_labs)
        adrenal_pattern = self._detect_adrenal_dysfunction(relevant_labs)
        glucose_pattern = self._detect_glucose_abnormality(relevant_labs)
        
        if thyroid_pattern:
            detected = True
            findings.append(f"Thyroid dysfunction pattern: {thyroid_pattern['type']}")
            for lab in thyroid_pattern['labs']:
                evidence.append(f"{lab.name} = {lab.value} {lab.unit}")
            confidence += 0.5
            severity = thyroid_pattern.get('severity', Severity.GRADE_2)
        
        if adrenal_pattern:
            detected = True
            findings.append(f"Possible adrenal insufficiency")
            for lab in adrenal_pattern['labs']:
                evidence.append(f"{lab.name} = {lab.value} {lab.unit}")
            confidence += 0.5
            severity = Severity.GRADE_3  # Adrenal insufficiency is typically severe
        
        if glucose_pattern:
            detected = True
            findings.append(f"Glucose abnormality: {glucose_pattern['type']}")
            for lab in glucose_pattern['labs']:
                evidence.append(f"{lab.name} = {lab.value} {lab.unit}")
            confidence += 0.4
            if glucose_pattern['type'] == 'severe_hyperglycemia':
                severity = Severity.GRADE_3
        
        # Other abnormal endocrine labs
        for lab in abnormal_labs:
            if lab.name not in [e.split('=')[0].strip() for e in evidence]:
                findings.append(f"Abnormal {lab.name}: {lab.value} {lab.unit}")
                evidence.append(f"{lab.name} = {lab.value}")
                confidence += 0.2
        
        # Check symptoms
        relevant_symptoms = self._find_relevant_symptoms(
            patient_data.symptoms, self.key_symptoms
        )
        
        if relevant_symptoms:
            detected = True
            for symptom in relevant_symptoms:
                findings.append(f"Patient reports {symptom.symptom}")
                evidence.append(symptom.symptom)
            confidence += 0.2 * len(relevant_symptoms)
        
        # Check clinical notes
        all_notes = " ".join([n.content for n in patient_data.notes])
        if patient_data.raw_notes:
            all_notes += " " + patient_data.raw_notes
        if patient_data.raw_labs:
            all_notes += " " + patient_data.raw_labs
        
        found_conditions = self._check_text_for_keywords(all_notes, self.conditions)
        if found_conditions:
            detected = True
            for condition in found_conditions:
                findings.append(f"Documentation mentions: {condition}")
                evidence.append(f"Condition: {condition}")
            confidence += 0.4
        
        # Check vitals for hypotension
        hypotension = self._check_vitals_for_hypotension(patient_data.vitals)
        if hypotension:
            detected = True
            findings.append(f"Hypotension: BP {hypotension}")
            evidence.append(f"BP = {hypotension}")
            confidence += 0.3
        
        confidence = min(confidence, 1.0)
        
        return self._create_finding(
            detected=detected,
            findings=findings,
            evidence=evidence,
            severity=severity,
            confidence=confidence if detected else None,
        )
    
    def _detect_thyroid_dysfunction(self, labs: list[LabResult]) -> Optional[dict]:
        """Detect thyroid dysfunction patterns."""
        tsh = None
        t4 = None
        
        for lab in labs:
            lab_lower = lab.name.lower()
            if 'tsh' in lab_lower:
                tsh = lab
            elif 't4' in lab_lower or 'free t4' in lab_lower:
                t4 = lab
        
        if not tsh:
            return None
        
        # Hypothyroidism: High TSH, Low T4
        if tsh.reference_high and tsh.value > tsh.reference_high:
            return {
                'type': 'Hypothyroidism (elevated TSH)',
                'labs': [lab for lab in [tsh, t4] if lab],
                'severity': Severity.GRADE_2,
            }
        
        # Hyperthyroidism: Low TSH
        if tsh.reference_low and tsh.value < tsh.reference_low:
            return {
                'type': 'Hyperthyroidism (suppressed TSH)',
                'labs': [lab for lab in [tsh, t4] if lab],
                'severity': Severity.GRADE_2,
            }
        
        return None
    
    def _detect_adrenal_dysfunction(self, labs: list[LabResult]) -> Optional[dict]:
        """Detect adrenal insufficiency patterns."""
        cortisol = None
        acth = None
        sodium = None
        
        for lab in labs:
            lab_lower = lab.name.lower()
            if 'cortisol' in lab_lower:
                cortisol = lab
            elif 'acth' in lab_lower:
                acth = lab
            elif 'sodium' in lab_lower:
                sodium = lab
        
        # Low cortisol is concerning for adrenal insufficiency
        if cortisol and cortisol.reference_low and cortisol.value < cortisol.reference_low:
            return {
                'type': 'Low cortisol',
                'labs': [lab for lab in [cortisol, acth, sodium] if lab],
            }
        
        # Hyponatremia can indicate adrenal insufficiency
        if sodium and sodium.value < 130:  # Significant hyponatremia
            return {
                'type': 'Hyponatremia (possible adrenal insufficiency)',
                'labs': [sodium],
            }
        
        return None
    
    def _detect_glucose_abnormality(self, labs: list[LabResult]) -> Optional[dict]:
        """Detect glucose/diabetes patterns."""
        glucose = None
        hba1c = None
        
        for lab in labs:
            lab_lower = lab.name.lower()
            if 'glucose' in lab_lower:
                glucose = lab
            elif 'hba1c' in lab_lower or 'a1c' in lab_lower:
                hba1c = lab
        
        if glucose:
            if glucose.value > 300:
                return {
                    'type': 'severe_hyperglycemia',
                    'labs': [glucose],
                }
            elif glucose.value > 200:
                return {
                    'type': 'hyperglycemia',
                    'labs': [glucose],
                }
        
        return None
    
    def _check_vitals_for_hypotension(self, vitals: list) -> Optional[str]:
        """Check vitals for hypotension."""
        for vital in vitals:
            if vital.blood_pressure_systolic and vital.blood_pressure_systolic < 90:
                return f"{vital.blood_pressure_systolic}/{vital.blood_pressure_diastolic or '?'}"
        return None
