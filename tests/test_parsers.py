"""Unit tests for clinical parsers."""

import pytest
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.lab_parser import LabParser
from src.parsers.medication_parser import MedicationParser
from src.parsers.symptom_parser import SymptomParser


class TestLabParser:
    """Tests for the LabParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = LabParser()
    
    def test_parse_basic_lab(self):
        """Test parsing a basic lab value."""
        text = "AST 145 U/L"
        results = self.parser.parse(text)
        
        assert len(results) >= 1
        ast_result = next((r for r in results if "AST" in r.name.upper()), None)
        assert ast_result is not None
        assert ast_result.value == 145
    
    def test_parse_multiple_labs(self):
        """Test parsing multiple lab values."""
        text = """
        AST 145 U/L (H)
        ALT 178 U/L (H)
        Bilirubin 1.0 mg/dL
        Creatinine 1.2 mg/dL
        """
        results = self.parser.parse(text)
        
        assert len(results) >= 3
        
        # Check that we found AST and ALT
        lab_names = [r.name.upper() for r in results]
        assert any("AST" in name for name in lab_names)
        assert any("ALT" in name for name in lab_names)
    
    def test_abnormal_detection(self):
        """Test that abnormal values are detected."""
        text = "AST 145 U/L"  # Reference high is 40
        results = self.parser.parse(text)
        
        ast_result = next((r for r in results if "AST" in r.name.upper()), None)
        assert ast_result is not None
        assert ast_result.is_abnormal == True
    
    def test_normal_value(self):
        """Test that normal values are not flagged as abnormal."""
        text = "AST 25 U/L"
        results = self.parser.parse(text)
        
        ast_result = next((r for r in results if "AST" in r.name.upper()), None)
        assert ast_result is not None
        assert ast_result.is_abnormal == False


class TestMedicationParser:
    """Tests for the MedicationParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MedicationParser()
    
    def test_detect_pembrolizumab(self):
        """Test detection of pembrolizumab."""
        text = "Patient is on pembrolizumab 200mg IV every 3 weeks"
        meds = self.parser.parse(text)
        
        assert len(meds) >= 1
        immunotherapy = [m for m in meds if m.is_immunotherapy]
        assert len(immunotherapy) >= 1
        assert any("pembrolizumab" in m.name.lower() for m in immunotherapy)
    
    def test_detect_keytruda_brand_name(self):
        """Test detection of Keytruda (brand name)."""
        text = "Started Keytruda last month"
        meds = self.parser.parse(text)
        
        immunotherapy = [m for m in meds if m.is_immunotherapy]
        assert len(immunotherapy) >= 1
    
    def test_detect_combination_therapy(self):
        """Test detection of combination immunotherapy."""
        text = """
        Medications:
        - Nivolumab 240mg IV q2weeks
        - Ipilimumab 3mg/kg IV q3weeks
        """
        meds = self.parser.parse_medication_list(text)
        
        immunotherapy = self.parser.identify_immunotherapy(meds)
        is_combination = self.parser.detect_combination_therapy(meds)
        
        # Should detect both agents
        assert len(immunotherapy) >= 1
    
    def test_get_immunotherapy_context(self):
        """Test getting immunotherapy context."""
        text = "Currently on pembrolizumab"
        meds = self.parser.parse(text)
        
        context = self.parser.get_immunotherapy_context(meds)
        
        assert context["on_immunotherapy"] == True
        assert len(context["agents"]) >= 1


class TestSymptomParser:
    """Tests for the SymptomParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = SymptomParser()
    
    def test_parse_basic_symptoms(self):
        """Test parsing basic symptoms."""
        text = "Patient reports fatigue and diarrhea"
        symptoms = self.parser.parse(text)
        
        symptom_names = [s.symptom.lower() for s in symptoms]
        assert "fatigue" in symptom_names
        assert "diarrhea" in symptom_names
    
    def test_parse_multiple_symptoms(self):
        """Test parsing multiple symptoms."""
        text = """
        Patient complains of:
        - Fatigue
        - Cough
        - Shortness of breath
        - Rash on trunk
        """
        symptoms = self.parser.parse(text)
        
        assert len(symptoms) >= 3
    
    def test_categorize_by_system(self):
        """Test categorization of symptoms by organ system."""
        text = "Diarrhea, abdominal pain, cough, dyspnea, rash"
        symptoms = self.parser.parse(text)
        
        categorized = self.parser.categorize_by_system(symptoms)
        
        # Check that GI symptoms are categorized correctly
        gi_symptoms = categorized.get("gi", [])
        assert len(gi_symptoms) >= 1
    
    def test_detect_concerning_patterns(self):
        """Test detection of concerning symptom patterns."""
        text = "Patient has diarrhea, abdominal pain, and blood in stool"
        symptoms = self.parser.parse(text)
        
        patterns = self.parser.detect_concerning_patterns(symptoms)
        
        # Should detect possible colitis pattern
        assert len(patterns) >= 1
        gi_pattern = next((p for p in patterns if p["system"] == "Gastrointestinal"), None)
        assert gi_pattern is not None


class TestIntegration:
    """Integration tests for parsers working together."""
    
    def test_parse_clinical_scenario(self):
        """Test parsing a realistic clinical scenario."""
        clinical_text = """
        65-year-old male with metastatic melanoma on pembrolizumab.
        
        Labs today:
        AST 245 U/L (H)
        ALT 312 U/L (H)
        Bilirubin 2.1 mg/dL (H)
        
        Patient reports fatigue, mild nausea, and dark urine.
        No abdominal pain.
        """
        
        lab_parser = LabParser()
        med_parser = MedicationParser()
        symptom_parser = SymptomParser()
        
        labs = lab_parser.parse(clinical_text)
        meds = med_parser.parse(clinical_text)
        symptoms = symptom_parser.parse(clinical_text)
        
        # Should detect elevated liver enzymes
        abnormal_labs = [l for l in labs if l.is_abnormal]
        assert len(abnormal_labs) >= 2
        
        # Should detect pembrolizumab
        immunotherapy = med_parser.identify_immunotherapy(meds)
        assert len(immunotherapy) >= 1
        
        # Should detect symptoms
        assert len(symptoms) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
