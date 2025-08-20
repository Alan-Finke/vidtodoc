import httpx
import os
import shutil
import ssl
import whisper
from argparse import ArgumentParser
from docx.shared import Inches
from Handlers.output_handlers import get_output_handler
from Utilities.extract_frame import extract_frame_at_time
from openai import OpenAI

# Get --infile and --outfile arguments from command line
parser = ArgumentParser();
parser.add_argument('--infile', type=str, required=True, help='Path to the input video file');
parser.add_argument('--outfile', type=str, required=True, help='Path to the output file');
parser.add_argument('--verbose', type=bool, default=False, help='Enable verbose output');
args = parser.parse_args();

input_path:str = args.infile;
output_path:str = args.outfile;
verbose:bool = args.verbose;

# Check the output format
if output_path.lower().endswith(".pdf"):
    output_format = "pdf"
elif output_path.lower().endswith(".md"):
    output_format = "md"
elif output_path.lower().endswith(".html"):
    output_format = "html"
elif output_path.lower().endswith(".docx"):
    output_format = "docx"
elif output_path.lower().endswith(".doc"):
    output_format = "doc"
else:
    # Find the file extension
    ext = output_path.split(".")[-1]
    print(f"\nUnsupported output file format: {ext.upper()}.")
    print("Supported formats are: pdf, md, html, docx.\n");
    exit(1)

# Define constants
CURRENT_DIR = os.getcwd();
TEMPLATES_PATH = os.path.join(CURRENT_DIR, "templates")
API_KEY = os.getenv('OPEN_API_KEY')
BASE_URL = "https://aips-ai-gateway.ue1.dev.ai-platform.int.wexfabric.com/"

print(f"Verbose mode is {'on' if verbose else 'off'}");
if verbose:
    print(f"Current working directory: {CURRENT_DIR}");
    print(f"Input file path: {input_path}");
    print(f"Output file path: {output_path}");

# Best to do this at all times
# (especially when using self-signed certs)
ssl._create_default_https_context = ssl._create_stdlib_context;

# Parse the video file and transcribe it using Whisper
model = whisper.load_model("base")  # or "medium", "large"
result = model.transcribe(input_path, verbose=verbose)

# Get the full text transcription
full_text = result["text"];

# Initialize OpenAI client
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    http_client = httpx.Client(verify=False)
)

# Create the title for the document 
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

# Create the summary for the document
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

# Create the frames directory
base_name = os.path.basename(output_path)
base_path = os.path.dirname(output_path)
root_frames_dir = f"{base_name.split('.')[0]}_{base_name.split('.')[1]}"
frames_path = os.path.join(base_path, root_frames_dir, "frames")
# Remove frames directory if it exists
if os.path.exists(frames_path):
    shutil.rmtree(frames_path)
os.makedirs(frames_path, exist_ok=True)
if verbose:
    print(f"Created frames directory at: {frames_path}")

# Get the output handler for the specified format
output_handler = get_output_handler(output_format, TEMPLATES_PATH)

# Add the title, summary, and steps heading
output_handler.add_title(title)
output_handler.add_summary(summary)
output_handler.add_steps_heading()

counter = 1
# Extract frames and add steps
for segment in result["segments"]:
    if verbose:
        print(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}")
    try:
        frame_file = os.path.join(frames_path, f'frame_{counter}.jpg')
        extract_frame_at_time(input_path, frames_path, segment['start'], output_format, counter, verbose)
        output_handler.add_step(segment['text'], frame_file, counter, Inches(5.00))
        counter += 1
    except Exception as e:
        print(f"Error occurred while processing segment {counter}:\n{e}\n")

output_handler.save(output_path)
output_handler.postprocess(output_path)

print(f"\nDocument saved to: {output_path}\n");