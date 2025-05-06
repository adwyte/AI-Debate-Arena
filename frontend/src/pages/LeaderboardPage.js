import React from 'react';
import { useNavigate } from 'react-router-dom';
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
import api from '../api';

export default function LeaderboardPage() {
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ['leaderboard'],
    queryFn:   () => api.get('/leaderboard').then(r => r.data),
  });

  if (isLoading) return <CircularProgress />;
  if (error)     return <Alert severity="error">Failed to load leaderboard</Alert>;

  const entries = data ?? [];
  if (entries.length === 0) {
    return <Alert severity="info">No speakers have scored yet.</Alert>;
  }

  // Medal colors for top 3
  const medalBg = ['#FFD700', '#C0C0C0', '#CD7F32'];
  const medalText = [
    'common.black',  // gold => black text
    'common.black',  // silver => black text
    'common.white'   // bronze => white text
  ];

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', px: 3, py: 4 }}>
      <Typography
        variant="h4"
        align="center"
        gutterBottom
        color="primary.main"
      >
        Speaker Leaderboard
      </Typography>

      <Paper elevation={2} sx={{ p: 2, bgcolor: 'background.paper' }}>
        <List disablePadding>
          {entries.map((entry, idx) => {
            // Determine avatar style
            const isMedal = idx < 3;
            const avatarSx = isMedal
              ? {
                  bgcolor: medalBg[idx],
                  color:  medalText[idx]
                }
              : {
                  bgcolor: 'primary.main',
                  color:  'common.white'
                };

            return (
              <ListItemButton
                key={entry.speaker}
                onClick={() =>
                  navigate(`/leaderboard/${encodeURIComponent(entry.speaker)}`)
                }
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  mb: 1,
                  borderRadius: 1,
                  px: 2,
                  py: 1.5,
                  bgcolor: 'background.default',
                  boxShadow: 1,
                  transition: 'background-color 0.2s',
                  '&:hover': { bgcolor: 'primary.light' }
                }}
              >
                <ListItemAvatar>
                  <Avatar sx={avatarSx}>
                    {idx + 1}
                  </Avatar>
                </ListItemAvatar>

                <Box sx={{ flexGrow: 1, ml: 2 }}>
                  <Typography
                    variant="body1"
                    sx={{ color: isMedal ? medalBg[idx] : 'text.primary' }}
                  >
                    {entry.speaker}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Points: {entry.total_points}
                  </Typography>
                </Box>
              </ListItemButton>
            );
          })}
        </List>
      </Paper>
    </Box>
  );
}
