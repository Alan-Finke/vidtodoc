import os
import cv2

def extract_frame_at_time(video_path, frames_dir, time_in_seconds, output_format, counter, verbose):
    """
    Extracts a frame from a video at a specific timestamp.

    Args:
        video_path (str): Path to the input video file.
        frames_dir (str): Directory to save the extracted image.
        time_in_seconds (float): The time in seconds at which to extract the frame.
        output_format (str): The output format of the document.
        counter (int): The current segment counter.
        verbose (bool): Whether to print verbose output.
    """
    # Initialize video capture
    vidcap = cv2.VideoCapture(video_path)

    # Set the position in milliseconds
    vidcap.set(cv2.CAP_PROP_POS_MSEC, time_in_seconds * 1000)

    # Read the frame
    success, image = vidcap.read()

    # Check if the frame was successfully extracted
    if success:
        filename = f"{os.path.join(frames_dir, f'frame_{counter}.jpg')}"
        # Save the extracted frame
        cv2.imwrite(filename, image)
        if verbose:
            print(f"Frame extracted and saved to: {filename}")
    else:
        raise ValueError(f"Could not extract frame at {time_in_seconds} seconds.")

    # Release the video capture object
    vidcap.release()
