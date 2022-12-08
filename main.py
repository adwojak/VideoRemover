from moviepy.editor import VideoFileClip
import numpy
import librosa
from scipy import signal


class VideoRemover:
    VIDEO_BITRATE = "300k"

    def __init__(self, video_file_path, opening_path, ending_path):
        self.video_file_path = video_file_path
        self.parsed_video_file_path = f"{video_file_path}_tmp.mp3"
        self.opening_path = opening_path
        self.ending_path = ending_path

    def mp4_to_mp3(self):
        video = VideoFileClip(self.video_file_path)
        video.audio.write_audiofile(self.parsed_video_file_path, bitrate=self.VIDEO_BITRATE)

    def librosa_load(self, filename, sampling_rate=None):
        return librosa.load(filename, sr=sampling_rate)

    def calculate_offset(self, filename, y_movie, sampling_rate_movie):
        y_sample, _ = self.librosa_load(filename, sampling_rate_movie)
        correlation = signal.correlate(y_movie, y_sample, mode='valid', method='fft')
        peak = numpy.argmax(correlation)
        return round(peak / sampling_rate_movie, 2)

    def parse_video_file(self):
        opening_offset, ending_offset = None, None
        # self.mp4_to_mp3()
        y_movie, sampling_rate_movie = self.librosa_load(self.parsed_video_file_path)
        if self.opening_path:
            opening_offset = self.calculate_offset(self.opening_path, y_movie, sampling_rate_movie)

        print(opening_offset, ending_offset)


aa = VideoRemover("naruto1.mp4", "opening.mp3", "")
aa.parse_video_file()
