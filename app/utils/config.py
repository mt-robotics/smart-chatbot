"""Configuration management for the project.

Loads settings from environment variables and .env files, with support for
different environments (dev/prod). See README.md for configuration options.
"""

import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored log levels"""

    # ANSI color codes as class-level constants
    # ALL_CAPS naming convention indicates these are constants
    ANSI_COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)

    def format(self, record):
        # Add color to levelname

        if record.levelname in self.ANSI_COLORS:
            record.levelname = f"{self.ANSI_COLORS[record.levelname]}{record.levelname}{self.ANSI_COLORS['RESET']}"

        return super().format(record)


@dataclass
class EnvironmentConfig:
    """Configuration for environment settings."""

    name: str
    file: str


@dataclass
class LoggingConfig:
    """Configuration for logging settings."""

    level: str
    format: str


@dataclass
class APIConfig:
    """Configuration for API settings."""

    title: str
    host: str
    port: int
    debug: bool


class Config:
    """Manages application configuration and logging setup.

    Provides typed access to configuration through dataclasses and
    automatically sets up logging based on the environment.
    """

    def __init__(self, environment: str = None):
        # Initialize environment config first
        self._init_environment(environment)

        # Load environment variables
        self._load_env_file()

        # Load all other configs
        self._load_config()

        # Set up logging AFTER loading config
        self._setup_logging()

        # Now we can log safely
        self.logger.info("Configuration loaded for environment: %s", self.env.name)
        if os.path.exists(self.env.file):
            self.logger.info("Using environment file: %s", self.env.file)
        else:
            self.logger.warning(
                "Environment file %s not found, using default .env", self.env.file
            )

    def _init_environment(self, environment: str = None):
        """Initialize environment configuration"""
        env_name = (
            environment
            or os.getenv("APP_ENV")
            or os.getenv("ENVIRONMENT", "development")
        )
        self.env = EnvironmentConfig(name=env_name, file=f".env.{env_name}")

    def _load_env_file(self):
        """Load environment variables from the appropriate file

        NOTE: override=False means Docker/system environment variables take precedence
        This is critical for containerized deployments where docker-compose sets DATABASE_URL, etc.
        Order of precedence (highest to lowest):
        1. System/Docker environment variables (e.g., from docker-compose)
        2. .env files (loaded here as defaults only)
        """
        if os.path.exists(self.env.file):
            load_dotenv(self.env.file, override=False)
        else:
            # Fall back to default .env
            load_dotenv(".env", override=False)

    def _load_config(self):
        """Load all configuration values from environment variables"""
        # API Configuration
        self.api = APIConfig(
            title=os.getenv("API_TITLE", "Smart Chatbot API"),
            host=os.getenv("API_HOST", "127.0.0.1"),
            port=int(os.getenv("API_PORT", "8000")),
            debug=os.getenv("API_DEBUG", "false").lower() == "true",
        )

        # CORS Configuration
        cors_origins = os.getenv("CORS_ORIGINS", "*")

        # Middleware Configuration
        self.middleware = {
            "enable_request_logging": os.getenv(
                "ENABLE_REQUEST_LOGGING", "false"
            ).lower()
            == "true",  # Request Logging Configuration
            "cors_origins": [origin.strip() for origin in cors_origins.split(",")],
        }

        # Frontend Configuration
        self.frontend = {
            "backend_url": os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")
        }

        # NLP Configuration
        self.nlp = {
            "confidence_threshold": float(os.getenv("CONFIDENCE_THRESHOLD", "0.5")),
            "max_history": int(os.getenv("MAX_CONVERSATION_HISTORY", "50")),
            "enable_debug": os.getenv("ENABLE_DEBUG_INFO", "false").lower() == "true",
        }

        # Response Configuration
        self.response = {
            "default_language": os.getenv("DEFAULT_LANGUAGE", "en"),
            "enable_fallback": os.getenv("ENABLE_FALLBACK_RESPONSES", "true").lower()
            == "true",
            "delay": float(os.getenv("RESPONSE_DELAY", "0")),
        }

        # Logging Configuration
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO").upper(),
            format=(
                "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
                if self.env.name == "development"
                else "%(asctime)s - %(levelname)s - %(message)s"
            ),
        )

    def _setup_logging(self):
        """Configure logging for the entire application"""
        # Create logger
        self.logger = logging.getLogger("chatbot")

        # Prevent duplicate handles if config is reloaded
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Set log level
        log_level = getattr(logging, self.logging.level, logging.INFO)
        self.logger.setLevel(log_level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create formatter
        formatter = (
            ColoredFormatter(self.logging.format)
            if self.env.name == "development"
            else logging.Formatter(self.logging.format)
        )

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Configure root logger to avoid duplicate logs
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Remove default handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def get_logger(self, name: str = None):
        """Get a logger instance for use in other modules"""
        if name:
            return logging.getLogger(f"chatbot.{name}")
        return logging.getLogger("chatbot")


class ConfigManager:
    """Singleton configuration manager"""

    def __init__(self):
        self.config = None

    def get_config(self, environment: str = None) -> Config:
        """Get the configuration instance (creates if doesn't exist)"""
        if self.config is None:
            self.config = Config(environment)
        return self.config

    def get_logger(self, name: str = None):
        """Get a logger instance from the configuration"""
        return self.get_config().get_logger(name)


# Create single instance of ConfigManager
config_manager = ConfigManager()


# Convenience functions for easier imports
def get_config(environment: str = None) -> Config:
    """Get the global configuration instance"""
    return config_manager.get_config(environment)


def get_logger(name: str = None):
    """Get a logger instance from anywhere in the app"""
    return config_manager.get_logger(name)
