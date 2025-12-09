#!/usr/bin/env python3
"""
Configuration Management Module
Централизованная конфигурация приложения
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Available log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AIProvider(Enum):
    """Available AI providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    HYBRID = "hybrid"


@dataclass
class TelegramConfig:
    """
    Telegram bot configuration
    Конфигурация Telegram бота
    """
    bot_token: str = field(default_factory=lambda: os.getenv('TELEGRAM_BOT_TOKEN', ''))
    
    # Rate limiting
    max_concurrent_handlers: int = int(os.getenv('TELEGRAM_MAX_HANDLERS', '10'))
    request_timeout: int = int(os.getenv('TELEGRAM_TIMEOUT', '30'))
    
    # Message settings
    max_message_length: int = 4096
    message_cleanup_interval: int = 3600  # 1 hour
    
    def validate(self) -> None:
        """Validate Telegram configuration"""
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not self.bot_token.startswith(('123456', '999')):
            # Simple format check (bot tokens start with numbers)
            logger.warning("TELEGRAM_BOT_TOKEN might be invalid (doesn't start with numbers)")


@dataclass
class GitHubConfig:
    """
    GitHub API configuration
    Конфигурация GitHub API
    """
    token: str = field(default_factory=lambda: os.getenv('GITHUB_TOKEN', ''))
    api_url: str = "https://api.github.com"
    api_timeout: int = int(os.getenv('GITHUB_API_TIMEOUT', '10'))
    
    # Rate limiting (GitHub allows 60 requests/hour for unauthenticated, 5000 for authenticated)
    rate_limit_requests: int = 100  # Max requests per minute
    rate_limit_window: int = 60     # Time window in seconds
    
    # Retry settings
    max_retries: int = 3
    retry_backoff: float = 1.0  # exponential backoff multiplier
    
    # Caching
    cache_ttl: int = int(os.getenv('GITHUB_CACHE_TTL', '3600'))  # 1 hour
    cache_max_entries: int = 1000
    
    def validate(self) -> None:
        """Validate GitHub configuration"""
        if not self.token:
            raise ValueError("GITHUB_TOKEN is required")
        if not self.token.startswith(('ghp_', 'ghu_', 'ghs_', 'gho_')):
            logger.warning("GITHUB_TOKEN might be invalid (wrong format)")


@dataclass
class DatabaseConfig:
    """
    PostgreSQL database configuration
    Конфигурация PostgreSQL
    """
    # Connection
    url: str = field(default_factory=lambda: os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/github_verifier'
    ))
    
    # Connection pooling
    pool_min_size: int = int(os.getenv('DB_POOL_MIN', '10'))
    pool_max_size: int = int(os.getenv('DB_POOL_MAX', '20'))
    pool_max_queries: int = 50000
    pool_max_inactive_lifetime: int = 300  # 5 minutes
    
    # Timeouts
    connection_timeout: int = 10
    statement_timeout: int = 30
    
    # Logging
    echo_sql: bool = os.getenv('DB_ECHO_SQL', 'false').lower() == 'true'
    
    def validate(self) -> None:
        """Validate database configuration"""
        if not self.url or self.url == 'postgresql://user:password@localhost:5432/github_verifier':
            logger.warning("DATABASE_URL not properly configured")
        if not self.url.startswith('postgresql'):
            raise ValueError("DATABASE_URL must start with 'postgresql'")


@dataclass
class OllamaConfig:
    """
    Ollama (local LLM) configuration
    Конфигурация Ollama
    """
    host: str = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    model: str = os.getenv('OLLAMA_MODEL', 'mistral')
    timeout: int = int(os.getenv('OLLAMA_TIMEOUT', '60'))
    
    # Generation parameters
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    
    # Response limits
    max_tokens: Optional[int] = 2000
    
    # Retry settings
    max_retries: int = 2
    retry_delay: int = 5
    
    enabled: bool = os.getenv('OLLAMA_ENABLED', 'true').lower() == 'true'
    
    def validate(self) -> None:
        """Validate Ollama configuration"""
        if self.enabled and not self.host:
            raise ValueError("OLLAMA_HOST is required when Ollama is enabled")
        if self.temperature < 0 or self.temperature > 1:
            raise ValueError("temperature must be between 0 and 1")
        if self.top_p < 0 or self.top_p > 1:
            raise ValueError("top_p must be between 0 and 1")


@dataclass
class OpenAIConfig:
    """
    OpenAI API configuration
    Конфигурация OpenAI API
    """
    api_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    model: str = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    timeout: int = int(os.getenv('OPENAI_TIMEOUT', '30'))
    
    # API settings
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # Rate limiting
    requests_per_minute: int = 3
    
    enabled: bool = os.getenv('OPENAI_ENABLED', 'false').lower() == 'true'
    
    def validate(self) -> None:
        """Validate OpenAI configuration"""
        if self.enabled and not self.api_key:
            raise ValueError("OPENAI_API_KEY is required when OpenAI is enabled")
        if not self.api_key.startswith('sk-'):
            if self.enabled:
                logger.warning("OPENAI_API_KEY has unexpected format")


