import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  List,
  ListItemButton,
  ListItemAvatar,
  Avatar,
  Paper
} from '@mui/material';
import GavelIcon from '@mui/icons-material/Gavel';
import api from '../api';

export default function SpeakerHistoryPage() {
  const { speaker } = useParams();
  const navigate    = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ['speakerHistory', speaker],
    queryFn:   () =>
      api
        .get(`/leaderboard/${encodeURIComponent(speaker)}/history`)
        .then(r => r.data),
  });

  if (isLoading) return <CircularProgress />;
  if (error)     return <Alert severity="error">Failed to load history</Alert>;

  const entries = data ?? [];
  if (entries.length === 0) {
    return <Alert severity="info">{speaker} has no completed debates yet.</Alert>;
  }

  // Sort most recent first
  const sortedEntries = [...entries].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  );

  return (
    <Box sx={{ maxWidth: 800, width: '90%', mx: 'auto', px: 3, py: 4 }}>
      {/* Page Title */}
      <Typography
        variant="h4"
        align="center"
        gutterBottom
        color="primary.main"
      >
        {speaker}’s Debate History
      </Typography>

      {/* Paper wrapping the list */}
      <Paper elevation={2} sx={{ width: '100%', p:2, bgcolor: 'background.paper' }}>
        <List disablePadding>
          {sortedEntries.map(item => (
            <ListItemButton
              key={item.debate_id}
              onClick={() => navigate(`/debate/${item.debate_id}/results`)}
              sx={{
                  width: '100%',
                  mb: 1,
                  borderRadius: 1,
                  px: 2,
                  py: 1.5,
                  bgcolor: 'background.default',
                  boxShadow: 1,
                  display: 'flex',
                  alignItems: 'center',
                  transition: 'background-color 0.2s',
                  '&:hover': { bgcolor: 'primary.light' }
              }}
            >
              {/* Gavel avatar */}
              <ListItemAvatar>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <GavelIcon />
                </Avatar>
              </ListItemAvatar>

              {/* Text block */}
              <Box sx={{ flexGrow: 1, ml: 2 }}>
                <Typography variant="subtitle1" color="text.primary">
                  {item.topic}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {new Date(item.created_at).toLocaleString()}
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  Winner: <strong>{item.winner}</strong> │ Your points:{' '}
                  <Box
                    component="span"
                    sx={{ color: 'primary.main', fontWeight: 500 }}
                  >
                    {item.my_points}
                  </Box>
                </Typography>
              </Box>
            </ListItemButton>
          ))}
        </List>
      </Paper>
    </Box>
  );
}
