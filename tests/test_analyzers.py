"""Unit tests for organ-specific analyzers."""

import pytest
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.patient import PatientData, LabResult, Medication, PatientSymptom, VitalSigns
from src.models.assessment import Severity, OrganSystem
from src.analyzers import (
    ImmunotherapyDetector,
    GIAnalyzer,
    LiverAnalyzer,
    LungAnalyzer,
    EndocrineAnalyzer,
    CardiacAnalyzer,
)


class TestImmunotherapyDetector:
    """Tests for the ImmunotherapyDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ImmunotherapyDetector()
    
    def test_detect_from_medications(self):
        """Test detection from medication list."""
        patient_data = PatientData(
            medications=[
                Medication(name="Pembrolizumab", is_immunotherapy=True, drug_class="PD-1"),
            ]
        )
        
        context = self.detector.detect(patient_data)
        
        assert context.on_immunotherapy == True
        assert len(context.agents) >= 1
    
    def test_detect_from_raw_text(self):
        """Test detection from raw medication text."""
        patient_data = PatientData(
            raw_medications="Currently on nivolumab 240mg IV q2weeks"
        )
        
        context = self.detector.detect(patient_data)
        
        assert context.on_immunotherapy == True
    
    def test_detect_combination_therapy(self):
        """Test detection of combination therapy."""
        patient_data = PatientData(
            medications=[
                Medication(name="Nivolumab", is_immunotherapy=True, drug_class="PD-1"),
                Medication(name="Ipilimumab", is_immunotherapy=True, drug_class="CTLA-4"),
            ]
        )
        
        context = self.detector.detect(patient_data)
        
        assert context.combination_therapy == True
    
    def test_no_immunotherapy(self):
        """Test when no immunotherapy is present."""
        patient_data = PatientData(
            medications=[
                Medication(name="Metformin"),
                Medication(name="Lisinopril"),
            ]
        )
        
        context = self.detector.detect(patient_data)
        
        assert context.on_immunotherapy == False


class TestLiverAnalyzer:
    """Tests for the LiverAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = LiverAnalyzer()
    
    def test_detect_elevated_transaminases(self):
        """Test detection of elevated liver enzymes."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="AST", value=245, unit="U/L",
                    reference_low=10, reference_high=40,
                    date=datetime.now(), is_abnormal=True
                ),
                LabResult(
                    name="ALT", value=312, unit="U/L",
                    reference_low=7, reference_high=56,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.system == OrganSystem.HEPATIC
        assert finding.severity in [Severity.GRADE_2, Severity.GRADE_3]
    
    def test_grade_severity_correctly(self):
        """Test correct severity grading based on CTCAE criteria."""
        # Grade 3 = >5x ULN (ULN for AST = 40)
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="AST", value=250, unit="U/L",  # ~6x ULN
                    reference_low=10, reference_high=40,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.severity == Severity.GRADE_3
    
    def test_normal_labs_no_detection(self):
        """Test that normal labs don't trigger detection."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="AST", value=25, unit="U/L",
                    reference_low=10, reference_high=40,
                    date=datetime.now(), is_abnormal=False
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        # May detect from other sources but not from labs alone
        assert len(finding.evidence) == 0 or not any("AST" in e for e in finding.evidence if "elevated" in e.lower())


