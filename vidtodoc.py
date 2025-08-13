import argparse
import cv2 
import gdown
import httpx
import os
import ssl
import whisper
from docx import Document 
from docx.shared import Inches
from openai import AsyncOpenAI, DefaultAsyncHttpxClient , OpenAI 

def extract_frame_at_time(video_path, output_dir, time_in_seconds, verbose):
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
        #filename = f"{output_dir}/frame_at_{time_in_seconds}s.jpg"
        filename = f"{output_dir}/frame.jpg"
        cv2.imwrite(filename, image)
        if verbose:
            print(f"Frame extracted and saved to: {filename}")
    else:
        print(f"Could not extract frame at {time_in_seconds} seconds.")

    vidcap.release()


    
### Initialize OpenAI client
dir = os.getcwd();

apikey = os.getenv('OPEN_API_KEY')
### Debug
#print(f"Value of OPEN_API_KEY: {apikey}")

BASE_URL = "https://aips-ai-gateway.ue1.dev.ai-platform.int.wexfabric.com/"

client = OpenAI(
    base_url=BASE_URL,
    api_key=apikey,
    http_client = httpx.Client(verify=False)
)

""" response =  client.chat.completions.create(model='azure-gpt-4o', messages = [
{
    'role' : 'system',
    'content' : 'You are a skilled technical writer.'
},
{
    'role' : 'user',
    'content' : 'create a title for the following text:  Hello everybody, I am going to show you how to enroll a user in this thing here in MBE50 using Reclaim. So first log in, go to Update Enrollment, I have enrolled before, so I \'m changing my enrollment. Make sure Communication Information is correct. And then if I want to add dependence, I can do this here, but in this case, I\'m just going to simply enroll. So I\'m going to enroll here, get started, I\'m going to, my name is demo widget, my daughter in demo widget, so I\'m going to continue to enroll here. Waiting for this to load. Once it\'s loaded, it will ask you a series of questions for your those affordable team. If you have any special medical needs coming up, if you have special, you select them, preview screen. If you have a position you prefer, you can enter that here, and it will look for plans that support your position. Now finds a match and decides what is the best plan for me. And here, me decide the bronze plan was best. So I\'m going to continue with this, I\'m all set, and I can confirm my enrollments, and finish enrollments. Enrollment is complete. Thank you. I will stop recording now.'
}])
#print(response.model_dump_json(indent=4))
print(response.choices[0].message.content); """


""" cd = os.getcwd();
#print("It's ", cd);

apikey = os.getenv('OPEN_API_KEY')
#print(f"Value of MY_ENV_VAR: {apikey}") """

### Get --infile and --outfile arguments from command line
parser = argparse.ArgumentParser();
parser.add_argument('--infile', type=str, required=True, help='Path to the input video file');
parser.add_argument('--outfile', type=str, required=True, help='Path to the output file');
parser.add_argument('--verbose', type=bool, default=False, help='Enable verbose output');
args = parser.parse_args();

input_path:str = args.infile;
output_path:str = args.outfile;
verbose:bool = args.verbose;

print(f"Verbose mode is {'on' if verbose else 'off'}");
if verbose:
    print(f"Current working directory: {dir}");
    print(f"Input file path: {input_path}");
    print(f"Output file path: {output_path}");

### Check if input_path is a path to a shareable video from GDrive
if input_path.startswith("https://drive.google.com/"):
    """
    Download the video from GDrive to the local directory
    This requires that the video is publicly accessible
    This functionality has not been tested
    """
    output_dir = os.path.join(dir, "input.mp4");
    if verbose:
        print(f"Downloading video from GDrive to {output_dir}");
    try:
        gdown.download(input_path, output_dir, quiet=not verbose, fuzzy=True, verify=False);
        input_path = output_dir;
    except Exception as e:
        print(f"Error downloading video from GDrive, see below.\n{e}\n");
        exit(1);

    ### If download fails
    if not os.path.exists(input_path):
        print(f"Failed to download video file from GDrive.");
        exit(1);

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
#print(response.model_dump_json(indent=4))
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

### Create the document and add content
document = Document();
document.add_heading(title, level=1)

document.add_heading("Summary", level=2)
document.add_paragraph(summary);

### Add the Steps section
document.add_heading("Steps", level=2)
for segment in result["segments"]:
    if verbose:
        print(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}")
    # Extract a frame at the start of each segment
    extract_frame_at_time(input_path, dir, segment['start'], verbose);

    #Add the text to the document
    document.add_paragraph(segment['text']) ;

    # Add the frame to the document
    document.add_picture("frame.jpg", width=Inches(5.00));  # Requires 'docx.shared.Inches'


### Close and save the document
document.save(output_path);
### Clean up the temporary frame image
os.remove(f"{dir}/frame.jpg");
### Clean up the downloaded video file
if input_path.startswith("https://drive.google.com/"):
    os.remove(input_path);

'''
# Print segments with timestamps
for segment in result["segments"]:
    print(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}")

'''
#print(result["text"]);

'''
#extract_frame_at_time(file_path, cd, 21.040)

document = Document();

document.add_heading("Main Heading", level=1)
document.add_paragraph("This is the first paragraph of text.")


document.add_heading("Subheading", level=2)
document.add_paragraph("This is another paragraph.")

document.add_picture('frame_at_21.04s.jpg', width=Inches(5.00)) # Requires 'docx.shared.Inches'

document.save("my_new_document.docx")
'''

