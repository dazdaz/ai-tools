#!/usr/bin/env python3
# Filename: addcomment.py

"""
Script to insert a comment with the filename at the beginning of various file types.
Supports excluding specific directories and files.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Tuple, List, Set

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
    
    # Kotlin and Kotlin Script
    '.kt': ('// ', '', ''),
    '.kts': ('// ', '', ''), 
    
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
        
        # Check first few lines to handle cases with/without shebang
        check_range = lines[0:3] 
        found_existing = False
        existing_index = -1
        
        for idx, line in enumerate(lines):
            if idx > 2: break # Only check top of file
            if expected_comment_content in line:
                found_existing = True
                existing_index = idx
                break

        if found_existing:
            if not overwrite:
                print(f"Info: Filename comment already exists in '{filepath}'. Skipping.")
                return True
            else:
                # Remove the old comment line
                lines.pop(existing_index)
                # Reconstruct content without the old comment
                # Note: We need to be careful about the shebang which is handled separately below
                if shebang and existing_index == 0:
                     # Should not happen given shebang logic, but for safety
                     shebang = '' 
                
                # If we popped a line, we need to join the rest
                remaining_content = '\n'.join(lines[1:] if shebang else lines)

        # Construct new content
        if shebang:
            # Ensure we don't duplicate the shebang if it was in 'remaining_content'
            if remaining_content.startswith(shebang.strip()):
                remaining_content = remaining_content[len(shebang):]
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

def should_exclude(path: Path, exclude_dirs: Set[str], exclude_files: Set[str]) -> bool:
    """
    Check if a path should be excluded based on directory or filename.
    """
    # Check file exclusion
    if path.name in exclude_files:
        return True
    
    # Check directory exclusion
    # We check if any part of the path matches an excluded directory
    for part in path.parts:
        if part in exclude_dirs:
            return True
            
    return False

def process_files(file_paths: list, overwrite: bool = False) -> None:
    """
    Process multiple files.
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

def process_directory(directory: str, 
                     recursive: bool = True, 
                     overwrite: bool = False,
                     exclude_dirs: List[str] = None,
                     exclude_files: List[str] = None) -> None:
    """
    Process all supported files in a directory with exclusions.
    """
    dir_path = Path(directory)
    exclude_dirs_set = set(exclude_dirs) if exclude_dirs else set()
    exclude_files_set = set(exclude_files) if exclude_files else set()

    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: '{directory}' is not a valid directory.")
        return

    # Collect all supported files
    files_to_process = []

    if recursive:
        # Use rglob but filter manually to handle exclusions properly
        # Note: rglob('*') is more efficient than multiple rglob extensions
        for path in dir_path.rglob('*'):
            if path.is_file() and path.suffix.lower() in COMMENT_STYLES:
                if not should_exclude(path, exclude_dirs_set, exclude_files_set):
                    files_to_process.append(path)
    else:
        for path in dir_path.glob('*'):
            if path.is_file() and path.suffix.lower() in COMMENT_STYLES:
                if not should_exclude(path, exclude_dirs_set, exclude_files_set):
                    files_to_process.append(path)

    # Convert to string paths
    file_paths = [str(f) for f in files_to_process]

    if not file_paths:
        print(f"No supported files found in '{directory}' (after exclusions).")
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
  .py, .sh, .css, .js, .ts, .tsx, .jsx, 
  .kt, .kts, .dart, .html, .xml, .sql, 
  .rb, .yaml, .yml

Examples:
  %(prog)s -d ./src --recursive --exclude-dir node_modules
  %(prog)s -d . --exclude-file config.py secret.yaml
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
    
    # New arguments for exclusions
    parser.add_argument('--exclude-dir', action='append', default=[],
                       help='Directory names to exclude (can be used multiple times)')
    parser.add_argument('--exclude-file', action='append', default=[],
                       help='Filenames to exclude (can be used multiple times)')

    args = parser.parse_args()

    # Determine recursive setting
    recursive = True
    if args.no_recursive:
        recursive = False
    elif args.recursive:
        recursive = True

    # Process based on arguments
    if args.directory:
        process_directory(
            args.directory, 
            recursive, 
            args.overwrite,
            args.exclude_dir,
            args.exclude_file
        )
    elif args.files:
        # Filter explicitly provided files against exclusions too
        files_to_process = []
        exclude_dirs_set = set(args.exclude_dir)
        exclude_files_set = set(args.exclude_file)
        
        for f in args.files:
            if not should_exclude(Path(f), exclude_dirs_set, exclude_files_set):
                files_to_process.append(f)
            else:
                print(f"Skipping excluded file: {f}")
                
        process_files(files_to_process, args.overwrite)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
