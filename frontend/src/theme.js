import { createTheme } from '@mui/material/styles';

export const getDesignTokens = mode => ({
  palette: {
    mode,
    ...(mode === 'dark'
      ? {
          background: {
            default: '#000000',  // pitch black
            paper:   '#111111',
          },
          text: {
            primary:   '#FFFFFF',
            secondary: '#BBBBBB',
          },
          primary: {
            main: '#00e5ff',     // bright cyan
            light: 'rgba(0,229,255,0.1)',
          },
          secondary: {
            main: '#ff1744',
          },
        }
      : {
          background: {
            default: '#f0f2f5',  // very light gray
            paper:   '#FFFFFF',
          },
          text: {
            primary:   '#000000',
            secondary: '#555555',
          },
          primary: {
            main: '#00bcd4',     // cyan
            light: 'rgba(0,188,212,0.1)',
          },
          secondary: {
            main: '#ff1744',
          },
        })
  },
  typography: {
    fontFamily: `"Montserrat", sans-serif`,
    h2: { fontWeight: 700, fontSize: '2.5rem' },
    h3: { fontWeight: 600, fontSize: '1.75rem' },
  },
});
