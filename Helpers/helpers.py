import json
import httpx
import logging
import os
import shutil
import whisper
from argparse import ArgumentParser
from docx.shared import Inches
from openai import OpenAI
from Utilities.extract_frame import extract_frame_at_time

def load_config(config_path="config.json"):
    """Loads the configuration from a JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)
    
def setup_logging(verbose: bool):
    """Sets up logging configuration based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create a StreamHandler for console output
    console_handler = logging.StreamHandler()
    
    # Create a Formatter with an empty format string
    # This ensures no message content, level, or timestamp is printed
    blank_formatter = logging.Formatter(fmt='')
    
    # Set the custom formatter for the handler
    console_handler.setFormatter(blank_formatter)

    # Ensure the root logger is configured to use the custom handler
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().setLevel(level)

def parse_args():
    """Parses command-line arguments."""
    parser = ArgumentParser()
    parser.add_argument('--infile', type=str, required=True, help='Path to the input video file')
    parser.add_argument('--outfile', type=str, required=True, help='Path to the output file')
    parser.add_argument('--verbose', type=bool, default=False, help='Enable verbose output')

    # Check if the input file exists
    args = parser.parse_args()
    if not os.path.exists(args.infile):
        raise FileNotFoundError(f"Input file '{args.infile}' does not exist.")

    return args

def get_output_format(output_path: str) -> str:
    """Determines the output format based on the file extension."""
    ext = output_path.lower().split('.')[-1]
    formats = {'pdf', 'md', 'html', 'docx', 'doc'}
    if ext in formats:
        return ext
    raise ValueError(f"Unsupported output file format: {ext.upper()}.\nSupported formats: {', '.join(formats)}\n")

def prepare_frames_dir(output_path: str) -> str:
    """Prepares the frames directory for extracted video frames."""
    base_name = os.path.basename(output_path)
    base_path = os.path.dirname(output_path)
    root_frames_dir = f"{base_name.split('.')[0]}_{base_name.split('.')[1]}"
    frames_path = os.path.join(base_path, root_frames_dir, "frames")
    if os.path.exists(frames_path):
        shutil.rmtree(frames_path)
    os.makedirs(frames_path, exist_ok=True)
    logging.debug(f"Created frames directory at: {frames_path}")
    return frames_path

def transcribe_video(input_path: str, verbose: bool):
    """
    Transcribes the audio from the video file.
    """
    model = whisper.load_model("base")
    return model.transcribe(
        input_path, 
        verbose=verbose,
        word_timestamps=True,
        hallucination_silence_threshold=0.5  # Skip silent periods longer than 0.5 seconds if hallucination is suspected
    )

def get_openai_client(api_key: str, base_url: str):
    """
    Creates an OpenAI client instance.
    """
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        http_client=httpx.Client(verify=False)
    )

def get_title_and_summary(client, full_text: str):
    """
    Gets the title and summary for the given text using the OpenAI client.
    """
    def ask(prompt):
        response = client.chat.completions.create(
            model='azure-gpt-4o',
            messages=[
                {'role': 'system', 'content': 'You are a skilled technical writer.'},
                {'role': 'user', 'content': prompt + full_text}
            ]
        )
        return response.choices[0].message.content
    title = ask('create a title for the following text: ')
    summary = ask('create a summary for the following text: ')
    return title, summary

def process_segments(result, input_path, frames_path, output_handler):
    """
    Processes the video segments and updates the output handler.
    """
    counter = 1
    for segment in result["segments"]:
        logging.debug(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}")
        try:
            frame_file = os.path.join(frames_path, f'frame_{counter}.jpg')
            extract_frame_at_time(input_path, frames_path, segment['start'], counter)
            output_handler.add_step(segment['text'], frame_file, counter, Inches(5.00))
            counter += 1
        except Exception as e:
            raise ValueError(f"Error occurred while processing segment {counter}: {e}")