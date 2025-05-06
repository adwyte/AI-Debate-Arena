import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Container,
  Button,
} from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';

import HomePage           from './pages/HomePage';
import DebateSetupPage    from './pages/DebateSetupPage';
import DebateSessionPage  from './pages/DebateSessionPage';
import DebateResultsPage  from './pages/DebateResultsPage';
import AboutPage          from './pages/AboutPage';
import LeaderboardPage    from './pages/LeaderboardPage';
import SpeakerHistoryPage from './pages/SpeakerHistoryPage';


export default function App({ mode, setMode }) {
  const toggleDark = () => setMode(prev => (prev === 'light' ? 'dark' : 'light'));

  return (
    <>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h3" sx={{ flexGrow: 1 }}>
            AI Debate Arena
          </Typography>

          <IconButton onClick={toggleDark} color="inherit">
            {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>

          {/* Nav buttons */}
          <Button
              component={Link}
              to="/"
              color="inherit"
              sx={{ ml: 2 }}
          >
            Home
          </Button>
          <Button
              component={Link}
              to="/about"
              color="inherit"
              sx={{ ml: 1 }}
          >
            About
          </Button>
          <Button
              component={Link}
              to="/leaderboard"
              color="inherit"
              sx={{ ml: 1 }}
          >
            Leaderboard
          </Button>
        </Toolbar>
      </AppBar>

      <Container sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/new/:mode" element={<DebateSetupPage />} />
          <Route path="/debate/:id/session" element={<DebateSessionPage />} />
          <Route path="/debate/:id/results" element={<DebateResultsPage />} />
          <Route path="/leaderboard" element={<LeaderboardPage />} />
          <Route path="/leaderboard/:speaker" element={<SpeakerHistoryPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </Container>
    </>
  );
}
