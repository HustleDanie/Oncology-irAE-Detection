"""
Tests for API endpoints.

Run with: pytest tests/test_api.py -v
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.routes import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns healthy status."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "components" in data


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["docs_url"] == "/docs"


class TestAssessmentEndpoint:
    """Tests for patient assessment endpoint."""
    
    def test_assess_minimal_patient(self, client):
        """Test assessment with minimal patient data."""
        response = client.post("/api/v1/assess", json={
            "medications": [
                {"name": "Pembrolizumab", "is_immunotherapy": True}
            ],
            "labs": [
                {"name": "AST", "value": 150, "unit": "U/L", "reference_high": 40}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "correlation_id" in data
        assert "irae_detected" in data
        assert "immunotherapy_context" in data
        assert data["immunotherapy_context"]["on_immunotherapy"] == True
        assert "affected_systems" in data
        assert "urgency" in data
        assert "disclaimer" in data
    
    def test_assess_hepatitis_case(self, client):
        """Test assessment with hepatitis scenario."""
        response = client.post("/api/v1/assess", json={
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
                    "reference_low": 10,
                    "reference_high": 40,
                    "is_abnormal": True
                },
                {
                    "name": "ALT",
                    "value": 220,
                    "unit": "U/L",
                    "reference_low": 7,
                    "reference_high": 56,
                    "is_abnormal": True
                }
            ],
            "symptoms": [
                {"symptom": "fatigue", "severity": "moderate"},
                {"symptom": "nausea", "severity": "mild"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect irAE
        assert data["irae_detected"] == True
        
        # Should detect PD-1 therapy
        assert "PD-1" in data["immunotherapy_context"]["drug_classes"]
        
        # Should detect hepatic involvement
        hepatic = next(
            (s for s in data["affected_systems"] if s["system"] == "Hepatic"),
            None
        )
        assert hepatic is not None
        assert hepatic["detected"] == True
        assert "Grade 2" in hepatic["severity"]
    
    def test_assess_colitis_case(self, client):
        """Test assessment with colitis scenario."""
        response = client.post("/api/v1/assess", json={
            "medications": [
                {"name": "Nivolumab", "is_immunotherapy": True, "drug_class": "PD-1"},
                {"name": "Ipilimumab", "is_immunotherapy": True, "drug_class": "CTLA-4"}
            ],
            "symptoms": [
                {"symptom": "bloody diarrhea", "severity": "severe"},
                {"symptom": "abdominal pain", "severity": "severe"}
            ],
            "vitals": [
                {"heart_rate": 105, "temperature": 38.2}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect combination therapy
        assert data["immunotherapy_context"]["combination_therapy"] == True
        
        # Should detect GI involvement
        gi = next(
            (s for s in data["affected_systems"] if s["system"] == "Gastrointestinal"),
            None
        )
        assert gi is not None
        assert gi["detected"] == True
    
    def test_assess_no_immunotherapy(self, client):
        """Test assessment without immunotherapy."""
        response = client.post("/api/v1/assess", json={
            "medications": [
                {"name": "Metformin"},
                {"name": "Lisinopril"}
            ],
            "labs": [
                {"name": "AST", "value": 45, "unit": "U/L"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should recognize no immunotherapy
        assert data["immunotherapy_context"]["on_immunotherapy"] == False
    
    def test_assess_empty_request(self, client):
        """Test assessment with empty request."""
        response = client.post("/api/v1/assess", json={})
        
        # Should succeed but show no immunotherapy
        assert response.status_code == 200
        data = response.json()
        assert data["immunotherapy_context"]["on_immunotherapy"] == False
    
    def test_assess_correlation_id_header(self, client):
        """Test that correlation ID is returned in response."""
        response = client.post(
            "/api/v1/assess",
            json={"medications": []},
            headers={"X-Correlation-ID": "test-correlation-123"}
        )
        
        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers
        
        data = response.json()
        assert data["correlation_id"] == "test-correlation-123"


class TestBatchAssessmentEndpoint:
    """Tests for batch assessment endpoint."""
    
    def test_batch_assess_multiple_patients(self, client):
        """Test batch assessment with multiple patients."""
        response = client.post("/api/v1/assess/batch", json={
            "patients": [
                {
                    "medications": [{"name": "Pembrolizumab"}],
                    "labs": [{"name": "AST", "value": 100, "unit": "U/L"}]
                },
                {
                    "medications": [{"name": "Nivolumab"}],
                    "symptoms": [{"symptom": "diarrhea"}]
                }
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_patients"] == 2
        assert data["completed"] == 2
        assert data["failed"] == 0
        assert len(data["results"]) == 2
    
    def test_batch_assess_empty_list(self, client):
        """Test batch assessment with empty patient list."""
        response = client.post("/api/v1/assess/batch", json={
            "patients": []
        })
        
        # Should fail validation (min_length=1)
        assert response.status_code == 422


class TestReferenceEndpoints:
    """Tests for reference data endpoints."""
    
    def test_supported_medications(self, client):
        """Test supported medications endpoint."""
        response = client.get("/api/v1/supported-medications")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "immunotherapy_agents" in data
        assert "PD-1 Inhibitors" in data["immunotherapy_agents"]
        assert "CTLA-4 Inhibitors" in data["immunotherapy_agents"]
    
    def test_ctcae_grades(self, client):
        """Test CTCAE grades endpoint."""
        response = client.get("/api/v1/ctcae-grades")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "grades" in data
        assert "Grade 1 - Mild" in data["grades"]
        assert "Grade 4 - Life-threatening" in data["grades"]
        assert "urgency_mapping" in data


class TestAPIDocumentation:
    """Tests for API documentation."""
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["info"]["title"] == "Oncology irAE Detection API"
        assert "/api/v1/assess" in data["paths"]
        assert "/api/v1/health" in data["paths"]
    
    def test_docs_page(self, client):
        """Test Swagger docs page is accessible."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
