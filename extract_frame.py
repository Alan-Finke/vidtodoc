import cv2 

def extract_frame(video_path, output_dir, time_in_seconds, name="frame.jpg"):
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
        filename = f"{output_dir}/{name}"
        cv2.imwrite(filename, image)
        print(f"Frame extracted and saved to: {filename}")
    else:
        print(f"Could not extract frame at {time_in_seconds} seconds.")

    vidcap.release()