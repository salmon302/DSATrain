import React from 'react';
import {
  Box,
  Breadcrumbs,
  Link,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Paper,
} from '@mui/material';
import {
  Home,
  NavigateNext,
  Share,
  Print,
  Bookmark,
  BookmarkBorder,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';

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

  const handleBookmark = () => {
    setBookmarked(!bookmarked);
    // TODO: Integrate with actual bookmark API
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
                  onClick={(e) => {
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
          <Box display="flex" gap={1}>
            <Tooltip title="Bookmark Page">
              <IconButton size="small" onClick={handleBookmark}>
                {bookmarked ? <Bookmark color="primary" /> : <BookmarkBorder />}
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Share Page">
              <IconButton size="small" onClick={handleShare}>
                <Share />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Print Page">
              <IconButton size="small" onClick={handlePrint}>
                <Print />
              </IconButton>
            </Tooltip>
          </Box>
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
