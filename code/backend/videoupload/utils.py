import logging
import os

from moviepy.editor import VideoFileClip, AudioFileClip


def extract_audio_from_video(file_path: str, audio_file_name: str = "audio.wav") -> str:
    """Copy file from source blob storage container async to sink blob storage container.

    file_path (str): The file path of the video from which the audio should be extracted.
    audio_file_name (str): The file name of the audio file.
    RETURNS (str): Returns the file path of the audio file path.
    """
    logging.info(f"Extracting audio from the following video file '{file_path}'.")

    # Load video file
    logging.debug(f"Loading video file '{file_path}'")
    video = VideoFileClip(
        filename=file_path,
        has_mask=False,
        audio=True,
    )

    # Define audio file path
    file_path_head_tail = os.path.split(file_path)
    audio_file_path = os.path.join(file_path_head_tail[0], audio_file_name)
    logging.debug(f"Audio file path '{audio_file_path}'")

    # Extract audio
    audio = video.audio
    audio.write_audiofile(audio_file_path) #, nbytes=2, codec="pcm_s16le", bitrate="16k", ffmpeg_params=["-ac", "1"])
    return audio_file_path
