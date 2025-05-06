import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Stack, TextField, Button, MenuItem } from '@mui/material';

export default function DebateForm({ onCreate, isLoading }) {
  const { control, handleSubmit, reset } = useForm({
    defaultValues: { topic: '', mode: 'ai_vs_human' }
  });

  const onSubmit = data => {
    onCreate(data);
    reset();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Stack direction="row" spacing={2} alignItems="center">
        <Controller
          name="topic"
          control={control}
          rules={{ required: true }}
          render={({ field }) =>
            <TextField {...field} label="Topic" fullWidth required />
          }
        />
        <Controller
          name="mode"
          control={control}
          render={({ field }) =>
            <TextField {...field} select label="Mode">
              <MenuItem value="1v1">1v1</MenuItem>
              <MenuItem value="ai_vs_human">AI vs Human</MenuItem>
            </TextField>
          }
        />
        <Button type="submit" variant="contained" disabled={isLoading}>
          {isLoading ? 'Creating…' : 'Create Debate'}
        </Button>
      </Stack>
    </form>
  );
}
