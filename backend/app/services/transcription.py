import os
import imageio_ffmpeg
import whisper

# Make sure ffmpeg is on PATH for Whisper’s use
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

class WhisperTranscriber:
    """
    Wraps OpenAI Whisper for audio->text.
    """
    def __init__(self, model_size: str = "medium"):
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe the given audio file path to plain text.
        """
        result = self.model.transcribe(audio_path)
        # strip leading/trailing whitespace
        return result.get("text", "").strip()
