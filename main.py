from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
from moviepy.editor import VideoFileClip, concatenate_videoclips
from numpy import argmax
from librosa import get_duration, load as librosa_load
from scipy.signal import correlate
import os

from dataclasses import dataclass


@dataclass
class VideoParser:
    video_file_path: str
    opening_path: str
    ending_path: str

    VIDEO_BITRATE = "300k"

    def __post_init__(self):
        self.extracted_audio_file_path = f"{self.video_file_path}_tmp.mp3"

    def extract_audio_file(self):
        # TODO Temporary solution - need to extract sound without creating .mp3 file
        ffmpeg_extract_audio(self.video_file_path, self.extracted_audio_file_path)

    def calculate_audio_offset(self, filename, y_movie, sampling_rate_movie):
        audio_sample, audio_sampling_rate = librosa_load(filename, sr=sampling_rate_movie)
        correlation = correlate(y_movie, audio_sample, mode='valid', method='fft')
        audio_starting_time = argmax(correlation) / sampling_rate_movie
        duration = get_duration(audio_sample, audio_sampling_rate)
        return float(round(audio_starting_time, 2)), float(round(audio_starting_time + duration, 2))

    def calculate_offsets(self):
        opening_offset, ending_offset = None, None
        y_movie, sampling_rate_movie = librosa_load(self.extracted_audio_file_path, sr=None)

        if self.opening_path:
            opening_offset = self.calculate_audio_offset(self.opening_path, y_movie, sampling_rate_movie)
        if self.ending_path:
            ending_offset = self.calculate_audio_offset(self.ending_path, y_movie, sampling_rate_movie)
        return opening_offset, ending_offset

    def calculate_subtimes(self, opening_offset, ending_offset):
        subtimes = []
        if opening_offset:
            subtimes.extend(((0, opening_offset[0]), opening_offset[1]))
        if ending_offset:
            subtimes.extend(((subtimes.pop(), ending_offset[0]), ending_offset[1]))
        return subtimes

    def write_video_file(self, opening_offset, ending_offset):
        # TODO Error with get_frame for cutted video
        subtimes = self.calculate_subtimes(opening_offset, ending_offset)
        with VideoFileClip(self.video_file_path) as video:
            subclips = []
            for subtime in subtimes:
                if isinstance(subtime, tuple):
                    subclips.append(video.subclip(*subtime))
                else:
                    subclips.append(video.subclip(subtime))
            final_video = concatenate_videoclips(subclips)
            final_video.write_videofile(f"NEW_{self.video_file_path}")

    def remove_temporary_audio_file(self):
        if os.path.exists(self.extracted_audio_file_path):
            os.remove(self.extracted_audio_file_path)

    def create_new_video_file(self):
        self.extract_audio_file()
        opening_offset, ending_offset = self.calculate_offsets()
        self.write_video_file(opening_offset, ending_offset)
        self.remove_temporary_audio_file()


class VideoRemover:
    pass


parsed_file = "naruto1.mp4"
opening_file = "opening.mp3"
ending_file = "ending.mp3"

# video_remover = VideoRemover(parsed_file, opening_file, ending_file)
# video_remover.create_new_video_file()
# # video_remover.write_video_file(1, 1)

# video_parser = VideoParser(parsed_file, opening_file, ending_file)
# video_parser.create_new_video_file()

# TODO CLI input
# TODO VideoRemover as logic for gathering data and running VideoParser
# TODO Add multiprocessing
# TODO Add to settings possibility to create new videos in separate directory
# TODO Add pydantic for creating and validating objects
