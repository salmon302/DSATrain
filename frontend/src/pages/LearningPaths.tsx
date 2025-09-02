import React, { useState, useEffect, useCallback } from 'react';
import { Box, Typography, Alert, Card, CardContent, Grid, Button, LinearProgress, Stepper, Step, StepLabel, StepContent, Chip, Dialog, DialogTitle, DialogContent, DialogActions, FormControl, InputLabel, Select, MenuItem, TextField, Avatar, List, ListItemAvatar, ListItemText, ListItemButton, Divider, IconButton, Tooltip } from '@mui/material';
import { School, Psychology, Code, Star, AccessTime, Assignment, PlayArrow, Add, Refresh, RocketLaunch } from '@mui/icons-material';

import { 
  learningPathsAPI, 
  trackingAPI, 
  getCurrentUserId, 
  generateSessionId,
  LearningPath,
  WeeklyPlan,
  Problem
} from '../services/api';

const LearningPaths: React.FC = () => {
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [currentPath, setCurrentPath] = useState<LearningPath | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newPathForm, setNewPathForm] = useState({
    goal: 'google_interview',
    level: 'intermediate',
    duration_weeks: 8
  });
  const [activeWeek, setActiveWeek] = useState(0);

  const userId = getCurrentUserId();
  const sessionId = React.useRef<string>(generateSessionId()).current;

  // Generate learning path
  const { goal, level, duration_weeks } = newPathForm;
  const generateLearningPath = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await learningPathsAPI.generateLearningPath({
        user_id: userId,
        goal,
        level,
        duration_weeks
      });

      if (response.learning_path) {
        setCurrentPath(response.learning_path);
        setLearningPaths(prev => [...prev, response.learning_path]);
        setShowCreateDialog(false);

        setSuccess(`Learning path created: ${response.learning_path.name || 'Personalized Plan'}`);

        // Track learning path generation
    await trackingAPI.trackInteraction({
          user_id: userId,
          problem_id: 'learning_path_generated',
          action: 'generated',
          session_id: sessionId,
          // Avoid referencing the entire object to keep useCallback deps precise
          metadata: JSON.stringify({
      goal,
      level,
      duration_weeks,
          }),
        });
      }

    } catch (err: any) {
      console.error('Error generating learning path:', err);
      setError('Failed to generate learning path. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [userId, sessionId, goal, level, duration_weeks]);

  // Quick start for beginners
  const quickStartBeginner = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await learningPathsAPI.quickStart({
        user_id: userId,
        hours_per_week: 5,
        goals: ['foundations']
      });
      if (res?.learning_path) {
        setCurrentPath(res.learning_path);
        setLearningPaths(prev => [...prev, res.learning_path]);
        setShowCreateDialog(false);
        setSuccess(`Beginner quick start created: ${res.learning_path.name || 'Beginner Plan'}`);
      }
    } catch (err: any) {
      console.error('Quick start failed', err);
      setError('Quick start failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Track problem start from learning path
  const trackProblemStart = async (problem: Problem, week: number) => {
    try {
      await trackingAPI.trackInteraction({
        user_id: userId,
        problem_id: problem.id,
        action: 'attempted',
        session_id: sessionId,
        metadata: JSON.stringify({ 
          source: 'learning_path',
          week: week + 1,
          goal: currentPath?.target_goal
        })
      });
    } catch (error) {
      console.error('Failed to track problem start:', error);
    }
  };

  // Get difficulty color
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  // Get goal display name
  const getGoalDisplayName = (goal: string) => {
    const goalMap: { [key: string]: string } = {
      'google_interview': 'Google Interview Preparation',
      'faang_preparation': 'FAANG Interview Prep',
      'competitive_programming': 'Competitive Programming',
      'algorithm_mastery': 'Algorithm Mastery',
      'data_structures': 'Data Structures Focus'
    };
    return goalMap[goal] || goal;
  };

  // Get level display name
  const getLevelDisplayName = (level: string) => {
    const levelMap: { [key: string]: string } = {
      'beginner': 'Beginner',
      'intermediate': 'Intermediate',
      'advanced': 'Advanced',
      'expert': 'Expert'
    };
    return levelMap[level] || level;
  };

  useEffect(() => {
    // Auto-generate a sample learning path on load
    if (learningPaths.length === 0) {
      setTimeout(() => {
    void generateLearningPath();
      }, 1000);
    }
  }, [learningPaths.length, generateLearningPath]);

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            🎓 Learning Paths
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            ML-generated personalized study plans tailored to your goals and timeline
          </Typography>
        </Box>
        
        <Box display="flex" gap={1}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setShowCreateDialog(true)}
          >
            Create Path
          </Button>
          <Tooltip title="Refresh Current Path">
            <IconButton onClick={generateLearningPath}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            startIcon={<RocketLaunch />}
            onClick={quickStartBeginner}
          >
            Beginner Quick Start
          </Button>
        </Box>
      </Box>

      {/* Notifications */}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body1" gutterBottom>
            Generating your personalized learning path...
          </Typography>
          <LinearProgress />
        </Box>
      )}

      {/* Current Learning Path */}
      {currentPath && (
        <Grid container spacing={3}>
          {/* Path Overview */}
          <Grid item xs={12} md={4}>
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={3}>
                  <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
                    <School sx={{ fontSize: 28 }} />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      Your Learning Path
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {getGoalDisplayName(currentPath.target_goal)}
                    </Typography>
                  </Box>
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Current Level
                    </Typography>
                    <Chip 
                      label={getLevelDisplayName(currentPath.current_level)}
                      color="primary"
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Duration
                    </Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {currentPath.duration_weeks} weeks
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Total Problems
                    </Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {currentPath.total_problems}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Total Hours
                    </Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {currentPath.estimated_completion_time.total_hours}h
                    </Typography>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                {/* Weekly Breakdown */}
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Time Commitment
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {currentPath.estimated_completion_time.hours_per_week} hours per week
                </Typography>

                <Box display="flex" gap={1} flexWrap="wrap" mt={2}>
                  <Chip 
                    label={`${currentPath.estimated_completion_time.easy_problems} Easy`}
                    color="success"
                    size="small"
                    variant="outlined"
                  />
                  <Chip 
                    label={`${currentPath.estimated_completion_time.medium_problems} Medium`}
                    color="warning"
                    size="small"
                    variant="outlined"
                  />
                  <Chip 
                    label={`${currentPath.estimated_completion_time.hard_problems} Hard`}
                    color="error"
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>

            {/* Progress Card */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📈 Progress Overview
                </Typography>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <LinearProgress
                    variant="determinate"
                    value={(activeWeek + 1) / currentPath.duration_weeks * 100}
                    sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="body2" fontWeight="bold">
                    Week {activeWeek + 1}/{currentPath.duration_weeks}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Complete your current week to unlock the next phase
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Weekly Plan */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📅 Weekly Study Plan
                </Typography>
                
                <Stepper activeStep={activeWeek} orientation="vertical">
                  {currentPath.weekly_plan.map((week: WeeklyPlan, index) => (
                    <Step key={index}>
                      <StepLabel
                        onClick={() => setActiveWeek(index)}
                        sx={{ cursor: 'pointer' }}
                      >
                        <Box display="flex" alignItems="center" gap={2}>
                          <Typography variant="subtitle1" fontWeight="bold">
                            Week {week.week}
                          </Typography>
                          <Chip 
                            label={`${week.estimated_hours}h`}
                            size="small"
                            icon={<AccessTime />}
                          />
                          <Chip 
                            label={`${week.problems.length} problems`}
                            size="small"
                            icon={<Assignment />}
                          />
                        </Box>
                      </StepLabel>
                      <StepContent>
                        {/* Focus Areas */}
                        <Box mb={2}>
                          <Typography variant="subtitle2" gutterBottom>
                            Focus Areas:
                          </Typography>
                          <Box display="flex" gap={1} flexWrap="wrap">
                            {week.focus_areas.map((area, areaIndex) => (
                              <Chip 
                                key={areaIndex}
                                label={area}
                                size="small"
                                color="secondary"
                                variant="outlined"
                              />
                            ))}
                          </Box>
                        </Box>

                        {/* Problems */}
                        <Typography variant="subtitle2" gutterBottom>
                          Problems to Solve:
                        </Typography>
                        <List dense>
                          {week.problems.map((problem: Problem, problemIndex) => (
                            <ListItemButton
                              key={problemIndex}
                              onClick={() => trackProblemStart(problem, index)}
                              sx={{ 
                                border: '1px solid',
                                borderColor: 'divider',
                                borderRadius: 1,
                                mb: 1
                              }}
                            >
                              <ListItemAvatar>
                                <Avatar sx={{ width: 32, height: 32 }}>
                                  <Code sx={{ fontSize: 18 }} />
                                </Avatar>
                              </ListItemAvatar>
                              <ListItemText
                                primary={
                                  <Box display="flex" alignItems="center" gap={1}>
                                    <Typography variant="body1" fontWeight="medium">
                                      {problem.title}
                                    </Typography>
                                    <Chip 
                                      label={problem.difficulty}
                                      size="small"
                                      color={getDifficultyColor(problem.difficulty) as any}
                                    />
                                  </Box>
                                }
                                secondary={
                                  <Box display="flex" gap={1} mt={0.5}>
                                    <Chip 
                                      label={problem.platform}
                                      size="small"
                                      variant="outlined"
                                    />
                                    <Chip 
                                      label={`Quality: ${problem.quality_score?.toFixed(1) || 'N/A'}`}
                                      size="small"
                                      variant="outlined"
                                      icon={<Star sx={{ fontSize: 14 }} />}
                                    />
                                    {problem.algorithm_tags?.slice(0, 2).map((tag, tagIndex) => (
                                      <Chip 
                                        key={tagIndex}
                                        label={tag}
                                        size="small"
                                        variant="outlined"
                                      />
                                    ))}
                                  </Box>
                                }
                              />
                              <IconButton color="primary">
                                <PlayArrow />
                              </IconButton>
                            </ListItemButton>
                          ))}
                        </List>

                        <Box mt={2}>
                          <Button
                            variant="outlined"
                            onClick={() => setActiveWeek(Math.min(index + 1, currentPath.duration_weeks - 1))}
                            disabled={index === currentPath.duration_weeks - 1}
                          >
                            Complete Week {week.week}
                          </Button>
                        </Box>
                      </StepContent>
                    </Step>
                  ))}
                </Stepper>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Empty State */}
      {!currentPath && !loading && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <School sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Learning Path Created Yet
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3}>
              Create a personalized learning path tailored to your goals and timeline.
            </Typography>
            <Button 
              variant="contained" 
              startIcon={<Add />}
              onClick={() => setShowCreateDialog(true)}
            >
              Create Your First Learning Path
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Create Learning Path Dialog */}
      <Dialog 
        open={showCreateDialog} 
        onClose={() => setShowCreateDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Create Personalized Learning Path
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            Our ML algorithm will generate a customized study plan based on your goals and timeline.
          </Typography>
          
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Learning Goal</InputLabel>
                <Select
                  value={newPathForm.goal}
                  onChange={(e) => setNewPathForm(prev => ({ ...prev, goal: e.target.value }))}
                >
                  <MenuItem value="google_interview">Google Interview Preparation</MenuItem>
                  <MenuItem value="faang_preparation">FAANG Interview Prep</MenuItem>
                  <MenuItem value="competitive_programming">Competitive Programming</MenuItem>
                  <MenuItem value="algorithm_mastery">Algorithm Mastery</MenuItem>
                  <MenuItem value="data_structures">Data Structures Focus</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Current Level</InputLabel>
                <Select
                  value={newPathForm.level}
                  onChange={(e) => setNewPathForm(prev => ({ ...prev, level: e.target.value }))}
                >
                  <MenuItem value="beginner">Beginner</MenuItem>
                  <MenuItem value="intermediate">Intermediate</MenuItem>
                  <MenuItem value="advanced">Advanced</MenuItem>
                  <MenuItem value="expert">Expert</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Duration (weeks)"
                type="number"
                value={newPathForm.duration_weeks}
                onChange={(e) => setNewPathForm(prev => ({ 
                  ...prev, 
                  duration_weeks: parseInt(e.target.value) || 8 
                }))}
                inputProps={{ min: 2, max: 24 }}
                helperText="Recommended: 8-12 weeks for comprehensive preparation"
              />
            </Grid>
          </Grid>

          {/* Quick Start Action */}
          <Box mt={2}>
            <Button
              size="small"
              startIcon={<RocketLaunch />}
              onClick={quickStartBeginner}
            >
              Use Beginner Quick Start
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCreateDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={generateLearningPath}
            disabled={loading}
            startIcon={<Psychology />}
          >
            {loading ? 'Generating...' : 'Generate Path'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LearningPaths;
