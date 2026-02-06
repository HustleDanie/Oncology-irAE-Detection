"""Clinical note parser for extracting structured information."""

import re
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from ..models.patient import ClinicalNote, PatientSymptom, VitalSigns

# Use TYPE_CHECKING to avoid circular import
if TYPE_CHECKING:
    from ..llm.client import BaseLLMClient


class NoteParser:
    """Parser for clinical documentation and notes."""
    
    # Section headers commonly found in clinical notes
    SECTION_PATTERNS = {
        "chief_complaint": r"(?:chief complaint|cc|reason for visit)[\s:]+(.+?)(?=\n\n|\n[A-Z]|$)",
        "hpi": r"(?:history of present illness|hpi)[\s:]+(.+?)(?=\n\n|\n[A-Z]|$)",
        "assessment": r"(?:assessment|impression|a/p|assessment and plan)[\s:]+(.+?)(?=\n\n|\n[A-Z]|$)",
        "plan": r"(?:plan|recommendations)[\s:]+(.+?)(?=\n\n|\n[A-Z]|$)",
        "medications": r"(?:medications|current medications|med list)[\s:]+(.+?)(?=\n\n|\n[A-Z]|$)",
        "allergies": r"(?:allergies|drug allergies)[\s:]+(.+?)(?=\n\n|\n[A-Z]|$)",
        "vital_signs": r"(?:vital signs|vitals|vs)[\s:]+(.+?)(?=\n\n|\n[A-Z]|$)",
        "physical_exam": r"(?:physical exam|pe|examination)[\s:]+(.+?)(?=\n\n|\n[A-Z]|$)",
        "labs": r"(?:labs|laboratory|lab results)[\s:]+(.+?)(?=\n\n|\n[A-Z]|$)",
    }
    
    # Note type indicators
    NOTE_TYPE_PATTERNS = {
        "progress": ["progress note", "daily note", "follow-up"],
        "oncology": ["oncology", "chemotherapy", "immunotherapy", "tumor board"],
        "emergency": ["emergency", "ed note", "er note", "emergency department"],
        "admission": ["admission", "h&p", "history and physical"],
        "discharge": ["discharge summary", "discharge note"],
        "nursing": ["nursing note", "rn note", "nursing assessment"],
        "consult": ["consult", "consultation"],
    }
    
    def __init__(self, llm_client: Optional["BaseLLMClient"] = None):
        self.llm_client = llm_client
        self.compiled_sections = {
            name: re.compile(pattern, re.IGNORECASE | re.DOTALL)
            for name, pattern in self.SECTION_PATTERNS.items()
        }
    
    async def parse_with_llm(
        self,
        note: ClinicalNote,
    ) -> tuple[List[PatientSymptom], Optional[VitalSigns]]:
        """
        Use LLM to extract structured symptoms and vitals from a note.
        
        Args:
            note: The clinical note to parse.
            
        Returns:
            A tuple containing a list of PatientSymptom objects and an optional VitalSigns object.
        """
        if not self.llm_client:
            return [], None

        # Use MedGemma for symptom extraction
        symptoms_prompt = self._build_symptoms_prompt(note.content)
        symptoms_json = await self.llm_client.complete_json(
            system_prompt="You are a medical AI assistant trained to extract clinical information. Extract patient symptoms from the clinical note accurately.",
            user_prompt=symptoms_prompt,
        )
        symptoms = self._parse_symptoms_from_llm(symptoms_json, note.date)

        # Use MedGemma for vital signs extraction
        vitals_prompt = self._build_vitals_prompt(note.content)
        vitals_json = await self.llm_client.complete_json(
            system_prompt="You are a medical AI assistant trained to extract clinical information. Extract vital signs from the clinical note accurately.",
            user_prompt=vitals_prompt,
        )
        vitals = self._parse_vitals_from_llm(vitals_json, note.date)

        return symptoms, vitals

    def _build_symptoms_prompt(self, note_content: str) -> str:
        return f"""
        Please extract all patient-reported symptoms and observed signs from the following clinical note.
        For each symptom, provide the name, whether it is present, and any relevant details (e.g., severity, frequency, location).
        Format the output as a JSON object with a single key "symptoms" which is a list of objects, each with "name", "present", and "details" keys.

        Example:
        {{
          "symptoms": [
            {{ "name": "diarrhea", "present": true, "details": "3 watery stools per day" }},
            {{ "name": "fever", "present": false, "details": "denies fever" }}
          ]
        }}

        Clinical Note:
        ---
        {note_content}
        ---
        """

    def _build_vitals_prompt(self, note_content: str) -> str:
        return f"""
        Please extract all vital signs from the following clinical note.
        Provide the temperature (in Celsius), blood pressure (systolic and diastolic), heart rate, respiratory rate, and oxygen saturation.
        Format the output as a JSON object with a single key "vitals" containing the extracted values.

        Example:
        {{
          "vitals": {{
            "temperature_c": 37.2,
            "bp_systolic": 120,
            "bp_diastolic": 80,
            "heart_rate": 78,
            "respiratory_rate": 16,
            "oxygen_saturation": 98
          }}
        }}

        Clinical Note:
        ---
        {note_content}
        ---
        """

    def _parse_symptoms_from_llm(self, llm_output: dict, note_date: datetime) -> List[PatientSymptom]:
        symptoms = []
        if "symptoms" in llm_output and isinstance(llm_output["symptoms"], list):
            for item in llm_output["symptoms"]:
                if item.get("present"):
                    symptoms.append(
                        PatientSymptom(
                            symptom=item.get("name", "unknown"),
                            date_reported=note_date,
                            details=item.get("details", "")
                        )
                    )
        return symptoms

    def _parse_vitals_from_llm(self, llm_output: dict, note_date: datetime) -> Optional[VitalSigns]:
        if "vitals" in llm_output and isinstance(llm_output["vitals"], dict):
            data = llm_output["vitals"]
            return VitalSigns(
                date=note_date,
                temperature_c=data.get("temperature_c"),
                bp_systolic=data.get("bp_systolic"),
                bp_diastolic=data.get("bp_diastolic"),
                heart_rate=data.get("heart_rate"),
                respiratory_rate=data.get("respiratory_rate"),
                oxygen_saturation=data.get("oxygen_saturation"),
            )
        return None

    def parse(
        self, 
        text: str, 
        date: Optional[datetime] = None,
        note_type: Optional[str] = None,
        author: Optional[str] = None,
    ) -> ClinicalNote:
        """
        Parse a clinical note.
        
        Args:
            text: Raw note text
            date: Note date
            note_type: Type of note
            author: Note author
            
        Returns:
            ClinicalNote object
        """
        if date is None:
            date = datetime.now()
        
        if note_type is None:
            note_type = self._detect_note_type(text)
        
        department = self._detect_department(text)
        
        return ClinicalNote(
            date=date,
            note_type=note_type,
            author=author,
            content=text,
            department=department,
        )
    
    def _detect_note_type(self, text: str) -> str:
        """Detect the type of clinical note."""
        text_lower = text.lower()
        
        for note_type, patterns in self.NOTE_TYPE_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return note_type
        
        return "general"
    
    def _detect_department(self, text: str) -> Optional[str]:
        """Detect the department from note content."""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ["oncology", "cancer", "chemotherapy", "immunotherapy"]):
            return "Oncology"
        elif any(term in text_lower for term in ["emergency", "ed ", "er "]):
            return "Emergency"
        elif any(term in text_lower for term in ["icu", "intensive care", "critical care"]):
            return "ICU"
        elif any(term in text_lower for term in ["cardiology", "cardiac"]):
            return "Cardiology"
        elif any(term in text_lower for term in ["pulmonology", "pulmonary"]):
            return "Pulmonology"
        elif any(term in text_lower for term in ["neurology", "neurologic"]):
            return "Neurology"
        
        return None
    
    def extract_sections(self, text: str) -> dict[str, str]:
        """
        Extract named sections from a clinical note.
        
        Args:
            text: Raw note text
            
        Returns:
            Dictionary of section name to content
        """
        sections = {}
        
        for section_name, pattern in self.compiled_sections.items():
            match = pattern.search(text)
            if match:
                sections[section_name] = match.group(1).strip()
        
        return sections
    
    def extract_irae_mentions(self, text: str) -> list[dict]:
        """
        Extract mentions of irAE-related terms in clinical notes.
        
        Args:
            text: Clinical note text
            
        Returns:
            List of irAE mentions with context
        """
        mentions = []
        
        # irAE-specific terms to search for
        irae_terms = [
            r"immune[- ]?related",
            r"irae",
            r"checkpoint inhibitor",
            r"immunotherapy[- ]?toxicity",
            r"autoimmune",
            r"colitis",
            r"pneumonitis",
            r"hepatitis",
            r"thyroiditis",
            r"hypophysitis",
            r"myocarditis",
            r"nephritis",
            r"dermatitis",
            r"encephalitis",
            r"neuropathy",
            r"myasthenia",
        ]
        
        pattern = re.compile(
            r"(.{0,100})(" + "|".join(irae_terms) + r")(.{0,100})",
            re.IGNORECASE
        )
        
        for match in pattern.finditer(text):
            mentions.append({
                "term": match.group(2),
                "context_before": match.group(1).strip(),
                "context_after": match.group(3).strip(),
                "full_context": match.group(0).strip(),
            })
        
        return mentions
    
    def extract_symptom_mentions(self, text: str) -> list[str]:
        """
        Extract symptom mentions from clinical notes.
        
        Args:
            text: Clinical note text
            
        Returns:
            List of symptoms mentioned
        """
        # Common symptom terms
        symptom_terms = [
            "diarrhea", "nausea", "vomiting", "abdominal pain",
            "cough", "dyspnea", "shortness of breath",
            "fatigue", "weakness", "malaise",
            "rash", "pruritus", "itching",
            "headache", "confusion", "dizziness",
            "chest pain", "palpitations",
            "fever", "chills",
            "joint pain", "arthralgia", "myalgia",
        ]
        
        pattern = re.compile(
            r"\b(" + "|".join(symptom_terms) + r")\b",
            re.IGNORECASE
        )
        
        symptoms = list(set(match.group(1).lower() for match in pattern.finditer(text)))
        return symptoms
    
    def assess_urgency_language(self, text: str) -> dict:
        """
        Assess urgency indicators in clinical note language.
        
        Args:
            text: Clinical note text
            
        Returns:
            Dictionary with urgency indicators
        """
        text_lower = text.lower()
        
        urgent_terms = [
            "emergent", "urgent", "stat", "immediate",
            "critical", "life-threatening", "severe",
            "decompensating", "deteriorating", "unstable",
            "icu", "code", "rapid response",
        ]
        
        concerning_terms = [
            "concern", "worried", "suspicious",
            "rule out", "possible", "cannot exclude",
            "monitor closely", "follow up",
        ]
        
        urgent_found = [term for term in urgent_terms if term in text_lower]
        concerning_found = [term for term in concerning_terms if term in text_lower]
        
        return {
            "urgent_language": urgent_found,
            "concerning_language": concerning_found,
            "urgency_score": len(urgent_found) * 2 + len(concerning_found),
        }
