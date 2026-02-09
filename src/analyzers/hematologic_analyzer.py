"""Hematologic irAE analyzer for blood-related toxicity detection."""

from typing import Optional

from ..models.patient import PatientData, LabResult
from ..models.assessment import OrganSystemFinding, OrganSystem, Severity
from .base import BaseAnalyzer


class HematologicAnalyzer(BaseAnalyzer):
    """
    Analyzer for hematologic immune-related adverse events.
    
    Immune-related hematologic toxicities are rare but can be life-threatening.
    They include:
    - Immune thrombocytopenia (ITP)
    - Autoimmune hemolytic anemia (AIHA)
    - Neutropenia / Agranulocytosis
    - Aplastic anemia
    - Hemophagocytic lymphohistiocytosis (HLH)
    
    CTCAE v5.0 Grading:
    
    Platelet count decreased:
    - Grade 1: <LLN - 75,000/mm³
    - Grade 2: <75,000 - 50,000/mm³
    - Grade 3: <50,000 - 25,000/mm³
    - Grade 4: <25,000/mm³
    
    Anemia (Hemoglobin):
    - Grade 1: <LLN - 10.0 g/dL
    - Grade 2: <10.0 - 8.0 g/dL
    - Grade 3: <8.0 g/dL; transfusion indicated
    - Grade 4: Life-threatening consequences
    
    Neutropenia (ANC):
    - Grade 1: <LLN - 1500/mm³
    - Grade 2: <1500 - 1000/mm³
    - Grade 3: <1000 - 500/mm³
    - Grade 4: <500/mm³
    """
    
    def __init__(self):
        super().__init__()
        self.organ_system = OrganSystem.HEMATOLOGIC
        self.key_symptoms = [
            # Anemia symptoms
            "fatigue", "weakness", "pallor", "pale skin",
            "shortness of breath", "dyspnea on exertion",
            "dizziness", "lightheadedness", "syncope",
            "tachycardia", "palpitations",
            # Thrombocytopenia symptoms
            "bleeding", "bruising", "petechiae", "purpura",
            "epistaxis", "nosebleed", "gum bleeding",
            "hematuria", "blood in urine",
            "melena", "blood in stool", "hematochezia",
            "menorrhagia", "heavy menstrual bleeding",
            # Neutropenia symptoms
            "fever", "infection", "sepsis",
            "mouth sores", "mucositis",
            # General
            "easy bruising", "prolonged bleeding",
        ]
        self.key_labs = [
            "hemoglobin", "hgb", "hematocrit", "hct",
            "platelet", "plt", "thrombocyte",
            "WBC", "white blood cell", "leukocyte",
            "ANC", "absolute neutrophil count", "neutrophil",
            "reticulocyte", "retic",
            "LDH", "lactate dehydrogenase",
            "haptoglobin", "bilirubin",  # Hemolysis markers
            "direct coombs", "DAT", "indirect coombs",
            "ferritin", "fibrinogen",  # HLH markers
        ]
        self.conditions = [
            "thrombocytopenia", "anemia", "neutropenia", "pancytopenia",
            "immune thrombocytopenia", "ITP", "autoimmune hemolytic anemia", "AIHA",
            "hemolysis", "hemolytic anemia", "aplastic anemia",
            "agranulocytosis", "leukopenia", "cytopenia",
            "HLH", "hemophagocytic", "macrophage activation syndrome",
            "bone marrow suppression", "myelosuppression",
        ]
    
    def analyze(self, patient_data: PatientData) -> OrganSystemFinding:
        """Analyze patient data for hematologic irAE signals."""
        findings = []
        evidence = []
        detected = False
        severity = None
        confidence = 0.0
        max_severity = None
        
        # Check hematologic labs
        relevant_labs = self._find_relevant_labs(patient_data.labs, self.key_labs)
        
        for lab in relevant_labs:
            lab_name_lower = lab.name.lower()
            
            # Check for low values (most hematologic irAEs cause cytopenias)
            if lab.is_abnormal:
                # Hemoglobin/Anemia
                if any(x in lab_name_lower for x in ["hemoglobin", "hgb"]):
                    if lab.value < 10:  # Below 10 g/dL is significant
                        detected = True
                        findings.append(f"Low hemoglobin: {lab.value} g/dL")
                        evidence.append(f"Hemoglobin = {lab.value} g/dL")
                        
                        hgb_severity = self._grade_anemia(lab.value)
                        if hgb_severity and (max_severity is None or 
                            self._severity_rank(hgb_severity) > self._severity_rank(max_severity)):
                            max_severity = hgb_severity
                        confidence += 0.3
                
                # Platelet count / Thrombocytopenia
                if any(x in lab_name_lower for x in ["platelet", "plt"]):
                    # Assuming value is in thousands (e.g., 45 = 45,000)
                    plt_value = lab.value
                    if plt_value < 150:  # Below normal
                        detected = True
                        findings.append(f"Low platelets: {plt_value} x10³/µL")
                        evidence.append(f"Platelets = {plt_value} x10³/µL")
                        
                        plt_severity = self._grade_thrombocytopenia(plt_value)
                        if plt_severity and (max_severity is None or 
                            self._severity_rank(plt_severity) > self._severity_rank(max_severity)):
                            max_severity = plt_severity
                        confidence += 0.35
                
                # WBC / Neutropenia
                if any(x in lab_name_lower for x in ["wbc", "white blood", "leukocyte"]):
                    if lab.value < 4.0:  # Below normal WBC
                        detected = True
                        findings.append(f"Low WBC: {lab.value} x10⁹/L")
                        evidence.append(f"WBC = {lab.value} x10⁹/L")
                        confidence += 0.2
                
                # ANC
                if any(x in lab_name_lower for x in ["anc", "neutrophil"]):
                    anc_value = lab.value
                    # ANC might be in different units, assuming x10³/µL or x10⁹/L
                    if anc_value < 1.5:  # Below 1500/mm³
                        detected = True
                        findings.append(f"Low ANC: {anc_value} x10⁹/L")
                        evidence.append(f"ANC = {anc_value} x10⁹/L")
                        
                        anc_severity = self._grade_neutropenia(anc_value)
                        if anc_severity and (max_severity is None or 
                            self._severity_rank(anc_severity) > self._severity_rank(max_severity)):
                            max_severity = anc_severity
                        confidence += 0.35
                
                # Hemolysis markers
                if "ldh" in lab_name_lower and lab.value > lab.reference_high:
                    findings.append(f"Elevated LDH: {lab.value} U/L (possible hemolysis)")
                    evidence.append(f"LDH = {lab.value} U/L (elevated)")
                    confidence += 0.15
                
                if "haptoglobin" in lab_name_lower and lab.value < lab.reference_low:
                    detected = True
                    findings.append(f"Low haptoglobin: {lab.value} (hemolysis marker)")
                    evidence.append(f"Haptoglobin = {lab.value} (low)")
                    confidence += 0.25
                
                # HLH markers
                if "ferritin" in lab_name_lower and lab.value > 500:
                    detected = True  # Markedly elevated ferritin is a finding
                    findings.append(f"Elevated ferritin: {lab.value} ng/mL")
                    evidence.append(f"Ferritin = {lab.value} ng/mL")
                    if lab.value > 10000:
                        findings.append("Markedly elevated ferritin - consider HLH")
                        confidence += 0.3
                        # HLH is life-threatening
                        if max_severity is None or self._severity_rank(max_severity) < self._severity_rank(Severity.GRADE_4):
                            max_severity = Severity.GRADE_4
                    else:
                        confidence += 0.1
        
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
            confidence += 0.1 * min(len(relevant_symptoms), 4)
        
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
        
        # Check for transfusion mentions (indicates severity)
        transfusion_patterns = self._check_text_for_keywords(
            all_notes,
            ["transfusion", "prbc", "packed red blood cells", "platelet transfusion",
             "blood products", "transfuse"]
        )
        if transfusion_patterns:
            findings.append("Transfusion mentioned - indicates significant cytopenia")
            evidence.append("Transfusion required")
            confidence += 0.2
            if severity is None or self._severity_rank(severity) < self._severity_rank(Severity.GRADE_3):
                severity = Severity.GRADE_3
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        return self._create_finding(
            detected=detected,
            findings=findings,
            evidence=evidence,
            severity=severity,
            confidence=confidence if detected else None,
        )
    
    def _grade_anemia(self, hemoglobin: float) -> Optional[Severity]:
        """
        Grade anemia severity based on hemoglobin.
        
        CTCAE v5.0:
        Grade 1: <LLN - 10.0 g/dL
        Grade 2: <10.0 - 8.0 g/dL
        Grade 3: <8.0 g/dL
        Grade 4: Life-threatening (usually <6.5 g/dL)
        """
        if hemoglobin < 6.5:
            return Severity.GRADE_4
        elif hemoglobin < 8.0:
            return Severity.GRADE_3
        elif hemoglobin < 10.0:
            return Severity.GRADE_2
        elif hemoglobin < 12.0:  # Approximate LLN for adults
            return Severity.GRADE_1
        return None
    
    def _grade_thrombocytopenia(self, platelets: float) -> Optional[Severity]:
        """
        Grade thrombocytopenia based on platelet count (in thousands).
        
        CTCAE v5.0:
        Grade 1: <LLN - 75 x10³/µL
        Grade 2: <75 - 50 x10³/µL
        Grade 3: <50 - 25 x10³/µL
        Grade 4: <25 x10³/µL
        """
        if platelets < 25:
            return Severity.GRADE_4
        elif platelets < 50:
            return Severity.GRADE_3
        elif platelets < 75:
            return Severity.GRADE_2
        elif platelets < 150:
            return Severity.GRADE_1
        return None
    
    def _grade_neutropenia(self, anc: float) -> Optional[Severity]:
        """
        Grade neutropenia based on ANC (in x10⁹/L or x10³/µL).
        
        CTCAE v5.0:
        Grade 1: <LLN - 1.5
        Grade 2: <1.5 - 1.0
        Grade 3: <1.0 - 0.5
        Grade 4: <0.5
        """
        if anc < 0.5:
            return Severity.GRADE_4
        elif anc < 1.0:
            return Severity.GRADE_3
        elif anc < 1.5:
            return Severity.GRADE_2
        elif anc < 2.0:  # Approximate LLN
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
