# from moviepy.editor import VideoFileClip
#
# video = VideoFileClip("naruto1.mp4")
# video.audio.write_audiofile("naruto_odcinek_sound2.mp3", bitrate="300k")
import librosa
from scipy import signal
import numpy as np

y_within, sr_within = librosa.load("naruto1.mp3", sr=None)
y_find, _ = librosa.load("opening.mp3", sr=sr_within)

c = signal.correlate(y_within, y_find, mode='valid', method='fft')

peak = np.argmax(c)
offset = round(peak / sr_within, 2)
print(offset)
