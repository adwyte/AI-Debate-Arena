import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { Stack, TextField, Button, Typography } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import api from '../api';

export default function DebateSetupPage() {
  const { mode } = useParams();            // "1v1" or "ai_vs_human"
  const navigate = useNavigate();

  // Our form only cares about topic & speakers
  const { control, handleSubmit } = useForm({
    defaultValues: mode === '1v1'
      ? { topic: '', speaker1: '', speaker2: '' }
      : { topic: '', speaker1: '' }
  });

  // 1️⃣ mutationFn: take the formData, but only send {topic, mode} to the API
  // 2️⃣ onSuccess: the second argument ("vars") is exactly our formData,
  //                 so we can pull speaker1/speaker2 out of it for the redirect
  const createDebate = useMutation({
    mutationFn: ({ topic }) =>
      api.post('/debates/', { topic, mode }).then(res => res.data),
    onSuccess: (debate, vars) => {
      const { speaker1, speaker2 } = vars;
      const speakers = mode === '1v1'
        ? [ speaker1, speaker2 ]
        : [ speaker1, 'AI' ];

      // navigate to the session screen, passing our speaker names in state
      navigate(`/debate/${debate.id}/session`, {
        state: { speakers }
      });
    }
  });

  // handleSubmit will give us an object { topic, speaker1, speaker2? }
  const onSubmit = data => {
    createDebate.mutate(data);
  };

  return (
    <Stack spacing={4} maxWidth={600} mx="auto" my={6}>
      <Typography variant="h2" textAlign="center">
        {mode === '1v1' ? '1v1 Structured Debate' : 'AI vs Human Debate'}
      </Typography>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Stack spacing={3}>
          <Controller
            name="topic"
            control={control}
            rules={{ required: 'Debate topic is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Debate Topic"
                fullWidth
                required
              />
            )}
          />

          <Controller
            name="speaker1"
            control={control}
            rules={{ required: 'Your name is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Your Name"
                fullWidth
                required
              />
            )}
          />

          {mode === '1v1' && (
            <Controller
              name="speaker2"
              control={control}
              rules={{ required: 'Opponent name is required' }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Opponent Name"
                  fullWidth
                  required
                />
              )}
            />
          )}

          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={createDebate.isLoading}
          >
            {createDebate.isLoading ? 'Starting…' : 'Start Debate'}
          </Button>
        </Stack>
      </form>
    </Stack>
  );
}
