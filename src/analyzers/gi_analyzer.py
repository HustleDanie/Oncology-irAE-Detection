"""Gastrointestinal irAE analyzer for colitis/diarrhea detection."""

from typing import Optional

from ..models.patient import PatientData
from ..models.assessment import OrganSystemFinding, OrganSystem, Severity
from .base import BaseAnalyzer


class GIAnalyzer(BaseAnalyzer):
    """Analyzer for gastrointestinal immune-related adverse events."""
    
    def __init__(self):
        super().__init__()
        self.organ_system = OrganSystem.GASTROINTESTINAL
        self.key_symptoms = [
            "diarrhea", "loose stool", "watery stool",
            "abdominal pain", "cramping", "abdominal cramp",
            "bloody stool", "blood in stool", "hematochezia", "melena",
            "nausea", "vomiting",
            "urgency", "tenesmus", "fecal urgency",
            "mucus in stool",
        ]
        self.conditions = ["colitis", "enteritis", "enterocolitis"]
    
    def analyze(self, patient_data: PatientData) -> OrganSystemFinding:
        """Analyze patient data for GI irAE signals."""
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
                if symptom.severity:
                    evidence.append(f"{symptom.symptom} ({symptom.severity})")
                else:
                    evidence.append(symptom.symptom)
            confidence += 0.3 * len(relevant_symptoms)
        
        # Check clinical notes for symptoms/conditions
        all_notes = " ".join([n.content for n in patient_data.notes])
        if patient_data.raw_notes:
            all_notes += " " + patient_data.raw_notes
        if patient_data.raw_symptoms:
            all_notes += " " + patient_data.raw_symptoms
        
        found_symptoms = self._check_text_for_keywords(all_notes, self.key_symptoms)
        found_conditions = self._check_text_for_keywords(all_notes, self.conditions)
        
        if found_symptoms:
            detected = True
            for symptom in found_symptoms:
                if symptom not in [e for e in evidence]:
                    findings.append(f"Clinical note mentions: {symptom}")
                    evidence.append(f"Note: '{symptom}'")
            confidence += 0.2 * len(found_symptoms)
        
        if found_conditions:
            detected = True
            for condition in found_conditions:
                findings.append(f"Documentation mentions: {condition}")
                evidence.append(f"Condition: {condition}")
            confidence += 0.4
        
        # Estimate severity based on symptom pattern
        if detected:
            severity = self._estimate_gi_severity(
                relevant_symptoms, found_symptoms, all_notes
            )
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        return self._create_finding(
            detected=detected,
            findings=findings,
            evidence=evidence,
            severity=severity,
            confidence=confidence if detected else None,
        )
    
    def _estimate_gi_severity(
        self, 
        symptoms: list, 
        keyword_symptoms: list[str],
        notes_text: str
    ) -> Severity:
        """
        Estimate GI irAE severity based on symptoms.
        
        CTCAE grading for diarrhea:
        Grade 1: <4 stools/day above baseline
        Grade 2: 4-6 stools/day above baseline
        Grade 3: ≥7 stools/day, incontinence, hospitalization
        Grade 4: Life-threatening, urgent intervention
        """
        notes_lower = notes_text.lower()
        
        # Check for severe indicators
        severe_indicators = [
            "bloody stool", "hematochezia", "melena",
            "dehydration", "hospitalization", "admission",
            "iv fluids", "severe", "grade 3", "grade 4",
            "perforation", "toxic megacolon",
        ]
        
        moderate_indicators = [
            "moderate", "grade 2", "cramping",
            "multiple episodes", "interfering with daily",
        ]
        
        if any(ind in notes_lower for ind in severe_indicators):
            return Severity.GRADE_3
        
        if any(ind in notes_lower for ind in moderate_indicators):
            return Severity.GRADE_2
        
        # Check for bloody stool in symptoms
        bloody_symptoms = ["bloody stool", "blood in stool", "hematochezia", "melena"]
        if any(s in keyword_symptoms for s in bloody_symptoms):
            return Severity.GRADE_3
        
        # Multiple GI symptoms suggest at least Grade 2
        gi_symptom_count = len([s for s in keyword_symptoms if s in self.key_symptoms])
        if gi_symptom_count >= 3:
            return Severity.GRADE_2
        
        return Severity.GRADE_1
