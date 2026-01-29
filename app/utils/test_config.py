# Absolute import from project root
from app.utils.config import get_config

# Load config
config = get_config()

# Print all values
print("=" * 50)
print("TESTING CONFIGURATION")
print("=" * 50)
print(f"Environment: {config.env.name}")
print(f"API Title: {config.api.title}")
print(f"API Host: {config.api.host}")
print(f"API Port: {config.api.port}")
print(f"API Debug: {config.api.debug}")
print(f"CORS Origins: {config.middleware['cors_origins']}")
print(f"Enable Request Logging: {config.middleware['enable_request_logging']}")
print(f"Confidence Threshold: {config.nlp['confidence_threshold']}")
print(f"Enable Debug Info: {config.nlp['enable_debug']}")
print(f"Max History: {config.nlp['max_history']}")
print(f"Default Language: {config.response['default_language']}")
print(f"Log Level: {config.logging.level}")
print("=" * 50)
