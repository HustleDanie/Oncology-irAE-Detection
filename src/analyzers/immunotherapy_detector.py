"""Immunotherapy detection module."""

from datetime import datetime
from typing import Optional

from ..models.patient import PatientData, Medication
from ..models.assessment import ImmunotherapyContext
from ..utils.constants import IMMUNOTHERAPY_AGENTS


class ImmunotherapyDetector:
    """Detector for immunotherapy exposure in patient data."""
    
    def __init__(self):
        self.agents = IMMUNOTHERAPY_AGENTS
    
    def detect(self, patient_data: PatientData) -> ImmunotherapyContext:
        """
        Detect immunotherapy exposure from patient data.
        
        Args:
            patient_data: Complete patient clinical data
            
        Returns:
            ImmunotherapyContext with exposure details
        """
        # Check structured medications
        immunotherapy_meds = self._check_medications(patient_data.medications)
        
        # Check raw medication text
        raw_agents = []
        if patient_data.raw_medications:
            raw_agents = self._search_text_for_agents(patient_data.raw_medications)
        
        # Check clinical notes for mentions
        note_agents = []
        for note in patient_data.notes:
            found = self._search_text_for_agents(note.content)
            note_agents.extend(found)
        
        if patient_data.raw_notes:
            note_agents.extend(self._search_text_for_agents(patient_data.raw_notes))
        
        # Combine all detected agents
        all_agents = list(set(
            [med.name for med in immunotherapy_meds] + 
            raw_agents + 
            note_agents
        ))
        
        # Determine drug classes
        drug_classes = self._get_drug_classes(all_agents + [med.drug_class for med in immunotherapy_meds if med.drug_class])
        
        # Check for combination therapy
        combination = len(set(drug_classes)) > 1
        
        # Get most recent dose date
        most_recent = self._get_most_recent_date(immunotherapy_meds)
        
        return ImmunotherapyContext(
            on_immunotherapy=len(all_agents) > 0,
            agents=all_agents,
            drug_classes=list(set(drug_classes)),
            most_recent_dose=most_recent,
            combination_therapy=combination,
        )
    
    def _check_medications(self, medications: list[Medication]) -> list[Medication]:
        """Check medication list for immunotherapy agents."""
        immunotherapy = []
        
        for med in medications:
            # Check if already flagged as immunotherapy
            if med.is_immunotherapy:
                immunotherapy.append(med)
                continue
            
            # Check medication name against known agents
            med_name_lower = med.name.lower()
            for agent_name in self.agents:
                if agent_name in med_name_lower:
                    med.is_immunotherapy = True
                    med.drug_class = self.agents[agent_name].get("class")
                    immunotherapy.append(med)
                    break
        
        return immunotherapy
    
    def _search_text_for_agents(self, text: str) -> list[str]:
        """Search text for immunotherapy agent mentions."""
        text_lower = text.lower()
        found = []
        
        for agent_name, agent_info in self.agents.items():
            if agent_name in text_lower:
                # Get display name (capitalize)
                display_name = agent_name.title()
                if display_name not in found:
                    found.append(display_name)
        
        return found
    
    def _get_drug_classes(self, agents_and_classes: list[str]) -> list[str]:
        """Determine drug classes from agent names."""
        classes = set()
        
        for item in agents_and_classes:
            if not item:
                continue
            
            item_lower = item.lower()
            
            # Check if this is already a class name
            if item_lower in ["pd-1", "pd-l1", "ctla-4"]:
                classes.add(item.upper())
                continue
            
            # Look up agent class
            for agent_name, agent_info in self.agents.items():
                if agent_name in item_lower:
                    drug_class = agent_info.get("class")
                    if drug_class:
                        classes.add(drug_class)
                    break
        
        return list(classes)
    
    def _get_most_recent_date(self, medications: list[Medication]) -> Optional[datetime]:
        """Get the most recent start date from medications."""
        dates = [med.start_date for med in medications if med.start_date]
        if dates:
            return max(dates)
        return None
    
    def get_risk_level(self, context: ImmunotherapyContext) -> str:
        """
        Assess irAE risk level based on immunotherapy context.
        
        Args:
            context: Immunotherapy exposure context
            
        Returns:
            Risk level string: "high", "moderate", "low", or "none"
        """
        if not context.on_immunotherapy:
            return "none"
        
        # Combination therapy has highest risk
        if context.combination_therapy:
            return "high"
        
        # CTLA-4 inhibitors have higher risk than PD-1/PD-L1
        if "CTLA-4" in context.drug_classes:
            return "high"
        
        # PD-1 or PD-L1 alone
        if context.drug_classes:
            return "moderate"
        
        return "low"
