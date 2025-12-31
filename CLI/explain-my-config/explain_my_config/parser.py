"""
Configuration file parsers for the explain-my-config CLI tool.

This module handles parsing of different configuration file formats:
- .env files (KEY=VALUE format)
- .json files (JSON format)
- .yaml/.yml files (YAML format)
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any

# Import YAML parser (optional dependency handling)
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def parse_env(content: str) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    """
    Parse a .env file content into key-value pairs.
    
    Handles:
    - Standard KEY=VALUE format
    - Comments (lines starting with #)
    - Empty lines
    - Quoted values (single and double quotes)
    - Inline comments
    
    Args:
        content: The raw content of the .env file.
        
    Returns:
        A tuple of (list of (key, value) pairs, error_message).
        
    Example:
        >>> pairs, error = parse_env("PORT=8080\\nDEBUG=true")
        >>> pairs
        [('PORT', '8080'), ('DEBUG', 'true')]
    """
    pairs = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Strip whitespace
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip comment lines (lines starting with #)
        if line.startswith('#'):
            continue
        
        # Look for KEY=VALUE pattern
        # The key can contain letters, numbers, and underscores
        # The value is everything after the first =
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', line)
        
        if match:
            key = match.group(1)
            value = match.group(2)
            
            # Handle quoted values
            value = _strip_quotes(value)
            
            # Remove inline comments (but be careful with URLs and other valid # uses)
            # Only remove if there's a space before #
            if ' #' in value and not value.startswith(('http://', 'https://')):
                value = value.split(' #')[0].strip()
            
            pairs.append((key, value))
    
    return pairs, None


def _strip_quotes(value: str) -> str:
    """
    Remove surrounding quotes from a value.
    
    Args:
        value: The value that may be quoted.
        
    Returns:
        The value with surrounding quotes removed.
    """
    value = value.strip()
    
    # Remove double quotes
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1]
    
    # Remove single quotes
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        return value[1:-1]
    
    return value


def parse_json(content: str) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    """
    Parse a JSON file content into key-value pairs.
    
    Handles nested objects by flattening with dot notation.
    
    Args:
        content: The raw content of the JSON file.
        
    Returns:
        A tuple of (list of (key, value) pairs, error_message).
        
    Example:
        >>> pairs, error = parse_json('{"port": 8080, "debug": true}')
        >>> pairs
        [('port', '8080'), ('debug', 'true')]
    """
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return [], f"Invalid JSON: {str(e)}"
    
    # Handle non-object JSON (like arrays or primitives)
    if not isinstance(data, dict):
        return [], "JSON file must contain an object at the root level"
    
    # Flatten the JSON and convert to pairs
    pairs = _flatten_dict(data)
    
    return pairs, None


def _flatten_dict(data: Dict[str, Any], prefix: str = "") -> List[Tuple[str, str]]:
    """
    Flatten a nested dictionary into a list of key-value pairs.
    
    Uses dot notation for nested keys (e.g., "database.host").
    
    Args:
        data: The dictionary to flatten.
        prefix: The current key prefix for nested values.
        
    Returns:
        A list of (key, value) tuples.
    """
    pairs = []
    
    for key, value in data.items():
        # Build the full key path
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            pairs.extend(_flatten_dict(value, full_key))
        elif isinstance(value, list):
            # Convert lists to string representation
            pairs.append((full_key, str(value)))
        else:
            # Convert value to string
            pairs.append((full_key, str(value)))
    
    return pairs


def parse_yaml(content: str) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    """
    Parse a YAML file content into key-value pairs.
    
    Handles nested objects by flattening with dot notation.
    
    Args:
        content: The raw content of the YAML file.
        
    Returns:
        A tuple of (list of (key, value) pairs, error_message).
        
    Example:
        >>> pairs, error = parse_yaml("port: 8080\\ndebug: true")
        >>> pairs
        [('port', '8080'), ('debug', 'true')]
    """
    if not YAML_AVAILABLE:
        return [], "YAML support requires PyYAML. Install with: pip install PyYAML"
    
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        return [], f"Invalid YAML: {str(e)}"
    
    # Handle empty YAML files
    if data is None:
        return [], None
    
    # Handle non-object YAML
    if not isinstance(data, dict):
        return [], "YAML file must contain a mapping at the root level"
    
    # Flatten the YAML and convert to pairs
    pairs = _flatten_dict(data)
    
    return pairs, None


def parse_file(file_path: str, file_type: str, content: str) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    """
    Parse a configuration file based on its type.
    
    This is the main entry point for parsing, which delegates to the
    appropriate parser based on the file type.
    
    Args:
        file_path: Path to the file (for error messages).
        file_type: The type of file ('env', 'json', or 'yaml').
        content: The raw content of the file.
        
    Returns:
        A tuple of (list of (key, value) pairs, error_message).
    """
    parsers = {
        'env': parse_env,
        'json': parse_json,
        'yaml': parse_yaml,
    }
    
    parser = parsers.get(file_type)
    if parser is None:
        return [], f"Unsupported file type: {file_type}"
    
    return parser(content)
