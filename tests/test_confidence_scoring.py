"""Unit tests for confidence scoring system."""

import pytest
from datetime import datetime
import asyncio

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.patient import PatientData, LabResult, Medication, PatientSymptom, VitalSigns, ClinicalNote
from src.models.assessment import Severity, OrganSystem, ConfidenceScore
from src.llm.assessment_engine import IRAEAssessmentEngine


class TestConfidenceScoring:
    """Tests for the confidence scoring system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Use rule-based only (no LLM)
        self.engine = IRAEAssessmentEngine(llm_client=None, use_llm=False)
    
    def test_confidence_model_structure(self):
        """Test ConfidenceScore model structure."""
        score = ConfidenceScore(
            overall_confidence=0.75,
            evidence_strength=0.8,
            data_completeness=0.5,
            rule_match_count=3,
            confidence_factors=["Lab data available"],
            uncertainty_factors=["No vital signs provided"],
        )
        
        assert score.overall_confidence == 0.75
        assert score.confidence_level == "Moderate"
    
    def test_confidence_level_high(self):
        """Test high confidence level (>=0.8)."""
        score = ConfidenceScore(
            overall_confidence=0.85,
            evidence_strength=0.9,
            data_completeness=0.75,
        )
        
        assert score.confidence_level == "High"
    
    def test_confidence_level_low(self):
        """Test low confidence level (0.3-0.5)."""
        score = ConfidenceScore(
            overall_confidence=0.35,
            evidence_strength=0.4,
            data_completeness=0.25,
        )
        
        assert score.confidence_level == "Low"
    
    def test_confidence_level_very_low(self):
        """Test very low confidence level (<0.3)."""
        score = ConfidenceScore(
            overall_confidence=0.2,
            evidence_strength=0.15,
            data_completeness=0.25,
        )
        
        assert score.confidence_level == "Very Low"
    
    def test_assessment_includes_confidence(self):
        """Test that assessment includes confidence score."""
        patient_data = PatientData(
            medications=[
                Medication(name="Pembrolizumab", is_immunotherapy=True, drug_class="PD-1"),
            ],
            labs=[
                LabResult(
                    name="AST", value=245, unit="U/L",
                    reference_low=10, reference_high=40,
                    date=datetime.now(), is_abnormal=True
                ),
            ]
        )
        
        assessment = self.engine.assess_sync(patient_data)
        
        # Should have confidence score
        assert assessment.confidence_score is not None
        assert 0 <= assessment.confidence_score.overall_confidence <= 1
        assert 0 <= assessment.confidence_score.evidence_strength <= 1
        assert 0 <= assessment.confidence_score.data_completeness <= 1
    
    def test_confidence_data_completeness_full(self):
        """Test data completeness with all data types present."""
        patient_data = PatientData(
            medications=[
                Medication(name="Pembrolizumab", is_immunotherapy=True),
            ],
            labs=[
                LabResult(
                    name="AST", value=245, unit="U/L",
                    reference_low=10, reference_high=40,
                    date=datetime.now(), is_abnormal=True
                ),
            ],
            vitals=[
                VitalSigns(date=datetime.now(), heart_rate=72),
            ],
            notes=[
                ClinicalNote(date=datetime.now(), note_type="Progress Note", content="Patient doing well."),
            ]
        )
        
        assessment = self.engine.assess_sync(patient_data)
        
        # All 4 data types present = 100% data completeness
        assert assessment.confidence_score.data_completeness == 1.0
    
    def test_confidence_data_completeness_partial(self):
        """Test data completeness with some data types missing."""
        patient_data = PatientData(
            medications=[
                Medication(name="Pembrolizumab", is_immunotherapy=True),
            ],
            # No labs, no vitals, no notes
        )
        
        assessment = self.engine.assess_sync(patient_data)
        
        # Only 1 of 4 data types present = 25% data completeness
        assert assessment.confidence_score.data_completeness == 0.25
    
    def test_confidence_factors_populated(self):
        """Test that confidence factors are populated."""
        patient_data = PatientData(
            medications=[
                Medication(name="Pembrolizumab", is_immunotherapy=True, drug_class="PD-1"),
            ],
            labs=[
                LabResult(
                    name="Troponin", value=0.5, unit="ng/mL",
                    reference_low=0, reference_high=0.04,
                    date=datetime.now(), is_abnormal=True
                ),
            ],
        )
        
        assessment = self.engine.assess_sync(patient_data)
        
        # Should have some confidence factors
        assert len(assessment.confidence_score.confidence_factors) > 0
        assert "Immunotherapy status confirmed" in assessment.confidence_score.confidence_factors
    
    def test_uncertainty_factors_populated(self):
        """Test that uncertainty factors are populated when data is missing."""
        patient_data = PatientData(
            medications=[
                Medication(name="Pembrolizumab", is_immunotherapy=True),
            ],
            # Missing labs, vitals, notes
        )
        
        assessment = self.engine.assess_sync(patient_data)
        
        # Should have uncertainty factors for missing data
        assert len(assessment.confidence_score.uncertainty_factors) > 0
        assert any("No laboratory" in f for f in assessment.confidence_score.uncertainty_factors)
    
    def test_rule_match_count(self):
        """Test that rule match count is tracked."""
        patient_data = PatientData(
            medications=[
                Medication(name="Pembrolizumab", is_immunotherapy=True),
            ],
            labs=[
                LabResult(
                    name="AST", value=500, unit="U/L",
                    reference_low=10, reference_high=40,
                    date=datetime.now(), is_abnormal=True
                ),
                LabResult(
                    name="Creatinine", value=3.0, unit="mg/dL",
                    reference_low=0.7, reference_high=1.2,
                    date=datetime.now(), is_abnormal=True
                ),
            ],
        )
        
        assessment = self.engine.assess_sync(patient_data)
        
        # Should have at least 2 rule matches (liver + renal)
        assert assessment.confidence_score.rule_match_count >= 2
    
    def test_no_irae_detected_low_confidence(self):
        """Test that no irAE detection results in lower confidence."""
        patient_data = PatientData(
            medications=[
                Medication(name="Metformin"),  # Not immunotherapy
            ],
        )
        
        assessment = self.engine.assess_sync(patient_data)
        
        # Should have low confidence when no irAE detected
        assert assessment.confidence_score.overall_confidence < 0.5


class TestConfidenceScoreProperties:
    """Tests for ConfidenceScore property methods."""
    
    def test_confidence_level_boundaries(self):
        """Test confidence level boundary values."""
        # Exactly at boundaries
        assert ConfidenceScore(
            overall_confidence=0.80, evidence_strength=0.5, data_completeness=0.5
        ).confidence_level == "High"
        
        assert ConfidenceScore(
            overall_confidence=0.50, evidence_strength=0.5, data_completeness=0.5
        ).confidence_level == "Moderate"
        
        assert ConfidenceScore(
            overall_confidence=0.30, evidence_strength=0.5, data_completeness=0.5
        ).confidence_level == "Low"
        
        assert ConfidenceScore(
            overall_confidence=0.29, evidence_strength=0.5, data_completeness=0.5
        ).confidence_level == "Very Low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
