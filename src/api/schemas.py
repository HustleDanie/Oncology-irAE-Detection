"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


# =============================================================================
# Request Schemas
# =============================================================================

class LabResultRequest(BaseModel):
    """Lab result input schema."""
    name: str = Field(..., description="Lab test name (e.g., 'AST', 'ALT')")
    value: float = Field(..., description="Numeric value")
    unit: str = Field(..., description="Unit of measurement")
    reference_low: Optional[float] = Field(None, description="Lower reference range")
    reference_high: Optional[float] = Field(None, description="Upper reference range")
    date: Optional[datetime] = Field(None, description="Date of result")
    is_abnormal: Optional[bool] = Field(None, description="Whether value is abnormal")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "AST",
                "value": 185.0,
                "unit": "U/L",
                "reference_low": 10,
                "reference_high": 40,
                "is_abnormal": True
            }
        }
    )


class MedicationRequest(BaseModel):
    """Medication input schema."""
    name: str = Field(..., description="Medication name")
    dose: Optional[str] = Field(None, description="Dose (e.g., '200mg')")
    route: Optional[str] = Field(None, description="Route (e.g., 'IV', 'PO')")
    frequency: Optional[str] = Field(None, description="Frequency (e.g., 'q3weeks')")
    is_immunotherapy: Optional[bool] = Field(None, description="Is this an immunotherapy drug?")
    drug_class: Optional[str] = Field(None, description="Drug class (e.g., 'PD-1', 'CTLA-4')")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Pembrolizumab",
                "dose": "200mg",
                "route": "IV",
                "frequency": "every 3 weeks",
                "is_immunotherapy": True,
                "drug_class": "PD-1"
            }
        }
    )


class SymptomRequest(BaseModel):
    """Patient symptom input schema."""
    symptom: str = Field(..., description="Symptom description")
    severity: Optional[str] = Field(None, description="Severity (mild/moderate/severe)")
    reported_date: Optional[datetime] = Field(None, description="When symptom was reported")
    duration: Optional[str] = Field(None, description="Duration of symptom")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symptom": "diarrhea",
                "severity": "moderate",
                "duration": "5 days"
            }
        }
    )


class VitalSignsRequest(BaseModel):
    """Vital signs input schema."""
    date: Optional[datetime] = Field(None, description="Date/time of vitals")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    heart_rate: Optional[int] = Field(None, description="Heart rate (bpm)")
    blood_pressure_systolic: Optional[int] = Field(None, description="Systolic BP")
    blood_pressure_diastolic: Optional[int] = Field(None, description="Diastolic BP")
    respiratory_rate: Optional[int] = Field(None, description="Respiratory rate")
    oxygen_saturation: Optional[float] = Field(None, description="SpO2 (%)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "temperature": 37.2,
                "heart_rate": 88,
                "blood_pressure_systolic": 128,
                "blood_pressure_diastolic": 76,
                "oxygen_saturation": 98
            }
        }
    )


class ClinicalNoteRequest(BaseModel):
    """Clinical note input schema."""
    content: str = Field(..., description="Note content")
    date: Optional[datetime] = Field(None, description="Note date")
    note_type: Optional[str] = Field("progress", description="Type of note")
    author: Optional[str] = Field(None, description="Note author")


class ImagingRequest(BaseModel):
    """Imaging summary input schema."""
    modality: str = Field(..., description="Imaging modality (CT, MRI, X-ray)")
    body_region: str = Field(..., description="Body region imaged")
    findings: str = Field(..., description="Imaging findings")
    impression: Optional[str] = Field(None, description="Radiologist impression")
    date: Optional[datetime] = Field(None, description="Date of imaging")


class PatientDataRequest(BaseModel):
    """
    Complete patient data request for irAE assessment.
    """
    patient_id: Optional[str] = Field(None, description="Patient identifier (not logged)")
    age: Optional[int] = Field(None, ge=0, le=120, description="Patient age")
    cancer_type: Optional[str] = Field(None, description="Primary cancer type")
    
    # Clinical data
    medications: List[MedicationRequest] = Field(default_factory=list)
    labs: List[LabResultRequest] = Field(default_factory=list)
    symptoms: List[SymptomRequest] = Field(default_factory=list)
    vitals: List[VitalSignsRequest] = Field(default_factory=list)
    notes: List[ClinicalNoteRequest] = Field(default_factory=list)
    imaging: List[ImagingRequest] = Field(default_factory=list)
    
    # Raw text inputs (alternative to structured data)
    raw_notes: Optional[str] = Field(None, description="Unstructured clinical notes")
    raw_labs: Optional[str] = Field(None, description="Unstructured lab text")
    raw_medications: Optional[str] = Field(None, description="Unstructured medication list")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "age": 58,
                "cancer_type": "Melanoma",
                "medications": [
                    {
                        "name": "Pembrolizumab",
                        "dose": "200mg",
                        "is_immunotherapy": True,
                        "drug_class": "PD-1"
                    }
                ],
                "labs": [
                    {
                        "name": "AST",
                        "value": 185,
                        "unit": "U/L",
                        "reference_high": 40,
                        "is_abnormal": True
                    }
                ],
                "symptoms": [
                    {
                        "symptom": "fatigue",
                        "severity": "moderate"
                    }
                ]
            }
        }
    )


