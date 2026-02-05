"""Integration tests for the complete assessment pipeline."""

import pytest
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.patient import PatientData, LabResult, Medication, PatientSymptom, VitalSigns
from src.models.assessment import Likelihood, Severity, Urgency
from src.llm.assessment_engine import IRAEAssessmentEngine


class TestAssessmentEngine:
    """Integration tests for the assessment engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = IRAEAssessmentEngine(use_llm=False)
    
    def test_hepatitis_scenario(self):
        """Test assessment of possible immune-related hepatitis."""
        patient_data = PatientData(
            patient_id="TEST001",
            age=65,
            cancer_type="Melanoma",
            medications=[
                Medication(name="Pembrolizumab", is_immunotherapy=True, drug_class="PD-1"),
            ],
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
                LabResult(
                    name="Bilirubin", value=2.1, unit="mg/dL",
                    reference_low=0.1, reference_high=1.2,
                    date=datetime.now(), is_abnormal=True
                ),
            ],
            symptoms=[
                PatientSymptom(symptom="fatigue", reported_date=datetime.now()),
                PatientSymptom(symptom="nausea", reported_date=datetime.now()),
            ],
        )
        
        result = self.engine.assess_sync(patient_data)
        
        # Should detect irAE
        assert result.irae_detected == True
        
        # Should identify hepatic system
        hepatic_finding = next(
            (f for f in result.affected_systems if f.system.value == "Hepatic"),
            None
        )
        assert hepatic_finding is not None
        assert hepatic_finding.detected == True
        
        # Should recognize immunotherapy context
        assert result.immunotherapy_context.on_immunotherapy == True
        
        # Severity should be at least Grade 2 (AST/ALT > 5x ULN)
        assert result.overall_severity in [Severity.GRADE_2, Severity.GRADE_3, Severity.GRADE_4]
    
    def test_colitis_scenario(self):
        """Test assessment of possible immune-related colitis."""
        patient_data = PatientData(
            patient_id="TEST002",
            age=58,
            cancer_type="Lung cancer",
            medications=[
                Medication(name="Nivolumab", is_immunotherapy=True, drug_class="PD-1"),
            ],
            symptoms=[
                PatientSymptom(symptom="diarrhea", severity="moderate", reported_date=datetime.now()),
                PatientSymptom(symptom="abdominal pain", reported_date=datetime.now()),
            ],
            raw_notes="Patient reports 6 watery stools per day for the past 3 days. Started after 2nd cycle of nivolumab.",
        )
        
        result = self.engine.assess_sync(patient_data)
        
        # Should detect irAE
        assert result.irae_detected == True
        
        # Should identify GI system
        gi_finding = next(
            (f for f in result.affected_systems if f.system.value == "Gastrointestinal"),
            None
        )
        assert gi_finding is not None
        assert gi_finding.detected == True
    
    def test_pneumonitis_scenario(self):
        """Test assessment of possible immune-related pneumonitis."""
        patient_data = PatientData(
            medications=[
                Medication(name="Atezolizumab", is_immunotherapy=True, drug_class="PD-L1"),
            ],
            vitals=[
                VitalSigns(
                    date=datetime.now(),
                    oxygen_saturation=91,
                    respiratory_rate=24,
                ),
            ],
            symptoms=[
                PatientSymptom(symptom="dyspnea", reported_date=datetime.now()),
                PatientSymptom(symptom="cough", reported_date=datetime.now()),
            ],
            raw_notes="CT chest shows new bilateral ground-glass opacities",
        )
        
        result = self.engine.assess_sync(patient_data)
        
        # Should detect irAE
        assert result.irae_detected == True
        
        # Should identify pulmonary system
        pulm_finding = next(
            (f for f in result.affected_systems if f.system.value == "Pulmonary"),
            None
        )
        assert pulm_finding is not None
        assert pulm_finding.detected == True
        
        # Should be at least moderately urgent given hypoxia (SpO2 91%)
        # Note: The exact urgency depends on severity calculation
        assert result.urgency in [Urgency.SOON, Urgency.URGENT, Urgency.EMERGENCY]
    
    def test_myocarditis_scenario(self):
        """Test assessment of possible immune-related myocarditis."""
        patient_data = PatientData(
            medications=[
                Medication(name="Nivolumab", is_immunotherapy=True, drug_class="PD-1"),
                Medication(name="Ipilimumab", is_immunotherapy=True, drug_class="CTLA-4"),
            ],
            labs=[
                LabResult(
                    name="Troponin", value=0.25, unit="ng/mL",
                    reference_low=0, reference_high=0.04,
                    date=datetime.now(), is_abnormal=True
                ),
                LabResult(
                    name="BNP", value=450, unit="pg/mL",
                    reference_low=0, reference_high=100,
                    date=datetime.now(), is_abnormal=True
                ),
            ],
            symptoms=[
                PatientSymptom(symptom="chest pain", reported_date=datetime.now()),
                PatientSymptom(symptom="dyspnea", reported_date=datetime.now()),
            ],
        )
        
        result = self.engine.assess_sync(patient_data)
        
        # Should detect irAE
        assert result.irae_detected == True
        
        # Should identify cardiac system
        cardiac_finding = next(
            (f for f in result.affected_systems if f.system.value == "Cardiac"),
            None
        )
        assert cardiac_finding is not None
        assert cardiac_finding.detected == True
        
        # Combination therapy + elevated troponin should be urgent/emergency
        assert result.urgency in [Urgency.URGENT, Urgency.EMERGENCY]
        
        # Should recognize combination therapy
        assert result.immunotherapy_context.combination_therapy == True
    
    def test_no_irae_scenario(self):
        """Test assessment when no irAE is present."""
        patient_data = PatientData(
            medications=[
                Medication(name="Pembrolizumab", is_immunotherapy=True, drug_class="PD-1"),
            ],
            labs=[
                LabResult(
                    name="AST", value=25, unit="U/L",
                    reference_low=10, reference_high=40,
                    date=datetime.now(), is_abnormal=False
                ),
                LabResult(
                    name="ALT", value=30, unit="U/L",
                    reference_low=7, reference_high=56,
                    date=datetime.now(), is_abnormal=False
                ),
            ],
            vitals=[
                VitalSigns(
                    date=datetime.now(),
                    oxygen_saturation=98,
                    heart_rate=72,
                    blood_pressure_systolic=120,
                    blood_pressure_diastolic=80,
                ),
            ],
        )
        
        result = self.engine.assess_sync(patient_data)
        
        # Should not detect significant irAE
        assert result.irae_detected == False
        
        # Urgency should be routine
        assert result.urgency == Urgency.ROUTINE
    
    def test_no_immunotherapy_scenario(self):
        """Test assessment when patient is not on immunotherapy."""
        patient_data = PatientData(
            medications=[
                Medication(name="Carboplatin"),
                Medication(name="Paclitaxel"),
            ],
            symptoms=[
                PatientSymptom(symptom="diarrhea", reported_date=datetime.now()),
            ],
        )
        
        result = self.engine.assess_sync(patient_data)
        
        # Should recognize no immunotherapy
        assert result.immunotherapy_context.on_immunotherapy == False
        
        # Causality should be unlikely or uncertain
        assert result.causality.likelihood in [Likelihood.UNLIKELY, Likelihood.UNCERTAIN]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
