"""Renal irAE analyzer for nephritis and kidney toxicity detection."""

from typing import Optional

from ..models.patient import PatientData, LabResult
from ..models.assessment import OrganSystemFinding, OrganSystem, Severity
from .base import BaseAnalyzer


class RenalAnalyzer(BaseAnalyzer):
    """
    Analyzer for renal immune-related adverse events.
    
    Immune-related nephritis is a rare but serious irAE that can occur with
    checkpoint inhibitors. It typically presents as acute interstitial nephritis
    but can also manifest as glomerulonephritis or minimal change disease.
    
    CTCAE v5.0 Grading for Acute Kidney Injury:
    - Grade 1: Creatinine >1.0 - 1.5x baseline or >ULN - 1.5x ULN
    - Grade 2: Creatinine >1.5 - 3.0x baseline or >1.5 - 3.0x ULN
    - Grade 3: Creatinine >3.0x baseline or >3.0 - 6.0x ULN; hospitalization
    - Grade 4: Creatinine >6.0x ULN; dialysis indicated
    
    Key markers:
    - Creatinine elevation
    - BUN elevation
    - Proteinuria
    - Hematuria (sterile pyuria)
    - eGFR decline
    """
    
    def __init__(self):
        super().__init__()
        self.organ_system = OrganSystem.RENAL
        self.key_symptoms = [
            "decreased urine output", "oliguria", "anuria",
            "edema", "swelling", "peripheral edema",
            "fatigue", "weakness", "malaise",
            "nausea", "vomiting",
            "flank pain", "back pain",
            "foamy urine", "frothy urine",
            "blood in urine", "hematuria", "dark urine",
            "hypertension", "high blood pressure",
            "shortness of breath", "dyspnea",  # From fluid overload
        ]
        self.key_labs = [
            "creatinine", "BUN", "urea", "eGFR", "GFR",
            "potassium", "phosphorus", "calcium",
            "urinalysis", "urine protein", "proteinuria",
            "urine RBC", "urine WBC", "urine eosinophils",
        ]
        self.conditions = [
            "nephritis", "acute kidney injury", "AKI", "renal failure",
            "interstitial nephritis", "glomerulonephritis",
            "kidney injury", "renal insufficiency", "azotemia",
            "proteinuria", "hematuria",
        ]
    
    def analyze(self, patient_data: PatientData) -> OrganSystemFinding:
        """Analyze patient data for renal irAE signals."""
        findings = []
        evidence = []
        detected = False
        severity = None
        confidence = 0.0
        
        # Check renal labs
        relevant_labs = self._find_relevant_labs(patient_data.labs, self.key_labs)
        abnormal_labs = self._get_abnormal_labs(relevant_labs)
        
        creatinine_lab = None
        max_severity = None
        
        for lab in abnormal_labs:
            detected = True
            lab_name_lower = lab.name.lower()
            
            findings.append(f"Abnormal {lab.name}: {lab.value} {lab.unit}")
            
            if lab.reference_high:
                ratio = lab.value / lab.reference_high
                evidence.append(f"{lab.name} = {lab.value} ({ratio:.1f}x ULN)")
            else:
                evidence.append(f"{lab.name} = {lab.value} (abnormal)")
            
            # Track creatinine specifically for severity grading
            if "creatinine" in lab_name_lower:
                creatinine_lab = lab
                lab_severity = self._estimate_renal_severity(lab)
                if lab_severity:
                    if max_severity is None or self._severity_rank(lab_severity) > self._severity_rank(max_severity):
                        max_severity = lab_severity
            
            # BUN elevation supports renal dysfunction
            if "bun" in lab_name_lower or "urea" in lab_name_lower:
                confidence += 0.2
            
            # Electrolyte abnormalities
            if lab_name_lower in ["potassium", "phosphorus"]:
                confidence += 0.1
        
        if creatinine_lab:
            confidence += 0.4
            severity = max_severity
        
        # Check for low eGFR
        egfr_labs = [l for l in patient_data.labs if "gfr" in l.name.lower()]
        for lab in egfr_labs:
            if lab.value < 60:  # eGFR < 60 indicates kidney disease
                detected = True
                findings.append(f"Reduced eGFR: {lab.value} mL/min/1.73m²")
                evidence.append(f"eGFR = {lab.value} (reduced)")
                confidence += 0.3
                
                if lab.value < 15:
                    severity = Severity.GRADE_4
                elif lab.value < 30:
                    if severity is None or self._severity_rank(Severity.GRADE_3) > self._severity_rank(severity):
                        severity = Severity.GRADE_3
                elif lab.value < 45:
                    if severity is None or self._severity_rank(Severity.GRADE_2) > self._severity_rank(severity):
                        severity = Severity.GRADE_2
        
        # Check symptoms
        relevant_symptoms = self._find_relevant_symptoms(
            patient_data.symptoms, self.key_symptoms
        )
        
        if relevant_symptoms:
            detected = True
            for symptom in relevant_symptoms:
                findings.append(f"Patient reports {symptom.symptom}")
                evidence.append(symptom.symptom)
            confidence += 0.15 * min(len(relevant_symptoms), 3)
        
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
        
        # Check for urinalysis abnormalities in notes
        urine_patterns = self._check_text_for_keywords(
            all_notes,
            ["proteinuria", "hematuria", "pyuria", "eosinophiluria",
             "urine protein", "urine blood", "casts", "wbc casts"]
        )
        if urine_patterns:
            detected = True
            for pattern in urine_patterns:
                findings.append(f"Urinalysis finding: {pattern}")
                evidence.append(f"UA: {pattern}")
            confidence += 0.2
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        return self._create_finding(
            detected=detected,
            findings=findings,
            evidence=evidence,
            severity=severity,
            confidence=confidence if detected else None,
        )
    
    def _estimate_renal_severity(self, lab: LabResult) -> Optional[Severity]:
        """
        Estimate renal irAE severity based on creatinine.
        
        CTCAE v5.0 grading for Acute Kidney Injury:
        Grade 1: Creatinine >ULN - 1.5x ULN
        Grade 2: Creatinine >1.5 - 3.0x ULN
        Grade 3: Creatinine >3.0 - 6.0x ULN
        Grade 4: Creatinine >6.0x ULN
        """
        if not lab.reference_high or lab.reference_high == 0:
            return None
        
        ratio = lab.value / lab.reference_high
        
        if ratio > 6.0:
            return Severity.GRADE_4
        elif ratio > 3.0:
            return Severity.GRADE_3
        elif ratio > 1.5:
            return Severity.GRADE_2
        elif ratio > 1.0:
            return Severity.GRADE_1
        
        return None
    
    def _severity_rank(self, severity: Severity) -> int:
        """Convert severity to numeric rank for comparison."""
        ranks = {
            Severity.GRADE_1: 1,
            Severity.GRADE_2: 2,
            Severity.GRADE_3: 3,
            Severity.GRADE_4: 4,
            Severity.UNKNOWN: 0,
        }
        return ranks.get(severity, 0)
