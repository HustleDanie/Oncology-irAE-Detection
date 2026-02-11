"""Evaluation module for irAE detection system."""

from .evaluation_framework import (
    EvaluationFramework,
    EvaluationResult,
    ExpectedOutcome,
    AggregateMetrics,
    TEST_CASES,
)

__all__ = [
    "EvaluationFramework",
    "EvaluationResult", 
    "ExpectedOutcome",
    "AggregateMetrics",
    "TEST_CASES",
]
