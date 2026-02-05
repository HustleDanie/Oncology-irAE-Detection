"""
FastAPI dependency injection for API routes.
"""

from typing import Optional, Generator
from functools import lru_cache
import logging

from ..llm.assessment_engine import IRAEAssessmentEngine
from ..llm.client import HuggingFaceClient
from ..utils.logging_config import get_logger, setup_logging


# Initialize logging
_root_logger = setup_logging(level="INFO", enable_file_logging=True)


@lru_cache()
def get_settings():
    """Get application settings (cached)."""
    try:
        from config.settings import Settings
        return Settings()
    except ImportError:
        return None


def get_logger_dependency() -> logging.Logger:
    """Get logger for API routes."""
    return get_logger('api')


def get_assessment_engine() -> IRAEAssessmentEngine:
    """
    Get the irAE assessment engine.
    
    Creates a new engine instance for each request.
    In production, you might want to use a singleton pattern
    or connection pooling for the LLM client.
    """
    logger = get_logger('api.dependencies')
    
    try:
        # Try to get settings, but don't fail if unavailable
        try:
            settings = get_settings()
            use_llm = settings.use_llm if hasattr(settings, 'use_llm') else False
        except Exception:
            use_llm = False
        
        # Create engine without LLM by default (faster, no external dependencies)
        engine = IRAEAssessmentEngine(
            llm_client=None,
            use_llm=False
        )
        
        logger.debug("Created assessment engine instance")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create assessment engine: {e}")
        raise


def get_huggingface_client() -> Optional[HuggingFaceClient]:
    """
    Get HuggingFace client for LLM-enhanced analysis.
    
    Returns None if HuggingFace is not configured or unavailable.
    """
    logger = get_logger('api.dependencies')
    
    try:
        settings = get_settings()
        
        if not hasattr(settings, 'huggingface_model'):
            logger.warning("HuggingFace model not configured")
            return None
        
        client = HuggingFaceClient(
            model_name=settings.huggingface_model,
            use_quantization=getattr(settings, 'use_quantization', True)
        )
        
        logger.info(f"Created HuggingFace client with model: {settings.huggingface_model}")
        return client
        
    except Exception as e:
        logger.warning(f"Could not create HuggingFace client: {e}")
        return None


class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    For production, use Redis-based rate limiting.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self._requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed."""
        import time
        
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old entries
        if client_id in self._requests:
            self._requests[client_id] = [
                t for t in self._requests[client_id] 
                if t > minute_ago
            ]
        else:
            self._requests[client_id] = []
        
        # Check limit
        if len(self._requests[client_id]) >= self.requests_per_minute:
            return False
        
        # Record request
        self._requests[client_id].append(current_time)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)


def check_rate_limit(client_id: str) -> bool:
    """Check if client is within rate limit."""
    return rate_limiter.is_allowed(client_id)
