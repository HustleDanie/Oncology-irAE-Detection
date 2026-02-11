"""
Accuracy Monitoring for MedGemma irAE Detection System

Logs predictions vs expected outcomes for tracking model performance over time.
Enables drift detection and continuous improvement.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# Metrics storage path
METRICS_LOG_PATH = Path(__file__).parent.parent.parent / "logs" / "accuracy_metrics.jsonl"


@dataclass
class PredictionRecord:
    """Record of a single prediction for accuracy tracking."""
    timestamp: str
    case_id: str
    
    # Predictions
    predicted_irae: bool
    predicted_severity: str
    predicted_urgency: str
    predicted_systems: List[str]
    
    # Expected (ground truth) - optional
    expected_irae: Optional[bool] = None
    expected_severity: Optional[str] = None
    expected_urgency: Optional[str] = None
    expected_systems: Optional[List[str]] = None
    
    # Correctness scores (calculated)
    irae_correct: Optional[bool] = None
    severity_correct: Optional[bool] = None
    urgency_correct: Optional[bool] = None
    systems_f1: Optional[float] = None
    
    # Metadata
    model_version: str = "medgemma-4b-it"
    inference_time_ms: Optional[float] = None


class AccuracyMonitor:
    """
    Monitor and log MedGemma prediction accuracy over time.
    
    Usage:
        monitor = AccuracyMonitor()
        
        # Log a prediction
        monitor.log_prediction(
            case_id="GI-001",
            predicted_irae=True,
            predicted_severity="Grade 2",
            predicted_urgency="soon",
            predicted_systems=["Gastrointestinal"],
            expected_irae=True,  # Optional ground truth
            expected_severity="Grade 2",
            expected_urgency="soon",
            expected_systems=["Gastrointestinal"],
        )
        
        # Get summary
        summary = monitor.get_daily_summary()
    """
    
    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or METRICS_LOG_PATH
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_prediction(
        self,
        case_id: str,
        predicted_irae: bool,
        predicted_severity: str,
        predicted_urgency: str,
        predicted_systems: List[str],
        expected_irae: Optional[bool] = None,
        expected_severity: Optional[str] = None,
        expected_urgency: Optional[str] = None,
        expected_systems: Optional[List[str]] = None,
        inference_time_ms: Optional[float] = None,
    ) -> PredictionRecord:
        """
        Log a prediction with optional ground truth for accuracy tracking.
        """
        record = PredictionRecord(
            timestamp=datetime.now().isoformat(),
            case_id=case_id,
            predicted_irae=predicted_irae,
            predicted_severity=predicted_severity,
            predicted_urgency=predicted_urgency,
            predicted_systems=predicted_systems,
            expected_irae=expected_irae,
            expected_severity=expected_severity,
            expected_urgency=expected_urgency,
            expected_systems=expected_systems,
            inference_time_ms=inference_time_ms,
        )
        
        # Calculate correctness if ground truth provided
        if expected_irae is not None:
            record.irae_correct = predicted_irae == expected_irae
        
        if expected_severity is not None:
            record.severity_correct = self._severity_match(predicted_severity, expected_severity)
        
        if expected_urgency is not None:
            record.urgency_correct = self._urgency_match(predicted_urgency, expected_urgency)
        
        if expected_systems is not None:
            record.systems_f1 = self._calculate_systems_f1(predicted_systems, expected_systems)
        
        # Append to JSONL log
        self._append_to_log(record)
        
        # Log summary
        logger.info(f"[MONITOR] Prediction logged: case={case_id}, "
                   f"irae_correct={record.irae_correct}, "
                   f"severity_correct={record.severity_correct}, "
                   f"urgency_correct={record.urgency_correct}")
        
        return record
    
    def _severity_match(self, predicted: str, expected: str, tolerance: int = 1) -> bool:
        """Check if severity matches within tolerance (±1 grade)."""
        grade_map = {"grade 1": 1, "grade 2": 2, "grade 3": 3, "grade 4": 4, "unknown": 0}
        pred_grade = grade_map.get(predicted.lower().replace("-", " ").split()[0:2][-1] if "grade" in predicted.lower() else "unknown", 0)
        exp_grade = grade_map.get(expected.lower().replace("-", " ").split()[0:2][-1] if "grade" in expected.lower() else "unknown", 0)
        
        # Extract grade number
        for key, val in [("1", 1), ("2", 2), ("3", 3), ("4", 4)]:
            if key in predicted:
                pred_grade = val
            if key in expected:
                exp_grade = val
        
        return abs(pred_grade - exp_grade) <= tolerance
    
    def _urgency_match(self, predicted: str, expected: str) -> bool:
        """Check if urgency matches (or is higher for safety)."""
        urgency_rank = {"routine": 1, "soon": 2, "urgent": 3, "emergency": 4}
        pred_rank = urgency_rank.get(predicted.lower(), 0)
        exp_rank = urgency_rank.get(expected.lower(), 0)
        
        # Correct if exact match OR higher urgency (safer)
        return pred_rank >= exp_rank
    
    def _calculate_systems_f1(self, predicted: List[str], expected: List[str]) -> float:
        """Calculate F1 score for organ system detection."""
        pred_set = set(s.lower() for s in predicted)
        exp_set = set(s.lower() for s in expected)
        
        if len(pred_set) == 0 and len(exp_set) == 0:
            return 1.0
        
        tp = len(pred_set & exp_set)
        precision = tp / len(pred_set) if pred_set else 0
        recall = tp / len(exp_set) if exp_set else 0
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def _append_to_log(self, record: PredictionRecord):
        """Append record to JSONL log file."""
        with open(self.log_path, "a") as f:
            f.write(json.dumps(asdict(record)) + "\n")
    
    def get_recent_records(self, n: int = 100) -> List[Dict]:
        """Get the most recent n prediction records."""
        if not self.log_path.exists():
            return []
        
        records = []
        with open(self.log_path, "r") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        
        return records[-n:]
    
    def get_daily_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get accuracy summary for a specific date (or today).
        
        Returns:
            Dict with accuracy metrics
        """
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        records = self.get_recent_records(1000)  # Last 1000 records
        
        # Filter by date
        day_records = [
            r for r in records 
            if r.get("timestamp", "").startswith(target_date)
        ]
        
        if not day_records:
            return {"date": target_date, "total_predictions": 0, "message": "No predictions logged for this date"}
        
        # Calculate metrics
        total = len(day_records)
        irae_correct = sum(1 for r in day_records if r.get("irae_correct") is True)
        severity_correct = sum(1 for r in day_records if r.get("severity_correct") is True)
        urgency_correct = sum(1 for r in day_records if r.get("urgency_correct") is True)
        
        # Only count records with ground truth
        irae_total = sum(1 for r in day_records if r.get("irae_correct") is not None)
        severity_total = sum(1 for r in day_records if r.get("severity_correct") is not None)
        urgency_total = sum(1 for r in day_records if r.get("urgency_correct") is not None)
        
        avg_f1 = sum(r.get("systems_f1", 0) or 0 for r in day_records) / total if total > 0 else 0
        avg_inference = sum(r.get("inference_time_ms", 0) or 0 for r in day_records) / total if total > 0 else 0
        
        return {
            "date": target_date,
            "total_predictions": total,
            "with_ground_truth": irae_total,
            "metrics": {
                "irae_accuracy": round(irae_correct / irae_total, 3) if irae_total > 0 else None,
                "severity_accuracy": round(severity_correct / severity_total, 3) if severity_total > 0 else None,
                "urgency_safety_rate": round(urgency_correct / urgency_total, 3) if urgency_total > 0 else None,
                "systems_f1_mean": round(avg_f1, 3),
                "inference_time_ms_mean": round(avg_inference, 1),
            }
        }
    
    def print_summary(self, date: Optional[str] = None):
        """Print formatted accuracy summary."""
        summary = self.get_daily_summary(date)
        
        print("\n" + "="*50)
        print(f"📊 ACCURACY MONITOR - {summary['date']}")
        print("="*50)
        print(f"Total Predictions: {summary['total_predictions']}")
        print(f"With Ground Truth: {summary.get('with_ground_truth', 0)}")
        
        if summary.get("metrics"):
            m = summary["metrics"]
            print("\nMetrics:")
            if m.get("irae_accuracy") is not None:
                print(f"  irAE Detection:   {m['irae_accuracy']:.1%}")
            if m.get("severity_accuracy") is not None:
                print(f"  Severity (±1):    {m['severity_accuracy']:.1%}")
            if m.get("urgency_safety_rate") is not None:
                print(f"  Urgency Safety:   {m['urgency_safety_rate']:.1%}")
            print(f"  Systems F1:       {m['systems_f1_mean']:.1%}")
            print(f"  Avg Inference:    {m['inference_time_ms_mean']:.0f}ms")
        
        print("="*50 + "\n")


# Global monitor instance
_monitor: Optional[AccuracyMonitor] = None


def get_monitor() -> AccuracyMonitor:
    """Get or create the global accuracy monitor."""
    global _monitor
    if _monitor is None:
        _monitor = AccuracyMonitor()
    return _monitor


# Convenience functions
def log_prediction(**kwargs) -> PredictionRecord:
    """Log a prediction using the global monitor."""
    return get_monitor().log_prediction(**kwargs)


def get_daily_summary(date: Optional[str] = None) -> Dict[str, Any]:
    """Get daily accuracy summary using the global monitor."""
    return get_monitor().get_daily_summary(date)


def print_summary(date: Optional[str] = None):
    """Print accuracy summary using the global monitor."""
    get_monitor().print_summary(date)
