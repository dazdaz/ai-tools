#!/bin/bash

# create_project.sh - Creates project folder structure and files from a formatted text file
# Used to create folders and copies content into those, created for use with Claude Opus 4.1 Opus LLM
# Usage: ./create_project.sh <input_file> [output_directory]

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
INPUT_FILE=""
OUTPUT_DIR="generated_project"
FILES_CREATED=0
DIRS_CREATED=0

# Function to print colored output
print_color() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Function to print usage
print_usage() {
    echo "Usage: $0 <input_file> [output_directory]"
    echo ""
    echo "Example:"
    echo "  $0 project_template.txt my_project"
    exit 1
}

# Function to create directory if it doesn't exist
create_directory() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        ((DIRS_CREATED++))
        print_color "$BLUE" "  üìÅ Created directory: $dir"
    fi
}

# Function to extract and create files
process_input_file() {
    local current_file=""
    local in_code_block=false
    local collecting_content=false
    local content_buffer=""
    
    # Create output directory
    create_directory "$OUTPUT_DIR"
    
    while IFS= read -r line; do
        # Check for file path (text between ** markers)
        if [[ "$line" =~ \*\*([^*]+)\*\* ]]; then
            # Save previous file if exists
            if [ -n "$current_file" ] && [ -n "$content_buffer" ]; then
                write_file "$current_file" "$content_buffer"
            fi
            
            # Extract new file path
            current_file="${BASH_REMATCH[1]}"
            content_buffer=""
            in_code_block=false
            collecting_content=false
            
            print_color "$YELLOW" "üìÑ Processing: $current_file"
            
        # Check for code block start
        elif [[ "$line" =~ ^\`\`\` ]]; then
            if [ "$in_code_block" = false ]; then
                in_code_block=true
                collecting_content=true
            else
                in_code_block=false
                collecting_content=false
            fi
            
        # Collect content
        elif [ "$in_code_block" = true ] && [ -n "$current_file" ]; then
            if [ -n "$content_buffer" ]; then
                content_buffer="$content_buffer"$'\n'"$line"
            else
                content_buffer="$line"
            fi
        fi
        
    done < "$INPUT_FILE"
    
    # Save last file if exists
    if [ -n "$current_file" ] && [ -n "$content_buffer" ]; then
        write_file "$current_file" "$content_buffer"
    fi
}

# Function to write content to file
write_file() {
    local file_path=$1
    local content=$2
    local full_path="$OUTPUT_DIR/$file_path"
    local dir_path=$(dirname "$full_path")
    
    # Create directory structure
    create_directory "$dir_path"
    
    # Write content to file
    echo "$content" > "$full_path"
    
    if [ $? -eq 0 ]; then
        ((FILES_CREATED++))
        print_color "$GREEN" "  ‚úì Created: $file_path"
    else
        print_color "$RED" "  ‚úó Error creating: $file_path"
    fi
}

# Function to generate tree structure
generate_tree() {
    local dir=${1:-$OUTPUT_DIR}
    local indent="${2:-}"
    local is_last="${3:-false}"
    
    local items=($(ls -A "$dir" 2>/dev/null | sort))
    local item_count=${#items[@]}
    
    for i in "${!items[@]}"; do
        local item="${items[$i]}"
        local path="$dir/$item"
        local is_last_item=false
        
        if [ $((i + 1)) -eq $item_count ]; then
            is_last_item=true
        fi
        
        # Print item
        if [ "$is_last_item" = true ]; then
            echo "${indent}‚îî‚îÄ‚îÄ $item"
            local new_indent="${indent}    "
        else
            echo "${indent}‚îú‚îÄ‚îÄ $item"
            local new_indent="${indent}‚îÇ   "
        fi
        
        # Recurse if directory
        if [ -d "$path" ]; then
            generate_tree "$path" "$new_indent" "$is_last_item"
        fi
    done
}

# Function to create summary file
create_summary() {
    local summary_file="$OUTPUT_DIR/PROJECT_SUMMARY.md"
    
    {
        echo "# Project Summary"
        echo ""
        echo "Generated from: $INPUT_FILE"
        echo "Generated on: $(date)"
        echo ""
        echo "## Statistics"
        echo ""
        echo "- Total files created: $FILES_CREATED"
        echo "- Total directories created: $DIRS_CREATED"
        echo ""
        echo "## Directory Structure"
        echo ""
        echo '```'
        echo "$(basename "$OUTPUT_DIR")/"
        generate_tree "$OUTPUT_DIR"
        echo '```'
    } > "$summary_file"
    
    print_color "$GREEN" "  ‚úì Created summary: PROJECT_SUMMARY.md"
}

# Main execution
main() {
    # Check arguments
    if [ $# -lt 1 ]; then
        print_usage
    fi
    
    INPUT_FILE="$1"
    
    # Check if input file exists
    if [ ! -f "$INPUT_FILE" ]; then
        print_color "$RED" "Error: Input file '$INPUT_FILE' not found"
        exit 1
    fi
    
    # Set output directory if provided
    if [ $# -ge 2 ]; then
        OUTPUT_DIR="$2"
    fi
    
    # Print header
    echo ""
    print_color "$BLUE" "============================================================"
    print_color "$BLUE" "Creating project from: $INPUT_FILE"
    print_color "$BLUE" "Output directory: $OUTPUT_DIR"
    print_color "$BLUE" "============================================================"
    echo ""
    
    # Process the input file
    process_input_file
    
    # Create summary
    create_summary
    
    # Print summary
    echo ""
    print_color "$GREEN" "============================================================"
    print_color "$GREEN" "‚úì Project creation complete!"
    print_color "$GREEN" "  Files created: $FILES_CREATED"
    print_color "$GREEN" "  Directories created: $DIRS_CREATED"
    print_color "$GREEN" "  Location: $(realpath "$OUTPUT_DIR")"
    print_color "$GREEN" "============================================================"
    echo ""
}

# Run main function
main "$@"
