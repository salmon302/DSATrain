import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

type ColorMode = 'light' | 'dark';

export const ColorModeContext = React.createContext<{ mode: ColorMode; toggleColorMode: () => void }>({
  mode: 'light',
  toggleColorMode: () => {},
});

const getStoredMode = (): ColorMode => {
  try {
    const m = localStorage.getItem('theme:mode');
    return m === 'dark' ? 'dark' : 'light';
  } catch {
    return 'light';
  }
};

export const ColorModeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mode, setMode] = React.useState<ColorMode>(getStoredMode());

  React.useEffect(() => {
    try { localStorage.setItem('theme:mode', mode); } catch {}
  }, [mode]);

  const toggleColorMode = React.useCallback(() => {
    setMode(prev => (prev === 'light' ? 'dark' : 'light'));
  }, []);

  const theme = React.useMemo(() => createTheme({
    palette: {
      mode,
      primary: { main: '#1976d2', light: '#42a5f5', dark: '#1565c0' },
      secondary: { main: '#9c27b0', light: '#ba68c8', dark: '#7b1fa2' },
    },
    typography: {
      fontFamily: 'Inter, system-ui, sans-serif',
      h1: { fontSize: '2.5rem', fontWeight: 600 },
      h2: { fontSize: '2rem', fontWeight: 600 },
      h3: { fontSize: '1.5rem', fontWeight: 500 },
      body1: { fontSize: '1rem', lineHeight: 1.6 },
    },
    shape: { borderRadius: 8 },
  }), [mode]);

  const value = React.useMemo(() => ({ mode, toggleColorMode }), [mode, toggleColorMode]);

  return (
    <ColorModeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
};


