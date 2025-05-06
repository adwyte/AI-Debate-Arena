import React from 'react';
import api from '../api';

export default function AiResponseButton({ debateId, argumentId, onRespond }) {
  const go = () => {
    api.post(`/debates/${debateId}/ai_response/${argumentId}`, {})
      .then(res => onRespond(res.data))
      .catch(console.error);
  };
  return <button onClick={go}>AI Rebuttal</button>;
}
