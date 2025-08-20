import logging
import os
import ssl
from Handlers.output_handlers import get_output_handler
from Utilities.helpers import (
    load_config,
    parse_args,
    setup_logging,
    get_output_format,
    prepare_frames_dir,
    process_segments,
    transcribe_video,
    get_openai_client,
    get_title_and_summary
)

def main():
    """
    Main entry point for the video to document conversion.
    """
    
    # Parse command-line arguments
    args = parse_args()
    
    setup_logging(args.verbose)
    
    logging.info(f"Verbose mode is {'on' if args.verbose else 'off'}")
    logging.debug(f"Current working directory: {os.getcwd()}")
    logging.debug(f"Input file path: {args.infile}")
    logging.debug(f"Output file path: {args.outfile}")

    # Create SSL context
    ssl._create_default_https_context = ssl._create_stdlib_context

    # Load config
    config = load_config()
    BASE_URL = config.get("base_url")
    
    # Set up constants
    OUTPUT_FORMAT = get_output_format(args.outfile)
    TEMPLATES_PATH = os.path.join(os.getcwd(), "templates")
    API_KEY = os.getenv('OPEN_API_KEY')
    
    # Transcribe video
    result = transcribe_video(args.infile, args.verbose)
    full_text = result["text"]

    # Get OpenAI client
    client = get_openai_client(API_KEY, BASE_URL)
    
    title, summary = get_title_and_summary(client, full_text)

    logging.debug(f"Writing {OUTPUT_FORMAT.upper()} file...")

    # Prepare frames directory and output handler
    frames_path = prepare_frames_dir(args.outfile)
    output_handler = get_output_handler(OUTPUT_FORMAT, TEMPLATES_PATH)

    output_handler.add_title(title)
    output_handler.add_summary(summary)
    output_handler.add_steps_heading()

    # Process video segments
    process_segments(result, args.infile, frames_path, output_handler, OUTPUT_FORMAT, args.verbose)

    output_handler.save(args.outfile)
    output_handler.postprocess(args.outfile)

    logging.info('')
    logging.info(f"Document saved to: {args.outfile}\n")

if __name__ == "__main__":
    main()