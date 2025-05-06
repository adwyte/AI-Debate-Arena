import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import '@fontsource/montserrat/400.css';
import '@fontsource/montserrat/700.css';

import App from './App';
import { getDesignTokens } from './theme';

const queryClient = new QueryClient();

function Root() {
  const [mode, setMode] = useState('dark');
  const theme = useMemo(() => createTheme(getDesignTokens(mode)), [mode]);

  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <App mode={mode} setMode={setMode} />
        </ThemeProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );
}

createRoot(document.getElementById('root')).render(<Root />);
