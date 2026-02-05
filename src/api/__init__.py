"""
API module for Oncology irAE Detection System.

Provides RESTful API endpoints using FastAPI.
"""

from .routes import router, app
from .schemas import (
    PatientDataRequest,
    AssessmentResponse,
    HealthCheckResponse,
    ErrorResponse,
)
from .dependencies import get_assessment_engine, get_logger

__all__ = [
    'router',
    'app',
    'PatientDataRequest',
    'AssessmentResponse',
    'HealthCheckResponse',
    'ErrorResponse',
    'get_assessment_engine',
    'get_logger',
]
