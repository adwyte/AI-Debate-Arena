import pyaudio
import wave
import keyboard

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000
CHUNK = 1024


OUTPUT_WAV_FILE = "recorded_audio.wav"

audio = pyaudio.PyAudio()

stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Press SPACE to start recording and press ENTER "
      " to stop.")

frames = []
recording = False

while True:
    if keyboard.is_pressed("space"):
        if not recording:
            print("Recording started...")
            recording = True
    elif keyboard.is_pressed("enter"):
        print("Recording stopped.")
        break

    if recording:
        data = stream.read(CHUNK)
        frames.append(data)

stream.stop_stream()
stream.close()
audio.terminate()

with wave.open(OUTPUT_WAV_FILE, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

print(f"Audio saved as {OUTPUT_WAV_FILE}")
