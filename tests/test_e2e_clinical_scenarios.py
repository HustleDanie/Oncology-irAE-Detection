"""
End-to-End Clinical Scenario Tests

This module tests the complete irAE detection pipeline from raw patient data
through to final assessment output. Each test represents a realistic clinical
case that exercises the full system.

Run with: python -m pytest tests/test_e2e_clinical_scenarios.py -v -s
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.patient import (
    PatientData, LabResult, Medication, PatientSymptom,
    VitalSigns, ClinicalNote, ImagingSummary
)
from src.models.assessment import Likelihood, Severity, Urgency, OrganSystem
from src.llm.assessment_engine import IRAEAssessmentEngine
from src.analyzers import ImmunotherapyDetector
from src.parsers import LabParser, MedicationParser, SymptomParser


def print_assessment_summary(result, patient_id: str):
    """Print a formatted summary of the assessment."""
    print(f"\n{'='*70}")
    print(f"PATIENT: {patient_id}")
    print(f"{'='*70}")
    print(f"irAE Detected: {'✓ YES' if result.irae_detected else '✗ NO'}")
    print(f"Overall Severity: {result.overall_severity.value}")
    print(f"Urgency: {result.urgency.value}")
    
    print(f"\nAffected Systems:")
    for finding in result.affected_systems:
        if finding.detected:
            print(f"  • {finding.system.value}: {finding.severity.value if finding.severity else 'Unknown'}")
            for f in finding.findings[:3]:  # First 3 findings
                print(f"    - {f}")
    
    print(f"\nImmunotherapy Context:")
    ctx = result.immunotherapy_context
    print(f"  On Immunotherapy: {ctx.on_immunotherapy}")
    print(f"  Agents: {', '.join(ctx.agents) if ctx.agents else 'None'}")
    print(f"  Drug Classes: {', '.join(ctx.drug_classes) if ctx.drug_classes else 'None'}")
    print(f"  Combination Therapy: {ctx.combination_therapy}")
    
    print(f"\nRecommended Actions:")
    for action in result.recommended_actions[:5]:
        print(f"  [{action.priority}] {action.action}")
    
    print(f"\n{result.disclaimer}")
    print(f"{'='*70}\n")


class TestEndToEndClinicalScenarios:
    """End-to-end tests with complete patient scenarios."""
    
    def setup_method(self):
        self.engine = IRAEAssessmentEngine(use_llm=False)
    
    # =========================================================================
    # SCENARIO 1: Immune-Related Hepatitis (Grade 2)
    # =========================================================================
    
    def test_e2e_hepatitis_grade2(self):
        """
        E2E Test: 58-year-old melanoma patient on pembrolizumab with 
        moderate transaminase elevation (Grade 2 hepatitis).
        """
        patient = PatientData(
            patient_id="E2E_HEPATITIS_001",
            age=58,
            cancer_type="Metastatic Melanoma",
            medications=[
                Medication(
                    name="Pembrolizumab",
                    dose="200mg",
                    route="IV",
                    frequency="every 3 weeks",
                    is_immunotherapy=True,
                    drug_class="PD-1"
                ),
                Medication(name="Ondansetron", dose="8mg", frequency="PRN"),
            ],
            labs=[
                LabResult(
                    name="AST",
                    value=185,
                    unit="U/L",
                    reference_low=10,
                    reference_high=40,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="ALT",
                    value=220,
                    unit="U/L",
                    reference_low=7,
                    reference_high=56,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="Total Bilirubin",
                    value=1.8,
                    unit="mg/dL",
                    reference_low=0.1,
                    reference_high=1.2,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="Alkaline Phosphatase",
                    value=145,
                    unit="U/L",
                    reference_low=44,
                    reference_high=147,
                    date=datetime.now(),
                    is_abnormal=False
                ),
            ],
            symptoms=[
                PatientSymptom(
                    symptom="fatigue",
                    severity="moderate",
                    reported_date=datetime.now() - timedelta(days=5)
                ),
                PatientSymptom(
                    symptom="nausea",
                    severity="mild",
                    reported_date=datetime.now() - timedelta(days=3)
                ),
                PatientSymptom(
                    symptom="decreased appetite",
                    reported_date=datetime.now() - timedelta(days=4)
                ),
            ],
            vitals=[
                VitalSigns(
                    date=datetime.now(),
                    temperature=37.2,
                    heart_rate=78,
                    blood_pressure_systolic=128,
                    blood_pressure_diastolic=76,
                    respiratory_rate=16,
                    oxygen_saturation=98
                ),
            ],
            notes=[
                ClinicalNote(
                    date=datetime.now(),
                    note_type="progress",
                    author="Dr. Smith, Oncology",
                    content="""
                    58yo male with metastatic melanoma on pembrolizumab, cycle 5.
                    Presents with fatigue and mild nausea x 5 days.
                    
                    Labs today show elevated transaminases:
                    - AST 185 (4.6x ULN)
                    - ALT 220 (3.9x ULN)
                    - Total bilirubin 1.8 (mildly elevated)
                    
                    No jaundice on exam. Abdomen soft, mild RUQ tenderness.
                    
                    Assessment: Likely immune-related hepatitis, Grade 2
                    Plan:
                    1. Hold pembrolizumab
                    2. Hepatitis panel to rule out viral etiology
                    3. Start prednisone 1mg/kg daily
                    4. Recheck LFTs in 3 days
                    """
                )
            ],
            raw_notes="Patient on pembrolizumab for melanoma with elevated liver enzymes"
        )
        
        # Run assessment
        result = self.engine.assess_sync(patient)
        
        # Print summary
        print_assessment_summary(result, patient.patient_id)
        
        # Assertions
        assert result.irae_detected == True
        assert result.immunotherapy_context.on_immunotherapy == True
        assert "PD-1" in result.immunotherapy_context.drug_classes
        
        # Find hepatic system
        hepatic = next(
            (f for f in result.affected_systems if f.system == OrganSystem.HEPATIC),
            None
        )
        assert hepatic is not None
        assert hepatic.detected == True
        assert hepatic.severity == Severity.GRADE_2
    
    # =========================================================================
    # SCENARIO 2: Immune-Related Colitis (Grade 3)
    # =========================================================================
    
    def test_e2e_colitis_grade3(self):
        """
        E2E Test: 65-year-old with NSCLC on combination ipi/nivo
        with severe bloody diarrhea (Grade 3 colitis).
        """
        patient = PatientData(
            patient_id="E2E_COLITIS_001",
            age=65,
            cancer_type="Non-Small Cell Lung Cancer",
            medications=[
                Medication(
                    name="Nivolumab",
                    dose="3mg/kg",
                    route="IV",
                    frequency="every 3 weeks",
                    is_immunotherapy=True,
                    drug_class="PD-1"
                ),
                Medication(
                    name="Ipilimumab",
                    dose="1mg/kg",
                    route="IV",
                    frequency="every 3 weeks",
                    is_immunotherapy=True,
                    drug_class="CTLA-4"
                ),
            ],
            labs=[
                LabResult(
                    name="Hemoglobin",
                    value=10.5,
                    unit="g/dL",
                    reference_low=13.5,
                    reference_high=17.5,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="WBC",
                    value=11.8,
                    unit="x10^9/L",
                    reference_low=4.5,
                    reference_high=11.0,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="CRP",
                    value=75,
                    unit="mg/L",
                    reference_low=0,
                    reference_high=10,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="Albumin",
                    value=2.9,
                    unit="g/dL",
                    reference_low=3.5,
                    reference_high=5.0,
                    date=datetime.now(),
                    is_abnormal=True
                ),
            ],
            symptoms=[
                PatientSymptom(
                    symptom="bloody diarrhea",
                    severity="severe",
                    reported_date=datetime.now() - timedelta(days=2)
                ),
                PatientSymptom(
                    symptom="severe abdominal pain",
                    severity="severe",
                    reported_date=datetime.now() - timedelta(days=2)
                ),
                PatientSymptom(
                    symptom="urgency",
                    reported_date=datetime.now() - timedelta(days=3)
                ),
                PatientSymptom(
                    symptom="tenesmus",
                    reported_date=datetime.now() - timedelta(days=2)
                ),
            ],
            vitals=[
                VitalSigns(
                    date=datetime.now(),
                    temperature=38.2,
                    heart_rate=105,
                    blood_pressure_systolic=108,
                    blood_pressure_diastolic=65,
                    respiratory_rate=18,
                    oxygen_saturation=97
                ),
            ],
            notes=[
                ClinicalNote(
                    date=datetime.now(),
                    note_type="emergency",
                    author="Dr. Johnson, ED",
                    content="""
                    65yo with NSCLC on ipi/nivo combination therapy x 4 cycles.
                    Presents with 8-10 bloody stools daily x 3 days.
                    Severe crampy abdominal pain, tenesmus.
                    Unable to tolerate PO intake.
                    
                    Vitals: T 38.2, HR 105, BP 108/65
                    Labs: Anemia (Hgb 10.5), leukocytosis, elevated CRP
                    
                    Exam: Diffuse abdominal tenderness, hyperactive bowel sounds
                    
                    Assessment: Severe immune-related colitis (Grade 3)
                    
                    Plan:
                    - Admit to hospital
                    - NPO, IV fluids
                    - IV methylprednisolone 2mg/kg daily
                    - GI consult for colonoscopy
                    - C. diff toxin, stool cultures
                    - Hold all immunotherapy
                    """
                )
            ],
            raw_notes="Severe bloody diarrhea on combination immunotherapy"
        )
        
        # Run assessment
        result = self.engine.assess_sync(patient)
        
        # Print summary
        print_assessment_summary(result, patient.patient_id)
        
        # Assertions
        assert result.irae_detected == True
        assert result.immunotherapy_context.combination_therapy == True
        
        # Find GI system
        gi = next(
            (f for f in result.affected_systems if f.system == OrganSystem.GASTROINTESTINAL),
            None
        )
        assert gi is not None
        assert gi.detected == True
        assert gi.severity in [Severity.GRADE_2, Severity.GRADE_3, Severity.GRADE_4]
        
        # Should be urgent
        assert result.urgency in [Urgency.URGENT, Urgency.EMERGENCY]
    
    # =========================================================================
    # SCENARIO 3: Immune-Related Pneumonitis (Grade 2)
    # =========================================================================
    
    def test_e2e_pneumonitis_grade2(self):
        """
        E2E Test: 70-year-old with RCC on nivolumab with cough,
        dyspnea, and ground-glass opacities on CT.
        """
        patient = PatientData(
            patient_id="E2E_PNEUMONITIS_001",
            age=70,
            cancer_type="Renal Cell Carcinoma",
            medications=[
                Medication(
                    name="Nivolumab",
                    dose="240mg",
                    route="IV",
                    frequency="every 2 weeks",
                    is_immunotherapy=True,
                    drug_class="PD-1"
                ),
            ],
            labs=[
                LabResult(
                    name="WBC",
                    value=9.5,
                    unit="x10^9/L",
                    reference_low=4.5,
                    reference_high=11.0,
                    date=datetime.now(),
                    is_abnormal=False
                ),
                LabResult(
                    name="LDH",
                    value=320,
                    unit="U/L",
                    reference_low=140,
                    reference_high=280,
                    date=datetime.now(),
                    is_abnormal=True
                ),
            ],
            symptoms=[
                PatientSymptom(
                    symptom="dry cough",
                    severity="moderate",
                    reported_date=datetime.now() - timedelta(days=10)
                ),
                PatientSymptom(
                    symptom="dyspnea on exertion",
                    severity="moderate",
                    reported_date=datetime.now() - timedelta(days=7)
                ),
                PatientSymptom(
                    symptom="fatigue",
                    severity="moderate",
                    reported_date=datetime.now() - timedelta(days=14)
                ),
            ],
            vitals=[
                VitalSigns(
                    date=datetime.now(),
                    temperature=37.0,
                    heart_rate=88,
                    blood_pressure_systolic=135,
                    blood_pressure_diastolic=82,
                    respiratory_rate=20,
                    oxygen_saturation=93
                ),
            ],
            imaging=[
                ImagingSummary(
                    date=datetime.now(),
                    modality="CT",
                    body_region="Chest",
                    findings="New bilateral ground-glass opacities predominantly in lower lobes. No pleural effusion. Organizing pneumonia pattern.",
                    impression="Findings concerning for drug-induced/immune-related pneumonitis. Recommend clinical correlation."
                )
            ],
            notes=[
                ClinicalNote(
                    date=datetime.now(),
                    note_type="progress",
                    author="Dr. Williams, Oncology",
                    content="""
                    70yo with mRCC on nivolumab x 8 cycles.
                    Progressive dry cough and dyspnea on exertion x 2 weeks.
                    Can walk about half a block before SOB (baseline was several blocks).
                    
                    SpO2 93% on room air (baseline 97%)
                    
                    CT chest: Bilateral GGO with organizing pneumonia pattern
                    
                    Assessment: Grade 2 immune-related pneumonitis
                    
                    Plan:
                    - Hold nivolumab
                    - Start prednisone 1-2mg/kg daily
                    - Pulmonary function tests
                    - Consider bronchoscopy with BAL if no improvement
                    - Recheck in 48-72 hours
                    """
                )
            ],
            raw_notes="Cough and dyspnea on nivolumab, CT shows ground-glass opacities"
        )
        
        # Run assessment
        result = self.engine.assess_sync(patient)
        
        # Print summary
        print_assessment_summary(result, patient.patient_id)
        
        # Assertions
        assert result.irae_detected == True
        
        # Find pulmonary system
        lung = next(
            (f for f in result.affected_systems if f.system == OrganSystem.PULMONARY),
            None
        )
        assert lung is not None
        assert lung.detected == True
        assert lung.severity in [Severity.GRADE_2, Severity.GRADE_3]
    
    # =========================================================================
    # SCENARIO 4: Immune-Related Thyroiditis
    # =========================================================================
    
    def test_e2e_hypothyroidism(self):
        """
        E2E Test: 52-year-old with melanoma developing hypothyroidism
        on pembrolizumab.
        """
        patient = PatientData(
            patient_id="E2E_THYROID_001",
            age=52,
            cancer_type="Melanoma",
            medications=[
                Medication(
                    name="Pembrolizumab",
                    dose="200mg",
                    route="IV",
                    frequency="every 3 weeks",
                    is_immunotherapy=True,
                    drug_class="PD-1"
                ),
            ],
            labs=[
                LabResult(
                    name="TSH",
                    value=42.5,
                    unit="mIU/L",
                    reference_low=0.4,
                    reference_high=4.0,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="Free T4",
                    value=0.5,
                    unit="ng/dL",
                    reference_low=0.8,
                    reference_high=1.8,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="Free T3",
                    value=1.5,
                    unit="pg/mL",
                    reference_low=2.3,
                    reference_high=4.2,
                    date=datetime.now(),
                    is_abnormal=True
                ),
            ],
            symptoms=[
                PatientSymptom(
                    symptom="fatigue",
                    severity="moderate",
                    reported_date=datetime.now() - timedelta(days=21)
                ),
                PatientSymptom(
                    symptom="cold intolerance",
                    reported_date=datetime.now() - timedelta(days=14)
                ),
                PatientSymptom(
                    symptom="constipation",
                    severity="mild",
                    reported_date=datetime.now() - timedelta(days=10)
                ),
                PatientSymptom(
                    symptom="weight gain",
                    reported_date=datetime.now() - timedelta(days=30)
                ),
            ],
            vitals=[
                VitalSigns(
                    date=datetime.now(),
                    temperature=36.5,
                    heart_rate=58,
                    blood_pressure_systolic=118,
                    blood_pressure_diastolic=72,
                    respiratory_rate=14,
                    oxygen_saturation=99
                ),
            ],
            notes=[
                ClinicalNote(
                    date=datetime.now(),
                    note_type="progress",
                    author="Dr. Lee, Oncology",
                    content="""
                    52yo with melanoma on pembrolizumab, cycle 12.
                    Complains of progressive fatigue, cold intolerance, 
                    constipation, and 10lb weight gain over 2 months.
                    
                    Labs: TSH 42.5 (very elevated), Free T4 0.5 (low)
                    Prior TSH 2 months ago was 2.8 (normal)
                    
                    Exam: Bradycardic, dry skin, delayed DTRs
                    
                    Assessment: Immune-related hypothyroidism
                    
                    Plan:
                    - Start levothyroxine 50mcg daily
                    - Recheck TSH in 6 weeks
                    - Can continue pembrolizumab
                    - Endocrine follow-up
                    """
                )
            ],
            raw_notes="Hypothyroidism on pembrolizumab"
        )
        
        # Run assessment
        result = self.engine.assess_sync(patient)
        
        # Print summary
        print_assessment_summary(result, patient.patient_id)
        
        # Assertions
        assert result.irae_detected == True
        
        # Find endocrine system
        endo = next(
            (f for f in result.affected_systems if f.system == OrganSystem.ENDOCRINE),
            None
        )
        assert endo is not None
        assert endo.detected == True
    
    # =========================================================================
    # SCENARIO 5: Immune-Related Myocarditis (EMERGENCY)
    # =========================================================================
    
    def test_e2e_myocarditis_emergency(self):
        """
        E2E Test: 62-year-old on combination therapy with chest pain
        and elevated troponin - EMERGENCY scenario.
        """
        patient = PatientData(
            patient_id="E2E_CARDIAC_001",
            age=62,
            cancer_type="Melanoma",
            medications=[
                Medication(
                    name="Nivolumab",
                    dose="3mg/kg",
                    route="IV",
                    is_immunotherapy=True,
                    drug_class="PD-1"
                ),
                Medication(
                    name="Ipilimumab",
                    dose="1mg/kg",
                    route="IV",
                    is_immunotherapy=True,
                    drug_class="CTLA-4"
                ),
            ],
            labs=[
                LabResult(
                    name="Troponin I",
                    value=3.2,
                    unit="ng/mL",
                    reference_low=0,
                    reference_high=0.04,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="BNP",
                    value=1250,
                    unit="pg/mL",
                    reference_low=0,
                    reference_high=100,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="CK-MB",
                    value=58,
                    unit="ng/mL",
                    reference_low=0,
                    reference_high=5,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="CRP",
                    value=145,
                    unit="mg/L",
                    reference_low=0,
                    reference_high=10,
                    date=datetime.now(),
                    is_abnormal=True
                ),
            ],
            symptoms=[
                PatientSymptom(
                    symptom="chest pain",
                    severity="moderate",
                    reported_date=datetime.now() - timedelta(days=1)
                ),
                PatientSymptom(
                    symptom="dyspnea",
                    severity="moderate",
                    reported_date=datetime.now() - timedelta(days=2)
                ),
                PatientSymptom(
                    symptom="palpitations",
                    reported_date=datetime.now() - timedelta(days=2)
                ),
                PatientSymptom(
                    symptom="fatigue",
                    severity="severe",
                    reported_date=datetime.now() - timedelta(days=3)
                ),
            ],
            vitals=[
                VitalSigns(
                    date=datetime.now(),
                    temperature=37.4,
                    heart_rate=115,
                    blood_pressure_systolic=95,
                    blood_pressure_diastolic=60,
                    respiratory_rate=22,
                    oxygen_saturation=94
                ),
            ],
            notes=[
                ClinicalNote(
                    date=datetime.now(),
                    note_type="emergency",
                    author="Dr. Chen, Cardiology",
                    content="""
                    URGENT - Possible immune-related myocarditis
                    
                    62yo on ipi/nivo combination for melanoma, 2nd cycle.
                    Presents with chest pain, dyspnea, palpitations x 2 days.
                    
                    EKG: Diffuse ST changes, low voltage, PVCs
                    Echo: EF 32% (prior 58%), diffuse hypokinesis
                    Troponin: 3.2 (markedly elevated)
                    BNP: 1250
                    
                    Cardiac MRI pending
                    
                    Assessment: High suspicion for immune-related myocarditis
                    This is LIFE-THREATENING
                    
                    Plan:
                    - CCU admission
                    - Continuous telemetry
                    - STOP all immunotherapy permanently
                    - High-dose methylprednisolone 1g IV daily x 3-5 days
                    - Cardiology co-management
                    - If no response, consider ATG or abatacept
                    """
                )
            ],
            raw_notes="Myocarditis on combination immunotherapy - emergency"
        )
        
        # Run assessment
        result = self.engine.assess_sync(patient)
        
        # Print summary
        print_assessment_summary(result, patient.patient_id)
        
        # Assertions
        assert result.irae_detected == True
        assert result.immunotherapy_context.combination_therapy == True
        
        # Find cardiac system
        cardiac = next(
            (f for f in result.affected_systems if f.system == OrganSystem.CARDIAC),
            None
        )
        assert cardiac is not None
        assert cardiac.detected == True
        assert cardiac.severity in [Severity.GRADE_3, Severity.GRADE_4]
        
        # Must be emergency
        assert result.urgency == Urgency.EMERGENCY
    
    # =========================================================================
    # SCENARIO 6: Multi-Organ irAE
    # =========================================================================
    
    def test_e2e_multiorgan_irae(self):
        """
        E2E Test: Patient with concurrent hepatitis AND colitis
        (common with CTLA-4 inhibitors).
        """
        patient = PatientData(
            patient_id="E2E_MULTIORGAN_001",
            age=55,
            cancer_type="Melanoma",
            medications=[
                Medication(
                    name="Ipilimumab",
                    dose="3mg/kg",
                    route="IV",
                    is_immunotherapy=True,
                    drug_class="CTLA-4"
                ),
            ],
            labs=[
                # Hepatic
                LabResult(
                    name="AST",
                    value=245,
                    unit="U/L",
                    reference_low=10,
                    reference_high=40,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="ALT",
                    value=310,
                    unit="U/L",
                    reference_low=7,
                    reference_high=56,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="Total Bilirubin",
                    value=2.4,
                    unit="mg/dL",
                    reference_low=0.1,
                    reference_high=1.2,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                # Inflammatory markers
                LabResult(
                    name="CRP",
                    value=95,
                    unit="mg/L",
                    reference_low=0,
                    reference_high=10,
                    date=datetime.now(),
                    is_abnormal=True
                ),
            ],
            symptoms=[
                # GI symptoms
                PatientSymptom(
                    symptom="diarrhea",
                    severity="moderate",
                    reported_date=datetime.now() - timedelta(days=4)
                ),
                PatientSymptom(
                    symptom="abdominal cramping",
                    severity="moderate",
                    reported_date=datetime.now() - timedelta(days=4)
                ),
                # Hepatic symptoms
                PatientSymptom(
                    symptom="fatigue",
                    severity="severe",
                    reported_date=datetime.now() - timedelta(days=7)
                ),
                PatientSymptom(
                    symptom="nausea",
                    severity="moderate",
                    reported_date=datetime.now() - timedelta(days=5)
                ),
            ],
            vitals=[
                VitalSigns(
                    date=datetime.now(),
                    temperature=37.6,
                    heart_rate=95,
                    blood_pressure_systolic=115,
                    blood_pressure_diastolic=70,
                    respiratory_rate=16,
                    oxygen_saturation=98
                ),
            ],
            notes=[
                ClinicalNote(
                    date=datetime.now(),
                    note_type="progress",
                    author="Dr. Martinez, Oncology",
                    content="""
                    55yo with melanoma on ipilimumab, 3rd cycle.
                    Presenting with both GI and hepatic symptoms.
                    
                    GI: 6-8 loose stools daily with cramping x 4 days
                    Hepatic: Fatigue, nausea, labs showing transaminitis
                    
                    Labs:
                    - AST 245 (6x ULN), ALT 310 (5.5x ULN)
                    - Bilirubin 2.4
                    - CRP elevated at 95
                    
                    Assessment: Multi-organ immune toxicity
                    1. Immune-related colitis (Grade 2)
                    2. Immune-related hepatitis (Grade 2-3)
                    
                    Plan:
                    - Admit for IV steroids
                    - Hold ipilimumab
                    - GI and hepatology consults
                    - May need colonoscopy and/or liver biopsy
                    """
                )
            ],
            raw_notes="Multi-organ irAE: hepatitis and colitis on ipilimumab"
        )
        
        # Run assessment
        result = self.engine.assess_sync(patient)
        
        # Print summary
        print_assessment_summary(result, patient.patient_id)
        
        # Assertions
        assert result.irae_detected == True
        
        # Should detect multiple organ systems
        affected = [f.system for f in result.affected_systems if f.detected]
        assert OrganSystem.HEPATIC in affected
        assert OrganSystem.GASTROINTESTINAL in affected
        
        # Should be at least urgent
        assert result.urgency in [Urgency.URGENT, Urgency.EMERGENCY]
    
    # =========================================================================
    # SCENARIO 7: Negative Control - Not on Immunotherapy
    # =========================================================================
    
    def test_e2e_no_immunotherapy(self):
        """
        E2E Test: Patient with similar symptoms but NOT on immunotherapy.
        System should recognize no ICI context.
        """
        patient = PatientData(
            patient_id="E2E_NEGATIVE_001",
            age=60,
            cancer_type="Breast Cancer",
            medications=[
                Medication(name="Tamoxifen", dose="20mg", frequency="daily"),
                Medication(name="Metformin", dose="1000mg", frequency="twice daily"),
                Medication(name="Lisinopril", dose="10mg", frequency="daily"),
            ],
            labs=[
                LabResult(
                    name="AST",
                    value=65,
                    unit="U/L",
                    reference_low=10,
                    reference_high=40,
                    date=datetime.now(),
                    is_abnormal=True
                ),
                LabResult(
                    name="ALT",
                    value=78,
                    unit="U/L",
                    reference_low=7,
                    reference_high=56,
                    date=datetime.now(),
                    is_abnormal=True
                ),
            ],
            symptoms=[
                PatientSymptom(
                    symptom="fatigue",
                    severity="mild",
                    reported_date=datetime.now() - timedelta(days=14)
                ),
            ],
            notes=[
                ClinicalNote(
                    date=datetime.now(),
                    note_type="progress",
                    author="Dr. Brown, Primary Care",
                    content="""
                    60yo with breast cancer on tamoxifen, also has diabetes.
                    Routine labs show mildly elevated LFTs.
                    Likely medication-related (tamoxifen vs metformin).
                    Not on any immunotherapy.
                    """
                )
            ],
            raw_notes="Elevated LFTs on tamoxifen, no immunotherapy"
        )
        
        # Run assessment
        result = self.engine.assess_sync(patient)
        
        # Print summary
        print_assessment_summary(result, patient.patient_id)
        
        # Assertions - should recognize no immunotherapy
        assert result.immunotherapy_context.on_immunotherapy == False
        assert result.immunotherapy_context.combination_therapy == False
        assert len(result.immunotherapy_context.agents) == 0


# =============================================================================
# MAIN - Run with verbose output
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ONCOLOGY irAE DETECTION SYSTEM - END-TO-END CLINICAL TESTS")
    print("="*70)
    
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s", "--tb=short"])
