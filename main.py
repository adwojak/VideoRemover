from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip, concatenate_videoclips
import moviepy
import numpy
import librosa
from scipy import signal
from soundfile import SoundFile


class VideoRemover:
    VIDEO_BITRATE = "300k"

    def __init__(self, video_file_path, opening_path, ending_path):
        self.video_file_path = video_file_path
        self.parsed_video_file_path = f"{video_file_path}_tmp.mp3"
        self.opening_path = opening_path
        self.ending_path = ending_path

    def extract_audio_file(self):
        # TODO Temporary solution - need to extract sound without creating .mp3 file
        with VideoFileClip(self.video_file_path) as video:
            video.audio.write_audiofile(self.parsed_video_file_path, bitrate=self.VIDEO_BITRATE)

    def calculate_audio_offset(self, filename, y_movie, sampling_rate_movie):
        audio_sample, audio_sampling_rage = librosa.load(filename, sr=sampling_rate_movie)
        correlation = signal.correlate(y_movie, audio_sample, mode='valid', method='fft')
        audio_starting_time = numpy.argmax(correlation) / sampling_rate_movie
        duration = librosa.get_duration(audio_sample, audio_sampling_rage)
        return float(round(audio_starting_time, 2)), float(round(audio_starting_time + duration, 2))

    def calculate_offsets(self):
        opening_offset, ending_offset = None, None
        y_movie, sampling_rate_movie = librosa.load(self.parsed_video_file_path, sr=None)

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
        subtimes = self.calculate_subtimes(opening_offset, ending_offset)
        with VideoFileClip(self.video_file_path) as video:
            subclips = []
            for subtime in subtimes:
                if isinstance(subtime, tuple):
                    subclips.append(video.subclip(*subtime))
                else:
                    subclips.append(video.subclip(subtime))
            # video = video.subclip(ending_offset[0], ending_offset[1])
            # video = video.subclip(opening_offset[0], opening_offset[1])
            # video = video.cutout(opening_offset[0], opening_offset[1])
            # TODO Error with get_frame for cutted video
            final_video = concatenate_videoclips(subclips)
            final_video.write_videofile(f"NEW_{self.video_file_path}")

    def create_new_video_file(self):
        # self.extract_audio_file()
        opening_offset, ending_offset = self.calculate_offsets()
        self.write_video_file(opening_offset, ending_offset)


# TODO CLI input
parsed_file = "naruto1.mp4"
opening_file = "opening.mp3"
ending_file = "ending.mp3"

video_remover = VideoRemover(parsed_file, opening_file, ending_file)
video_remover.create_new_video_file()
# video_remover.write_video_file(1, 1)
