"""Cardiac irAE analyzer for cardiotoxicity detection."""

from typing import Optional

from ..models.patient import PatientData, LabResult
from ..models.assessment import OrganSystemFinding, OrganSystem, Severity
from .base import BaseAnalyzer


class CardiacAnalyzer(BaseAnalyzer):
    """Analyzer for cardiac immune-related adverse events."""
    
    def __init__(self):
        super().__init__()
        self.organ_system = OrganSystem.CARDIAC
        self.key_symptoms = [
            "chest pain", "chest discomfort", "chest tightness",
            "palpitations", "heart racing", "irregular heartbeat",
            "dyspnea", "shortness of breath", "orthopnea",
            "edema", "leg swelling", "ankle swelling",
            "syncope", "near-syncope", "lightheadedness",
            "fatigue", "exercise intolerance",
        ]
        self.key_labs = [
            "troponin", "troponin I", "troponin T",
            "BNP", "NT-proBNP", "pro-BNP",
            "CK", "CK-MB", "creatine kinase",
        ]
        self.conditions = [
            "myocarditis", "pericarditis", "cardiomyopathy",
            "arrhythmia", "atrial fibrillation", "heart block",
            "heart failure", "cardiac dysfunction",
            "takotsubo", "stress cardiomyopathy",
        ]
    
    def analyze(self, patient_data: PatientData) -> OrganSystemFinding:
        """Analyze patient data for cardiac irAE signals."""
        findings = []
        evidence = []
        detected = False
        severity = None
        confidence = 0.0
        
        # Check cardiac labs
        relevant_labs = self._find_relevant_labs(patient_data.labs, self.key_labs)
        abnormal_labs = self._get_abnormal_labs(relevant_labs)
        
        # Troponin elevation is particularly concerning
        troponin_elevated = False
        bnp_elevated = False
        
        if abnormal_labs:
            for lab in abnormal_labs:
                lab_lower = lab.name.lower()
                
                if "troponin" in lab_lower:
                    detected = True
                    troponin_elevated = True
                    findings.append(f"ELEVATED TROPONIN: {lab.value} {lab.unit}")
                    evidence.append(f"⚠️ Troponin = {lab.value} (ELEVATED - cardiac injury marker)")
                    confidence += 0.6
                
                elif "bnp" in lab_lower:
                    detected = True
                    bnp_elevated = True
                    findings.append(f"Elevated BNP: {lab.value} {lab.unit}")
                    evidence.append(f"BNP = {lab.value} (elevated)")
                    confidence += 0.4
                
                elif "ck" in lab_lower:
                    detected = True
                    findings.append(f"Elevated {lab.name}: {lab.value} {lab.unit}")
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
            confidence += 0.2 * len(relevant_symptoms)
        
        # Check vitals for concerning patterns
        vital_concerns = self._check_vitals_for_cardiac(patient_data.vitals)
        if vital_concerns:
            detected = True
            for concern in vital_concerns:
                findings.append(concern['finding'])
                evidence.append(concern['evidence'])
            confidence += 0.3 * len(vital_concerns)
        
        # Check clinical notes
        all_notes = " ".join([n.content for n in patient_data.notes])
        if patient_data.raw_notes:
            all_notes += " " + patient_data.raw_notes
        if patient_data.raw_labs:
            all_notes += " " + patient_data.raw_labs
        
        found_symptoms = self._check_text_for_keywords(all_notes, self.key_symptoms)
        if found_symptoms:
            detected = True
            for symptom in found_symptoms:
                if symptom not in evidence:
                    findings.append(f"Clinical note mentions: {symptom}")
                    evidence.append(f"Note: '{symptom}'")
            confidence += 0.2
        
        found_conditions = self._check_text_for_keywords(all_notes, self.conditions)
        if found_conditions:
            detected = True
            for condition in found_conditions:
                findings.append(f"Documentation mentions: {condition}")
                evidence.append(f"Condition: {condition}")
            confidence += 0.5
        
        # Check for EKG/ECG findings
        ekg_findings = self._check_text_for_keywords(
            all_notes,
            ["st elevation", "st depression", "t wave", "arrhythmia", 
             "bradycardia", "tachycardia", "heart block", "prolonged qt"]
        )
        if ekg_findings:
            detected = True
            for finding in ekg_findings:
                findings.append(f"EKG finding: {finding}")
                evidence.append(f"EKG: '{finding}'")
            confidence += 0.4
        
        # Estimate severity
        if detected:
            severity = self._estimate_cardiac_severity(
                troponin_elevated, bnp_elevated, found_conditions, 
                vital_concerns, all_notes
            )
        
        confidence = min(confidence, 1.0)
        
        return self._create_finding(
            detected=detected,
            findings=findings,
            evidence=evidence,
            severity=severity,
            confidence=confidence if detected else None,
        )
    
    def _check_vitals_for_cardiac(self, vitals: list) -> list[dict]:
        """Check vitals for cardiac concerning patterns."""
        concerns = []
        
        for vital in vitals:
            # Tachycardia
            if vital.heart_rate and vital.heart_rate > 100:
                concerns.append({
                    'finding': f"Tachycardia: HR {vital.heart_rate}",
                    'evidence': f"HR = {vital.heart_rate} bpm",
                })
            
            # Bradycardia
            if vital.heart_rate and vital.heart_rate < 50:
                concerns.append({
                    'finding': f"Bradycardia: HR {vital.heart_rate}",
                    'evidence': f"HR = {vital.heart_rate} bpm",
                })
            
            # Hypotension
            if vital.blood_pressure_systolic and vital.blood_pressure_systolic < 90:
                concerns.append({
                    'finding': f"Hypotension: BP {vital.blood_pressure_systolic}/{vital.blood_pressure_diastolic or '?'}",
                    'evidence': f"BP = {vital.blood_pressure_systolic}/{vital.blood_pressure_diastolic or '?'}",
                })
            
            # Hypoxia
            if vital.oxygen_saturation and vital.oxygen_saturation < 94:
                concerns.append({
                    'finding': f"Hypoxia: SpO2 {vital.oxygen_saturation}%",
                    'evidence': f"SpO2 = {vital.oxygen_saturation}%",
                })
        
        return concerns
    
    def _estimate_cardiac_severity(
        self,
        troponin_elevated: bool,
        bnp_elevated: bool,
        conditions: list[str],
        vital_concerns: list[dict],
        notes_text: str
    ) -> Severity:
        """
        Estimate cardiac irAE severity.
        
        Cardiac irAEs (especially myocarditis) are potentially life-threatening
        and should be treated with high urgency.
        """
        notes_lower = notes_text.lower()
        
        # Grade 4 indicators - life-threatening
        grade4_indicators = [
            "cardiogenic shock", "cardiac arrest",
            "life-threatening", "unstable",
            "lvef <", "ejection fraction <20",
            "complete heart block", "ventricular",
            "hemodynamic compromise",
        ]
        if any(ind in notes_lower for ind in grade4_indicators):
            return Severity.GRADE_4
        
        # Grade 3 indicators - severe
        grade3_indicators = [
            "myocarditis", "hospitalization", "icu",
            "inotropes", "severe", "grade 3",
            "symptomatic heart failure", "ef <40",
            "high-grade", "moderate-severe",
        ]
        if any(ind in notes_lower for ind in grade3_indicators):
            return Severity.GRADE_3
        
        # Myocarditis is always at least Grade 3
        if "myocarditis" in [c.lower() for c in conditions]:
            return Severity.GRADE_3
        
        # Elevated troponin with symptoms is concerning
        if troponin_elevated:
            if vital_concerns or bnp_elevated:
                return Severity.GRADE_3
            return Severity.GRADE_2
        
        # Grade 2 indicators
        if bnp_elevated or vital_concerns:
            return Severity.GRADE_2
        
        return Severity.GRADE_1
