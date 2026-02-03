"""Neurologic irAE analyzer for neurotoxicity detection."""

from typing import Optional

from ..models.patient import PatientData, LabResult
from ..models.assessment import OrganSystemFinding, OrganSystem, Severity
from .base import BaseAnalyzer


class NeuroAnalyzer(BaseAnalyzer):
    """Analyzer for neurologic immune-related adverse events."""
    
    def __init__(self):
        super().__init__()
        self.organ_system = OrganSystem.NEUROLOGIC
        self.key_symptoms = [
            "weakness", "muscle weakness", "limb weakness",
            "numbness", "tingling", "paresthesia",
            "confusion", "altered mental status", "encephalopathy",
            "headache", "severe headache",
            "vision changes", "diplopia", "double vision", "blurred vision",
            "ptosis", "drooping eyelid",
            "dysphagia", "difficulty swallowing",
            "dysarthria", "slurred speech",
            "gait disturbance", "ataxia", "balance problems",
            "seizure", "convulsion",
            "facial weakness", "facial droop",
        ]
        self.key_labs = ["CK", "creatine kinase", "aldolase"]
        self.conditions = [
            "neuropathy", "peripheral neuropathy", "polyneuropathy",
            "encephalitis", "meningitis", "meningoencephalitis",
            "myasthenia", "myasthenic syndrome", "myasthenia gravis",
            "guillain-barre", "gbs", "aidp",
            "myelitis", "transverse myelitis",
            "myositis", "inflammatory myopathy",
        ]
    
    def analyze(self, patient_data: PatientData) -> OrganSystemFinding:
        """Analyze patient data for neurologic irAE signals."""
        findings = []
        evidence = []
        detected = False
        severity = None
        confidence = 0.0
        
        # Check labs (CK for myositis)
        relevant_labs = self._find_relevant_labs(patient_data.labs, self.key_labs)
        abnormal_labs = self._get_abnormal_labs(relevant_labs)
        
        if abnormal_labs:
            detected = True
            for lab in abnormal_labs:
                findings.append(f"Elevated {lab.name}: {lab.value} {lab.unit}")
                if lab.reference_high:
                    ratio = lab.value / lab.reference_high
                    evidence.append(f"{lab.name} = {lab.value} ({ratio:.1f}x ULN)")
                else:
                    evidence.append(f"{lab.name} = {lab.value}")
            confidence += 0.3
        
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
            confidence += 0.5
        
        # Estimate severity
        if detected:
            severity = self._estimate_neuro_severity(
                found_symptoms, found_conditions, abnormal_labs, all_notes
            )
        
        confidence = min(confidence, 1.0)
        
        return self._create_finding(
            detected=detected,
            findings=findings,
            evidence=evidence,
            severity=severity,
            confidence=confidence if detected else None,
        )
    
    def _estimate_neuro_severity(
        self,
        symptoms: list[str],
        conditions: list[str],
        abnormal_labs: list[LabResult],
        notes_text: str
    ) -> Severity:
        """
        Estimate neurologic irAE severity.
        
        Neurologic irAEs are often serious and require careful grading.
        """
        notes_lower = notes_text.lower()
        
        # Grade 4 indicators - life-threatening
        grade4_indicators = [
            "respiratory failure", "intubation", "ventilator",
            "paralysis", "quadriplegia", "paraplegia",
            "life-threatening", "icu", "critical",
            "status epilepticus", "coma",
        ]
        if any(ind in notes_lower for ind in grade4_indicators):
            return Severity.GRADE_4
        
        # Grade 3 indicators - severe
        grade3_indicators = [
            "hospitalization", "severe", "grade 3",
            "significant weakness", "falling",
            "ivig", "plasmapheresis", "steroids",
            "guillain-barre", "gbs", "myasthenia crisis",
            "encephalitis", "meningitis",
            "unable to walk", "wheelchair",
        ]
        if any(ind in notes_lower for ind in grade3_indicators):
            return Severity.GRADE_3
        
        # Certain conditions are inherently severe
        severe_conditions = ["guillain-barre", "gbs", "encephalitis", "myasthenia", "myelitis"]
        if any(cond in [c.lower() for c in conditions] for cond in severe_conditions):
            return Severity.GRADE_3
        
        # Grade 2 indicators
        grade2_indicators = [
            "moderate", "grade 2",
            "interfering", "limiting daily",
            "sensory neuropathy", "paresthesia",
        ]
        if any(ind in notes_lower for ind in grade2_indicators):
            return Severity.GRADE_2
        
        # Multiple neurologic symptoms
        neuro_count = len([s for s in symptoms if s in self.key_symptoms])
        if neuro_count >= 3:
            return Severity.GRADE_2
        
        # Elevated CK suggests myositis
        for lab in abnormal_labs:
            if "ck" in lab.name.lower() or "creatine kinase" in lab.name.lower():
                if lab.reference_high and lab.value > 5 * lab.reference_high:
                    return Severity.GRADE_3
                elif lab.reference_high and lab.value > 2 * lab.reference_high:
                    return Severity.GRADE_2
        
        return Severity.GRADE_1
