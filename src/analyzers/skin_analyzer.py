"""Dermatologic irAE analyzer for skin toxicity detection."""

from typing import Optional

from ..models.patient import PatientData
from ..models.assessment import OrganSystemFinding, OrganSystem, Severity
from .base import BaseAnalyzer


class SkinAnalyzer(BaseAnalyzer):
    """Analyzer for dermatologic immune-related adverse events."""
    
    def __init__(self):
        super().__init__()
        self.organ_system = OrganSystem.DERMATOLOGIC
        self.key_symptoms = [
            "rash", "skin rash", "maculopapular rash",
            "pruritus", "itching", "itch",
            "dermatitis", "eczema",
            "vitiligo", "depigmentation",
            "dry skin", "xerosis",
            "blistering", "bullae", "vesicles",
            "peeling", "desquamation",
            "ulceration", "skin ulcer",
            "mucosal involvement", "oral lesions",
            "photosensitivity",
        ]
        self.key_labs = []  # No specific labs for skin toxicity
        self.conditions = [
            "dermatitis", "rash", "sjs", "stevens-johnson",
            "ten", "toxic epidermal necrolysis",
            "dress", "lichenoid", "psoriasiform",
            "bullous pemphigoid", "vitiligo",
        ]
        self.severe_conditions = [
            "sjs", "stevens-johnson", "ten", "toxic epidermal",
            "dress", "blistering", "bullae", "desquamation",
            "mucosal involvement",
        ]
    
    def analyze(self, patient_data: PatientData) -> OrganSystemFinding:
        """Analyze patient data for dermatologic irAE signals."""
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
        
        found_conditions = self._check_text_for_keywords(all_notes, self.conditions)
        if found_conditions:
            detected = True
            for condition in found_conditions:
                findings.append(f"Documentation mentions: {condition}")
                evidence.append(f"Condition: {condition}")
            confidence += 0.4
        
        # Check for BSA (body surface area) involvement
        bsa_info = self._extract_bsa_involvement(all_notes)
        if bsa_info:
            findings.append(f"Body surface area involvement: {bsa_info}")
            evidence.append(f"BSA: {bsa_info}")
            confidence += 0.3
        
        # Estimate severity
        if detected:
            severity = self._estimate_skin_severity(
                found_symptoms, found_conditions, bsa_info, all_notes
            )
        
        confidence = min(confidence, 1.0)
        
        return self._create_finding(
            detected=detected,
            findings=findings,
            evidence=evidence,
            severity=severity,
            confidence=confidence if detected else None,
        )
    
    def _extract_bsa_involvement(self, text: str) -> Optional[str]:
        """Extract body surface area involvement from text."""
        import re
        
        # Look for BSA percentages
        bsa_pattern = r'(\d+)\s*%?\s*(?:bsa|body surface area)'
        match = re.search(bsa_pattern, text.lower())
        if match:
            return f"{match.group(1)}%"
        
        # Look for extent descriptions
        extent_terms = {
            "localized": "<10%",
            "limited": "<10%",
            "widespread": "10-30%",
            "extensive": ">30%",
            "generalized": ">30%",
        }
        for term, extent in extent_terms.items():
            if term in text.lower():
                return f"{term} (~{extent})"
        
        return None
    
    def _estimate_skin_severity(
        self,
        symptoms: list[str],
        conditions: list[str],
        bsa_info: Optional[str],
        notes_text: str
    ) -> Severity:
        """
        Estimate dermatologic irAE severity.
        
        CTCAE grading for rash:
        Grade 1: Macules/papules covering <10% BSA with or without symptoms
        Grade 2: Macules/papules covering 10-30% BSA with or without symptoms; limiting instrumental ADL
        Grade 3: Macules/papules covering >30% BSA with or without symptoms; limiting self-care ADL
        Grade 4: SJS/TEN, life-threatening
        """
        notes_lower = notes_text.lower()
        
        # Grade 4 - SJS/TEN
        if any(cond.lower() in notes_lower for cond in ["sjs", "stevens-johnson", "ten", "toxic epidermal"]):
            return Severity.GRADE_4
        
        # Grade 4 indicators
        grade4_indicators = [
            "life-threatening", "desquamation >30%",
            "mucosal involvement", "hemodynamic",
        ]
        if any(ind in notes_lower for ind in grade4_indicators):
            return Severity.GRADE_4
        
        # Grade 3 indicators
        grade3_indicators = [
            "generalized", "extensive", ">30%",
            "hospitalization", "systemic steroids",
            "limiting self-care", "blistering",
        ]
        if any(ind in notes_lower for ind in grade3_indicators):
            return Severity.GRADE_3
        
        # Check BSA
        if bsa_info:
            if ">30%" in bsa_info or "extensive" in bsa_info.lower():
                return Severity.GRADE_3
            elif "10-30%" in bsa_info or "widespread" in bsa_info.lower():
                return Severity.GRADE_2
        
        # Grade 2 indicators
        grade2_indicators = [
            "moderate", "10-30%", "widespread",
            "topical steroids", "interfering",
        ]
        if any(ind in notes_lower for ind in grade2_indicators):
            return Severity.GRADE_2
        
        # Multiple skin symptoms suggest at least Grade 2
        skin_symptom_count = len([s for s in symptoms if s in self.key_symptoms])
        if skin_symptom_count >= 2:
            return Severity.GRADE_2
        
        return Severity.GRADE_1
