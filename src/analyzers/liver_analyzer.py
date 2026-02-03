"""Hepatic irAE analyzer for liver toxicity detection."""

from typing import Optional

from ..models.patient import PatientData, LabResult
from ..models.assessment import OrganSystemFinding, OrganSystem, Severity
from .base import BaseAnalyzer


class LiverAnalyzer(BaseAnalyzer):
    """Analyzer for hepatic immune-related adverse events."""
    
    def __init__(self):
        super().__init__()
        self.organ_system = OrganSystem.HEPATIC
        self.key_symptoms = [
            "jaundice", "icterus", "yellow skin", "yellow eyes",
            "fatigue", "weakness", "malaise",
            "abdominal pain", "right upper quadrant pain", "ruq pain",
            "dark urine", "tea-colored urine",
            "pale stool", "clay-colored stool",
            "nausea", "vomiting", "anorexia",
            "pruritus", "itching",
        ]
        self.key_labs = ["AST", "ALT", "bilirubin", "alkaline phosphatase", "ALP", "GGT"]
        self.conditions = ["hepatitis", "liver injury", "hepatotoxicity", "transaminitis"]
    
    def analyze(self, patient_data: PatientData) -> OrganSystemFinding:
        """Analyze patient data for hepatic irAE signals."""
        findings = []
        evidence = []
        detected = False
        severity = None
        confidence = 0.0
        
        # Check liver labs
        relevant_labs = self._find_relevant_labs(patient_data.labs, self.key_labs)
        abnormal_labs = self._get_abnormal_labs(relevant_labs)
        
        if abnormal_labs:
            detected = True
            max_severity = None
            
            for lab in abnormal_labs:
                findings.append(f"Elevated {lab.name}: {lab.value} {lab.unit}")
                
                # Calculate elevation ratio
                if lab.reference_high:
                    ratio = lab.value / lab.reference_high
                    evidence.append(
                        f"{lab.name} = {lab.value} ({ratio:.1f}x ULN)"
                    )
                    
                    # Determine severity based on lab elevation
                    lab_severity = self._estimate_liver_severity(lab)
                    if lab_severity:
                        if max_severity is None or self._severity_rank(lab_severity) > self._severity_rank(max_severity):
                            max_severity = lab_severity
                else:
                    evidence.append(f"{lab.name} = {lab.value} (elevated)")
            
            confidence += 0.4 * len(abnormal_labs)
            severity = max_severity
        
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
            confidence += 0.3
        
        # Check for liver lab mentions in raw text
        lab_patterns = self._check_text_for_keywords(
            all_notes, 
            ["elevated ast", "elevated alt", "elevated bilirubin", 
             "ast increased", "alt increased", "transaminases elevated"]
        )
        if lab_patterns:
            detected = True
            for pattern in lab_patterns:
                if pattern not in [e.lower() for e in evidence]:
                    findings.append(f"Note mentions: {pattern}")
                    evidence.append(f"Note: '{pattern}'")
            confidence += 0.3
        
        confidence = min(confidence, 1.0)
        
        return self._create_finding(
            detected=detected,
            findings=findings,
            evidence=evidence,
            severity=severity,
            confidence=confidence if detected else None,
        )
    
    def _estimate_liver_severity(self, lab: LabResult) -> Optional[Severity]:
        """
        Estimate hepatic irAE severity based on lab values.
        
        CTCAE grading for hepatitis (transaminases):
        Grade 1: >ULN - 3x ULN
        Grade 2: >3 - 5x ULN
        Grade 3: >5 - 20x ULN
        Grade 4: >20x ULN
        
        For bilirubin:
        Grade 1: >ULN - 1.5x ULN
        Grade 2: >1.5 - 3x ULN
        Grade 3: >3 - 10x ULN
        Grade 4: >10x ULN
        """
        if not lab.reference_high or lab.reference_high == 0:
            return None
        
        ratio = lab.value / lab.reference_high
        lab_name_lower = lab.name.lower()
        
        # Different thresholds for bilirubin vs transaminases
        if "bilirubin" in lab_name_lower:
            if ratio > 10:
                return Severity.GRADE_4
            elif ratio > 3:
                return Severity.GRADE_3
            elif ratio > 1.5:
                return Severity.GRADE_2
            elif ratio > 1:
                return Severity.GRADE_1
        else:
            # AST, ALT, ALP
            if ratio > 20:
                return Severity.GRADE_4
            elif ratio > 5:
                return Severity.GRADE_3
            elif ratio > 3:
                return Severity.GRADE_2
            elif ratio > 1:
                return Severity.GRADE_1
        
        return None
    
    def _severity_rank(self, severity: Severity) -> int:
        """Get numeric rank for severity comparison."""
        ranks = {
            Severity.GRADE_1: 1,
            Severity.GRADE_2: 2,
            Severity.GRADE_3: 3,
            Severity.GRADE_4: 4,
            Severity.UNKNOWN: 0,
        }
        return ranks.get(severity, 0)
