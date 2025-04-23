import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.run(asyncio.sleep(0))

import whisper
import av
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

st.title("🎙️ Real-Time Speech to Text Transcription")

model = whisper.load_model("medium")

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv(self, frame: av.AudioFrame):
        audio_data = frame.to_ndarray()
        self.frames.append(audio_data)
        return frame

webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"video": False, "audio": True},
)

if webrtc_ctx.audio_processor:
    if st.button("📝 Transcribe Audio"):
        audio_bytes = b''.join(webrtc_ctx.audio_processor.frames)
        with open("live_audio.wav", "wb") as f:
            f.write(audio_bytes)

        result = model.transcribe("live_audio.wav")
        st.text_area("📝 Transcription:", result["text"], height=300)
