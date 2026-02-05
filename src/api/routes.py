"""
FastAPI routes for Oncology irAE Detection API.

Provides RESTful endpoints for:
- Patient assessment
- Batch processing
- Health checks
"""

from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .schemas import (
    PatientDataRequest,
    AssessmentResponse,
    BatchAssessmentRequest,
    BatchAssessmentResponse,
    HealthCheckResponse,
    ErrorResponse,
    OrganSystemFindingResponse,
    ImmunotherapyContextResponse,
    CausalityResponse,
    RecommendedActionResponse,
)
from .dependencies import (
    get_assessment_engine,
    check_rate_limit,
)
from ..models.patient import (
    PatientData, LabResult, Medication, PatientSymptom,
    VitalSigns, ClinicalNote, ImagingSummary
)
from ..llm.assessment_engine import IRAEAssessmentEngine
from ..utils.logging_config import (
    get_logger, set_correlation_id, get_correlation_id, LogContext
)


# =============================================================================
# FastAPI App Configuration
# =============================================================================

app = FastAPI(
    title="Oncology irAE Detection API",
    description="""
    AI-powered clinical decision support for detecting immune-related adverse events (irAEs)
    in oncology immunotherapy patients.
    
    ## Features
    - Parse clinical notes, labs, vitals, medications
    - Detect organ-specific irAE patterns (GI, hepatic, pulmonary, endocrine, skin, neuro, cardiac)
    - CTCAE v5.0 severity grading (Grade 1-4)
    - Urgency triage classification
    - Structured clinical output
    
    ## Safety Notice
    This tool supports clinical decision-making but does not replace clinical judgment.
    All findings should be verified by the treating clinician.
    """,
    version="1.0.0",
    contact={
        "name": "Oncology irAE Detection Team",
    },
    license_info={
        "name": "MIT License",
    },
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router for grouping endpoints
from fastapi import APIRouter
router = APIRouter(prefix="/api/v1", tags=["Assessment"])


# =============================================================================
# Middleware
# =============================================================================

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to each request for tracing."""
    # Get or generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = set_correlation_id()
    else:
        set_correlation_id(correlation_id)
    
    # Process request
    response = await call_next(request)
    
    # Add correlation ID to response headers
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests."""
    logger = get_logger('api.middleware')
    
    start_time = datetime.now()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # Log response
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Response: {response.status_code} ({elapsed:.3f}s)")
        
        return response
        
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.error(f"Request failed after {elapsed:.3f}s: {e}")
        raise


# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with structured response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            correlation_id=get_correlation_id(),
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger = get_logger('api.errors')
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred. Please try again.",
            correlation_id=get_correlation_id(),
        ).model_dump()
    )


# =============================================================================
# Helper Functions
# =============================================================================

def convert_request_to_patient_data(request: PatientDataRequest) -> PatientData:
    """Convert API request to internal PatientData model."""
    
    # Convert labs
    labs = []
    for lab in request.labs:
        labs.append(LabResult(
            name=lab.name,
            value=lab.value,
            unit=lab.unit,
            reference_low=lab.reference_low,
            reference_high=lab.reference_high,
            date=lab.date or datetime.now(),
            is_abnormal=lab.is_abnormal if lab.is_abnormal is not None else (
                (lab.reference_high is not None and lab.value > lab.reference_high) or
                (lab.reference_low is not None and lab.value < lab.reference_low)
            )
        ))
    
    # Convert medications
    medications = []
    for med in request.medications:
        medications.append(Medication(
            name=med.name,
            dose=med.dose,
            route=med.route,
            frequency=med.frequency,
            is_immunotherapy=med.is_immunotherapy if med.is_immunotherapy is not None else False,
            drug_class=med.drug_class
        ))
    
    # Convert symptoms
    symptoms = []
    for symptom in request.symptoms:
        symptoms.append(PatientSymptom(
            symptom=symptom.symptom,
            severity=symptom.severity,
            reported_date=symptom.reported_date or datetime.now()
        ))
    
    # Convert vitals
    vitals = []
    for vital in request.vitals:
        vitals.append(VitalSigns(
            date=vital.date or datetime.now(),
            temperature=vital.temperature,
            heart_rate=vital.heart_rate,
            blood_pressure_systolic=vital.blood_pressure_systolic,
            blood_pressure_diastolic=vital.blood_pressure_diastolic,
            respiratory_rate=vital.respiratory_rate,
            oxygen_saturation=vital.oxygen_saturation
        ))
    
    # Convert notes
    notes = []
    for note in request.notes:
        notes.append(ClinicalNote(
            date=note.date or datetime.now(),
            note_type=note.note_type or "progress",
            author=note.author,
            content=note.content
        ))
    
    # Convert imaging
    imaging = []
    for img in request.imaging:
        imaging.append(ImagingSummary(
            date=img.date or datetime.now(),
            modality=img.modality,
            body_region=img.body_region,
            findings=img.findings,
            impression=img.impression
        ))
    
    return PatientData(
        patient_id=request.patient_id,
        age=request.age,
        cancer_type=request.cancer_type,
        labs=labs,
        medications=medications,
        symptoms=symptoms,
        vitals=vitals,
        notes=notes,
        imaging=imaging,
        raw_notes=request.raw_notes,
        raw_labs=request.raw_labs,
        raw_medications=request.raw_medications
    )


