"""Pulmonary irAE analyzer for pneumonitis detection."""

from typing import Optional

from ..models.patient import PatientData
from ..models.assessment import OrganSystemFinding, OrganSystem, Severity
from .base import BaseAnalyzer


class LungAnalyzer(BaseAnalyzer):
    """Analyzer for pulmonary immune-related adverse events."""
    
    def __init__(self):
        super().__init__()
        self.organ_system = OrganSystem.PULMONARY
        self.key_symptoms = [
            "cough", "dry cough", "nonproductive cough",
            "dyspnea", "shortness of breath", "sob", "breathlessness",
            "hypoxia", "low oxygen", "desaturation",
            "chest pain", "pleuritic pain",
            "wheezing", "wheeze",
            "tachypnea", "rapid breathing",
        ]
        self.key_labs = []  # No specific labs for pneumonitis
        self.imaging_findings = [
            "ground glass", "ground-glass", "ggo",
            "infiltrate", "opacity", "consolidation",
            "interstitial", "ild", "pneumonitis",
            "bilateral", "diffuse", "patchy",
        ]
        self.conditions = ["pneumonitis", "ild", "interstitial lung disease"]
    
    def analyze(self, patient_data: PatientData) -> OrganSystemFinding:
        """Analyze patient data for pulmonary irAE signals."""
        findings = []
        evidence = []
        detected = False
        severity = None
        confidence = 0.0
        
        # Check symptoms
        relevant_symptoms = self._find_relevant_symptoms(
            patient_data.symptoms, self.key_symptoms
        )
        
        if relevant_symptoms:
            detected = True
            for symptom in relevant_symptoms:
                findings.append(f"Patient reports {symptom.symptom}")
                evidence.append(symptom.symptom)
            confidence += 0.3 * len(relevant_symptoms)
        
        # Check vitals for hypoxia
        hypoxia_found = self._check_vitals_for_hypoxia(patient_data.vitals)
        if hypoxia_found:
            detected = True
            findings.append(f"Hypoxia detected: SpO2 {hypoxia_found}%")
            evidence.append(f"SpO2 = {hypoxia_found}%")
            confidence += 0.4
        
        # Check clinical notes
        all_notes = " ".join([n.content for n in patient_data.notes])
        if patient_data.raw_notes:
            all_notes += " " + patient_data.raw_notes
        if patient_data.raw_symptoms:
            all_notes += " " + patient_data.raw_symptoms
        
        found_symptoms = self._check_text_for_keywords(all_notes, self.key_symptoms)
        if found_symptoms:
            detected = True
            for symptom in found_symptoms:
                if symptom not in evidence:
                    findings.append(f"Clinical note mentions: {symptom}")
                    evidence.append(f"Note: '{symptom}'")
            confidence += 0.2 * len(found_symptoms)
        
        # Check for imaging findings
        found_imaging = self._check_text_for_keywords(all_notes, self.imaging_findings)
        if found_imaging:
            detected = True
            for finding in found_imaging:
                findings.append(f"Imaging finding: {finding}")
                evidence.append(f"Imaging: '{finding}'")
            confidence += 0.4
        
        # Check for condition mentions
        found_conditions = self._check_text_for_keywords(all_notes, self.conditions)
        if found_conditions:
            detected = True
            for condition in found_conditions:
                findings.append(f"Documentation mentions: {condition}")
                evidence.append(f"Condition: {condition}")
            confidence += 0.4
        
        # Check imaging summaries
        for imaging in patient_data.imaging:
            if imaging.modality.upper() in ["CT", "CXR", "X-RAY", "CHEST"]:
                img_findings = self._check_text_for_keywords(
                    imaging.findings + " " + (imaging.impression or ""),
                    self.imaging_findings
                )
                if img_findings:
                    detected = True
                    for f in img_findings:
                        findings.append(f"Imaging report: {f}")
                        evidence.append(f"Radiology: '{f}'")
                    confidence += 0.5
        
        # Estimate severity
        if detected:
            severity = self._estimate_lung_severity(
                relevant_symptoms, found_symptoms, hypoxia_found, all_notes
            )
        
        confidence = min(confidence, 1.0)
        
        return self._create_finding(
            detected=detected,
            findings=findings,
            evidence=evidence,
            severity=severity,
            confidence=confidence if detected else None,
        )
    
    def _check_vitals_for_hypoxia(self, vitals: list) -> Optional[float]:
        """Check vitals for hypoxia (SpO2 < 94%)."""
        for vital in vitals:
            if vital.oxygen_saturation and vital.oxygen_saturation < 94:
                return vital.oxygen_saturation
        return None
    
    def _estimate_lung_severity(
        self, 
        symptoms: list,
        keyword_symptoms: list[str],
        hypoxia_spo2: Optional[float],
        notes_text: str
    ) -> Severity:
        """
        Estimate pneumonitis severity.
        
        CTCAE grading for pneumonitis:
        Grade 1: Asymptomatic, clinical/diagnostic observations only
        Grade 2: Symptomatic, medical intervention indicated, limiting ADL
        Grade 3: Severe symptoms, limiting self-care ADL, O2 indicated
        Grade 4: Life-threatening, urgent intervention
        """
        notes_lower = notes_text.lower()
        
        # Grade 4 indicators
        grade4_indicators = [
            "life-threatening", "intubation", "ventilator",
            "respiratory failure", "ards", "icu",
        ]
        if any(ind in notes_lower for ind in grade4_indicators):
            return Severity.GRADE_4
        
        # Grade 3 indicators
        grade3_indicators = [
            "oxygen therapy", "supplemental oxygen", "o2 requirement",
            "severe dyspnea", "significant hypoxia", "hospitalization",
            "grade 3",
        ]
        if any(ind in notes_lower for ind in grade3_indicators):
            return Severity.GRADE_3
        
        # Check SpO2 for severity
        if hypoxia_spo2:
            if hypoxia_spo2 < 88:
                return Severity.GRADE_4
            elif hypoxia_spo2 < 90:
                return Severity.GRADE_3
            elif hypoxia_spo2 < 94:
                return Severity.GRADE_2
        
        # Symptomatic = at least Grade 2
        respiratory_symptoms = ["dyspnea", "shortness of breath", "sob", "cough"]
        if any(s in keyword_symptoms for s in respiratory_symptoms):
            return Severity.GRADE_2
        
        return Severity.GRADE_1
