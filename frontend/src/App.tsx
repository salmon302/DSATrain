import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Quiz,
  TrendingUp,
  School,
  Person,
  Analytics as AnalyticsIcon,
  Code,
  Info,
  AccountTree as SkillTreeIcon,
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
import SkillTreeVisualization from './components/SkillTreeVisualization';

// API service
import { apiService } from './services/api';

const App: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [apiHealth, setApiHealth] = useState<boolean | null>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();

  // Test API connection on app load
  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        const response = await apiService.get('/');
        setApiHealth(true);
      } catch (error) {
        console.error('API health check failed:', error);
        setApiHealth(false);
      }
    };

    checkApiHealth();
  }, []);

  const navigationItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Interview Guide', icon: <Info />, path: '/guide' },
    { text: 'Skill Tree', icon: <SkillTreeIcon />, path: '/skill-tree' },
    { text: 'Browse Problems', icon: <Quiz />, path: '/problems' },
    { text: 'Code Practice', icon: <Code />, path: '/practice' },
    { text: 'Recommendations', icon: <TrendingUp />, path: '/recommendations' },
    { text: 'Learning Paths', icon: <School />, path: '/learning-paths' },
    { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
    { text: 'Profile', icon: <Person />, path: '/profile' },
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setDrawerOpen(false);
    }
  };

  const drawer = (
    <Box sx={{ width: 250 }}>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          DSA Training
        </Typography>
      </Toolbar>
      <List>
        {navigationItems.map((item) => (
          <ListItemButton 
            key={item.text}
            onClick={() => handleNavigation(item.path)}
            selected={location.pathname === item.path}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItemButton>
        ))}
      </List>
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
          
          {/* API Status Indicator */}
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
            <Route path="/profile" element={<UserProfile />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
};

export default App;
