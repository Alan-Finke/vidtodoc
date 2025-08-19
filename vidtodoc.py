import argparse
import httpx
import os
import shutil
import ssl
import whisper
from docx import Document 
from docx_conversions import convert_docx_to_pdf_libreoffice
from docx.shared import Inches
from extract_frame import extract_frame_at_time
from html_writer import HTMLWriter
from markdown_writer import MarkdownWriter
from openai import OpenAI

def perform_cleanup():
    """
    Perform any necessary cleanup actions after processing.
    """
    ### Clean up the output.docx file
    if output_format == "docx" or output_format == "pdf":
        if os.path.exists(output_file):
            os.remove(output_file)
        ### Clean up the temporary frame.jpg file
        if os.path.exists(frame_file):
            os.remove(frame_file)

    ### Clean up the pycache dir
    output_dir = os.path.dirname(output_path)
    pycache_dir = os.path.join(output_dir, "__pycache__")
    if os.path.exists(pycache_dir):
        shutil.rmtree(pycache_dir);

### Initialize OpenAI client
current_dir = os.getcwd();
apikey = os.getenv('OPEN_API_KEY')
BASE_URL = "https://aips-ai-gateway.ue1.dev.ai-platform.int.wexfabric.com/"

client = OpenAI(
    base_url=BASE_URL,
    api_key=apikey,
    http_client = httpx.Client(verify=False)
)

### Get --infile and --outfile arguments from command line
parser = argparse.ArgumentParser();
parser.add_argument('--infile', type=str, required=True, help='Path to the input video file');
parser.add_argument('--outfile', type=str, required=True, help='Path to the output file');
parser.add_argument('--verbose', type=bool, default=False, help='Enable verbose output');
args = parser.parse_args();

input_path:str = args.infile;
output_path:str = args.outfile;
verbose:bool = args.verbose;

### Check the output format
if output_path.lower().endswith(".pdf"):
    output_format = "pdf"
elif output_path.lower().endswith(".md"):
    output_format = "md"
elif output_path.lower().endswith(".html"):
    output_format = "html"
elif output_path.lower().endswith(".docx"):
    output_format = "docx"
else:
    ### Find the file extension
    ext = output_path.split(".")[-1]
    print(f"\nUnsupported output file format: {ext.upper()}.")
    print("Supported formats are: pdf, md, html, docx.\n");
    exit(1)

print(f"Verbose mode is {'on' if verbose else 'off'}");
if verbose:
    print(f"Current working directory: {current_dir}");
    print(f"Input file path: {input_path}");
    print(f"Output file path: {output_path}");

### Best to do this at all times
ssl._create_default_https_context = ssl._create_stdlib_context;

### Parse the video file and transcribe it using Whisper
model = whisper.load_model("base")  # or "medium", "large"
result = model.transcribe(input_path, verbose=verbose)

### Get the full text transcription
full_text = result["text"];

### Create the title for the document 
response =  client.chat.completions.create(model='azure-gpt-4o', messages = [
{
    'role' : 'system',
    'content' : 'You are a skilled technical writer.'
},
{
    'role' : 'user',
    'content' : 'create a title for the following text: ' + full_text
}])

title = response.choices[0].message.content

### Create the summary for the document
response =  client.chat.completions.create(model='azure-gpt-4o', messages = [
{
    'role' : 'system',
    'content' : 'You are a skilled technical writer.'
},
{
    'role' : 'user',
    'content' : 'create a summary for the following text: ' + full_text
}])

summary = response.choices[0].message.content 

if verbose:
    print(f"\nWriting {output_format.upper()} file...")

### Create the docx document
if output_format == "docx" or output_format == "pdf":
    document = Document();
    document.add_heading(title, level=1)
    document.add_heading("Summary", level=2)
    document.add_paragraph(summary);

### Create the HTML document
if output_format == "html":
    html_document = HTMLWriter(current_dir)
    html_document.add_title(title)
    html_document.add_summary(summary)

### If specified, create the Markdown document
if output_format == "md":
    md_document = MarkdownWriter()
    md_document.add_heading(title, level=1)
    md_document.add_heading("Summary", level=2)
    md_document.add_paragraph(summary)

### Create the frames directory
if output_format == "docx" or output_format == "pdf":
    frames_path = os.path.dirname(output_path)

elif output_format == "md" or output_format == "html":
    base_name = os.path.basename(output_path)
    base_path = os.path.dirname(output_path)
    root_frames_dir = f"{base_name.split('.')[0]}_{base_name.split('.')[1]}"
    frames_path = os.path.join(base_path, root_frames_dir, "frames")
    ### Remove frames directory if it exists
    if os.path.exists(frames_path):
        shutil.rmtree(frames_path)
    os.makedirs(frames_path, exist_ok=True)

### Add the Steps section
if output_format == "docx" or output_format == "pdf":
    document.add_heading("Steps", level=2)
elif output_format == "md":
    md_document.add_heading("Steps", level=2)

counter = 1
for segment in result["segments"]:
    if verbose:
        print(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}")
    try:
        # Extract a frame at the start of each segment
        extract_frame_at_time(input_path, frames_path, segment['start'], output_format, counter, verbose)

        if output_format == "docx" or output_format == "pdf":
            ### Add the text to the document
            document.add_paragraph(segment['text']);
            ### Add the frame to the document
            frame_file = os.path.join(frames_path, 'frame.jpg')
            document.add_picture(frame_file, width=Inches(5.00));  # Requires 'docx.shared.Inches'
        
        elif output_format == "md":
            ### Add the text to the Markdown document
            md_document.add_paragraph(segment['text']);
            ### Add the frame to the Markdown document
            frame_file = os.path.join(frames_path, f'frame_{counter}.jpg')
            md_document.add_image(frame_file, width=Inches(5.00), alt_text=f"Image {counter}");
        
        elif output_format == "html":
            frame_file = os.path.join(frames_path, f'frame_{counter}.jpg')
            ### Add the step to the HTML document
            html_document.add_step(counter, segment['text'], frame_file, alt_text=f"Image {counter}");

        if verbose:
            print(f"Added frame: {frame_file} to {output_format.upper()} document, step {counter}.\n")
        counter += 1
    except Exception as e:
        print(f"Error occurred while processing segment {counter}:\n{e}\n")

if output_format == "docx" or output_format == "pdf":
    ### Get the path without filename
    output_dir = os.path.dirname(output_path)
    output_file = os.path.join(output_dir, "output.docx")
    ### Save the output document
    document.save(output_file);

elif output_format == "md":
    ### If the md document already exists
    if os.path.exists(output_path):
        os.remove(output_path)
    ### Save the Markdown document
    md_document.save(output_path);

elif output_format == "html":
    ### If the html document already exists
    if os.path.exists(output_path):
        os.remove(output_path)
    ### Save the HTML document
    html_document.save(output_path);

### Check the format selected in output_format and perform conversion if needed
try:
    if output_format == "pdf":
        ### Convert the document to PDF
        convert_docx_to_pdf_libreoffice(output_file, output_path, verbose=verbose)
    
    elif output_format == "docx":
        ### If the output document already exists
        if os.path.exists(output_path):
            os.remove(output_path)
        ### Rename the output file already saved with the name the user specified
        os.rename(output_file, output_path);
except Exception as e:
    print(f"\nError occurred during conversion:\n{e}\n")

perform_cleanup()
print(f"\nDocument saved to: {output_path}\n");