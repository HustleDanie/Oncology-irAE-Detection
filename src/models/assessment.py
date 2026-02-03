"""Assessment models for irAE detection results."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Likelihood(str, Enum):
    """Likelihood that findings represent an irAE."""
    
    HIGHLY_LIKELY = "Highly likely"
    POSSIBLE = "Possible"
    UNLIKELY = "Unlikely"
    UNCERTAIN = "Uncertain"


class Severity(str, Enum):
    """CTCAE-style severity grading."""
    
    GRADE_1 = "Grade 1 - Mild"
    GRADE_2 = "Grade 2 - Moderate"
    GRADE_3 = "Grade 3 - Severe"
    GRADE_4 = "Grade 4 - Life-threatening"
    UNKNOWN = "Unknown"


class Urgency(str, Enum):
    """Clinical urgency/triage level."""
    
    ROUTINE = "🟢 Routine monitoring"
    SOON = "🟡 Needs oncology review soon"
    URGENT = "🟠 Urgent (same day)"
    EMERGENCY = "🔴 Emergency evaluation"


class OrganSystem(str, Enum):
    """Organ systems affected by irAEs."""
    
    GASTROINTESTINAL = "Gastrointestinal"
    HEPATIC = "Hepatic"
    PULMONARY = "Pulmonary"
    ENDOCRINE = "Endocrine"
    DERMATOLOGIC = "Dermatologic"
    NEUROLOGIC = "Neurologic"
    CARDIAC = "Cardiac"
    RENAL = "Renal"
    HEMATOLOGIC = "Hematologic"
    MUSCULOSKELETAL = "Musculoskeletal"
    OCULAR = "Ocular"


class OrganSystemFinding(BaseModel):
    """Findings for a specific organ system."""
    
    system: OrganSystem = Field(..., description="Affected organ system")
    detected: bool = Field(..., description="Whether toxicity signals were detected")
    findings: list[str] = Field(default_factory=list, description="Specific findings")
    evidence: list[str] = Field(default_factory=list, description="Supporting evidence from data")
    severity: Optional[Severity] = Field(None, description="Estimated severity for this system")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence level 0-1")


class ImmunotherapyContext(BaseModel):
    """Context about patient's immunotherapy exposure."""
    
    on_immunotherapy: bool = Field(..., description="Whether patient is on immunotherapy")
    agents: list[str] = Field(default_factory=list, description="Immunotherapy agents")
    drug_classes: list[str] = Field(default_factory=list, description="Drug classes (PD-1, CTLA-4, etc.)")
    most_recent_dose: Optional[datetime] = Field(None, description="Date of most recent dose")
    duration_on_therapy: Optional[str] = Field(None, description="Duration on therapy")
    combination_therapy: bool = Field(False, description="Whether on combination ICI therapy")


class CausalityAssessment(BaseModel):
    """Assessment of whether findings are likely irAE-related."""
    
    likelihood: Likelihood = Field(..., description="Overall likelihood of irAE")
    reasoning: str = Field(..., description="Explanation of causality reasoning")
    temporal_relationship: Optional[str] = Field(None, description="Timing relative to therapy")
    alternative_causes: list[str] = Field(default_factory=list, description="Other possible causes")
    supporting_factors: list[str] = Field(default_factory=list, description="Factors supporting irAE")
    against_factors: list[str] = Field(default_factory=list, description="Factors against irAE")


class RecommendedAction(BaseModel):
    """Recommended clinical action."""
    
    action: str = Field(..., description="Recommended action")
    priority: int = Field(..., ge=1, le=5, description="Priority 1-5 (1 is highest)")
    rationale: Optional[str] = Field(None, description="Rationale for recommendation")


class IRAEAssessment(BaseModel):
    """Complete irAE assessment result."""
    
    # Metadata
    assessment_id: Optional[str] = Field(None, description="Unique assessment ID")
    assessment_date: datetime = Field(default_factory=datetime.now, description="Assessment timestamp")
    
    # Immunotherapy context
    immunotherapy_context: ImmunotherapyContext = Field(
        ..., description="Patient's immunotherapy exposure"
    )
    
    # Detection results
    irae_detected: bool = Field(..., description="Whether possible irAE was detected")
    affected_systems: list[OrganSystemFinding] = Field(
        default_factory=list, description="Findings by organ system"
    )
    
    # Causality and severity
    causality: CausalityAssessment = Field(..., description="Causality assessment")
    overall_severity: Severity = Field(..., description="Overall severity grade")
    severity_reasoning: str = Field(..., description="Explanation for severity grade")
    
    # Triage
    urgency: Urgency = Field(..., description="Urgency/triage level")
    urgency_reasoning: str = Field(..., description="Explanation for urgency level")
    
    # Recommendations
    recommended_actions: list[RecommendedAction] = Field(
        default_factory=list, description="Recommended clinical actions"
    )
    
    # Supporting data
    key_evidence: list[str] = Field(
        default_factory=list, description="Key supporting data points"
    )
    
    # Safety disclaimer
    disclaimer: str = Field(
        default="This assessment is for clinical decision support only. "
        "It does not replace clinical judgment. All findings should be "
        "verified by the treating clinician.",
        description="Safety disclaimer"
    )
    
    def get_affected_system_names(self) -> list[str]:
        """Get names of affected organ systems."""
        return [f.system.value for f in self.affected_systems if f.detected]
    
    def get_highest_severity(self) -> Severity:
        """Get the highest severity among affected systems."""
        severities = [f.severity for f in self.affected_systems if f.severity]
        if not severities:
            return Severity.UNKNOWN
        
        severity_order = [
            Severity.GRADE_4,
            Severity.GRADE_3,
            Severity.GRADE_2,
            Severity.GRADE_1,
        ]
        for sev in severity_order:
            if sev in severities:
                return sev
        return Severity.UNKNOWN
