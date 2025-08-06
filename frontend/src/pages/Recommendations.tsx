import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Alert,
  Card,
  CardContent,
  Grid,
  Button,
  LinearProgress,
  Chip,
  Avatar,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Switch,
  FormControlLabel,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
} from '@mui/material';
import {
  Psychology,
  TrendingUp,
  Star,
  AutoAwesome,
  FilterList,
  Refresh,
  Lightbulb,
  School,
  BusinessCenter,
  Timer,
  ExpandMore,
  PlayArrow,
  Bookmark,
  Share,
  ThumbUp,
  ThumbDown,
} from '@mui/icons-material';

import { 
  recommendationsAPI, 
  problemsAPI, 
  trackingAPI, 
  getCurrentUserId, 
  generateSessionId,
  Problem,
  Recommendation 
} from '../services/api';

interface RecommendationWithRating extends Recommendation {
  userRating?: 'helpful' | 'not-helpful' | null;
}

const Recommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<RecommendationWithRating[]>([]);
  const [similarProblems, setSimilarProblems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [mlTraining, setMlTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
  const [preferences, setPreferences] = useState({
    difficulty_level: '',
    focus_area: '',
    limit: 10,
    personalizedMode: true
  });
  const [showPreferences, setShowPreferences] = useState(false);

  const userId = getCurrentUserId();
  const sessionId = generateSessionId();

  // Load recommendations
  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = {
        user_id: preferences.personalizedMode ? userId : undefined,
        limit: preferences.limit
      };

      if (preferences.difficulty_level) {
        params.difficulty_level = preferences.difficulty_level;
      }
      if (preferences.focus_area) {
        params.focus_area = preferences.focus_area;
      }

      const response = await recommendationsAPI.getRecommendations(params);
      
      // Add user rating state to recommendations
      const recommendationsWithRating = (response.recommendations || []).map((rec: Recommendation) => ({
        ...rec,
        userRating: null
      }));
      
      setRecommendations(recommendationsWithRating);

      // Track recommendation view
      await trackingAPI.trackInteraction({
        user_id: userId,
        problem_id: 'recommendations_page',
        action: 'viewed',
        session_id: sessionId,
        metadata: JSON.stringify({ 
          recommendation_count: recommendationsWithRating.length,
          personalized: preferences.personalizedMode
        })
      });

    } catch (err: any) {
      console.error('Error loading recommendations:', err);
      setError('Failed to load recommendations. Please check if the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  // Train ML models
  const trainMLModels = async () => {
    try {
      setMlTraining(true);
      await recommendationsAPI.trainModels();
      
      // Reload recommendations after training
      await loadRecommendations();
      
      // Show success message
      setError(null);
    } catch (err: any) {
      console.error('Error training ML models:', err);
      setError('Failed to train ML models. Please try again.');
    } finally {
      setMlTraining(false);
    }
  };

  // Load similar problems for a specific problem
  const loadSimilarProblems = async (problemId: string) => {
    try {
      const response = await recommendationsAPI.getSimilarProblems(problemId, 5);
      setSimilarProblems(response.similar_problems || []);
    } catch (error) {
      console.error('Error loading similar problems:', error);
      setSimilarProblems([]);
    }
  };

  // Handle recommendation rating
  const handleRecommendationRating = async (
    recommendation: RecommendationWithRating, 
    rating: 'helpful' | 'not-helpful'
  ) => {
    try {
      // Update local state
      setRecommendations(prev => 
        prev.map(rec => 
          rec.id === recommendation.id 
            ? { ...rec, userRating: rating }
            : rec
        )
      );

      // Track the rating
      await trackingAPI.trackInteraction({
        user_id: userId,
        problem_id: recommendation.id,
        action: 'rating',
        session_id: sessionId,
        metadata: JSON.stringify({ 
          rating,
          recommendation_score: recommendation.recommendation_score,
          difficulty: recommendation.difficulty
        })
      });

    } catch (error) {
      console.error('Error rating recommendation:', error);
    }
  };

  // Handle problem selection
  const handleProblemSelect = async (problem: any) => {
    setSelectedProblem(problem);
    await loadSimilarProblems(problem.id);
    
    // Track problem view
    await trackingAPI.trackInteraction({
      user_id: userId,
      problem_id: problem.id,
      action: 'viewed',
      session_id: sessionId,
      metadata: JSON.stringify({ source: 'recommendations' })
    });
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

  // Get recommendation score color
  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  useEffect(() => {
    loadRecommendations();
  }, []);

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            🤖 ML-Powered Recommendations
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            Personalized problem suggestions based on your learning patterns and goals
          </Typography>
        </Box>
        
        <Box display="flex" gap={1}>
          <Tooltip title="Configure Preferences">
            <IconButton onClick={() => setShowPreferences(!showPreferences)}>
              <FilterList />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh Recommendations">
            <IconButton onClick={loadRecommendations}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Train ML Models">
            <Button
              variant="outlined"
              onClick={trainMLModels}
              disabled={mlTraining}
              startIcon={mlTraining ? <CircularProgress size={16} /> : <Psychology />}
            >
              {mlTraining ? 'Training...' : 'Train ML'}
            </Button>
          </Tooltip>
        </Box>
      </Box>

      {/* Preferences Panel */}
      {showPreferences && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recommendation Preferences
            </Typography>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6} md={3}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.personalizedMode}
                      onChange={(e) => setPreferences(prev => ({ 
                        ...prev, 
                        personalizedMode: e.target.checked 
                      }))}
                    />
                  }
                  label="Personalized Mode"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Difficulty Level</InputLabel>
                  <Select
                    value={preferences.difficulty_level}
                    onChange={(e) => setPreferences(prev => ({ 
                      ...prev, 
                      difficulty_level: e.target.value 
                    }))}
                  >
                    <MenuItem value="">All Levels</MenuItem>
                    <MenuItem value="Easy">Easy</MenuItem>
                    <MenuItem value="Medium">Medium</MenuItem>
                    <MenuItem value="Hard">Hard</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Focus Area"
                  value={preferences.focus_area}
                  onChange={(e) => setPreferences(prev => ({ 
                    ...prev, 
                    focus_area: e.target.value 
                  }))}
                  placeholder="e.g., Dynamic Programming"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Number of Recommendations"
                  type="number"
                  value={preferences.limit}
                  onChange={(e) => setPreferences(prev => ({ 
                    ...prev, 
                    limit: parseInt(e.target.value) || 10 
                  }))}
                  inputProps={{ min: 1, max: 50 }}
                />
              </Grid>
            </Grid>
            <Box mt={2} display="flex" justifyContent="flex-end">
              <Button 
                variant="contained" 
                onClick={() => {
                  loadRecommendations();
                  setShowPreferences(false);
                }}
              >
                Apply Preferences
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && <LinearProgress sx={{ mb: 3 }} />}

      {/* ML Training Status */}
      {mlTraining && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center" gap={2}>
            <CircularProgress size={20} />
            <Typography>
              Training ML models with current data. This may take a moment...
            </Typography>
          </Box>
        </Alert>
      )}

      {/* Personalization Status */}
      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar sx={{ bgcolor: 'white', color: 'primary.main' }}>
              <AutoAwesome />
            </Avatar>
            <Box>
              <Typography variant="h6" color="white" fontWeight="bold">
                {preferences.personalizedMode ? 'Personalized Mode Active' : 'General Recommendations'}
              </Typography>
              <Typography variant="body2" color="white" sx={{ opacity: 0.9 }}>
                {preferences.personalizedMode 
                  ? `Recommendations tailored for user: ${userId}`
                  : 'Showing general high-quality problems'
                }
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Recommendations Grid */}
      <Grid container spacing={3}>
        {recommendations.map((recommendation, index) => (
          <Grid item xs={12} md={6} lg={4} key={recommendation.id}>
            <Card 
              sx={{ 
                height: '100%',
                cursor: 'pointer',
                position: 'relative',
                '&:hover': { 
                  boxShadow: 6,
                  transform: 'translateY(-2px)',
                  transition: 'all 0.2s ease-in-out'
                }
              }}
              onClick={() => handleProblemSelect(recommendation)}
            >
              {/* Recommendation Rank Badge */}
              <Box
                sx={{
                  position: 'absolute',
                  top: 8,
                  left: 8,
                  backgroundColor: 'primary.main',
                  color: 'white',
                  borderRadius: '50%',
                  width: 30,
                  height: 30,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.8rem',
                  fontWeight: 'bold',
                  zIndex: 1
                }}
              >
                #{index + 1}
              </Box>

              <CardContent sx={{ pt: 5 }}>
                <Typography 
                  variant="h6" 
                  fontWeight="bold" 
                  gutterBottom
                  sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    minHeight: '3rem'
                  }}
                >
                  {recommendation.title}
                </Typography>

                {/* Recommendation Score */}
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <Psychology color="primary" />
                  <Typography variant="body2" fontWeight="bold">
                    ML Score: 
                  </Typography>
                  <Chip
                    label={`${(recommendation.recommendation_score * 100).toFixed(0)}%`}
                    size="small"
                    color={getScoreColor(recommendation.recommendation_score) as any}
                  />
                </Box>

                {/* Problem Details */}
                <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                  <Chip 
                    label={recommendation.difficulty}
                    size="small"
                    color={getDifficultyColor(recommendation.difficulty) as any}
                  />
                  <Chip
                    label={`${recommendation.google_interview_relevance?.toFixed(0) || 0}% Google`}
                    size="small"
                    variant="outlined"
                    icon={<BusinessCenter sx={{ fontSize: 14 }} />}
                  />
                  <Chip
                    label={`Quality: ${recommendation.quality_score?.toFixed(1) || 'N/A'}`}
                    size="small"
                    variant="outlined"
                    icon={<Star sx={{ fontSize: 14 }} />}
                  />
                </Box>

                {/* Algorithm Tags */}
                <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                  {recommendation.algorithm_tags?.slice(0, 2).map((tag, tagIndex) => (
                    <Chip key={tagIndex} label={tag} size="small" variant="outlined" />
                  ))}
                  {recommendation.algorithm_tags && recommendation.algorithm_tags.length > 2 && (
                    <Chip 
                      label={`+${recommendation.algorithm_tags.length - 2} more`} 
                      size="small" 
                      variant="outlined" 
                    />
                  )}
                </Box>

                {/* Recommendation Reasoning */}
                <Typography 
                  variant="body2" 
                  color="textSecondary" 
                  sx={{ 
                    fontStyle: 'italic',
                    mb: 2,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical'
                  }}
                >
                  💡 {recommendation.recommendation_reasoning || 'High-quality problem recommended for your learning path.'}
                </Typography>

                <Divider sx={{ my: 2 }} />

                {/* Action Buttons */}
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" gap={1}>
                    <Tooltip title="Start Solving">
                      <IconButton 
                        size="small" 
                        color="primary"
                        onClick={(e) => {
                          e.stopPropagation();
                          trackingAPI.trackInteraction({
                            user_id: userId,
                            problem_id: recommendation.id,
                            action: 'attempted',
                            session_id: sessionId
                          });
                        }}
                      >
                        <PlayArrow />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Bookmark">
                      <IconButton 
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          trackingAPI.trackInteraction({
                            user_id: userId,
                            problem_id: recommendation.id,
                            action: 'bookmarked',
                            session_id: sessionId
                          });
                        }}
                      >
                        <Bookmark />
                      </IconButton>
                    </Tooltip>
                  </Box>

                  {/* Rating Buttons */}
                  <Box display="flex" gap={1}>
                    <Tooltip title="Helpful Recommendation">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRecommendationRating(recommendation, 'helpful');
                        }}
                        color={recommendation.userRating === 'helpful' ? 'success' : 'default'}
                      >
                        <ThumbUp fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Not Helpful">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRecommendationRating(recommendation, 'not-helpful');
                        }}
                        color={recommendation.userRating === 'not-helpful' ? 'error' : 'default'}
                      >
                        <ThumbDown fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Empty State */}
      {!loading && recommendations.length === 0 && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <Psychology sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No recommendations available
            </Typography>
            <Typography variant="body2" color="textSecondary" mb={3}>
              {preferences.personalizedMode 
                ? 'Start solving problems to get personalized recommendations.'
                : 'Try enabling personalized mode or adjusting your preferences.'
              }
            </Typography>
            <Box display="flex" gap={2} justifyContent="center">
              <Button 
                variant="outlined" 
                onClick={() => setPreferences(prev => ({ ...prev, personalizedMode: !prev.personalizedMode }))}
              >
                {preferences.personalizedMode ? 'Try General Mode' : 'Enable Personalized Mode'}
              </Button>
              <Button variant="contained" onClick={trainMLModels}>
                Train ML Models
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Problem Details Dialog */}
      <Dialog 
        open={!!selectedProblem} 
        onClose={() => setSelectedProblem(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedProblem && (
          <>
            <DialogTitle>
              <Typography variant="h5" fontWeight="bold">
                {selectedProblem.title}
              </Typography>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2} mb={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>Problem Details</Typography>
                  <Box display="flex" flexDirection="column" gap={1}>
                    <Box display="flex" justifyContent="space-between">
                      <Typography>Difficulty:</Typography>
                      <Chip 
                        label={selectedProblem.difficulty}
                        size="small"
                        color={getDifficultyColor(selectedProblem.difficulty) as any}
                      />
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Typography>Quality Score:</Typography>
                      <Typography fontWeight="bold">
                        {selectedProblem.quality_score?.toFixed(1) || 'N/A'}/100
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Typography>Google Relevance:</Typography>
                      <Typography fontWeight="bold">
                        {selectedProblem.google_interview_relevance?.toFixed(1) || 'N/A'}%
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>Algorithm Tags</Typography>
                  <Box display="flex" gap={1} flexWrap="wrap">
                    {selectedProblem.algorithm_tags?.map((tag, index) => (
                      <Chip key={index} label={tag} size="small" color="primary" variant="outlined" />
                    ))}
                  </Box>
                </Grid>
              </Grid>

              {/* Similar Problems */}
              {similarProblems.length > 0 && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">
                      Similar Problems ({similarProblems.length})
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      {similarProblems.map((problem, index) => (
                        <Grid item xs={12} key={index}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography variant="subtitle1" fontWeight="bold">
                                {problem.title}
                              </Typography>
                              <Box display="flex" gap={1} mt={1}>
                                <Chip 
                                  label={problem.difficulty}
                                  size="small"
                                  color={getDifficultyColor(problem.difficulty) as any}
                                />
                                <Chip
                                  label={`Similarity: ${(problem.similarity_score * 100).toFixed(0)}%`}
                                  size="small"
                                  variant="outlined"
                                />
                              </Box>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedProblem(null)}>Close</Button>
              <Button 
                variant="contained" 
                startIcon={<PlayArrow />}
                onClick={() => {
                  // Track problem attempt
                  trackingAPI.trackInteraction({
                    user_id: userId,
                    problem_id: selectedProblem.id,
                    action: 'attempted',
                    session_id: sessionId
                  });
                  setSelectedProblem(null);
                }}
              >
                Start Solving
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default Recommendations;
