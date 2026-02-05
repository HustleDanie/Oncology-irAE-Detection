"""
Logging Configuration for Oncology irAE Detection System

Provides structured logging with:
- Console and file output
- JSON formatting for production
- Request tracing with correlation IDs
- PHI-safe logging (no patient data in logs)
"""

import logging
import logging.handlers
import sys
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
from contextvars import ContextVar
from functools import wraps
import time

# Context variable for request correlation
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')


class PHISafeFilter(logging.Filter):
    """
    Filter that redacts potential PHI from log messages.
    Ensures HIPAA compliance by not logging patient identifiers.
    """
    
    PHI_PATTERNS = [
        'patient_id', 'mrn', 'ssn', 'date_of_birth', 'dob',
        'address', 'phone', 'email', 'name'
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Redact PHI from log message."""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            msg_lower = record.msg.lower()
            for pattern in self.PHI_PATTERNS:
                if pattern in msg_lower:
                    # Log warning but don't include the actual value
                    record.msg = f"[PHI REDACTED] {record.msg.split('=')[0] if '=' in record.msg else record.msg}"
                    break
        return True


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    Ideal for log aggregation systems (ELK, Splunk, CloudWatch).
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add correlation ID if present
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data['correlation_id'] = correlation_id
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Colored console formatter for development.
    """
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        correlation_id = correlation_id_var.get()
        
        # Format timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Build message
        prefix = f"{timestamp} | {color}{record.levelname:8}{self.RESET}"
        if correlation_id:
            prefix += f" | {correlation_id[:8]}"
        prefix += f" | {record.name}"
        
        return f"{prefix} | {record.getMessage()}"


def setup_logging(
    level: str = "INFO",
    log_dir: Optional[str] = None,
    json_format: bool = False,
    enable_file_logging: bool = True,
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: ./logs)
        json_format: Use JSON format for logs (recommended for production)
        enable_file_logging: Whether to write logs to files
    
    Returns:
        Root logger for the application
    """
    # Create root logger for our application
    logger = logging.getLogger('oncology_irae')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Add PHI filter
    phi_filter = PHISafeFilter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.addFilter(phi_filter)
    
    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredConsoleFormatter())
    
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if enable_file_logging:
        log_path = Path(log_dir) if log_dir else Path('logs')
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler (10MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / 'oncology_irae.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.addFilter(phi_filter)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
        
        # Error-specific log file
        error_handler = logging.handlers.RotatingFileHandler(
            log_path / 'oncology_irae_errors.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.addFilter(phi_filter)
        error_handler.setFormatter(JSONFormatter())
        logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f'oncology_irae.{name}')


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracing."""
    return str(uuid.uuid4())


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set the correlation ID for the current context.
    
    Args:
        correlation_id: ID to use (generates new one if None)
    
    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return correlation_id_var.get()


def log_execution_time(logger: logging.Logger = None):
    """
    Decorator to log function execution time.
    
    Args:
        logger: Logger to use (defaults to function's module logger)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            start_time = time.time()
            logger.debug(f"Starting {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(f"Completed {func.__name__} in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Failed {func.__name__} after {elapsed:.3f}s: {e}")
                raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            start_time = time.time()
            logger.debug(f"Starting {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(f"Completed {func.__name__} in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Failed {func.__name__} after {elapsed:.3f}s: {e}")
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return decorator


class LogContext:
    """
    Context manager for logging with additional context.
    
    Usage:
        with LogContext(logger, operation='assess_patient'):
            # ... code ...
    """
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting operation", extra={'extra_data': self.context})
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        self.context['elapsed_seconds'] = round(elapsed, 3)
        
        if exc_type is not None:
            self.context['error'] = str(exc_val)
            self.logger.error(
                f"Operation failed: {exc_val}",
                extra={'extra_data': self.context}
            )
        else:
            self.logger.info(
                f"Operation completed",
                extra={'extra_data': self.context}
            )
        
        return False  # Don't suppress exceptions


# Import asyncio for the decorator check
import asyncio
