import React from 'react';
import { Box, Typography, List, ListItem, Divider } from '@mui/material';

export default function AboutPage() {
  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', px: 3, py: 6 }}>
      {/* Cyan‐accented main heading */}
      <Typography variant="h4" color="primary.main" gutterBottom>
        AI Debate Arena
      </Typography>

      <Divider sx={{ mb: 3 }} />

      {/* Project description */}
      <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem' }}>
        AI Debate Arena is a real-time debate judging platform that analyzes and
        scores arguments on logical consistency, evidence support, bias, and ethics.
        Built to make debates more rigorous and transparent through AI-driven scoring.
      </Typography>

      {/* Team */}
      <Typography variant="h5" color="primary.main" gutterBottom sx={{ mt: 4 }}>
        Team
      </Typography>
      <List sx={{ pl: 4, '& .MuiListItem-root': { display: 'list-item', py: 0 } }}>
        <ListItem>TY AIML A8 – Software Engineering Course Project</ListItem>
      </List>

      {/* Tech Stack */}
      <Typography variant="h5" color="primary.main" gutterBottom sx={{ mt: 4 }}>
        Tech Stack
      </Typography>
      <Typography variant="body1" sx={{ pl: 4, fontSize: '1.05rem' }}>
        FastAPI • React.js • PostgreSQL • Groq Llama 3 8B
      </Typography>
    </Box>
  );
}
