import subprocess
import logging
import os

def convert_docx_to_pdf_libreoffice(docx_path: str, pdf_path: str, verbose: bool = False) -> None:
    """
    Converts a DOCX file to PDF using LibreOffice.

    Args:
        docx_path (str): Path to the DOCX file.
        pdf_path (str): Desired output PDF file path.

    Raises:
        RuntimeError: If conversion fails.
    """
    try:
        # LibreOffice outputs to the directory, so get the directory and filename
        output_dir = os.path.dirname(pdf_path)
        cmd = [
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            docx_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        # Move the generated PDF to the desired path if needed
        generated_pdf = os.path.join(output_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
        if generated_pdf != pdf_path:
            os.replace(generated_pdf, pdf_path)
        if verbose:
            logging.info(f"Converted {docx_path} to {pdf_path} using LibreOffice.")
    except Exception as e:
        raise RuntimeError(f"LibreOffice conversion failed: {e}")
    except FileNotFoundError:
        raise FileNotFoundError("SOffice command not found. Ensure LibreOffice is installed and in your PATH.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during conversion to PDF:\n{e}")