"""
Utility functions for the explain-my-config CLI tool.

This module provides helper functions for file operations and output formatting.
"""

import os
from typing import Optional, Tuple


# Supported file extensions and their types
SUPPORTED_EXTENSIONS = {
    '.env': 'env',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
}


def detect_file_type(file_path: str) -> Optional[str]:
    """
    Detect the configuration file type based on its extension.
    
    Args:
        file_path: Path to the configuration file.
        
    Returns:
        The file type ('env', 'json', or 'yaml') if supported, None otherwise.
    
    Example:
        >>> detect_file_type("config.env")
        'env'
        >>> detect_file_type("settings.json")
        'json'
        >>> detect_file_type("config.yaml")
        'yaml'
    """
    # Get the file extension (lowercase for case-insensitive matching)
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    
    return SUPPORTED_EXTENSIONS.get(extension)


def read_file_content(file_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Read the contents of a file safely.
    
    Args:
        file_path: Path to the file to read.
        
    Returns:
        A tuple of (content, error_message).
        - If successful: (file_content, None)
        - If error: (None, error_message)
    
    Example:
        >>> content, error = read_file_content("config.env")
        >>> if error:
        ...     print(f"Error: {error}")
        ... else:
        ...     print(content)
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return None, f"File not found: {file_path}"
    
    # Check if it's a file (not a directory)
    if not os.path.isfile(file_path):
        return None, f"Not a file: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, None
    except PermissionError:
        return None, f"Permission denied: {file_path}"
    except UnicodeDecodeError:
        return None, f"Unable to read file (encoding error): {file_path}"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"


def format_output(key: str, value: str, explanation: str) -> str:
    """
    Format a single config entry for display.
    
    Args:
        key: The configuration key.
        value: The configuration value.
        explanation: The beginner-friendly explanation.
        
    Returns:
        A formatted string for display.
    
    Example:
        >>> print(format_output("PORT", "8080", "The network port the application listens on."))
        PORT = 8080
        -> The network port the application listens on.
    """
    # Truncate very long values for readability
    display_value = str(value)
    if len(display_value) > 80:
        display_value = display_value[:77] + "..."
    
    return f"{key} = {display_value}\n-> {explanation}\n"


def get_supported_extensions() -> str:
    """
    Get a formatted string of supported file extensions.
    
    Returns:
        A comma-separated string of supported extensions.
    
    Example:
        >>> print(get_supported_extensions())
        .env, .json, .yaml, .yml
    """
    return ", ".join(sorted(SUPPORTED_EXTENSIONS.keys()))