def convert_assessment_to_response(assessment, correlation_id: str) -> AssessmentResponse:
    """Convert internal assessment to API response."""
    
    # Convert affected systems
    affected_systems = []
    for finding in assessment.affected_systems:
        affected_systems.append(OrganSystemFindingResponse(
            system=finding.system.value,
            detected=finding.detected,
            findings=finding.findings,
            evidence=finding.evidence,
            severity=finding.severity.value if finding.severity else None,
            confidence=finding.confidence
        ))
    
    # Convert immunotherapy context
    imm_ctx = ImmunotherapyContextResponse(
        on_immunotherapy=assessment.immunotherapy_context.on_immunotherapy,
        agents=assessment.immunotherapy_context.agents,
        drug_classes=assessment.immunotherapy_context.drug_classes,
        combination_therapy=assessment.immunotherapy_context.combination_therapy
    )
    
    # Convert causality
    causality = CausalityResponse(
        likelihood=assessment.causality.likelihood.value,
        reasoning=assessment.causality.reasoning,
        temporal_relationship=assessment.causality.temporal_relationship,
        alternative_causes=assessment.causality.alternative_causes,
        supporting_factors=assessment.causality.supporting_factors,
        against_factors=assessment.causality.against_factors
    )
    
    # Convert recommended actions
    actions = []
    for action in assessment.recommended_actions:
        actions.append(RecommendedActionResponse(
            action=action.action,
            priority=action.priority,
            rationale=action.rationale
        ))
    
    return AssessmentResponse(
        correlation_id=correlation_id,
        assessment_date=assessment.assessment_date,
        irae_detected=assessment.irae_detected,
        affected_systems=affected_systems,
        immunotherapy_context=imm_ctx,
        causality=causality,
        overall_severity=assessment.overall_severity.value,
        severity_reasoning=assessment.severity_reasoning,
        urgency=assessment.urgency.value,
        urgency_reasoning=assessment.urgency_reasoning,
        recommended_actions=actions,
        key_evidence=assessment.key_evidence,
        disclaimer=assessment.disclaimer
    )


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the current status of the API and its components.
    """
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(),
        components={
            "api": "healthy",
            "assessment_engine": "healthy",
        }
    )


@router.post(
    "/assess",
    response_model=AssessmentResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Assess patient for irAEs",
    description="""
    Perform irAE assessment on patient data.
    
    Analyzes clinical data including:
    - Medications (immunotherapy detection)
    - Laboratory results
    - Symptoms
    - Vital signs
    - Clinical notes
    - Imaging findings
    
    Returns a structured assessment including:
    - irAE detection status
    - Affected organ systems with severity grading
    - Urgency/triage classification
    - Recommended actions
    """
)
async def assess_patient(
    request: PatientDataRequest,
    engine: IRAEAssessmentEngine = Depends(get_assessment_engine)
):
    """Assess a patient for immune-related adverse events."""
    logger = get_logger('api.assess')
    correlation_id = get_correlation_id()
    
    with LogContext(logger, operation='assess_patient', correlation_id=correlation_id):
        # Rate limiting (using correlation_id as client identifier for demo)
        if not check_rate_limit(correlation_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        try:
            # Convert request to internal model
            patient_data = convert_request_to_patient_data(request)
            
            # Perform assessment (use async method directly)
            assessment = await engine.assess(patient_data)
            
            # Convert to response
            response = convert_assessment_to_response(assessment, correlation_id)
            
            logger.info(f"Assessment complete: irAE_detected={assessment.irae_detected}")
            
            return response
            
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Assessment failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Assessment failed. Please check input data and try again."
            )


@router.post(
    "/assess/batch",
    response_model=BatchAssessmentResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
    summary="Batch assess multiple patients",
    description="Process multiple patient assessments in a single request (max 100)."
)
async def batch_assess(
    request: BatchAssessmentRequest,
    engine: IRAEAssessmentEngine = Depends(get_assessment_engine)
):
    """Batch assess multiple patients for irAEs."""
    logger = get_logger('api.batch_assess')
    correlation_id = get_correlation_id()
    
    with LogContext(logger, operation='batch_assess', 
                   correlation_id=correlation_id, 
                   patient_count=len(request.patients)):
        
        results = []
        errors = []
        
        for i, patient_request in enumerate(request.patients):
            try:
                patient_data = convert_request_to_patient_data(patient_request)
                assessment = await engine.assess(patient_data)
                response = convert_assessment_to_response(
                    assessment, 
                    f"{correlation_id}-{i}"
                )
                results.append(response)
            except Exception as e:
                logger.warning(f"Failed to assess patient {i}: {e}")
                errors.append(ErrorResponse(
                    error="AssessmentError",
                    message=str(e),
                    correlation_id=f"{correlation_id}-{i}",
                    details={"patient_index": i}
                ))
        
        return BatchAssessmentResponse(
            correlation_id=correlation_id,
            total_patients=len(request.patients),
            completed=len(results),
            failed=len(errors),
            results=results,
            errors=errors
        )


@router.get(
    "/supported-medications",
    response_model=dict,
    summary="List supported immunotherapy medications",
    tags=["Reference Data"]
)
async def get_supported_medications():
    """
    Get list of supported immunotherapy medications.
    
    Returns medications the system can detect as immunotherapy agents.
    """
    return {
        "immunotherapy_agents": {
            "PD-1 Inhibitors": [
                "Pembrolizumab (Keytruda)",
                "Nivolumab (Opdivo)",
                "Cemiplimab (Libtayo)"
            ],
            "PD-L1 Inhibitors": [
                "Atezolizumab (Tecentriq)",
                "Durvalumab (Imfinzi)",
                "Avelumab (Bavencio)"
            ],
            "CTLA-4 Inhibitors": [
                "Ipilimumab (Yervoy)",
                "Tremelimumab"
            ],
            "LAG-3 Inhibitors": [
                "Relatlimab"
            ]
        },
        "note": "System can detect both generic and brand names"
    }


@router.get(
    "/ctcae-grades",
    response_model=dict,
    summary="Get CTCAE grading criteria",
    tags=["Reference Data"]
)
async def get_ctcae_grades():
    """
    Get CTCAE v5.0 grading criteria reference.
    
    Returns severity grading definitions used by the system.
    """
    return {
        "grades": {
            "Grade 1 - Mild": "Asymptomatic or mild symptoms; clinical or diagnostic observations only; intervention not indicated",
            "Grade 2 - Moderate": "Moderate; minimal, local or noninvasive intervention indicated; limiting age-appropriate instrumental ADL",
            "Grade 3 - Severe": "Severe or medically significant but not immediately life-threatening; hospitalization or prolongation of hospitalization indicated; disabling; limiting self care ADL",
            "Grade 4 - Life-threatening": "Life-threatening consequences; urgent intervention indicated"
        },
        "urgency_mapping": {
            "Grade 1": "🟢 Routine monitoring",
            "Grade 2": "🟡 Needs oncology review soon (1-3 days)",
            "Grade 3": "🟠 Urgent - same day evaluation",
            "Grade 4": "🔴 Emergency - immediate evaluation"
        },
        "reference": "Common Terminology Criteria for Adverse Events (CTCAE) v5.0"
    }


# Include router in app
app.include_router(router)


# =============================================================================
# Root endpoint
# =============================================================================

@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Oncology irAE Detection API",
        "version": "1.0.0",
        "description": "AI-powered clinical decision support for detecting immune-related adverse events",
        "docs_url": "/docs",
        "health_check": "/api/v1/health"
    }
