"""
Settings and configuration management for Sokkary V2
"""

import os
from pathlib import Path
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Keys
    anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    groq_api_key: Optional[str] = Field(None, alias="GROQ_API_KEY")
    kimi_api_key: str = Field(..., alias="KIMI_API_KEY")

    # Kimi Configuration
    kimi_api_url: str = Field(
        "https://api.moonshot.ai/v1/chat/completions",
        alias="KIMI_API_URL"
    )
    kimi_model: str = Field("kimi-k2-turbo-preview", alias="KIMI_MODEL")

    # Model Configuration
    default_model: Literal["kimi", "claude", "groq", "openai"] = Field(
        "kimi",
        alias="DEFAULT_MODEL"
    )
    max_tokens: int = Field(4000, alias="MAX_TOKENS", ge=100, le=32000)
    temperature: float = Field(0.7, alias="TEMPERATURE", ge=0.0, le=2.0)

    # Agent Configuration
    agent_timeout: int = Field(60, alias="AGENT_TIMEOUT", ge=10, le=600)
    enable_parallel_agents: bool = Field(False, alias="ENABLE_PARALLEL_AGENTS")
    max_agent_retries: int = Field(3, alias="MAX_AGENT_RETRIES", ge=1, le=10)
    agent_protocol: Literal["sequential", "parallel"] = Field(
        "sequential",
        alias="AGENT_PROTOCOL"
    )

    # MCP Configuration
    mcp_enabled: bool = Field(True, alias="MCP_ENABLED")
    mcp_context_size: int = Field(8192, alias="MCP_CONTEXT_SIZE", ge=1024, le=32768)
    mcp_cache_dir: Path = Field(Path(".cache/mcp"), alias="MCP_CACHE_DIR")

    # Tools & Skills
    enable_file_tools: bool = Field(True, alias="ENABLE_FILE_TOOLS")
    enable_web_tools: bool = Field(True, alias="ENABLE_WEB_TOOLS")
    enable_code_tools: bool = Field(True, alias="ENABLE_CODE_TOOLS")
    enable_data_tools: bool = Field(True, alias="ENABLE_DATA_TOOLS")
    skill_safety_level: Literal["low", "medium", "high"] = Field(
        "medium",
        alias="SKILL_SAFETY_LEVEL"
    )

    # Logging
    debug: bool = Field(False, alias="DEBUG")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        "INFO",
        alias="LOG_LEVEL"
    )
    log_dir: Path = Field(Path("logs"), alias="LOG_DIR")
    log_retention_days: int = Field(30, alias="LOG_RETENTION_DAYS", ge=1, le=365)

    # LangSmith (Optional)
    langsmith_api_key: Optional[str] = Field(None, alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field("sokkary-v2", alias="LANGSMITH_PROJECT")
    langsmith_tracing: bool = Field(False, alias="LANGSMITH_TRACING")

    @field_validator("mcp_cache_dir", "log_dir", mode="before")
    @classmethod
    def ensure_path(cls, v):
        """Ensure path exists"""
        if isinstance(v, str):
            v = Path(v)
        if not v.exists():
            v.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def has_anthropic(self) -> bool:
        """Check if Anthropic API key is configured"""
        return bool(self.anthropic_api_key)

    @property
    def has_openai(self) -> bool:
        """Check if OpenAI API key is configured"""
        return bool(self.openai_api_key)

    @property
    def has_groq(self) -> bool:
        """Check if Groq API key is configured"""
        return bool(self.groq_api_key)

    @property
    def available_models(self) -> list[str]:
        """List of available models based on configured API keys"""
        models = ["kimi"]  # Always available
        if self.has_anthropic:
            models.append("claude")
        if self.has_groq:
            models.append("groq")
        if self.has_openai:
            models.append("openai")
        return models

    def validate_model(self, model: str) -> bool:
        """Check if a model is available"""
        return model in self.available_models

    def get_model_config(self, model: Optional[str] = None) -> dict:
        """Get configuration for a specific model"""
        model = model or self.default_model

        if model == "kimi":
            return {
                "api_key": self.kimi_api_key,
                "api_url": self.kimi_api_url,
                "model": self.kimi_model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
        elif model == "claude":
            return {
                "api_key": self.anthropic_api_key,
                "model": "claude-sonnet-4-20250514",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
        elif model == "groq":
            return {
                "api_key": self.groq_api_key,
                "model": "llama-3.3-70b-versatile",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
        elif model == "openai":
            return {
                "api_key": self.openai_api_key,
                "model": "gpt-4-turbo-preview",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
        else:
            raise ValueError(f"Unknown model: {model}")


# Global settings instance
settings = Settings()
