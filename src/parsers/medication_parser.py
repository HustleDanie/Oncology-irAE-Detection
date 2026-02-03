"""Medication parser for identifying immunotherapy and other drugs."""

import re
from datetime import datetime
from typing import Optional

from ..models.patient import Medication
from ..utils.constants import IMMUNOTHERAPY_AGENTS


class MedicationParser:
    """Parser for extracting medication information from clinical text."""
    
    def __init__(self):
        # Build regex patterns for immunotherapy agents
        all_agents = list(IMMUNOTHERAPY_AGENTS.keys())
        self.immunotherapy_pattern = re.compile(
            r"\b(" + "|".join(all_agents) + r")\b",
            re.IGNORECASE
        )
        
        # General medication pattern
        self.medication_pattern = re.compile(
            r"(?P<name>[A-Za-z]+(?:\s+[A-Za-z]+)?)\s*"
            r"(?P<dose>[\d.]+\s*(?:mg|mcg|g|units?|mL)?)?[\s,]*"
            r"(?P<route>(?:PO|IV|IM|SC|SubQ|topical|oral|intravenous))?[\s,]*"
            r"(?P<frequency>(?:daily|BID|TID|QID|weekly|q\d+[hd]|every\s+\d+\s+(?:hours?|days?|weeks?)|once|PRN))?",
            re.IGNORECASE
        )
    
    def parse(
        self, 
        text: str, 
        start_date: Optional[datetime] = None
    ) -> list[Medication]:
        """
        Parse medications from clinical text.
        
        Args:
            text: Raw text containing medication information
            start_date: Default start date for medications
            
        Returns:
            List of parsed Medication objects
        """
        medications = []
        seen = set()
        
        # First pass: Look for immunotherapy agents specifically
        for match in self.immunotherapy_pattern.finditer(text):
            name = match.group(1).lower()
            
            if name in seen:
                continue
            seen.add(name)
            
            agent_info = IMMUNOTHERAPY_AGENTS.get(name, {})
            drug_class = agent_info.get("class", "Unknown")
            
            # Try to get generic name if this is a brand name
            generic_name = agent_info.get("generic", name)
            if generic_name != name:
                display_name = f"{name.title()} ({generic_name})"
            else:
                display_name = name.title()
            
            medications.append(Medication(
                name=display_name,
                is_immunotherapy=True,
                drug_class=drug_class,
                start_date=start_date,
            ))
        
        return medications
    
    def parse_medication_list(
        self, 
        text: str,
        start_date: Optional[datetime] = None
    ) -> list[Medication]:
        """
        Parse a structured medication list.
        
        Args:
            text: Text containing medication list (one per line)
            start_date: Default start date
            
        Returns:
            List of Medication objects
        """
        medications = []
        lines = text.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Remove common list prefixes
            line = re.sub(r"^[\d\.\-\*\•]\s*", "", line)
            
            # Check if this line contains an immunotherapy agent
            is_immunotherapy = False
            drug_class = None
            
            for agent, info in IMMUNOTHERAPY_AGENTS.items():
                if agent.lower() in line.lower():
                    is_immunotherapy = True
                    drug_class = info.get("class")
                    break
            
            # Parse medication components
            match = self.medication_pattern.match(line)
            if match:
                name = match.group("name").strip()
                dose = match.group("dose")
                route = match.group("route")
                frequency = match.group("frequency")
                
                medications.append(Medication(
                    name=name,
                    dose=dose.strip() if dose else None,
                    route=route.strip() if route else None,
                    frequency=frequency.strip() if frequency else None,
                    is_immunotherapy=is_immunotherapy,
                    drug_class=drug_class,
                    start_date=start_date,
                ))
            elif line:
                # If no pattern match, just use the line as the name
                medications.append(Medication(
                    name=line,
                    is_immunotherapy=is_immunotherapy,
                    drug_class=drug_class,
                    start_date=start_date,
                ))
        
        return medications
    
    def identify_immunotherapy(self, medications: list[Medication]) -> list[Medication]:
        """
        Filter to only immunotherapy medications.
        
        Args:
            medications: List of all medications
            
        Returns:
            List of immunotherapy medications only
        """
        return [med for med in medications if med.is_immunotherapy]
    
    def detect_combination_therapy(self, medications: list[Medication]) -> bool:
        """
        Detect if patient is on combination immunotherapy.
        
        Args:
            medications: List of medications
            
        Returns:
            True if patient is on multiple ICI classes
        """
        immunotherapy = self.identify_immunotherapy(medications)
        classes = set()
        
        for med in immunotherapy:
            if med.drug_class:
                classes.add(med.drug_class)
        
        # Combination therapy = multiple drug classes (e.g., PD-1 + CTLA-4)
        return len(classes) > 1
    
    def get_immunotherapy_context(self, medications: list[Medication]) -> dict:
        """
        Get summary context about immunotherapy exposure.
        
        Args:
            medications: List of medications
            
        Returns:
            Dictionary with immunotherapy context
        """
        immunotherapy = self.identify_immunotherapy(medications)
        
        if not immunotherapy:
            return {
                "on_immunotherapy": False,
                "agents": [],
                "classes": [],
                "combination": False,
            }
        
        agents = [med.name for med in immunotherapy]
        classes = list(set(med.drug_class for med in immunotherapy if med.drug_class))
        
        return {
            "on_immunotherapy": True,
            "agents": agents,
            "classes": classes,
            "combination": len(classes) > 1,
        }
