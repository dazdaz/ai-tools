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
    
    # Kotlin
    '.kt': ('// ', '', ''),  # Added support for Kotlin
    
    # Dart
    '.dart': ('// ', '', ''),
    
    # Additional common formats
    '.html': ('<!-- ', ' -->', ''),
    '.xml': ('<!-- ', ' -->', ''),
    '.sql': ('-- ', '', ''),
    '.rb': ('# ', '', ''),
    '.yaml': ('# ', '', ''),
    '.yml': ('# ', '', ''),
}

def insert_filename_comment(filepath: str, overwrite: bool = False) -> bool:
    """
    Insert a comment with the filename at the beginning of the file.
    
    Args:
        filepath: Path to the file to process
        overwrite: If True, overwrites existing filename comment if present
    
    Returns:
        True if successful, False otherwise
    """
    path = Path(filepath)
    
    # Check if file exists
    if not path.exists():
        print(f"Error: File '{filepath}' does not exist.")
        return False
    
    # Get file extension
    ext = path.suffix.lower()
    
    # Check if we support this file type
    if ext not in COMMENT_STYLES:
        print(f"Warning: Unsupported file type '{ext}' for file '{filepath}'")
        return False
    
    # Get comment style
    prefix, suffix, _ = COMMENT_STYLES[ext]
    
    # Create the comment with filename
    filename = path.name
    comment = f"{prefix}Filename: {filename}{suffix}\n"
    
    try:
        # Read existing content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if shebang is present (for scripts)
        lines = content.split('\n')
        insert_position = 0
        
        # Preserve shebang if present
        if lines and lines[0].startswith('#!'):
            insert_position = 1
            shebang = lines[0] + '\n'
            remaining_content = '\n'.join(lines[1:])
        else:
            shebang = ''
            remaining_content = content
        
        # Check if filename comment already exists
        expected_comment_content = f"Filename: {filename}"
        if expected_comment_content in (lines[insert_position] if insert_position < len(lines) else ''):
            if not overwrite:
                print(f"Info: Filename comment already exists in '{filepath}'. Skipping.")
                return True
            else:
                # Remove the old comment
                if insert_position < len(lines):
                    lines.pop(insert_position)
                    remaining_content = '\n'.join(lines[insert_position:])
        
        # Construct new content
        if shebang:
            new_content = shebang + comment + remaining_content
        else:
            new_content = comment + remaining_content
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Added filename comment to '{filepath}'")
        return True
        
    except Exception as e:
        print(f"Error processing file '{filepath}': {str(e)}")
        return False

def process_files(file_paths: list, overwrite: bool = False) -> None:
    """
    Process multiple files.
    
    Args:
        file_paths: List of file paths to process
        overwrite: If True, overwrites existing filename comments
    """
    if not file_paths:
        print("No files specified.")
        return
    
    success_count = 0
    total_count = len(file_paths)
    
    for filepath in file_paths:
        if insert_filename_comment(filepath, overwrite):
            success_count += 1
    
    print(f"\nProcessed {success_count}/{total_count} files successfully.")

def process_directory(directory: str, recursive: bool = True, overwrite: bool = False) -> None:
    """
    Process all supported files in a directory.
    
    Args:
        directory: Directory path to process
        recursive: If True, process subdirectories recursively
        overwrite: If True, overwrites existing filename comments
    """
    dir_path = Path(directory)
    
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: '{directory}' is not a valid directory.")
        return
    
    # Collect all supported files
    files_to_process = []
    
    if recursive:
        for ext in COMMENT_STYLES.keys():
            files_to_process.extend(dir_path.rglob(f'*{ext}'))
    else:
        for ext in COMMENT_STYLES.keys():
            files_to_process.extend(dir_path.glob(f'*{ext}'))
    
    # Convert to string paths
    file_paths = [str(f) for f in files_to_process]
    
    if not file_paths:
        print(f"No supported files found in '{directory}'.")
        return
    
    print(f"Found {len(file_paths)} supported files in '{directory}'.")
    process_files(file_paths, overwrite)

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
  .kt - Kotlin
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
