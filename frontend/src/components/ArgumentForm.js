import React, { useState } from 'react';
import api from '../api';

export default function ArgumentForm({ debateId, onNew }) {
  const [text, setText] = useState('');

  const submit = e => {
    e.preventDefault();
    api.post('/arguments', { speaker: 'You', text, debate_id: debateId })
      .then(res => {
        onNew(res.data);
        setText('');
      })
      .catch(console.error);
  };

  return (
    <form onSubmit={submit}>
      <textarea
        rows={3}
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Your argument…"
        required
      />
      <button type="submit">Submit Argument</button>
    </form>
  );
}
