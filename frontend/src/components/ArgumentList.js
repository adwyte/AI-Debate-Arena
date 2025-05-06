import React from 'react';
import api from '../api';

export default function ArgumentList({ args, debate, onUpdate }) {
  const evaluate = id => {
    api.post(`/evaluate/${id}`, {}).then(() =>
      api.get(`/debates/${debate.id}`).then(r => onUpdate(r.data))
    ).catch(console.error);
  };

  return (
    <ul>
      {args.map(a => (
        <li key={a.id}>
          <strong>{a.speaker}:</strong> {a.text}
          {a.score
            ? <div>
                Score: {a.score.total_score}
                <button onClick={() => evaluate(a.id)}>Re‐evaluate</button>
              </div>
            : <button onClick={() => evaluate(a.id)}>Evaluate</button>
          }
        </li>
      ))}
    </ul>
  );
}
