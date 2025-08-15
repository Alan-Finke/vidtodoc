import argparse
import shutil
import cv2 
import httpx
import os
import ssl
import whisper
import markdown_writer
from docx_conversions import convert_docx_to_pdf_libreoffice, convert_docx_to_md, convert_docx_to_html
from docx import Document 
from docx.shared import Inches
from openai import AsyncOpenAI, DefaultAsyncHttpxClient , OpenAI

def extract_frame_at_time(video_path, output_dir, frames_dir, time_in_seconds, counter, verbose):
    """
    Extracts a frame from a video at a specific timestamp.

    Args:
        video_path (str): Path to the input video file.
        output_dir (str): Directory to save the extracted image.
        time_in_seconds (float): The time in seconds at which to extract the frame.
    """
    vidcap = cv2.VideoCapture(video_path)

    # Set the position in milliseconds
    vidcap.set(cv2.CAP_PROP_POS_MSEC, time_in_seconds * 1000)

    success, image = vidcap.read()

    if success:
        filename = f"{frames_dir}/frame_{counter}.jpg"
        cv2.imwrite(filename, image)
        if verbose:
            print(f"Frame extracted and saved to: {filename}")
    else:
        print(f"Could not extract frame at {time_in_seconds} seconds.")

    vidcap.release()

def perform_cleanup():
    """
    Perform any necessary cleanup actions after processing.
    """
    ### Clean up the temporary frame directory
    if output_format == "docx" or output_format == "pdf":
        head_tail = os.path.split(frames_path)
        if os.path.exists(head_tail[0]):
            shutil.rmtree(head_tail[0])

    ### Clean up the output.docx file
    if os.path.exists(output_file):
        os.remove(output_file)
    
    ### Clean up the pycache dir
    pycache_dir = os.path.join(output_dir, "__pycache__")
    if os.path.exists(pycache_dir):
        shutil.rmtree(pycache_dir);

### Initialize OpenAI client
dir = os.getcwd();
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
    print(f"Current working directory: {dir}");
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

### Create the docx document
document = Document();
document.add_heading(title, level=1)
document.add_heading("Summary", level=2)
document.add_paragraph(summary);

### If specified, create the Markdown document
if output_format == "md":
    md_document = markdown_writer.MarkdownWriter(output_path)
    md_document.add_heading(title, level=1)
    md_document.add_heading("Summary", level=2)
    md_document.add_paragraph(summary)

### We will create the frames directory, regardless of the specified file format
base_name = os.path.basename(output_path)
base_path = os.path.dirname(output_path)
root_frames_dir = f"{base_name.split('.')[0]}_{base_name.split('.')[1]}"
frames_path = os.path.join(base_path, root_frames_dir, "frames")

### Remove previously-used frames directory
if os.path.exists(frames_path):
    shutil.rmtree(frames_path)

### Create the frames directory
os.makedirs(frames_path, exist_ok=True)

### Add the Steps section
document.add_heading("Steps", level=2)
if output_format == "md":
    md_document.add_heading("Steps", level=2)

counter = 1
for segment in result["segments"]:
    if verbose:
        print(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}")
    # Extract a frame at the start of each segment
    extract_frame_at_time(input_path, dir, frames_path, segment['start'], counter, verbose)

    ### Add the text to the document
    document.add_paragraph(segment['text']);
    if output_format == "md":
        md_document.add_paragraph(segment['text']);

    ### Add the frame to the document
    document.add_picture(f"{frames_path}\\frame_{counter}.jpg", width=Inches(5.00));  # Requires 'docx.shared.Inches'
    if output_format == "md":
        md_document.add_image(f"{frames_path}\\frame_{counter}.jpg", width=Inches(5.00), alt_text=f"Image {counter}");

    if verbose:
        print(f"Added frame: {frames_path}\\frame_{counter}.jpg")
    
    counter += 1

### Get the path without filename
output_dir = os.path.dirname(output_path)
output_file = os.path.join(output_dir, "output.docx")

### Save the output document
document.save(output_file);

### If specified, save the Markdown document
if output_format == "md":
    ### If the md document already exists
    if os.path.exists(output_path):
        os.remove(output_path)
    md_document.save();

### Check the format selected in output_format and perform conversion if needed
try:
    if output_format == "pdf":
        ### Convert the document to PDF
        convert_docx_to_pdf_libreoffice(output_file, output_path, verbose=verbose)
    elif output_format == "html":
        ### Convert the document to HTML
        convert_docx_to_html(output_file, output_path)
    elif output_format == "docx":
        ### If the output document already exists
        if os.path.exists(output_path):
            os.remove(output_path)
        ### Rename the output file already saved with the name the user specified
        os.rename(output_file, output_path);
except Exception as e:
    print(f"\nError occurred during conversion:\n{e}\n")
finally:
    perform_cleanup()

print(f"\nDocument saved to: {output_path}\n");