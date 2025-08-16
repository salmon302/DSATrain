import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  IconButton,
  Drawer,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
} from '@mui/icons-material';

// Import page components
import Dashboard from './pages/Dashboard';
import ProblemBrowser from './pages/ProblemBrowser';
import CodePractice from './pages/CodePractice';
import Recommendations from './pages/Recommendations';
import LearningPaths from './pages/LearningPaths';
import Analytics from './pages/Analytics';
import UserProfile from './pages/UserProfile';
import GeneralInfo from './pages/GeneralInfo';
import Settings from './pages/Settings';
import AIDemo from './pages/AIDemo';
import SkillTreeVisualization from './components/SkillTreeVisualization';
import DevTools from './pages/DevTools';

// API service
import { apiService } from './services/api';
import AIStatusWidget from './components/AIStatusWidget';
import SRSReview from './pages/SRSReview';
import Interview from './pages/Interview';
import CognitiveAssessment from './pages/CognitiveAssessment';
import ImprovedNavigation from './components/ImprovedNavigation';
import ContextualBreadcrumbs from './components/ContextualBreadcrumbs';

const App: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [apiHealth, setApiHealth] = useState<boolean | null>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();

  // Test API connection on app load and periodically (self-recovers if backend comes online later)
  useEffect(() => {
    let intervalId: number | undefined;

    const checkApiHealth = async () => {
      try {
        // Try root endpoint first
        await apiService.get('/');
        setApiHealth(true);
        return;
      } catch (_) { /* try fallbacks below */ }

      try {
        // Fallback 1: AI status
        await apiService.get('/ai/status');
        setApiHealth(true);
        return;
      } catch (_) { /* try next */ }

      try {
        // Fallback 2: stats
        await apiService.get('/stats');
        setApiHealth(true);
        return;
      } catch (error) {
        console.error('API health check failed:', error);
        setApiHealth(false);
      }
    };

    void checkApiHealth();
    // Periodically re-check so banner clears if backend restarts
    intervalId = window.setInterval(() => { void checkApiHealth(); }, 15000);

    return () => {
      if (intervalId) window.clearInterval(intervalId);
    };
  }, []);

  const drawer = (
    <Box sx={{ width: 250 }}>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          DSA Training
        </Typography>
      </Toolbar>
      <ImprovedNavigation onNavigate={() => { if (isMobile) setDrawerOpen(false); }} />
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              edge="start"
              onClick={() => setDrawerOpen(!drawerOpen)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            DSA Training Platform - Phase 4 Week 2
          </Typography>
          
          {/* API & AI Status Indicator */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: 
                    apiHealth === null ? 'orange' : 
                    apiHealth ? 'lightgreen' : 'red',
                }}
              />
              <Typography variant="body2">
                API: {apiHealth === null ? 'Checking...' : apiHealth ? 'Connected' : 'Offline'}
              </Typography>
            </Box>
            <AIStatusWidget compact />
          </Box>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? drawerOpen : true}
        onClose={() => setDrawerOpen(false)}
        sx={{
          width: 250,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 250,
            boxSizing: 'border-box',
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: isMobile ? 0 : '250px',
        }}
      >
        <Container maxWidth="lg">
          {/* Contextual Breadcrumbs */}
          <ContextualBreadcrumbs />
          {apiHealth === false && (
            <Box
              sx={{
                p: 2,
                mb: 2,
                backgroundColor: 'error.light',
                color: 'error.contrastText',
                borderRadius: 1,
              }}
            >
              <Typography variant="body1">
                ⚠️ API Server is offline. Please start the backend server to access all features.
              </Typography>
            </Box>
          )}

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/guide" element={<GeneralInfo />} />
            <Route path="/skill-tree" element={<SkillTreeVisualization />} />
            <Route path="/problems" element={<ProblemBrowser />} />
            <Route path="/practice" element={<CodePractice />} />
            <Route path="/recommendations" element={<Recommendations />} />
            <Route path="/learning-paths" element={<LearningPaths />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/ai-demo" element={<AIDemo />} />
            <Route path="/dev-tools" element={<DevTools />} />
            <Route path="/profile" element={<UserProfile />} />
            <Route path="/settings" element={<Settings />} />
            {process.env.REACT_APP_FEATURE_SRS === 'off' ? null : <Route path="/srs" element={<SRSReview />} />}
            {process.env.REACT_APP_FEATURE_INTERVIEW === 'off' ? null : <Route path="/interview" element={<Interview />} />}
            {process.env.REACT_APP_FEATURE_COGNITIVE === 'off' ? null : <Route path="/cognitive" element={<CognitiveAssessment />} />}
          </Routes>
        </Container>
      </Box>
    </Box>
  );
};

export default App;