# =============================================================================
# Response Schemas
# =============================================================================

class OrganSystemFindingResponse(BaseModel):
    """Organ system finding in response."""
    system: str
    detected: bool
    findings: List[str]
    evidence: List[str]
    severity: Optional[str] = None
    confidence: Optional[float] = None


class ImmunotherapyContextResponse(BaseModel):
    """Immunotherapy context in response."""
    on_immunotherapy: bool
    agents: List[str]
    drug_classes: List[str]
    combination_therapy: bool


class CausalityResponse(BaseModel):
    """Causality assessment in response."""
    likelihood: str
    reasoning: str
    temporal_relationship: Optional[str] = None
    alternative_causes: List[str] = []
    supporting_factors: List[str] = []
    against_factors: List[str] = []


class RecommendedActionResponse(BaseModel):
    """Recommended action in response."""
    action: str
    priority: int
    rationale: Optional[str] = None


class AssessmentResponse(BaseModel):
    """
    Complete irAE assessment response.
    """
    # Request tracking
    correlation_id: str = Field(..., description="Request correlation ID for tracing")
    assessment_date: datetime = Field(..., description="Assessment timestamp")
    
    # Detection results
    irae_detected: bool = Field(..., description="Whether irAE was detected")
    affected_systems: List[OrganSystemFindingResponse] = Field(default_factory=list)
    
    # Context
    immunotherapy_context: ImmunotherapyContextResponse
    
    # Assessment
    causality: CausalityResponse
    overall_severity: str
    severity_reasoning: str
    
    # Triage
    urgency: str
    urgency_reasoning: str
    
    # Recommendations
    recommended_actions: List[RecommendedActionResponse]
    key_evidence: List[str]
    
    # Safety
    disclaimer: str = Field(
        default="This assessment is for clinical decision support only. "
        "It does not replace clinical judgment. All findings should be "
        "verified by the treating clinician."
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "correlation_id": "abc123",
                "assessment_date": "2026-02-05T12:00:00Z",
                "irae_detected": True,
                "affected_systems": [
                    {
                        "system": "Hepatic",
                        "detected": True,
                        "findings": ["Elevated AST: 185 U/L"],
                        "evidence": ["AST = 185 (4.6x ULN)"],
                        "severity": "Grade 2 - Moderate",
                        "confidence": 0.9
                    }
                ],
                "immunotherapy_context": {
                    "on_immunotherapy": True,
                    "agents": ["Pembrolizumab"],
                    "drug_classes": ["PD-1"],
                    "combination_therapy": False
                },
                "causality": {
                    "likelihood": "Highly likely",
                    "reasoning": "Temporal relationship with immunotherapy"
                },
                "overall_severity": "Grade 2 - Moderate",
                "severity_reasoning": "Based on transaminase elevation",
                "urgency": "Urgent (same day)",
                "urgency_reasoning": "Grade 2 hepatitis requires prompt evaluation",
                "recommended_actions": [
                    {
                        "action": "Hold immunotherapy",
                        "priority": 1,
                        "rationale": "Prevent further liver injury"
                    }
                ],
                "key_evidence": ["AST 185 U/L (4.6x ULN)"]
            }
        }
    )


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current timestamp")
    components: Dict[str, str] = Field(default_factory=dict, description="Component statuses")


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "ValidationError",
                "message": "Invalid lab value: must be numeric",
                "correlation_id": "abc123",
                "details": {"field": "labs[0].value"}
            }
        }
    )


class BatchAssessmentRequest(BaseModel):
    """Request for batch assessment of multiple patients."""
    patients: List[PatientDataRequest] = Field(..., min_length=1, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "patients": [
                    {
                        "patient_id": "P001",
                        "medications": [{"name": "Pembrolizumab"}],
                        "labs": [{"name": "AST", "value": 100, "unit": "U/L"}]
                    }
                ]
            }
        }
    )


class BatchAssessmentResponse(BaseModel):
    """Response for batch assessment."""
    correlation_id: str
    total_patients: int
    completed: int
    failed: int
    results: List[AssessmentResponse]
    errors: List[ErrorResponse] = Field(default_factory=list)
