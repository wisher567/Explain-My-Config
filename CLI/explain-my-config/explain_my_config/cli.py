"""
Command-line interface for the explain-my-config tool.

This module provides the main entry point for the CLI application.
"""

import argparse
import sys
from typing import List, Tuple

from . import __version__
from .utils import detect_file_type, read_file_content, format_output, get_supported_extensions
from .parser import parse_file
from .explainer import get_explanation


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        An ArgumentParser configured for the CLI.
    """
    parser = argparse.ArgumentParser(
        prog='explain-my-config',
        description='Read configuration files and output plain-English explanations.',
        epilog=f'Supported file types: {get_supported_extensions()}'
    )
    
    parser.add_argument(
        'file',
        metavar='FILE',
        help='Path to the configuration file to explain'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    return parser


def process_config(pairs: List[Tuple[str, str]]) -> str:
    """
    Process configuration pairs and generate explanations.
    
    Args:
        pairs: A list of (key, value) tuples from the config file.
        
    Returns:
        A formatted string with all explanations.
    """
    if not pairs:
        return "No configuration entries found in the file."
    
    output_parts = []
    
    for key, value in pairs:
        explanation = get_explanation(key, value)
        formatted = format_output(key, value, explanation)
        output_parts.append(formatted)
    
    return '\n'.join(output_parts)


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = create_parser()
    args = parser.parse_args()
    
    file_path = args.file
    
    # Step 1: Detect file type
    file_type = detect_file_type(file_path)
    if file_type is None:
        print(f"Error: Unsupported file type.", file=sys.stderr)
        print(f"Supported types: {get_supported_extensions()}", file=sys.stderr)
        return 1
    
    # Step 2: Read the file
    content, read_error = read_file_content(file_path)
    if read_error:
        print(f"Error: {read_error}", file=sys.stderr)
        return 1
    
    # Step 3: Parse the file
    pairs, parse_error = parse_file(file_path, file_type, content)
    if parse_error:
        print(f"Error: {parse_error}", file=sys.stderr)
        return 1
    
    # Step 4: Generate and print explanations
    output = process_config(pairs)
    print(output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
