import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  CircularProgress,
  Alert,
  Stack,
  Typography,
  Card,
  CardContent,
  Divider,
  Box
} from '@mui/material';

import api from '../api';

export default function DebateResultsPage() {
  const { id } = useParams();

  const { data: debate, isLoading, error } = useQuery({
    queryKey: ['debate', id],
    queryFn: () => api.get(`/debates/${id}`).then(r => r.data)
  });
  if (isLoading) return <CircularProgress />;
  if (error)     return <Alert severity="error">Failed to load results</Alert>;

  const totals = debate.arguments
    .filter(a => a.score)
    .reduce((acc, a) => {
      acc[a.speaker] = (acc[a.speaker] || 0) + a.score.total_score;
      return acc;
    }, {});

  const sorted = Object.entries(totals).sort(([,a],[,b]) => b - a);
  const [winner, loser] = sorted.map(([s]) => s);

  const winnerColor =
    debate.mode === 'ai_vs_human' && winner === 'AI'
      ? 'error.main'
      : 'primary.main';

  return (
    <Stack spacing={4} sx={{ px: 4, py: 2 }}>
      <Typography variant="h4" align="center">
        {debate.topic}
      </Typography>

      <Typography
        variant="h5"
        align="center"
        sx={{ color: winnerColor, fontWeight: 500 }}
      >
        {winner} wins! ({totals[winner]} vs {totals[loser]})
      </Typography>

      <Divider />

      <Stack spacing={2}>
        {debate.arguments.map(arg => {
          const raw = arg.score?.explanation || '';
          const items = raw
            .split(/\* +|\r?\n/)
            .map(s => s.trim())
            .filter(Boolean)
            .filter(item => !/^Explanation/i.test(item));

          const parsed = items.map(item => {
            const scoreIdx = item.lastIndexOf('Score:');
            let desc = item, score = '';
            if (scoreIdx !== -1) {
              desc  = item.slice(0, scoreIdx).trim();
              score = item.slice(scoreIdx).trim();
            }
            const [param, text] = desc.split(/:\s*/, 2);
            return { param, text, score };
          });

          return (
            <Card key={arg.id} variant="outlined">
              <CardContent>
                <Typography variant="subtitle1" color="primary.main" gutterBottom>
                  {arg.speaker}
                </Typography>

                <Typography variant="body2" paragraph>
                  {arg.text}
                </Typography>

                {arg.score && (
                  <>
                    <Divider sx={{ my: 1 }} />

                    {/* Total Score with colored number */}
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2">
                        <strong>Score:</strong>{' '}
                        <Box
                          component="span"
                          sx={{ color: 'primary.main' }}
                        >
                          {arg.score.total_score} / 100
                        </Box>
                      </Typography>
                    </Box>

                    {/* Explanation header */}
                    <Typography variant="body2" gutterBottom sx={{ ml: 2 }}>
                      <strong>Explanation:</strong>
                    </Typography>

                    {/* Per-parameter lines */}
                    {parsed.map((p, idx) => (
                      <Typography
                        key={idx}
                        variant="body2"
                        component="div"
                        sx={{ ml: 4, mb: 1, whiteSpace: 'pre-line' }}
                      >
                        • <strong>{p.param}:</strong> {p.text}{' '}
                        {p.score && <span>{p.score}</span>}
                      </Typography>
                    ))}

                    {/* NLP Insights */}
                    <Typography
                      variant="body2"
                      sx={{ fontStyle: 'italic', ml: 2 }}
                    >
                      Sentiment: <strong>{arg.score.nlp_insights.sentiment}</strong> │{' '}
                      Emotion:  <strong>{arg.score.nlp_insights.emotion}</strong> │{' '}
                      Tone:     <strong>{arg.score.nlp_insights.tone.join(', ')}</strong>
                    </Typography>
                  </>
                )}
              </CardContent>
            </Card>
          );
        })}
      </Stack>
    </Stack>
  );
}
