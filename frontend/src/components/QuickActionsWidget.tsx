import React from 'react';
import { Box, Card, CardContent, Typography, Button, Grid, Chip, LinearProgress, Avatar, IconButton, Tooltip, Slide } from '@mui/material';
import {
  PlayArrow,
  TrendingUp,
  School,
  Timer,
  Star,
  ChevronRight,
  Refresh,
  Psychology,
  Assessment,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactElement;
  action: () => void;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  progress?: number;
  metadata?: Record<string, any>;
}

interface UserProgress {
  problemsSolved: number;
  totalProblems: number;
  currentStreak: number;
  weeklyGoal: number;
  weeklyProgress: number;
  nextRecommendation?: {
    title: string;
    difficulty: string;
    estimatedTime: number;
  };
  activeLearningPath?: {
    name: string;
    progress: number;
    nextMilestone: string;
  };
}

interface QuickActionsWidgetProps {
  userProgress?: UserProgress;
  onActionComplete?: (actionId: string) => void;
}

const QuickActionsWidget: React.FC<QuickActionsWidgetProps> = ({
  userProgress,
  onActionComplete,
}) => {
  const navigate = useNavigate();
  const [lastAction, setLastAction] = React.useState<string | null>(null);

  const handleActionClick = (action: QuickAction) => {
    setLastAction(action.id);
    action.action();
    onActionComplete?.(action.id);
    
    // Clear the highlight after animation
    setTimeout(() => setLastAction(null), 1000);
  };

  const generateQuickActions = (): QuickAction[] => {
    const actions: QuickAction[] = [];

    // Primary action: Start practice session
    if (userProgress?.nextRecommendation) {
      actions.push({
        id: 'start-recommended',
        title: 'Start Recommended Problem',
        description: `${userProgress.nextRecommendation.title} (${userProgress.nextRecommendation.difficulty})`,
        icon: <PlayArrow />,
        color: 'primary',
        action: () => navigate('/practice', { 
          state: { 
            recommended: true,
            // Include title to allow title-based selection when id isn't known
            problemTitle: userProgress.nextRecommendation?.title,
            // If upstream starts providing an id, pass it through for direct selection
            problemId: (userProgress as any)?.nextRecommendation?.id
          } 
        }),
        metadata: {
          estimatedTime: userProgress.nextRecommendation.estimatedTime,
          difficulty: userProgress.nextRecommendation.difficulty,
        },
      });
    } else {
      actions.push({
        id: 'start-practice',
        title: 'Start Practice Session',
        description: 'Begin coding with a curated problem',
        icon: <PlayArrow />,
        color: 'primary',
        action: () => navigate('/practice'),
      });
    }

    // Learning path continuation
    if (userProgress?.activeLearningPath) {
      actions.push({
        id: 'continue-path',
        title: 'Continue Learning Path',
        description: `${userProgress.activeLearningPath.name} - ${userProgress.activeLearningPath.nextMilestone}`,
        icon: <School />,
        color: 'secondary',
        progress: userProgress.activeLearningPath.progress,
        action: () => navigate('/learning-paths'),
      });
    }

    // Get new recommendations
    actions.push({
      id: 'get-recommendations',
      title: 'Get AI Recommendations',
      description: 'Discover problems tailored to your skill level',
      icon: <Psychology />,
      color: 'success',
      action: () => navigate('/recommendations'),
    });

    // Review progress
    actions.push({
      id: 'view-analytics',
      title: 'Review Your Progress',
      description: 'Analyze your learning patterns and achievements',
      icon: <Assessment />,
      color: 'warning',
      action: () => navigate('/analytics'),
    });

    return actions;
  };

  const quickActions = generateQuickActions();

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
          <Typography variant="h6" fontWeight="bold">
            🚀 Quick Actions
          </Typography>
          <Tooltip title="Refresh recommendations">
            <IconButton size="small">
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>

        {/* User Progress Summary */}
        {userProgress && (
          <Box mb={3} p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <Box display="flex" alignItems="center" gap={2}>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    <Star />
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {userProgress.totalProblems > 0
                        ? `${userProgress.problemsSolved} / ${userProgress.totalProblems} Problems`
                        : `${userProgress.problemsSolved} Problems`}
                    </Typography>
                    {userProgress.currentStreak > 0 && (
                      <Typography variant="caption" color="text.secondary">
                        {userProgress.currentStreak} day streak 🔥
                      </Typography>
                    )}
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Box>
                  {userProgress.weeklyGoal > 0 ? (
                    <>
                      <Typography variant="caption" color="text.secondary">
                        Weekly Goal Progress
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={Math.min(100, (userProgress.weeklyProgress / userProgress.weeklyGoal) * 100)}
                        sx={{ mt: 0.5, height: 6, borderRadius: 1 }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        {userProgress.weeklyProgress} / {userProgress.weeklyGoal} problems
                      </Typography>
                    </>
                  ) : (
                    <Typography variant="caption" color="text.secondary">
                      No weekly goal set. Configure one in Settings.
                    </Typography>
                  )}
                </Box>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Quick Action Buttons */}
        <Grid container spacing={2}>
          {quickActions.map((action, index) => (
            <Grid item xs={12} sm={6} key={action.id}>
              <Slide direction="up" in timeout={300 + (index * 100)}>
                <Card
                  variant="outlined"
                  sx={{
                    cursor: 'pointer',
                    transition: 'all 0.2s ease-in-out',
                    border: lastAction === action.id ? 2 : 1,
                    borderColor: lastAction === action.id ? `${action.color}.main` : 'divider',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: 4,
                      borderColor: `${action.color}.main`,
                    },
                  }}
                  onClick={() => handleActionClick(action)}
                >
                  <CardContent sx={{ pb: 2 }}>
                    <Box display="flex" alignItems="flex-start" gap={2}>
                      <Avatar 
                        sx={{ 
                          bgcolor: `${action.color}.main`,
                          width: 40,
                          height: 40,
                        }}
                      >
                        {action.icon}
                      </Avatar>
                      
                      <Box flex={1}>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                          {action.title}
                        </Typography>
                        <Typography 
                          variant="body2" 
                          color="text.secondary"
                          sx={{ mb: 1 }}
                        >
                          {action.description}
                        </Typography>
                        
                        {/* Action metadata */}
                        <Box display="flex" gap={1} alignItems="center" flexWrap="wrap">
                          {action.metadata?.estimatedTime && (
                            <Chip
                              icon={<Timer />}
                              label={`${action.metadata.estimatedTime}min`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                          {action.metadata?.difficulty && (
                            <Chip
                              label={action.metadata.difficulty}
                              size="small"
                              color={
                                action.metadata.difficulty === 'Easy' ? 'success' :
                                action.metadata.difficulty === 'Medium' ? 'warning' : 'error'
                              }
                            />
                          )}
                          
                          {/* Progress bar for learning paths */}
                          {action.progress !== undefined && (
                            <Box sx={{ width: '100%', mt: 1 }}>
                              <LinearProgress 
                                variant="determinate" 
                                value={action.progress}
                                color={action.color}
                                sx={{ height: 4, borderRadius: 1 }}
                              />
                              <Typography variant="caption" color="text.secondary">
                                {action.progress.toFixed(0)}% complete
                              </Typography>
                            </Box>
                          )}
                        </Box>
                      </Box>
                      
                      <ChevronRight color="action" />
                    </Box>
                  </CardContent>
                </Card>
              </Slide>
            </Grid>
          ))}
        </Grid>

        {/* Additional Quick Links */}
        <Box mt={3} pt={2} borderTop={1} borderColor="divider">
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Quick Navigation
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            <Button 
              size="small" 
              onClick={() => navigate('/problems')}
              startIcon={<TrendingUp />}
            >
              Browse Problems
            </Button>
            <Button 
              size="small" 
              onClick={() => navigate('/skill-tree')}
              startIcon={<Star />}
            >
              Skill Tree
            </Button>
            <Button 
              size="small" 
              onClick={() => navigate('/profile')}
              startIcon={<Avatar sx={{ width: 16, height: 16 }} />}
            >
              Profile
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default QuickActionsWidget;