@dataclass
class LoggingConfig:
    """
    Logging configuration
    Конфигурация логирования
    """
    level: LogLevel = LogLevel(os.getenv('LOG_LEVEL', 'INFO'))
    
    # Format
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format: str = '%Y-%m-%d %H:%M:%S'
    
    # Files
    log_file: Optional[str] = os.getenv('LOG_FILE', None)
    log_file_max_size: int = 10 * 1024 * 1024  # 10 MB
    log_file_backup_count: int = 5
    
    # JSON logging
    use_json: bool = os.getenv('LOG_JSON', 'false').lower() == 'true'
    
    # Structured logging with structlog
    use_structlog: bool = os.getenv('LOG_STRUCTLOG', 'false').lower() == 'true'


@dataclass
class CacheConfig:
    """
    Caching configuration
    Конфигурация кэша
    """
    # TTL settings
    repository_ttl: int = 3600      # 1 hour
    commit_ttl: int = 1800          # 30 minutes
    user_ttl: int = 600             # 10 minutes
    api_response_ttl: int = 300     # 5 minutes
    
    # Cache size
    max_entries: int = 1000
    max_memory_mb: int = 100
    
    # Cleanup
    cleanup_interval: int = 3600    # 1 hour
    
    enabled: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'


@dataclass
class MonitoringConfig:
    """
    Monitoring and metrics configuration
    Конфигурация мониторинга
    """
    # Prometheus metrics
    prometheus_enabled: bool = os.getenv('PROMETHEUS_ENABLED', 'true').lower() == 'true'
    prometheus_port: int = int(os.getenv('PROMETHEUS_PORT', '8000'))
    
    # Health check
    health_check_interval: int = 60  # seconds
    
    # Sentry error tracking
    sentry_enabled: bool = os.getenv('SENTRY_ENABLED', 'false').lower() == 'true'
    sentry_dsn: str = os.getenv('SENTRY_DSN', '')


@dataclass
class AppConfig:
    """
    Main application configuration
    Основная конфигурация приложения
    """
    # Environment
    environment: str = os.getenv('ENVIRONMENT', 'production')
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Sub-configurations
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    github: GitHubConfig = field(default_factory=GitHubConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # AI provider selection
    ai_provider: AIProvider = AIProvider(os.getenv('AI_PROVIDER', 'hybrid'))
    
    # Misc settings
    version: str = "3.1.0"
    app_name: str = "GitHub Commits Verifier Bot"
    
    def validate(self) -> None:
        """
        Validate all configuration sections
        """
        try:
            self.telegram.validate()
            logger.info("Telegram config validated")
        except ValueError as e:
            logger.error("Telegram config error: %s", e)
            raise
        
        try:
            self.github.validate()
            logger.info("GitHub config validated")
        except ValueError as e:
            logger.error("GitHub config error: %s", e)
            raise
        
        try:
            self.database.validate()
            logger.info("Database config validated")
        except ValueError as e:
            logger.error("Database config error: %s", e)
            raise
        
        try:
            self.ollama.validate()
            logger.info("Ollama config validated")
        except ValueError as e:
            logger.error("Ollama config error: %s", e)
            raise
        
        try:
            self.openai.validate()
            logger.info("OpenAI config validated")
        except ValueError as e:
            logger.error("OpenAI config error: %s", e)
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        (useful for logging, but masks sensitive data)
        """
        return {
            'environment': self.environment,
            'debug': self.debug,
            'ai_provider': self.ai_provider.value,
            'telegram': {
                'bot_token': f"...{self.telegram.bot_token[-4:]}" if self.telegram.bot_token else 'NOT SET',
                'timeout': self.telegram.request_timeout,
            },
            'github': {
                'token': f"...{self.github.token[-4:]}" if self.github.token else 'NOT SET',
                'timeout': self.github.api_timeout,
                'cache_ttl': self.github.cache_ttl,
            },
            'database': {
                'url': self.database.url.replace(self.database.url.split('@')[0], 'user:***'),
                'pool_size': f"{self.database.pool_min_size}-{self.database.pool_max_size}",
            },
            'logging': {
                'level': self.logging.level.value,
                'use_json': self.logging.use_json,
            },
        }


def get_config() -> AppConfig:
    """
    Get application configuration instance
    Loads from environment variables
    
    Returns:
        AppConfig: Application configuration
        
    Raises:
        ValueError: If configuration is invalid
    """
    config = AppConfig()
    config.validate()
    return config


if __name__ == '__main__':
    # Test configuration loading
    print("Loading configuration...")
    try:
        app_config = get_config()
        print("Configuration loaded successfully:")
        print(app_config.to_dict())
    except ValueError as e:
        print(f"Configuration error: {e}")
        exit(1)
