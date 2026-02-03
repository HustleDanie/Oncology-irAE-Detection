"""Laboratory result parser for extracting structured lab data."""

import re
from datetime import datetime
from typing import Optional

from ..models.patient import LabResult
from ..utils.constants import LAB_REFERENCE_RANGES


class LabParser:
    """Parser for extracting laboratory results from clinical text."""
    
    # Common lab test patterns
    LAB_PATTERNS = [
        # Pattern: "AST 145 U/L" or "AST: 145 U/L" or "AST = 145"
        r"(?P<name>AST|ALT|bilirubin|alk phos|alkaline phosphatase|ALP|GGT|"
        r"TSH|free T4|T4|T3|cortisol|ACTH|troponin|BNP|NT-proBNP|"
        r"creatinine|BUN|GFR|eGFR|glucose|CK|CK-MB|sodium|potassium|"
        r"WBC|hemoglobin|Hgb|platelets|INR)"
        r"[\s:=]*(?P<value>[\d.]+)\s*(?P<unit>[a-zA-Z/%]+)?",
        
        # Pattern with H/L flags: "AST 145 H U/L"
        r"(?P<name>\w+)[\s:=]*(?P<value>[\d.]+)\s*(?P<flag>[HLhl])?\s*(?P<unit>[a-zA-Z/%]+)?",
    ]
    
    # Lab name normalization
    LAB_ALIASES = {
        "alk phos": "alkaline phosphatase",
        "alp": "alkaline phosphatase",
        "tbili": "bilirubin",
        "total bilirubin": "bilirubin",
        "hgb": "hemoglobin",
        "hb": "hemoglobin",
        "plt": "platelets",
        "cr": "creatinine",
        "scr": "creatinine",
        "ft4": "free T4",
        "tsh": "TSH",
    }
    
    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.LAB_PATTERNS]
    
    def parse(self, text: str, date: Optional[datetime] = None) -> list[LabResult]:
        """
        Parse laboratory results from clinical text.
        
        Args:
            text: Raw text containing lab results
            date: Date to assign to results (defaults to now)
            
        Returns:
            List of parsed LabResult objects
        """
        if date is None:
            date = datetime.now()
        
        results = []
        seen = set()  # Avoid duplicates
        
        for pattern in self.compiled_patterns:
            for match in pattern.finditer(text):
                try:
                    name = match.group("name").strip()
                    value_str = match.group("value")
                    unit = match.group("unit") if "unit" in match.groupdict() else None
                    
                    # Normalize lab name
                    name_lower = name.lower()
                    name = self.LAB_ALIASES.get(name_lower, name)
                    
                    # Parse value
                    value = float(value_str)
                    
                    # Skip if we've already captured this lab
                    key = (name.lower(), value)
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    # Get reference ranges
                    ref_low, ref_high = self._get_reference_range(name)
                    
                    # Create result
                    result = LabResult(
                        name=name,
                        value=value,
                        unit=unit or self._get_default_unit(name),
                        reference_low=ref_low,
                        reference_high=ref_high,
                        date=date,
                        is_abnormal=None,
                    )
                    result.is_abnormal = result.check_abnormal()
                    results.append(result)
                    
                except (ValueError, AttributeError):
                    continue
        
        return results
    
    def _get_reference_range(self, lab_name: str) -> tuple[Optional[float], Optional[float]]:
        """Get reference range for a lab test."""
        name_upper = lab_name.upper()
        for key, ranges in LAB_REFERENCE_RANGES.items():
            if key.upper() == name_upper:
                return ranges.get("low"), ranges.get("high")
        return None, None
    
    def _get_default_unit(self, lab_name: str) -> str:
        """Get default unit for a lab test."""
        name_upper = lab_name.upper()
        for key, ranges in LAB_REFERENCE_RANGES.items():
            if key.upper() == name_upper:
                return ranges.get("unit", "")
        return ""
    
    def extract_trends(self, results: list[LabResult]) -> dict[str, list[LabResult]]:
        """
        Group lab results by name for trend analysis.
        
        Args:
            results: List of lab results
            
        Returns:
            Dictionary mapping lab names to chronological results
        """
        trends = {}
        for result in results:
            name = result.name.lower()
            if name not in trends:
                trends[name] = []
            trends[name].append(result)
        
        # Sort each trend by date
        for name in trends:
            trends[name].sort(key=lambda x: x.date)
        
        return trends
    
    def detect_significant_changes(
        self, 
        results: list[LabResult], 
        threshold_multiplier: float = 2.0
    ) -> list[dict]:
        """
        Detect significant changes in lab values over time.
        
        Args:
            results: List of lab results
            threshold_multiplier: Factor for detecting significant change
            
        Returns:
            List of detected significant changes
        """
        trends = self.extract_trends(results)
        changes = []
        
        for name, values in trends.items():
            if len(values) < 2:
                continue
            
            for i in range(1, len(values)):
                prev = values[i - 1]
                curr = values[i]
                
                if prev.value == 0:
                    continue
                
                change_ratio = curr.value / prev.value
                
                if change_ratio >= threshold_multiplier:
                    changes.append({
                        "lab": name,
                        "previous": prev,
                        "current": curr,
                        "change_ratio": change_ratio,
                        "direction": "increased",
                    })
                elif change_ratio <= 1 / threshold_multiplier:
                    changes.append({
                        "lab": name,
                        "previous": prev,
                        "current": curr,
                        "change_ratio": change_ratio,
                        "direction": "decreased",
                    })
        
        return changes
