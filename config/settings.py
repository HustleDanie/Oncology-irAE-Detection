"""Application configuration settings."""

import os
from pathlib import Path
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "irAE Clinical Safety Assistant"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # LLM Configuration — Google MedGemma (HAI-DEF)
    llm_provider: str = Field(default="huggingface", description="LLM provider")

    # Hugging Face — Google HAI-DEF MedGemma
    huggingface_model: str = Field(default="google/medgemma-4b-it", description="Primary HuggingFace model for all medical tasks")
    huggingface_model_fallback: str = Field(default="google/medgemma-27b-text-it", description="Fallback model for complex reasoning (requires more resources)")
    use_quantization: bool = Field(default=True, description="Use 8-bit quantization to reduce memory usage")
    
    # Assessment Configuration
    default_use_llm: bool = Field(default=True, description="Use LLM by default for assessments")
    max_evidence_items: int = Field(default=10, description="Maximum evidence items to include")
    
    # Paths
    base_dir: Path = Field(default=Path(__file__).parent.parent, description="Base directory")
    
    @property
    def llm_enabled(self) -> bool:
        """Check if LLM is configured and enabled."""
        return self.llm_provider == "huggingface"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
