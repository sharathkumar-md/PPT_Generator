"""
Configuration module for RealtyAI
"""

from typing import Dict, Any, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for RealtyAI"""
    
    # Required API keys
    google_api_key: str = Field(..., description="Google AI API key for Gemini", alias="GOOGLE_API_KEY")
    serp_api_key: Optional[str] = Field(None, description="SerpAPI key for web search", alias="SERP_API_KEY")
    
    # Gemini Configuration
    gemini_model_name: str = Field(default="gemini-2.5-flash", description="Gemini model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens per request")
    
    # Search Configuration
    max_search_results: int = Field(default=10, gt=0, description="Maximum search results")
    
    # PowerPoint Configuration
    default_slide_count: int = Field(default=10, gt=0, description="Default number of slides")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator('google_api_key')
    @classmethod
    def validate_google_api_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('GOOGLE_API_KEY is required and cannot be empty')
        return v.strip()
    
    def validate_search_config(self) -> Dict[str, bool]:
        """Check if search is configured"""
        return {
            "serp_api_configured": bool(self.serp_api_key),
            "any_search_configured": bool(self.serp_api_key)
        }
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search engine configuration"""
        config = {}
        if self.serp_api_key:
            config["serp"] = {"api_key": self.serp_api_key}
        return config


# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get the global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
