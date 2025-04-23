import os
import wave
import whisper
import imageio_ffmpeg
import pyaudio

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

class AudioRecorder:
    def __init__(self, filename="recorded_audio.wav", rate=16000):
        self.filename = filename
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = rate
        self.chunk = 1024
        self.frames = []

    def record_audio(self, duration_sec: int):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=self.format, channels=self.channels,
                            rate=self.rate, input=True, frames_per_buffer=self.chunk)

        for _ in range(int(self.rate / self.chunk * duration_sec)):
            data = stream.read(self.chunk)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))

        return self.filename

class WhisperTranscriber:
    def __init__(self, model_size="medium"):
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_file: str) -> str:
        result = self.model.transcribe(audio_file)
        return result['text']
