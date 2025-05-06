import os
import whisper
import imageio_ffmpeg

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

model = whisper.load_model("medium")
result = model.transcribe("sample.mp4")
#result = model.transcribe("recorded-audio.mp3")

transcription = result['text'].replace('. ', '.\n')
print("Transcription:", transcription)

with open("transcription.txt", "w", encoding="utf-8") as f:
    f.write(transcription)
print("Saved to transcription.txt")
