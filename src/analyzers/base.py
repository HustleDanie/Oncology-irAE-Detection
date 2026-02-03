"""Base analyzer class for organ-specific irAE detection."""

from abc import ABC, abstractmethod
from typing import Optional

from ..models.patient import PatientData, LabResult, PatientSymptom
from ..models.assessment import OrganSystemFinding, OrganSystem, Severity


class BaseAnalyzer(ABC):
    """Abstract base class for organ-specific irAE analyzers."""
    
    def __init__(self):
        self.organ_system: OrganSystem = None
        self.key_symptoms: list[str] = []
        self.key_labs: list[str] = []
        self.conditions: list[str] = []
    
    @abstractmethod
    def analyze(self, patient_data: PatientData) -> OrganSystemFinding:
        """
        Analyze patient data for organ-specific irAE signals.
        
        Args:
            patient_data: Complete patient clinical data
            
        Returns:
            OrganSystemFinding with detection results
        """
        pass
    
    def _find_relevant_labs(
        self, 
        labs: list[LabResult], 
        lab_names: list[str]
    ) -> list[LabResult]:
        """Find labs matching the specified names."""
        relevant = []
        for lab in labs:
            for name in lab_names:
                if name.lower() in lab.name.lower():
                    relevant.append(lab)
                    break
        return relevant
    
    def _find_relevant_symptoms(
        self, 
        symptoms: list[PatientSymptom],
        symptom_keywords: list[str]
    ) -> list[PatientSymptom]:
        """Find symptoms matching the specified keywords."""
        relevant = []
        for symptom in symptoms:
            symptom_lower = symptom.symptom.lower()
            for keyword in symptom_keywords:
                if keyword.lower() in symptom_lower:
                    relevant.append(symptom)
                    break
        return relevant
    
    def _check_text_for_keywords(
        self, 
        text: str, 
        keywords: list[str]
    ) -> list[str]:
        """Check text for presence of keywords."""
        text_lower = text.lower()
        found = []
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found.append(keyword)
        return found
    
    def _get_abnormal_labs(self, labs: list[LabResult]) -> list[LabResult]:
        """Get labs that are outside reference ranges."""
        return [lab for lab in labs if lab.is_abnormal]
    
    def _estimate_severity_from_lab(
        self, 
        lab: LabResult, 
        mild_threshold: float = 1.5,
        moderate_threshold: float = 3.0,
        severe_threshold: float = 5.0
    ) -> Optional[Severity]:
        """
        Estimate severity based on lab value elevation.
        
        Args:
            lab: The lab result to evaluate
            mild_threshold: Multiplier for Grade 1 (e.g., 1.5x ULN)
            moderate_threshold: Multiplier for Grade 2
            severe_threshold: Multiplier for Grade 3
            
        Returns:
            Estimated Severity grade
        """
        if lab.reference_high is None or lab.reference_high == 0:
            return None
        
        ratio = lab.value / lab.reference_high
        
        if ratio >= severe_threshold:
            return Severity.GRADE_4
        elif ratio >= moderate_threshold:
            return Severity.GRADE_3
        elif ratio >= mild_threshold:
            return Severity.GRADE_2
        elif ratio > 1.0:
            return Severity.GRADE_1
        
        return None
    
    def _create_finding(
        self,
        detected: bool,
        findings: list[str],
        evidence: list[str],
        severity: Optional[Severity] = None,
        confidence: Optional[float] = None,
    ) -> OrganSystemFinding:
        """Create an OrganSystemFinding with standard structure."""
        return OrganSystemFinding(
            system=self.organ_system,
            detected=detected,
            findings=findings,
            evidence=evidence,
            severity=severity,
            confidence=confidence,
        )
