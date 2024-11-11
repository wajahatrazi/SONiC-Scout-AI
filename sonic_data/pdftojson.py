import os
import json
import markdown
import fitz  # PyMuPDF for PDF handling

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to extract text from a Markdown file
def extract_text_from_md(md_path):
    with open(md_path, 'r', encoding='utf-8') as file:
        md_content = file.read()
    html = markdown.markdown(md_content)  # You can optionally keep HTML, or just plain text
    return html  # Return HTML format (or you could strip HTML if you want plain text)

# Function to extract text from a plain text file
def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to convert files in a directory to JSON format
def convert_files_to_json(directory):
    json_data = []
    
    # Loop through all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        if os.path.isfile(file_path):
            file_extension = filename.split('.')[-1].lower()

            file_data = {
                'filename': filename,
                'content': ''
            }

            # Check file type and process accordingly
            if file_extension == 'pdf':
                file_data['content'] = extract_text_from_pdf(file_path)
            elif file_extension == 'md':
                file_data['content'] = extract_text_from_md(file_path)
            elif file_extension == 'txt':
                file_data['content'] = extract_text_from_txt(file_path)
            else:
                continue  # Skip unsupported file types

            # Append the extracted data as JSON
            json_data.append(file_data)

    # Write the resulting JSON data to a file
    with open('output_files.json', 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    print("Conversion complete. JSON output saved to 'output_files.json'.")

# Example usage
directory_path = '/home/rida/Music/hackathon-pdf'  # Change this to your directory path
convert_files_to_json(directory_path)
