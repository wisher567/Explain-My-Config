"""
Explanation generator for the explain-my-config CLI tool.

This module provides explanations for common configuration keys and
generates smart fallback explanations for unknown keys.
"""

import re
from typing import Optional


# Dictionary of known configuration keys and their explanations
# These are common keys found in many applications
KNOWN_KEYS = {
    # Database-related
    "DB_POOL_SIZE": "Controls how many database connections can exist at the same time.",
    "DB_HOST": "The hostname or IP address of the database server.",
    "DB_PORT": "The network port used to connect to the database.",
    "DB_NAME": "The name of the database to connect to.",
    "DB_USER": "The username for database authentication.",
    "DB_PASSWORD": "The password for database authentication.",
    "DATABASE_URL": "The full connection string for the database.",
    "DATABASE_HOST": "The hostname or IP address of the database server.",
    "DATABASE_PORT": "The network port used to connect to the database.",
    "DATABASE_NAME": "The name of the database to connect to.",
    
    # Server configuration
    "PORT": "The network port the application listens on.",
    "HOST": "The hostname or IP address the server binds to.",
    "BIND_ADDRESS": "The IP address the server binds to for incoming connections.",
    "LISTEN_ADDRESS": "The address the server listens on for incoming connections.",
    
    # Environment and debugging
    "DEBUG": "Enables or disables debug mode for development.",
    "NODE_ENV": "The environment mode (development, production, test).",
    "ENVIRONMENT": "The current running environment (dev, staging, production).",
    "ENV": "The current running environment.",
    "APP_ENV": "The application environment setting.",
    "FLASK_ENV": "The Flask framework environment mode.",
    "RAILS_ENV": "The Ruby on Rails environment mode.",
    "DJANGO_DEBUG": "Enables or disables Django debug mode.",
    
    # Logging
    "LOG_LEVEL": "Controls how much detail is written to logs (debug, info, warn, error).",
    "LOG_FILE": "The file path where logs are written.",
    "LOG_FORMAT": "The format pattern for log messages.",
    "LOGGING_LEVEL": "Controls the verbosity of application logging.",
    
    # Security
    "SECRET_KEY": "A secret value used for encryption and session security.",
    "API_KEY": "A key used to authenticate API requests.",
    "JWT_SECRET": "The secret key used to sign JSON Web Tokens.",
    "AUTH_SECRET": "A secret value used for authentication purposes.",
    "ENCRYPTION_KEY": "The key used for encrypting sensitive data.",
    "PASSWORD_SALT": "A value added to passwords before hashing for security.",
    
    # Timeouts and limits
    "TIMEOUT": "The maximum time to wait before canceling an operation.",
    "REQUEST_TIMEOUT": "The maximum time to wait for an HTTP request to complete.",
    "CONNECTION_TIMEOUT": "The maximum time to wait when establishing a connection.",
    "READ_TIMEOUT": "The maximum time to wait for data to be received.",
    "MAX_CONNECTIONS": "The maximum number of simultaneous connections allowed.",
    "MAX_RETRIES": "The maximum number of times to retry a failed operation.",
    "RATE_LIMIT": "The maximum number of requests allowed in a time period.",
    
    # Caching
    "CACHE_TTL": "How long cached data remains valid (in seconds).",
    "CACHE_ENABLED": "Enables or disables the caching system.",
    "CACHE_SIZE": "The maximum size of the cache in memory.",
    "REDIS_URL": "The connection URL for Redis cache server.",
    "MEMCACHED_SERVERS": "The list of Memcached server addresses.",
    
    # Email
    "SMTP_HOST": "The hostname of the email server.",
    "SMTP_PORT": "The port used to connect to the email server.",
    "SMTP_USER": "The username for email server authentication.",
    "SMTP_PASSWORD": "The password for email server authentication.",
    "EMAIL_FROM": "The default sender email address.",
    "MAIL_SERVER": "The hostname of the mail server.",
    
    # URLs and endpoints
    "API_URL": "The base URL for API endpoints.",
    "BASE_URL": "The root URL of the application.",
    "CALLBACK_URL": "The URL to redirect to after an operation completes.",
    "WEBHOOK_URL": "The URL that receives webhook notifications.",
    "FRONTEND_URL": "The URL of the frontend application.",
    "BACKEND_URL": "The URL of the backend API.",
    
    # Feature flags
    "FEATURE_FLAGS": "Toggles for enabling or disabling specific features.",
    "ENABLE_FEATURE": "Enables or disables a specific feature.",
    "EXPERIMENTAL": "Enables or disables experimental features.",
    
    # Miscellaneous
    "TZ": "The timezone for the application.",
    "TIMEZONE": "The timezone setting for date/time operations.",
    "LOCALE": "The language and region setting.",
    "LANG": "The language setting for the application.",
    "VERSION": "The version number of the application.",
    "APP_NAME": "The name of the application.",
    "APP_VERSION": "The version number of the application.",
}


# Patterns for generating fallback explanations
# These help us guess what unknown keys might mean
VALUE_PATTERNS = {
    'url': r'^https?://',
    'email': r'^[^@]+@[^@]+\.[^@]+$',
    'boolean_true': r'^(true|yes|on|1|enabled)$',
    'boolean_false': r'^(false|no|off|0|disabled)$',
    'number': r'^-?\d+(\.\d+)?$',
    'path': r'^(/|\.\.?/|[A-Za-z]:\\)',
}


