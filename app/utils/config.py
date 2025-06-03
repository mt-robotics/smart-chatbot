import os
import logging
from dotenv import load_dotenv


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored log levels"""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


class Config:
    def __init__(self, environment: str = None):
        # Determine environment
        self.environment = (
            environment
            or os.getenv("APP_ENV")
            or os.getenv("ENVIRONMENT", "development")
        )

        # Load environment-specific file first
        env_file = f".env.{self.environment}"

        if os.path.exists(env_file):
            load_dotenv(env_file, override=True)
        else:
            # Fall back to default .env
            load_dotenv(".env")

        # Load configuration values
        self._load_config()

        # Set up logging AFTER loading config
        self._setup_logging()

        # Now we can log safely
        self.logger.info("Configuration loaded for environment: %s", self.environment)
        if os.path.exists(env_file):
            self.logger.info("Using environment file: %s", env_file)
        else:
            self.logger.warning(
                "Environment file %s not found, using default .env", {env_file}
            )

    def _load_config(self):
        """Load all configuration values from environment variables"""

        # API Configurations
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.API_HOST = os.getenv("API_HOST", "127.0.0.1")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        self.API_TITLE = os.getenv("API_TITLE", "Smart Customer Service Chatbot")
        self.API_DEBUG = os.getenv("API_DEBUG", "false").lower() == "true"

        # CORS Configuration
        cors_origins = os.getenv("CORS_ORIGINS", "*")
        self.CORS_ORIGINS = [origin.strip() for origin in cors_origins.split(",")]

        # Frontend Configuration
        self.BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")

        # NLP Configuration
        self.CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
        self.MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))
        self.ENABLE_DEBUG_INFO = (
            os.getenv("ENABLE_DEBUG_INFO", "false").lower() == "true"
        )

        # Response Configuration
        self.DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
        self.ENABLE_FALLBACK_RESPONSES = (
            os.getenv("ENABLE_FALLBACK_RESPONSES", "true").lower() == "true"
        )
        self.RESPONSE_DELAY = float(os.getenv("RESPONSE_DELAY", "0"))

        # Logging Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        self.ENABLE_REQUEST_LOGGING = (
            os.getenv("ENABLE_REQUEST_LOGGING", "false").lower() == "true"
        )

    def _setup_logging(self):
        """Configure logging for the entire application"""
        # Create logger
        self.logger = logging.getLogger("chatbot")

        # Prevent duplicate handles if config is reloaded
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Set log level
        log_level = getattr(logging, self.LOG_LEVEL, logging.INFO)
        self.logger.setLevel(log_level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create formatter
        if self.environment == "development":
            # Detailed format for development
            formatter = ColoredFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
            )
        else:
            # Cleaner format for production
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

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
