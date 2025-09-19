#!/usr/bin/env python3
# Filename: addcomment.py
"""
Script to insert a comment with the filename at the beginning of various file types.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Tuple

# Define comment styles for different file extensions
COMMENT_STYLES: Dict[str, Tuple[str, str, str]] = {
    # Python
    '.py': ('# ', '', ''),
    
    # Shell scripts
    '.sh': ('# ', '', ''),
    
    # CSS
    '.css': ('/* ', ' */', ''),
    
    # JavaScript/TypeScript
    '.js': ('// ', '', ''),
    '.ts': ('// ', '', ''),
    '.tsx': ('// ', '', ''),
    '.jsx': ('// ', '', ''),
    
    # Dart
    '.dart': ('// ', '', ''),  # Added support for Dart
    
    # Additional common formats
    '.html': ('<!-- ', ' -->', ''),
    '.xml': ('<!-- ', ' -->', ''),
    '.sql': ('-- ', '', ''),
    '.rb': ('# ', '', ''),
    '.yaml': ('# ', '', ''),
    '.yml': ('# ', '', ''),
}

# ... (rest of the script remains unchanged until the main function)

def main():
    """Main function to handle command-line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Insert filename comments into various source code files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Supported file types:
  .py - Python
  .sh - Shell scripts
  .css - CSS stylesheets
  .js - JavaScript
  .ts - TypeScript
  .tsx - TypeScript React
  .jsx - JavaScript React
  .dart - Dart
  .html - HTML
  .xml - XML
  .sql - SQL
  .rb - Ruby
  .yaml - YAML
  .yml - YAML

Examples:
  %(prog)s file1.py file2.js file3.css
  %(prog)s -d ./src --recursive
  %(prog)s -d . --overwrite
        '''
    )
    
    parser.add_argument('files', nargs='*', help='Files to process')
    parser.add_argument('-d', '--directory', help='Process all supported files in directory')
    parser.add_argument('-r', '--recursive', action='store_true',
                      help='Process directories recursively (default: True)')
    parser.add_argument('--no-recursive', action='store_true',
                      help='Do not process directories recursively')
    parser.add_argument('-o', '--overwrite', action='store_true',
                      help='Overwrite existing filename comments')
    
    args = parser.parse_args()
    
    # Determine recursive setting
    recursive = True
    if args.no_recursive:
        recursive = False
    elif args.recursive:
        recursive = True
    
    # Process based on arguments
    if args.directory:
        process_directory(args.directory, recursive, args.overwrite)
    elif args.files:
        process_files(args.files, args.overwrite)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
