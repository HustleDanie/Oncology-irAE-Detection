"""Patient data models for clinical information."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LabResult(BaseModel):
    """Laboratory test result."""
    
    name: str = Field(..., description="Lab test name (e.g., AST, ALT, TSH)")
    value: float = Field(..., description="Numeric value of the result")
    unit: str = Field(..., description="Unit of measurement")
    reference_low: Optional[float] = Field(None, description="Lower reference range")
    reference_high: Optional[float] = Field(None, description="Upper reference range")
    date: datetime = Field(..., description="Date/time of the lab result")
    is_abnormal: Optional[bool] = Field(None, description="Whether result is out of range")
    
    def check_abnormal(self) -> bool:
        """Check if value is outside reference range."""
        if self.reference_low is not None and self.value < self.reference_low:
            return True
        if self.reference_high is not None and self.value > self.reference_high:
            return True
        return False


class Medication(BaseModel):
    """Medication record."""
    
    name: str = Field(..., description="Medication name")
    dose: Optional[str] = Field(None, description="Dosage")
    route: Optional[str] = Field(None, description="Route of administration")
    frequency: Optional[str] = Field(None, description="Frequency")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date if discontinued")
    is_immunotherapy: bool = Field(False, description="Whether this is an ICI agent")
    drug_class: Optional[str] = Field(None, description="Drug class (e.g., PD-1, CTLA-4)")


class VitalSigns(BaseModel):
    """Vital signs measurement."""
    
    date: datetime = Field(..., description="Date/time of measurement")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    heart_rate: Optional[int] = Field(None, description="Heart rate in bpm")
    blood_pressure_systolic: Optional[int] = Field(None, description="Systolic BP in mmHg")
    blood_pressure_diastolic: Optional[int] = Field(None, description="Diastolic BP in mmHg")
    respiratory_rate: Optional[int] = Field(None, description="Respiratory rate per minute")
    oxygen_saturation: Optional[float] = Field(None, description="SpO2 percentage")
    weight: Optional[float] = Field(None, description="Weight in kg")


class ClinicalNote(BaseModel):
    """Clinical documentation note."""
    
    date: datetime = Field(..., description="Date of the note")
    note_type: str = Field(..., description="Type of note (e.g., progress, ED, nursing)")
    author: Optional[str] = Field(None, description="Author of the note")
    content: str = Field(..., description="Full text content of the note")
    department: Optional[str] = Field(None, description="Department (e.g., Oncology, ED)")


class PatientSymptom(BaseModel):
    """Patient-reported symptom."""
    
    symptom: str = Field(..., description="Symptom description")
    severity: Optional[str] = Field(None, description="Severity (mild, moderate, severe)")
    onset_date: Optional[datetime] = Field(None, description="When symptom started")
    duration: Optional[str] = Field(None, description="Duration of symptom")
    reported_date: datetime = Field(..., description="When symptom was reported")


class ImagingSummary(BaseModel):
    """Imaging study summary."""
    
    date: datetime = Field(..., description="Date of imaging study")
    modality: str = Field(..., description="Imaging modality (CT, MRI, X-ray, etc.)")
    body_region: str = Field(..., description="Body region imaged")
    findings: str = Field(..., description="Summary of findings")
    impression: Optional[str] = Field(None, description="Radiologist impression")


class PatientData(BaseModel):
    """Complete patient clinical data for irAE assessment."""
    
    patient_id: Optional[str] = Field(None, description="Patient identifier")
    age: Optional[int] = Field(None, description="Patient age")
    cancer_type: Optional[str] = Field(None, description="Primary cancer diagnosis")
    
    # Clinical data components
    labs: list[LabResult] = Field(default_factory=list, description="Laboratory results")
    medications: list[Medication] = Field(default_factory=list, description="Medication list")
    vitals: list[VitalSigns] = Field(default_factory=list, description="Vital signs")
    notes: list[ClinicalNote] = Field(default_factory=list, description="Clinical notes")
    symptoms: list[PatientSymptom] = Field(default_factory=list, description="Patient symptoms")
    imaging: list[ImagingSummary] = Field(default_factory=list, description="Imaging studies")
    
    # Free text inputs (for direct entry)
    raw_notes: Optional[str] = Field(None, description="Raw clinical notes text")
    raw_labs: Optional[str] = Field(None, description="Raw lab results text")
    raw_medications: Optional[str] = Field(None, description="Raw medication list text")
    raw_symptoms: Optional[str] = Field(None, description="Raw symptoms text")
    
    def get_immunotherapy_medications(self) -> list[Medication]:
        """Return list of immunotherapy medications."""
        return [med for med in self.medications if med.is_immunotherapy]
    
    def has_immunotherapy(self) -> bool:
        """Check if patient has any immunotherapy medications."""
        return len(self.get_immunotherapy_medications()) > 0