# Common key suffixes and their meanings
KEY_SUFFIX_HINTS = {
    '_URL': "The URL endpoint for {}.",
    '_URI': "The URI for {}.",
    '_HOST': "The hostname or IP address for {}.",
    '_PORT': "The network port for {}.",
    '_KEY': "The authentication or API key for {}.",
    '_SECRET': "A secret value for {} (keep this private).",
    '_TOKEN': "An access token for {}.",
    '_PASSWORD': "The password for {}.",
    '_USER': "The username for {}.",
    '_USERNAME': "The username for {}.",
    '_NAME': "The name of {}.",
    '_PATH': "The file or directory path for {}.",
    '_DIR': "The directory path for {}.",
    '_FILE': "The file path for {}.",
    '_SIZE': "The size setting for {}.",
    '_LIMIT': "The maximum limit for {}.",
    '_COUNT': "The number of items for {}.",
    '_TIMEOUT': "The timeout duration (in seconds) for {}.",
    '_TTL': "The time-to-live duration for {}.",
    '_ENABLED': "Enables or disables {}.",
    '_DISABLED': "Disables {}.",
    '_MODE': "The operating mode for {}.",
    '_LEVEL': "The level setting for {}.",
    '_MAX': "The maximum value for {}.",
    '_MIN': "The minimum value for {}.",
    '_ID': "The unique identifier for {}.",
    '_VERSION': "The version of {}.",
}


def get_explanation(key: str, value: str) -> str:
    """
    Get an explanation for a configuration key.
    
    First checks the known keys dictionary, then generates a fallback
    explanation if the key is not found.
    
    Args:
        key: The configuration key.
        value: The configuration value.
        
    Returns:
        A beginner-friendly explanation of what this config setting does.
        
    Example:
        >>> get_explanation("PORT", "8080")
        'The network port the application listens on.'
        >>> get_explanation("CACHE_TTL", "300")
        'How long cached data remains valid (in seconds).'
    """
    # Normalize the key to uppercase for lookup
    normalized_key = key.upper()
    
    # Check if we know this exact key
    if normalized_key in KNOWN_KEYS:
        return KNOWN_KEYS[normalized_key]
    
    # Handle nested keys (like database.host becoming DATABASE_HOST)
    flat_key = normalized_key.replace('.', '_')
    if flat_key in KNOWN_KEYS:
        return KNOWN_KEYS[flat_key]
    
    # Generate a fallback explanation
    return generate_fallback(key, value)


def generate_fallback(key: str, value: str) -> str:
    """
    Generate a fallback explanation for an unknown key.
    
    Uses the key name structure and value type to make an educated guess
    about what the configuration setting does.
    
    Args:
        key: The configuration key.
        value: The configuration value.
        
    Returns:
        A generated explanation based on the key name and value type.
        
    Example:
        >>> generate_fallback("CACHE_TTL", "300")
        'The time-to-live duration for cache.'
        >>> generate_fallback("API_ENDPOINT", "https://api.example.com")
        'Sets the API endpoint (appears to be a URL).'
    """
    normalized_key = key.upper()
    
    # Check for known suffixes
    for suffix, template in KEY_SUFFIX_HINTS.items():
        if normalized_key.endswith(suffix):
            # Extract the prefix and make it human-readable
            prefix = normalized_key[:-len(suffix)]
            readable_prefix = _make_readable(prefix)
            return template.format(readable_prefix)
    
    # Analyze the value type
    value_hint = _analyze_value(value)
    
    # Generate a generic explanation based on key name
    readable_key = _make_readable(normalized_key)
    
    if value_hint:
        return f"Sets the {readable_key.lower()} ({value_hint})."
    else:
        return f"Configuration setting for {readable_key.lower()}."


def _make_readable(key: str) -> str:
    """
    Convert a KEY_NAME to a readable format.
    
    Args:
        key: The key in UPPER_SNAKE_CASE.
        
    Returns:
        A human-readable version of the key.
        
    Example:
        >>> _make_readable("DATABASE_CONNECTION")
        'database connection'
    """
    # Split by underscores and join with spaces
    words = key.lower().split('_')
    # Filter out empty strings
    words = [w for w in words if w]
    return ' '.join(words)


def _analyze_value(value: str) -> Optional[str]:
    """
    Analyze a value to determine its likely type or purpose.
    
    Args:
        value: The configuration value.
        
    Returns:
        A hint about the value type, or None if no pattern matches.
    """
    value_lower = value.lower().strip()
    
    # Check for URL
    if re.match(VALUE_PATTERNS['url'], value, re.IGNORECASE):
        return "appears to be a URL"
    
    # Check for email
    if re.match(VALUE_PATTERNS['email'], value):
        return "appears to be an email address"
    
    # Check for boolean true
    if re.match(VALUE_PATTERNS['boolean_true'], value_lower):
        return "enables this feature"
    
    # Check for boolean false
    if re.match(VALUE_PATTERNS['boolean_false'], value_lower):
        return "disables this feature"
    
    # Check for number
    if re.match(VALUE_PATTERNS['number'], value):
        return "numeric value"
    
    # Check for file path
    if re.match(VALUE_PATTERNS['path'], value):
        return "appears to be a file path"
    
    return None
