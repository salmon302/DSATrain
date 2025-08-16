import React from 'react';
import {
  Box,
  List,
  ListSubheader,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Divider,
  Tooltip,
  Badge,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Quiz,
  Code,
  AccountTree as SkillTreeIcon,
  TrendingUp,
  School,
  Analytics as AnalyticsIcon,
  Info,
  Person,
  Settings as SettingsIcon,
  Psychology,
  ExpandLess,
  ExpandMore,
  FiberNew,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';

interface NavigationItem {
  text: string;
  icon: React.ReactElement;
  path: string;
  isNew?: boolean;
  badge?: string;
  description?: string;
}

interface NavigationGroup {
  title: string;
  items: NavigationItem[];
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

interface ImprovedNavigationProps {
  onNavigate?: (path: string) => void;
  userLevel?: 'beginner' | 'intermediate' | 'advanced' | 'expert';
}

const ImprovedNavigation: React.FC<ImprovedNavigationProps> = ({
  onNavigate,
  userLevel = 'intermediate'
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [expandedGroups, setExpandedGroups] = React.useState<string[]>(['core', 'learning']);

  const handleNavigation = (path: string) => {
    navigate(path);
    onNavigate?.(path);
  };

  const toggleGroup = (groupTitle: string) => {
    setExpandedGroups(prev => 
      prev.includes(groupTitle) 
        ? prev.filter(g => g !== groupTitle)
        : [...prev, groupTitle]
    );
  };

  // Define navigation groups based on user level
  const getNavigationGroups = (): NavigationGroup[] => {
    const coreGroup: NavigationGroup = {
      title: 'Core Training',
      items: [
        { 
          text: 'Dashboard', 
          icon: <DashboardIcon />, 
          path: '/',
          description: 'Your learning overview and quick actions'
        },
        { 
          text: 'Browse Problems', 
          icon: <Quiz />, 
          path: '/problems',
          description: 'Explore coding challenges'
        },
        { 
          text: 'Code Practice', 
          icon: <Code />, 
          path: '/practice',
          description: 'Interactive coding environment'
        },
        { 
          text: 'Skill Tree', 
          icon: <SkillTreeIcon />, 
          path: '/skill-tree',
          description: 'Visual progress tracking'
        },
      ],
      defaultExpanded: true
    };

    const learningGroup: NavigationGroup = {
      title: 'Learning & Growth',
      items: [
        { 
          text: 'AI Recommendations', 
          icon: <TrendingUp />, 
          path: '/recommendations',
          description: 'Personalized problem suggestions',
          isNew: true
        },
        { 
          text: 'Learning Paths', 
          icon: <School />, 
          path: '/learning-paths',
          description: 'Structured learning journeys'
        },
        { 
          text: 'Interview Guide', 
          icon: <Info />, 
          path: '/guide',
          description: 'Preparation strategies and tips'
        },
      ],
      defaultExpanded: userLevel !== 'beginner'
    };

    const analyticsGroup: NavigationGroup = {
      title: 'Progress & Analytics',
      items: [
        { 
          text: 'Analytics', 
          icon: <AnalyticsIcon />, 
          path: '/analytics',
          description: 'Detailed performance insights'
        },
      ],
      defaultExpanded: false,
      collapsible: true
    };

    const personalGroup: NavigationGroup = {
      title: 'Personal',
      items: [
        { 
          text: 'Profile', 
          icon: <Person />, 
          path: '/profile',
          description: 'Your account and preferences'
        },
        { 
          text: 'Settings', 
          icon: <SettingsIcon />, 
          path: '/settings',
          description: 'Configure AI and features'
        },
      ],
      collapsible: true,
      defaultExpanded: false
    };

    const advancedGroup: NavigationGroup = {
      title: 'Advanced Features',
      items: [
        { 
          text: 'AI Demo', 
          icon: <Psychology />, 
          path: '/ai-demo',
          description: 'Experiment with AI capabilities',
          badge: 'Beta'
        },
        { 
          text: 'Dev Tools', 
          icon: <Code />, 
          path: '/dev-tools',
          description: 'Development utilities'
        },
      ],
      collapsible: true,
      defaultExpanded: false
    };

    // Return groups based on user level
    switch (userLevel) {
      case 'beginner':
        return [coreGroup, personalGroup];
      case 'intermediate':
        return [coreGroup, learningGroup, personalGroup];
      case 'advanced':
        return [coreGroup, learningGroup, analyticsGroup, personalGroup, advancedGroup];
      case 'expert':
        return [coreGroup, learningGroup, analyticsGroup, personalGroup, advancedGroup];
      default:
        return [coreGroup, learningGroup, personalGroup];
    }
  };

  const navigationGroups = getNavigationGroups();

  const renderNavigationItem = (item: NavigationItem) => {
    const isSelected = location.pathname === item.path;
    
    return (
      <Tooltip 
        key={item.path}
        title={item.description || ''} 
        placement="right"
        enterDelay={500}
      >
        <ListItemButton
          selected={isSelected}
          onClick={() => handleNavigation(item.path)}
          sx={{
            ml: 2,
            mr: 1,
            borderRadius: 1,
            '&.Mui-selected': {
              backgroundColor: 'primary.light',
              '&:hover': {
                backgroundColor: 'primary.light',
              },
            },
          }}
        >
          <ListItemIcon sx={{ minWidth: 40 }}>
            <Badge 
              color="error" 
              variant="dot" 
              invisible={!item.isNew}
              sx={{ '& .MuiBadge-badge': { right: 2, top: 2 } }}
            >
              {item.icon}
            </Badge>
          </ListItemIcon>
          <ListItemText 
            primary={
              <Box display="flex" alignItems="center" gap={1}>
                {item.text}
                {item.isNew && (
                  <Chip 
                    label="New" 
                    size="small" 
                    color="primary" 
                    icon={<FiberNew />}
                    sx={{ height: 16, fontSize: '0.7rem' }}
                  />
                )}
                {item.badge && (
                  <Chip 
                    label={item.badge} 
                    size="small" 
                    variant="outlined"
                    sx={{ height: 16, fontSize: '0.7rem' }}
                  />
                )}
              </Box>
            }
          />
        </ListItemButton>
      </Tooltip>
    );
  };

  const renderNavigationGroup = (group: NavigationGroup, index: number) => {
    const isExpanded = expandedGroups.includes(group.title.toLowerCase().replace(' ', ''));
    const showExpandButton = group.collapsible !== false;

    return (
      <Box key={group.title}>
        {index > 0 && <Divider sx={{ my: 1 }} />}
        
        <ListSubheader
          component="div"
          sx={{
            backgroundColor: 'transparent',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            pr: 1,
            cursor: showExpandButton ? 'pointer' : 'default',
          }}
          onClick={() => showExpandButton && toggleGroup(group.title.toLowerCase().replace(' ', ''))}
        >
          <Box sx={{ fontWeight: 'medium', fontSize: '0.875rem' }}>
            {group.title}
          </Box>
          {showExpandButton && (
            isExpanded ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />
          )}
        </ListSubheader>

        <Collapse in={!group.collapsible || isExpanded} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {group.items.map(renderNavigationItem)}
          </List>
        </Collapse>
      </Box>
    );
  };

  return (
    <Box sx={{ width: 250 }}>
      <List component="nav" sx={{ pt: 0 }}>
        {navigationGroups.map(renderNavigationGroup)}
      </List>
    </Box>
  );
};

export default ImprovedNavigation;
