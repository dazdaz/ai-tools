#!/usr/bin/env python3
"""
create_project.py - Creates project folder structure and files from a formatted text file
Typically generates folders and coopies content from output from the Claude Opus 4.1 LLM
Usage: python create_project.py <input_file> [output_directory]
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

class ProjectCreator:
    def __init__(self, input_file: str, output_dir: str = None):
        self.input_file = input_file
        self.output_dir = output_dir or "generated_project"
        self.current_file = None
        self.current_content = []
        self.files_created = 0
        self.dirs_created = set()
        
    def parse_input_file(self) -> Dict[str, str]:
        """Parse the input file and extract file paths with their content"""
        files_data = {}
        current_file = None
        current_content = []
        in_code_block = False
        code_block_lang = None
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: Input file '{self.input_file}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading input file: {e}")
            sys.exit(1)
        
        for line in lines:
            # Check for file path markers (bold text in markdown)
            file_match = re.match(r'\*\*([^*]+)\*\*', line.strip())
            
            if file_match:
                # Save previous file if exists
                if current_file and current_content:
                    files_data[current_file] = ''.join(current_content).strip()
                
                # Start new file
                current_file = file_match.group(1)
                current_content = []
                in_code_block = False
                code_block_lang = None
                
            # Check for code block markers
            elif line.strip().startswith('```'):
                if not in_code_block:
                    # Starting a code block
                    in_code_block = True
                    # Extract language if specified
                    lang_match = re.match(r'```(\w+)', line.strip())
                    if lang_match:
                        code_block_lang = lang_match.group(1)
                else:
                    # Ending a code block
                    in_code_block = False
                    code_block_lang = None
            
            # Collect content
            elif in_code_block and current_file:
                current_content.append(line)
        
        # Save last file if exists
        if current_file and current_content:
            files_data[current_file] = ''.join(current_content).strip()
        
        return files_data
    
    def create_directory_structure(self, file_path: str) -> str:
        """Create necessary directories for a file path"""
        full_path = os.path.join(self.output_dir, file_path)
        directory = os.path.dirname(full_path)
        
        if directory and directory not in self.dirs_created:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.dirs_created.add(directory)
            
        return full_path
    
    def write_file(self, file_path: str, content: str):
        """Write content to a file"""
        full_path = self.create_directory_structure(file_path)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
                # Add newline at end of file if not present
                if content and not content.endswith('\n'):
                    f.write('\n')
            
            self.files_created += 1
            print(f"‚úì Created: {file_path}")
            
        except Exception as e:
            print(f"‚úó Error creating {file_path}: {e}")
    
    def create_project(self):
        """Main method to create the project structure"""
        print(f"\n{'='*60}")
        print(f"Creating project from: {self.input_file}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*60}\n")
        
        # Parse input file
        files_data = self.parse_input_file()
        
        if not files_data:
            print("No files found in input file")
            return
        
        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create each file
        for file_path, content in files_data.items():
            self.write_file(file_path, content)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"‚úì Project creation complete!")
        print(f"  Files created: {self.files_created}")
        print(f"  Directories created: {len(self.dirs_created)}")
        print(f"  Location: {os.path.abspath(self.output_dir)}")
        print(f"{'='*60}\n")
        
        # Create a summary file
        self.create_summary()
    
    def create_summary(self):
        """Create a summary file with project statistics"""
        summary_path = os.path.join(self.output_dir, "PROJECT_SUMMARY.md")
        
        with open(summary_path, 'w') as f:
            f.write("# Project Summary\n\n")
            f.write(f"Generated from: {self.input_file}\n\n")
            f.write("## Statistics\n\n")
            f.write(f"- Total files created: {self.files_created}\n")
            f.write(f"- Total directories created: {len(self.dirs_created)}\n\n")
            f.write("## Directory Structure\n\n")
            f.write("```\n")
            f.write(self.generate_tree_structure())
            f.write("```\n")
    
    def generate_tree_structure(self, start_path: str = None) -> str:
        """Generate a tree structure of the created project"""
        if start_path is None:
            start_path = self.output_dir
        
        tree_lines = []
        
        def add_tree(path: str, prefix: str = ""):
            try:
                items = sorted(os.listdir(path))
                dirs = [item for item in items if os.path.isdir(os.path.join(path, item))]
                files = [item for item in items if os.path.isfile(os.path.join(path, item))]
                
                # Add directories first
                for i, dir_name in enumerate(dirs):
                    is_last_dir = (i == len(dirs) - 1) and len(files) == 0
                    tree_lines.append(f"{prefix}{'‚îî‚îÄ‚îÄ ' if is_last_dir else '‚îú‚îÄ‚îÄ '}{dir_name}/")
                    
                    new_prefix = prefix + ("    " if is_last_dir else "‚îÇ   ")
                    add_tree(os.path.join(path, dir_name), new_prefix)
                
                # Add files
                for i, file_name in enumerate(files):
                    is_last = i == len(files) - 1
                    tree_lines.append(f"{prefix}{'‚îî‚îÄ‚îÄ ' if is_last else '‚îú‚îÄ‚îÄ '}{file_name}")
                    
            except PermissionError:
                pass
        
        # Start with root directory name
        tree_lines.append(os.path.basename(start_path) + "/")
        add_tree(start_path, "")
        
        return "\n".join(tree_lines)

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python create_project.py <input_file> [output_directory]")
        print("\nExample:")
        print("  python create_project.py project_template.txt my_project")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    creator = ProjectCreator(input_file, output_dir)
    creator.create_project()

if __name__ == "__main__":
    main()
