import whisper
import ssl
import os
import cv2 
from docx import Document 
from docx.shared import Inches
from openai import AsyncOpenAI, DefaultAsyncHttpxClient , OpenAI 

def extract_frame_at_time(video_path, output_dir, time_in_seconds):
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
        print(f"Frame extracted and saved to: {filename}")
    else:
        print(f"Could not extract frame at {time_in_seconds} seconds.")

    vidcap.release()


""" async def getClientListAsync():
    BASE_URL = "https://aips-ai-gateway.ue1.dev.ai-platform.int.wexfabric.com/"

    client = await AsyncOpenAI(
        base_url=BASE_URL,api_key=apikey,
        # This http_client with verify=False is used to avoid SSL errors during local development. Remove this in production environments.
        http_client=DefaultAsyncHttpxClient(
            verify=False
        )
    )
    res =  client.models.list()
    print(res.model_dump_json(indent=4)) """

    
### Initialize OpenAI client
dir = os.getcwd();
#print("It's ", cd);

apikey = os.getenv('OPEN_API_KEY')
#print(f"Value of MY_ENV_VAR: {apikey}")
BASE_URL = "https://aips-ai-gateway.ue1.dev.ai-platform.int.wexfabric.com/"

client = OpenAI(
    base_url=BASE_URL,api_key=apikey
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

file_path = "ReclaimDemo.mp4";

""" if os.path.exists(file_path):
    print(f"The file '{file_path}' exists.")
else:
    print(f"The file '{file_path}' does not exist.") """


#ssl._create_default_https_context = ssl._create_stdlib_context - needed this the first time I ran this code, but not needed now

### Parse the video file and transcribe it using Whisper
model = whisper.load_model("base")  # or "medium", "large"
result = model.transcribe(file_path, verbose=True)

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
    print(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}")
    # Extract a frame at the start of each segment
    extract_frame_at_time(file_path, dir, segment['start']);

    #Add the text to the document
    document.add_paragraph(segment['text']) ;

    # Add the frame to the document
    document.add_picture("frame.jpg", width=Inches(5.00));  # Requires 'docx.shared.Inches'


### Close and save the document
document.save("MyVideo.docx");


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

