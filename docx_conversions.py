import os
import subprocess
from markitdown import MarkItDown
import mammoth

def convert_docx_to_pdf_libreoffice(input_docx_path: str, output_pdf_path: str, verbose: bool = False):
    """
    Converts a DOCX file to PDF using LibreOffice in headless mode.
    Requires LibreOffice to be installed and accessible in the system's PATH.
    """
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_pdf_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Construct the LibreOffice command
        command = [
            "soffice",  # Command for LibreOffice
            "--headless",
            "--convert-to", "pdf",
            "--outdir", os.path.dirname(output_pdf_path) or ".", # Output directory
            input_docx_path
        ]
        
        # Execute the command
        subprocess.run(command, check=True)

        # LibreOffice names the output file based on the input filename in the --outdir
        # We need to rename it if a specific output_pdf_path was provided
        base_filename = os.path.basename(input_docx_path)
        output_filename_libreoffice = os.path.join(
            os.path.dirname(output_pdf_path) or ".", 
            os.path.splitext(base_filename)[0] + ".pdf"
        )

        # Rename the output file if necessary
        if output_filename_libreoffice != output_pdf_path:
            # Remove the existing output file if it exists
            if os.path.exists(output_pdf_path):
                os.remove(output_pdf_path)
            os.rename(output_filename_libreoffice, output_pdf_path)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error during conversion to PDF:\n{e}")
    except FileNotFoundError:
        raise Exception("SOffice command not found. Ensure LibreOffice is installed and in your PATH.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred during conversion to PDF:\n{e}")

def convert_docx_to_md(input_docx: str, output_md: str):
    """
    Converts a DOCX file to Markdown format.
    """
    try:
        md_converter = MarkItDown()
        # Convert the DOCX file to Markdown
        result = md_converter.convert(input_docx)
        # Write the result to the output file
        with open(output_md, "w", encoding="utf-8") as md_file:
            md_file.write(result.text_content)
    except Exception as e:
        raise Exception(f"Error occurred during conversion to Markdown:\n{e}")

def convert_docx_to_html(input_docx: str, output_html: str):
    """
    Converts a DOCX file to HTML format.
    """
    try:
        # Convert the DOCX file to HTML
        with open(input_docx, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value  # The generated HTML
            # Write the HTML to the output file
            with open(output_html, "w", encoding="utf-8") as html_file:
                html_file.write(html)
    except Exception as e:
        raise Exception(f"Error occurred during conversion to HTML:\n{e}")