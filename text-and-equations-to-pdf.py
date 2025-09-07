#!/usr/bin/env python3

import argparse
import re
import subprocess
import os
import shutil
from datetime import datetime

def generate_latex_from_markdown(content_lines):
    """
    Converts a list of markdown-formatted lines into a full LaTeX document string.
    """
    # LaTeX preamble with necessary packages for formatting and math
    latex_preamble = r"""
\documentclass[12pt, a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{geometry}
\usepackage{booktabs} % For professional tables
\usepackage{hyperref}

\geometry{a4paper, margin=1in}
\setlength{\parskip}{0.5em} % A bit of space between paragraphs
\setlength{\parindent}{0pt} % No indent for paragraphs

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=cyan,
}

\begin{document}
"""
    latex_body = ""
    lines = iter(content_lines)
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        # Headings
        if stripped_line.startswith('### '):
            latex_body += f"\\subsection*{{{stripped_line[4:]}}}\n"
        elif stripped_line.startswith('## '):
            latex_body += f"\\section*{{{stripped_line[3:]}}}\n"
        elif stripped_line.startswith('# '):
            latex_body += f"\\section*{{{stripped_line[2:]}}}\n"
        
        # Tables (Pipe-delimited markdown format)
        elif stripped_line.startswith('|') and stripped_line.endswith('|'):
            table_lines = [stripped_line]
            # Peek at the next line to check for table separator
            try:
                # This logic is a bit complex to handle consuming lines from the iterator
                next_line = next(lines)
                if next_line.strip().startswith('|') and '---' in next_line:
                    # This is a table, consume all table lines
                    table_lines.append(next_line) # Add separator line
                    while True:
                        next_line = next(lines)
                        if next_line.strip().startswith('|'):
                            table_lines.append(next_line)
                        else:
                            # This line is not part of the table, process it as regular text
                            latex_body += f"{next_line.strip()} "
                            break # Exit the table-reading loop
                else:
                    # Not a table, process the original line and the line we peeked at
                    latex_body += f"{stripped_line} \n"
                    latex_body += f"{next_line.strip()} "
                    continue # Skip table processing
            except StopIteration:
                # End of file, not a table
                latex_body += f"{stripped_line} \n"
                continue

            # Process the collected table lines
            header = [h.strip() for h in table_lines[0].split('|')[1:-1]]
            num_cols = len(header)
            # Use left-alignment for all columns as a simple default
            col_spec = '{' + 'l' * num_cols + '}'
            
            latex_body += f"\\begin{{tabular}}{col_spec}\n"
            latex_body += "\\toprule\n"
            latex_body += " & ".join([f"\\textbf{{{h}}}" for h in header]) + " \\\\\n"
            latex_body += "\\midrule\n"
            
            # Process data rows (skip the separator line at index 1)
            for row_line in table_lines[2:]:
                cells = [c.strip() for c in row_line.split('|')[1:-1]]
                latex_body += " & ".join(cells) + " \\\\\n"
            
            latex_body += "\\bottomrule\n"
            latex_body += "\\end{tabular}\n\n"

        # Numbered lists (simple format: "1. Text")
        elif re.match(r'^\d+\.\s', stripped_line):
            item_text = re.sub(r'^\d+\.\s', '', stripped_line)
            # Escape special LaTeX characters that might be in the item text
            item_text = item_text.replace('&', '\\&').replace('%', '\\%').replace('#', '\\#').replace('_', '\\_')
            # Handle bold markdown **text** -> \textbf{text}
            item_text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', item_text)
            latex_body += f"\\begin{{itemize}}\\item {item_text}\\end{{itemize}}\n"
        
        # Regular text paragraphs
        else:
            # Escape special LaTeX characters
            processed_line = line.replace('&', '\\&').replace('%', '\\%').replace('#', '\\#').replace('_', '\\_')
            # Handle bold markdown **text** -> \textbf{text}
            processed_line = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', processed_line)
            latex_body += f"{processed_line.strip()} "
    
    latex_end = "\n\\end{document}\n"
    return latex_preamble + latex_body + latex_end

def create_pdf_via_latex(content_lines, output_filename):
    """
    Generates a PDF by converting markdown to LaTeX and compiling it.
    """
    print("Converting input text to LaTeX...")
    latex_content = generate_latex_from_markdown(content_lines)

    base_name = os.path.splitext(output_filename)[0]
    tex_filename = f"{base_name}.tex"
    pdf_filename = f"{base_name}.pdf"

    with open(tex_filename, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"LaTeX file '{tex_filename}' created. Compiling to PDF...")
    
    compiler = 'latexmk'
    if not shutil.which(compiler):
        print("Warning: 'latexmk' not found. Falling back to 'pdflatex'.")
        compiler = 'pdflatex'

    try:
        if compiler == 'latexmk':
            command = ['latexmk', '-pdf', '-interaction=nonstopmode', tex_filename]
        else: # pdflatex
            command = ['pdflatex', '-interaction=nonstopmode', tex_filename]

        # --- KEY CHANGE IS HERE ---
        # We removed 'capture_output=True'. This streams the compiler's
        # output directly to your terminal, preventing deadlocks and
        # showing you the live progress.
        process = subprocess.run(command, check=True)
        # --- END OF CHANGE ---

        print("PDF compilation successful.")
        
        if os.path.basename(pdf_filename) != os.path.basename(output_filename):
            shutil.move(pdf_filename, output_filename)
        
        print(f"Successfully created '{output_filename}'")

    except FileNotFoundError:
        print(f"Error: '{compiler}' command not found.")
        print("Please ensure a LaTeX distribution is installed and in your system's PATH.")
        return
    except subprocess.CalledProcessError as e:
        print(f"\n--- Error during PDF compilation with '{compiler}'. ---")
        print("The compiler exited with an error. Check the output above for details.")
        log_filename = f"{base_name}.log"
        if os.path.exists(log_filename):
             print(f"For more details, please review the log file: '{log_filename}'")
        return
    finally:
        # Clean up auxiliary files
        print("Cleaning up temporary files...")
        if compiler == 'latexmk':
            subprocess.run(['latexmk', '-c', tex_filename], capture_output=True)
        else:
            extensions_to_clean = ['.tex', '.aux', '.log', '.out']
            for ext in extensions_to_clean:
                try:
                    if os.path.exists(base_name + ext):
                        os.remove(base_name + ext)
                except OSError as e:
                    print(f"Warning: Could not remove temporary file {base_name + ext}: {e}")

def read_content_from_file(file_path):
    """
    Reads content from a text file, returning a list of lines.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{file_path}' not found.")
        return []

def main():
    parser = argparse.ArgumentParser(
        description="Convert a Markdown file with LaTeX equations into a high-quality PDF.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--input-file',
        required=True,
        help="Path to the input text/markdown file."
    )
    parser.add_argument(
        '--output',
        default="output.pdf",
        help="Output filename for the PDF (default: output.pdf)."
    )
    parser.epilog = (
        "Example usage:\n"
        "  python3 your_script_name.py --input-file report.txt --output report.pdf\n\n"
        "Input Format:\n"
        "- Use Markdown for headings (##), bold (**text**), etc.\n"
        "- Use LaTeX for math: $...$ for inline and $$...$$ for display.\n"
        "- Create tables using Markdown's pipe `|` syntax.\n\n"
        "**Requirement**: A full LaTeX distribution (e.g., TeX Live, MiKTeX) must be installed."
    )
    args = parser.parse_args()
    
    content_lines = read_content_from_file(args.input_file)
    if not content_lines:
        return
    
    create_pdf_via_latex(content_lines, args.output)

if __name__ == "__main__":
    main()
