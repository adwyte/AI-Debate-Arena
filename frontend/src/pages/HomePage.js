import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Box, Grid, Card, CardContent,
  CardActions, Button, Typography
} from '@mui/material';
import GavelIcon from '@mui/icons-material/Gavel';
import MemoryIcon from '@mui/icons-material/Memory';

const modes = [
  {
    key:   '1v1',
    title: '1v1 Structured Debate',
    desc:  'Go head-to-head in a formal debate with another participant.',
    icon:  <GavelIcon sx={{ fontSize: 50, color: 'primary.main' }} />,
    btn:   'Start 1v1 Debate',
  },
  {
    key:   'ai_vs_human',
    title: 'AI vs Human Debate',
    desc:  'Test your debating skills against our AI opponent.',
    icon:  <MemoryIcon sx={{ fontSize: 50, color: 'primary.main' }} />,
    btn:   'Challenge AI Opponent',
  }
];

export default function HomePage() {
  const nav = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      {/* Hero */}
      <Box textAlign="center" mb={6}>
        <Typography variant="h2">AI Debate Arena</Typography>
        <Typography variant="body1" color="text.secondary" mt={2}>
          Test your arguments, improve your critical thinking, and analyze debates in real-time
        </Typography>
      </Box>

      {/* Mode Cards */}
      <Grid container spacing={4} justifyContent="center">
        {modes.map(m => (
          <Grid item xs={12} md={6} lg={5} key={m.key}>
            <Card
              sx={{
                borderRadius: 3,
                boxShadow: 4,
                bgcolor: 'background.paper',
                '&:hover': { boxShadow: 6 }
              }}
            >
              <CardContent sx={{ textAlign: 'center', py: 5 }}>
                {/* Icon in a light‐primary circle */}
                <Box
                  sx={{
                    width: 100, height: 100, mx: 'auto',
                    borderRadius: '50%',
                    bgcolor: 'primary.light',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    mb: 3
                  }}
                >
                  {m.icon}
                </Box>

                <Typography variant="h3" gutterBottom>
                  {m.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {m.desc}
                </Typography>
              </CardContent>

              <CardActions sx={{ px: 3, pb: 3 }}>
                <Button
                  fullWidth
                  variant="contained"
                  color="primary"
                  size="large"
                  onClick={() => nav(`/new/${m.key}`)}
                  sx={{ borderRadius: 2, py: 1.5 }}
                >
                  {m.btn}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}
