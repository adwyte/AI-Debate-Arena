import React from 'react';
import { ReactMediaRecorder } from 'react-media-recorder';
import api from '../api';

export default function TranscribeButton({ debateId, onNew }) {
  return (
    <ReactMediaRecorder
      audio
      blobPropertyBag={{ type: 'audio/wav' }}
      render={({ status, startRecording, stopRecording, mediaBlobUrl }) => (
        <div>
          <p>Mic: {status}</p>
          <button onClick={startRecording}>🎤 Start</button>
          <button onClick={stopRecording}>⏹ Stop</button>
          {mediaBlobUrl && (
            <button onClick={async () => {
              const blob = await fetch(mediaBlobUrl).then(r => r.blob());
              const form = new FormData();
              form.append('debate_id', debateId);
              form.append('speaker', 'You');
              form.append('audio_file', blob, 'speech.wav');
              const res = await api.post(
                  '/transcribe/argument',
                  form,{
                      headers: { 'Content-Type': 'multipart/form-data' }
                  });
              onNew(res.data);
            }}>
              Upload & Transcribe
            </button>
          )}
        </div>
      )}
    />
  );
}
