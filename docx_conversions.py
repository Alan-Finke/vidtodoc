import os
import subprocess

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