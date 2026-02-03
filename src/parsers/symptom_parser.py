"""Symptom parser for extracting patient-reported symptoms."""

import re
from datetime import datetime
from typing import Optional

from ..models.patient import PatientSymptom
from ..utils.constants import ORGAN_SYSTEMS


class SymptomParser:
    """Parser for extracting symptoms from clinical text."""
    
    # Symptom severity modifiers
    SEVERITY_PATTERNS = {
        "mild": ["mild", "slight", "minimal", "minor", "1+"],
        "moderate": ["moderate", "2+", "some", "noticeable"],
        "severe": ["severe", "significant", "marked", "3+", "4+", "intense", "extreme"],
    }
    
    # Build comprehensive symptom list from organ systems
    def __init__(self):
        self.symptom_keywords = self._build_symptom_keywords()
        self.symptom_pattern = self._build_symptom_pattern()
    
    def _build_symptom_keywords(self) -> dict[str, list[str]]:
        """Build symptom keywords organized by organ system."""
        keywords = {}
        for system_key, system_info in ORGAN_SYSTEMS.items():
            keywords[system_key] = system_info.get("key_symptoms", [])
        
        # Add additional common symptoms
        keywords["general"] = [
            "fatigue", "weakness", "malaise", "fever", "chills",
            "weight loss", "weight gain", "anorexia", "night sweats",
        ]
        
        return keywords
    
    def _build_symptom_pattern(self) -> re.Pattern:
        """Build regex pattern for symptom detection."""
        all_symptoms = []
        for symptoms in self.symptom_keywords.values():
            all_symptoms.extend(symptoms)
        
        # Add common symptom variations
        all_symptoms.extend([
            "pain", "ache", "discomfort", "swelling", "edema",
            "nausea", "vomiting", "constipation", "bloating",
            "cough", "wheeze", "sob", "breathless",
            "rash", "itch", "lesion", "sore",
            "dizzy", "lightheaded", "syncope", "faint",
            "headache", "numbness", "tingling", "paresthesia",
            "palpitation", "chest pain", "chest tightness",
        ])
        
        # Remove duplicates and create pattern
        unique_symptoms = list(set(all_symptoms))
        pattern_str = r"\b(" + "|".join(re.escape(s) for s in unique_symptoms) + r")\b"
        return re.compile(pattern_str, re.IGNORECASE)
    
    def parse(
        self, 
        text: str, 
        reported_date: Optional[datetime] = None
    ) -> list[PatientSymptom]:
        """
        Parse symptoms from clinical text.
        
        Args:
            text: Raw clinical text
            reported_date: Date symptoms were reported
            
        Returns:
            List of PatientSymptom objects
        """
        if reported_date is None:
            reported_date = datetime.now()
        
        symptoms = []
        seen = set()
        
        # Find all symptom mentions
        for match in self.symptom_pattern.finditer(text):
            symptom_name = match.group(1).lower()
            
            if symptom_name in seen:
                continue
            seen.add(symptom_name)
            
            # Get surrounding context for severity
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].lower()
            
            severity = self._extract_severity(context)
            
            symptoms.append(PatientSymptom(
                symptom=symptom_name,
                severity=severity,
                reported_date=reported_date,
            ))
        
        return symptoms
    
    def _extract_severity(self, context: str) -> Optional[str]:
        """Extract severity from surrounding context."""
        for severity, patterns in self.SEVERITY_PATTERNS.items():
            for pattern in patterns:
                if pattern in context:
                    return severity
        return None
    
    def categorize_by_system(
        self, 
        symptoms: list[PatientSymptom]
    ) -> dict[str, list[PatientSymptom]]:
        """
        Categorize symptoms by organ system.
        
        Args:
            symptoms: List of symptoms
            
        Returns:
            Dictionary mapping system names to symptoms
        """
        categorized = {key: [] for key in self.symptom_keywords}
        categorized["other"] = []
        
        for symptom in symptoms:
            symptom_lower = symptom.symptom.lower()
            found = False
            
            for system, keywords in self.symptom_keywords.items():
                if symptom_lower in keywords:
                    categorized[system].append(symptom)
                    found = True
                    break
            
            if not found:
                categorized["other"].append(symptom)
        
        return categorized
    
    def get_irae_relevant_symptoms(
        self, 
        symptoms: list[PatientSymptom]
    ) -> dict[str, list[str]]:
        """
        Get symptoms organized by irAE-relevant organ systems.
        
        Args:
            symptoms: List of patient symptoms
            
        Returns:
            Dictionary of system to symptom list
        """
        categorized = self.categorize_by_system(symptoms)
        
        result = {}
        for system, symptom_list in categorized.items():
            if symptom_list and system in ORGAN_SYSTEMS:
                system_name = ORGAN_SYSTEMS[system]["name"]
                result[system_name] = [s.symptom for s in symptom_list]
        
        return result
    
    def detect_concerning_patterns(
        self, 
        symptoms: list[PatientSymptom]
    ) -> list[dict]:
        """
        Detect symptom patterns that may indicate serious irAEs.
        
        Args:
            symptoms: List of symptoms
            
        Returns:
            List of concerning patterns found
        """
        patterns = []
        symptom_names = [s.symptom.lower() for s in symptoms]
        
        # GI colitis pattern
        gi_symptoms = {"diarrhea", "abdominal pain", "bloody stool", "blood in stool"}
        if len(gi_symptoms.intersection(symptom_names)) >= 2:
            patterns.append({
                "system": "Gastrointestinal",
                "pattern": "Possible colitis",
                "symptoms": list(gi_symptoms.intersection(symptom_names)),
            })
        
        # Pneumonitis pattern
        lung_symptoms = {"cough", "dyspnea", "shortness of breath", "hypoxia"}
        if len(lung_symptoms.intersection(symptom_names)) >= 2:
            patterns.append({
                "system": "Pulmonary",
                "pattern": "Possible pneumonitis",
                "symptoms": list(lung_symptoms.intersection(symptom_names)),
            })
        
        # Endocrine pattern
        endo_symptoms = {"fatigue", "weakness", "hypotension", "headache"}
        if len(endo_symptoms.intersection(symptom_names)) >= 3:
            patterns.append({
                "system": "Endocrine",
                "pattern": "Possible endocrinopathy",
                "symptoms": list(endo_symptoms.intersection(symptom_names)),
            })
        
        # Cardiac pattern
        cardiac_symptoms = {"chest pain", "palpitations", "dyspnea", "syncope", "edema"}
        if len(cardiac_symptoms.intersection(symptom_names)) >= 2:
            patterns.append({
                "system": "Cardiac",
                "pattern": "Possible myocarditis/cardiotoxicity",
                "symptoms": list(cardiac_symptoms.intersection(symptom_names)),
            })
        
        # Neurologic pattern
        neuro_symptoms = {"weakness", "numbness", "confusion", "headache", "vision changes"}
        if len(neuro_symptoms.intersection(symptom_names)) >= 2:
            patterns.append({
                "system": "Neurologic",
                "pattern": "Possible neurotoxicity",
                "symptoms": list(neuro_symptoms.intersection(symptom_names)),
            })
        
        return patterns
