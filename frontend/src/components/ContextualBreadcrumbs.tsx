import React from 'react';
import {
  Box,
  Breadcrumbs,
  Link,
  Typography,
  Chip,
  IconButton,
  Paper,
  Menu,
  MenuItem,
} from '@mui/material';
import { Home, NavigateNext, MoreVert } from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { favoritesAPI, getCurrentUserId } from '../services/api';

interface BreadcrumbItem {
  label: string;
  path?: string;
  icon?: React.ReactElement;
}

interface ContextualBreadcrumbsProps {
  customBreadcrumbs?: BreadcrumbItem[];
  showActions?: boolean;
  currentPageTitle?: string;
  currentPageMeta?: {
    difficulty?: string;
    platform?: string;
    quality?: number;
  };
}

const ContextualBreadcrumbs: React.FC<ContextualBreadcrumbsProps> = ({
  customBreadcrumbs,
  showActions = true,
  currentPageTitle,
  currentPageMeta,
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [bookmarked, setBookmarked] = React.useState(false);
  const [menuAnchorEl, setMenuAnchorEl] = React.useState<null | HTMLElement>(null);
  const isMenuOpen = Boolean(menuAnchorEl);

  // Generate breadcrumbs based on current route
  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    if (customBreadcrumbs) return customBreadcrumbs;

    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'Dashboard', path: '/', icon: <Home fontSize="small" /> }
    ];

    // Route-specific breadcrumb generation
    const routeMap: Record<string, string> = {
      'problems': 'Browse Problems',
      'practice': 'Code Practice',
      'recommendations': 'AI Recommendations',
      'learning-paths': 'Learning Paths',
      'analytics': 'Analytics',
      'profile': 'Profile',
      'settings': 'Settings',
      'skill-tree': 'Skill Tree',
      'guide': 'Interview Guide',
      'ai-demo': 'AI Demo',
      'dev-tools': 'Dev Tools',
    };

    pathSegments.forEach((segment, index) => {
      const isLast = index === pathSegments.length - 1;
      const label = routeMap[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
      const path = isLast ? undefined : '/' + pathSegments.slice(0, index + 1).join('/');
      
      breadcrumbs.push({ label, path });
    });

    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs();

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: currentPageTitle || 'DSA Training Platform',
          url: window.location.href,
        });
      } catch (error) {
        // Fallback to clipboard
        navigator.clipboard.writeText(window.location.href);
      }
    } else {
      // Fallback to clipboard
      navigator.clipboard.writeText(window.location.href);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleBookmark = async () => {
    const userId = getCurrentUserId();
    const next = !bookmarked;
    setBookmarked(next);
    // If there is a problem context, integrate with favorites toggle.
    // In generic breadcrumbs we lack a problem_id; caller pages can pass actions.
    // Here we optimistically toggle a synthetic bookmark for the current path.
    try {
      const maybeProblemId = new URLSearchParams(window.location.search).get('problemId') || location.pathname.split('/').pop();
      if (maybeProblemId) {
        await favoritesAPI.toggle({ user_id: userId, problem_id: maybeProblemId, favorite: next });
      }
    } catch (e) {
      setBookmarked(!next);
    }
  };

  const handleOpenMenu = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const handleCloseMenu = () => {
    setMenuAnchorEl(null);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  return (
    <Paper 
      elevation={0} 
      sx={{ 
        p: 2, 
        mb: 2, 
        backgroundColor: 'grey.50',
        borderBottom: 1,
        borderColor: 'divider'
      }}
    >
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box display="flex" alignItems="center" gap={2} flex={1}>
          {/* Breadcrumb Navigation */}
          <Breadcrumbs 
            separator={<NavigateNext fontSize="small" />}
            aria-label="breadcrumb"
          >
            {breadcrumbs.map((crumb, index) => {
              const isLast = index === breadcrumbs.length - 1;
              
              if (isLast) {
                return (
                  <Box key={crumb.label} display="flex" alignItems="center" gap={1}>
                    {crumb.icon}
                    <Typography color="text.primary" fontWeight="medium">
                      {crumb.label}
                    </Typography>
                  </Box>
                );
              }
              
              return (
                <Link
                  key={crumb.label}
                  color="inherit"
                  href={crumb.path}
                  onClick={(e: React.MouseEvent<HTMLAnchorElement>) => {
                    e.preventDefault();
                    if (crumb.path) navigate(crumb.path);
                  }}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.5,
                    textDecoration: 'none',
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  {crumb.icon}
                  {crumb.label}
                </Link>
              );
            })}
          </Breadcrumbs>

          {/* Page Meta Information */}
          {currentPageMeta && (
            <Box display="flex" gap={1} ml={2}>
              {currentPageMeta.difficulty && (
                <Chip
                  label={currentPageMeta.difficulty}
                  size="small"
                  color={getDifficultyColor(currentPageMeta.difficulty) as any}
                />
              )}
              {currentPageMeta.platform && (
                <Chip
                  label={currentPageMeta.platform}
                  size="small"
                  variant="outlined"
                />
              )}
              {currentPageMeta.quality && (
                <Chip
                  label={`Quality: ${currentPageMeta.quality.toFixed(1)}`}
                  size="small"
                  variant="outlined"
                />
              )}
            </Box>
          )}
        </Box>

        {/* Page Actions */}
        {showActions && (
          <>
            <IconButton size="small" onClick={handleOpenMenu} aria-label="More actions">
              <MoreVert />
            </IconButton>
            <Menu
              anchorEl={menuAnchorEl}
              open={isMenuOpen}
              onClose={handleCloseMenu}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
              transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
              <MenuItem onClick={() => { handleBookmark(); handleCloseMenu(); }}>
                {bookmarked ? 'Remove Bookmark' : 'Add Bookmark'}
              </MenuItem>
              <MenuItem onClick={() => { void handleShare(); handleCloseMenu(); }}>
                Share Page
              </MenuItem>
              <MenuItem onClick={() => { handlePrint(); handleCloseMenu(); }}>
                Print Page
              </MenuItem>
            </Menu>
          </>
        )}
      </Box>

      {/* Current Page Title */}
      {currentPageTitle && (
        <Typography variant="h5" fontWeight="bold" sx={{ mt: 1 }}>
          {currentPageTitle}
        </Typography>
      )}
    </Paper>
  );
};

export default ContextualBreadcrumbs;
