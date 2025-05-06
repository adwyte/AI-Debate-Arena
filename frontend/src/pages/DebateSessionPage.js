import React, { useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Stack,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Box
} from '@mui/material';

import api from '../api';
import TranscribeButton from '../components/TranscribeButton';

export default function DebateSessionPage() {
  const { id } = useParams();
  const { state } = useLocation();
  const navigate = useNavigate();

  // speakers passed via state from SetupPage
  const speakers = state?.speakers || ['You', 'AI'];
  const mode     = speakers[1] === 'AI' ? 'ai_vs_human' : '1v1';

  // 1. Fetch the debate so we can show its topic
  const { data: debate, isLoading, error } = useQuery({
    queryKey: ['debate', id],
    queryFn:   () => api.get(`/debates/${id}`).then(r => r.data),
  });

  const [turn, setTurn]   = useState(0);      // index into speakers[]
  const [text, setText]   = useState('');
  const [args, setArgs]   = useState([]);

  if (isLoading) return <CircularProgress />;
  if (error)     return <Alert severity="error">Failed to load debate</Alert>;

  // 2. Called for both text and speech submissions
  const handleSubmit = async (argumentText) => {
    const speaker = speakers[turn];

    try {
      // a) save argument
      const { data: arg } = await api.post('/arguments', {
        speaker,
        text:      argumentText,
        debate_id: +id
      });

      setArgs(a => [...a, arg]);

      // b) evaluate it immediately
      await api.post(`/evaluate/${arg.id}`);

      // c) if AI-vs-Human, get AI rebuttal and eval that too
      if (mode === 'ai_vs_human') {
        const { data: aiArg } = await api.post(
          `/debates/${id}/ai_response/${arg.id}`
        );
        setArgs(a => [...a, aiArg]);
        await api.post(`/evaluate/${aiArg.id}`);
        // stay on human’s turn
      } else {
        // swap turn for 1v1
        setTurn(t => (t + 1) % 2);
      }

    } catch (e) {
      console.error(e);
      alert('Error saving or evaluating argument:\n' + (e.response?.data?.detail || e.message));
    }

    setText('');
  };

  return (
    <Stack spacing={4}>
      {/* 1. Show debate topic */}
      <Typography variant="h2" align="center">
        {debate.topic}
      </Typography>

      <Card>
        <CardContent>
          {/* 2. Show whose turn it is */}
          <Typography variant="subtitle1">
            {mode === '1v1'
              ? `Current turn: ${speakers[turn]}`
              : `Your turn`}
          </Typography>

          {/* 3. Text entry */}
          <TextField
            multiline
            minRows={4}
            fullWidth
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="Enter your argument…"
            sx={{ mt: 2 }}
          />

          {/* 4. Buttons: Submit Text, Submit Audio, Finish */}
          <Box mt={2} display="flex" gap={2}>
            <Button
              variant="contained"
              onClick={() => handleSubmit(text)}
              disabled={!text.trim()}
            >
              Submit Argument
            </Button>

            <TranscribeButton
              debateId={+id}
              speaker={speakers[turn]}
              onNew={arg => {
                // same flow as text: add & evaluate
                handleSubmit(arg.text);
              }}
            />

            <Button
              variant="outlined"
              onClick={() => navigate(`/debate/${id}/results`)}
            >
              Finish & Evaluate Debate
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* 5. Show submitted arguments in live view */}
      <Stack spacing={2}>
        {args.map(a => (
          <Card key={a.id} variant="outlined">
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                {a.speaker}
              </Typography>
              <Typography>{a.text}</Typography>
            </CardContent>
          </Card>
        ))}
      </Stack>
    </Stack>
  );
}
