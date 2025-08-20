import os
import cv2
import logging

def extract_frame_at_time(
    video_path: str,
    frames_dir: str,
    time_in_seconds: float,
    counter: int
) -> str:
    """
    Extracts a frame from a video at a specific timestamp.

    Args:
        video_path (str): Path to the input video file.
        frames_dir (str): Directory to save the extracted image.
        time_in_seconds (float): The time in seconds at which to extract the frame.
        output_format (str): The output format of the document.
        counter (int): The current segment counter.

    Returns:
        str: The path to the saved frame image.

    Raises:
        ValueError: If the frame could not be extracted.
    """
    # Create a VideoCapture object and set the position to the desired time
    vidcap = cv2.VideoCapture(video_path)
    vidcap.set(cv2.CAP_PROP_POS_MSEC, time_in_seconds * 1000)

    # Read the frame
    success, image = vidcap.read()

    if success:
        filename = os.path.join(frames_dir, f'frame_{counter}.jpg')
        # Save the extracted frame
        cv2.imwrite(filename, image)
        logging.debug(f"Frame extracted and saved to: {filename}")
        return filename
    else:
        raise ValueError(f"Could not extract frame at {time_in_seconds} seconds from {video_path}.")

    vidcap.release()
