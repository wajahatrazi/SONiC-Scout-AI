import os
import markdown
from weasyprint import HTML

def md_to_pdf(md_file, output_pdf):
    """Convert a single markdown file to PDF."""
    # Read the markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(md_content)

    # Convert HTML to PDF using WeasyPrint
    HTML(string=html_content).write_pdf(output_pdf)

    print(f"Successfully converted {md_file} to {output_pdf}")

def convert_md_files_in_folder(folder_path):
    """Convert all markdown files in the given folder to PDFs."""
    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is a markdown file (.md)
        if filename.endswith('.md'):
            md_file = os.path.join(folder_path, filename)
            output_pdf = os.path.join(folder_path, filename.replace('.md', '.pdf'))
            md_to_pdf(md_file, output_pdf)

# Example Usage
folder_path = "/home/rida/Videos/SonicHackathon"  # Replace with the path to your folder
convert_md_files_in_folder(folder_path)
