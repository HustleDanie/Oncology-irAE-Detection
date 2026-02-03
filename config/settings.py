"""Application configuration settings."""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "irAE Clinical Safety Assistant"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # LLM Configuration
    llm_provider: str = Field(default="openai", description="LLM provider: openai, anthropic, or huggingface")
    
    # API-based LLMs
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model name")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", description="Anthropic model name")

    # Local (Hugging Face) LLMs
    huggingface_reasoning_model: str = Field(default="google/gemma-med-lm-v1.1", description="HF model for clinical reasoning")
    huggingface_conditions_model: str = Field(default="google/gemma-conditions-chat-v1.1", description="HF model for condition extraction")
    huggingface_vitals_model: str = Field(default="google/gemma-vitals-chat-v1.1", description="HF model for vitals extraction")
    
    # Assessment Configuration
    default_use_llm: bool = Field(default=False, description="Use LLM by default for assessments")
    max_evidence_items: int = Field(default=10, description="Maximum evidence items to include")
    
    # Paths
    base_dir: Path = Field(default=Path(__file__).parent.parent, description="Base directory")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def llm_enabled(self) -> bool:
        """Check if LLM is configured and enabled."""
        if self.llm_provider == "openai":
            return self.openai_api_key is not None
        elif self.llm_provider == "anthropic":
            return self.anthropic_api_key is not None
        elif self.llm_provider == "huggingface":
            return True  # Assumes model is available locally
        return False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