class TestGIAnalyzer:
    """Tests for the GIAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = GIAnalyzer()
    
    def test_detect_diarrhea(self):
        """Test detection of GI symptoms."""
        patient_data = PatientData(
            symptoms=[
                PatientSymptom(symptom="diarrhea", reported_date=datetime.now()),
                PatientSymptom(symptom="abdominal pain", reported_date=datetime.now()),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.system == OrganSystem.GASTROINTESTINAL
    
    def test_detect_bloody_stool_severe(self):
        """Test that bloody stool indicates higher severity."""
        patient_data = PatientData(
            raw_symptoms="Patient has diarrhea with bloody stool",
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.severity in [Severity.GRADE_3, Severity.GRADE_4]


class TestLungAnalyzer:
    """Tests for the LungAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = LungAnalyzer()
    
    def test_detect_respiratory_symptoms(self):
        """Test detection of respiratory symptoms."""
        patient_data = PatientData(
            symptoms=[
                PatientSymptom(symptom="cough", reported_date=datetime.now()),
                PatientSymptom(symptom="dyspnea", reported_date=datetime.now()),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.system == OrganSystem.PULMONARY
    
    def test_detect_hypoxia(self):
        """Test detection of hypoxia from vitals."""
        patient_data = PatientData(
            vitals=[
                VitalSigns(
                    date=datetime.now(),
                    oxygen_saturation=88,
                )
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.severity in [Severity.GRADE_3, Severity.GRADE_4]


class TestCardiacAnalyzer:
    """Tests for the CardiacAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CardiacAnalyzer()
    
    def test_detect_elevated_troponin(self):
        """Test detection of elevated troponin."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="Troponin", value=0.15, unit="ng/mL",
                    reference_low=0, reference_high=0.04,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.system == OrganSystem.CARDIAC
        # Elevated troponin is serious
        assert finding.severity in [Severity.GRADE_2, Severity.GRADE_3]
    
    def test_detect_cardiac_symptoms(self):
        """Test detection of cardiac symptoms."""
        patient_data = PatientData(
            symptoms=[
                PatientSymptom(symptom="chest pain", reported_date=datetime.now()),
                PatientSymptom(symptom="palpitations", reported_date=datetime.now()),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True


class TestEndocrineAnalyzer:
    """Tests for the EndocrineAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = EndocrineAnalyzer()
    
    def test_detect_hypothyroidism(self):
        """Test detection of hypothyroidism pattern."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="TSH", value=15.0, unit="mIU/L",
                    reference_low=0.4, reference_high=4.0,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.system == OrganSystem.ENDOCRINE
    
    def test_detect_hyperthyroidism(self):
        """Test detection of hyperthyroidism pattern."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="TSH", value=0.05, unit="mIU/L",
                    reference_low=0.4, reference_high=4.0,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True


class TestRenalAnalyzer:
    """Tests for the RenalAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from src.analyzers import RenalAnalyzer
        self.analyzer = RenalAnalyzer()
    
    def test_detect_elevated_creatinine_grade_2(self):
        """Test detection of elevated creatinine (Grade 2 - >1.5-3x ULN)."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="Creatinine", value=2.5, unit="mg/dL",
                    reference_low=0.7, reference_high=1.2,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.system == OrganSystem.RENAL
        assert finding.severity == Severity.GRADE_2
    
    def test_detect_elevated_creatinine_grade_3(self):
        """Test detection of elevated creatinine (Grade 3 - >3-6x ULN)."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="Creatinine", value=5.0, unit="mg/dL",
                    reference_low=0.7, reference_high=1.2,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.severity == Severity.GRADE_3
    
    def test_detect_elevated_bun(self):
        """Test detection of elevated BUN."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="BUN", value=55, unit="mg/dL",
                    reference_low=7, reference_high=20,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
    
    def test_detect_low_egfr(self):
        """Test detection of low eGFR."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="eGFR", value=35, unit="mL/min/1.73m2",
                    reference_low=90, reference_high=120,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.severity in [Severity.GRADE_2, Severity.GRADE_3]
    
    def test_no_renal_abnormalities(self):
        """Test normal renal function."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="Creatinine", value=1.0, unit="mg/dL",
                    reference_low=0.7, reference_high=1.2,
                    date=datetime.now(), is_abnormal=False
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == False


class TestHematologicAnalyzer:
    """Tests for the HematologicAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from src.analyzers import HematologicAnalyzer
        self.analyzer = HematologicAnalyzer()
    
    def test_detect_thrombocytopenia_grade_3(self):
        """Test detection of thrombocytopenia (Grade 3 - <50-25K)."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="Platelets", value=35, unit="K/uL",
                    reference_low=150, reference_high=400,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.system == OrganSystem.HEMATOLOGIC
        # Platelet count 35K (between 25 and 50) = Grade 3
        assert finding.severity == Severity.GRADE_3
    
    def test_detect_severe_anemia(self):
        """Test detection of severe anemia (Grade 3 - <8 g/dL)."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="Hemoglobin", value=7.0, unit="g/dL",
                    reference_low=12, reference_high=16,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.severity == Severity.GRADE_3  # <8 is Grade 3
    
    def test_detect_neutropenia(self):
        """Test detection of neutropenia (Grade 3 - <1.0K)."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="ANC", value=0.8, unit="K/uL",
                    reference_low=1.5, reference_high=8.0,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        assert finding.severity == Severity.GRADE_3
    
    def test_detect_hemolysis_markers(self):
        """Test detection of hemolysis (elevated LDH, low haptoglobin)."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="LDH", value=800, unit="U/L",
                    reference_low=140, reference_high=280,
                    date=datetime.now(), is_abnormal=True
                ),
                LabResult(
                    name="Haptoglobin", value=5, unit="mg/dL",
                    reference_low=30, reference_high=200,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        # Should mention AIHA in findings
        assert any("hemolysis" in f.lower() or "aiha" in f.lower() for f in finding.findings)
    
    def test_detect_hlh_markers(self):
        """Test detection of HLH markers (very high ferritin)."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="Ferritin", value=15000, unit="ng/mL",
                    reference_low=20, reference_high=200,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == True
        # Should flag HLH concern
        assert any("hlh" in f.lower() or "ferritin" in f.lower() for f in finding.findings)
    
    def test_no_hematologic_abnormalities(self):
        """Test normal hematologic values."""
        patient_data = PatientData(
            labs=[
                LabResult(
                    name="Hemoglobin", value=14.0, unit="g/dL",
                    reference_low=12, reference_high=16,
                    date=datetime.now(), is_abnormal=False
                ),
                LabResult(
                    name="Platelets", value=250, unit="K/uL",
                    reference_low=150, reference_high=400,
                    date=datetime.now(), is_abnormal=False
                ),
            ]
        )
        
        finding = self.analyzer.analyze(patient_data)
        
        assert finding.detected == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
