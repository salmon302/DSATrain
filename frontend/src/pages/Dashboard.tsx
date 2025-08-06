import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Quiz,
  School,
  Star,
  Timeline,
} from '@mui/icons-material';

import { statsAPI, problemsAPI, recommendationsAPI, enhancedStatsAPI, getCurrentUserId } from '../services/api';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [interviewReadiness, setInterviewReadiness] = useState<any>(null);
  const [algorithmRelevance, setAlgorithmRelevance] = useState<any>(null);
  const [recentProblems, setRecentProblems] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const userId = getCurrentUserId();

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        
        // Load stats, interview readiness, and algorithm relevance in parallel
        const [statsData, interviewData, algorithmData, problemsData, recData] = await Promise.all([
          statsAPI.getStats(),
          enhancedStatsAPI.getInterviewReadiness().catch(() => null),
          enhancedStatsAPI.getAlgorithmRelevance().catch(() => null),
          problemsAPI.getProblems({ limit: 5 }),
          recommendationsAPI.getRecommendations({
            user_id: userId,
            limit: 3
          })
        ]);

        setStats(statsData);
        setInterviewReadiness(interviewData);
        setAlgorithmRelevance(algorithmData);
        setRecentProblems(problemsData.problems || []);
        setRecommendations(recData.recommendations || []);

        setError(null);
      } catch (err: any) {
        console.error('Error loading dashboard:', err);
        setError('Unable to load dashboard data. Please check if the API server is running.');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [userId]);

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Loading Dashboard...
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome to DSA Training Platform
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Phase 4 Week 2 - ML-Powered Recommendations
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Stats Overview */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Platform Statistics
              </Typography>
              {stats ? (
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <Quiz color="primary" fontSize="large" />
                      <Typography variant="h5">
                        {stats.total_problems || 0}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Total Problems
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <School color="secondary" fontSize="large" />
                      <Typography variant="h5">
                        {stats.total_solutions || 0}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Solutions
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <Star color="warning" fontSize="large" />
                      <Typography variant="h5">
                        {stats.average_quality?.toFixed(1) || 'N/A'}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Avg Quality
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <TrendingUp color="success" fontSize="large" />
                      <Typography variant="h5">
                        {stats.google_relevance?.toFixed(1) || 'N/A'}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Google Relevance
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              ) : (
                <Typography>No statistics available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="contained"
                  startIcon={<Quiz />}
                  fullWidth
                  href="/problems"
                >
                  Browse Problems
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<TrendingUp />}
                  fullWidth
                  href="/recommendations"
                >
                  Get Recommendations
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<School />}
                  fullWidth
                  href="/learning-paths"
                >
                  Learning Paths
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Interview Readiness */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📝 Interview Readiness
              </Typography>
              {interviewReadiness ? (
                <Box>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Typography variant="h4" color="primary" fontWeight="bold">
                      {interviewReadiness.overview?.readiness_score || 0}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Overall Readiness
                    </Typography>
                  </Box>
                  
                  <Typography variant="subtitle2" gutterBottom>
                    Interview Ready Problems: {interviewReadiness.overview?.total_interview_ready?.toLocaleString() || 0}
                  </Typography>
                  
                  {interviewReadiness.readiness_by_difficulty && (
                    <Box mt={2}>
                      <Typography variant="subtitle2" gutterBottom>By Difficulty:</Typography>
                      {interviewReadiness.readiness_by_difficulty.slice(0, 3).map((item: any, index: number) => (
                        <Box key={index} display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Chip 
                            label={item.difficulty}
                            size="small"
                            color={item.difficulty === 'Easy' ? 'success' : item.difficulty === 'Medium' ? 'warning' : 'error'}
                          />
                          <Typography variant="body2">
                            {item.interview_ready} / {item.total} ({item.readiness_percentage}%)
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  )}

                  {interviewReadiness.recommendations?.focus_areas && (
                    <Box mt={2}>
                      <Typography variant="subtitle2" gutterBottom>Focus Areas:</Typography>
                      <Box display="flex" gap={1} flexWrap="wrap">
                        {interviewReadiness.recommendations.focus_areas.slice(0, 3).map((area: string, index: number) => (
                          <Chip key={index} label={area} size="small" variant="outlined" color="primary" />
                        ))}
                      </Box>
                    </Box>
                  )}
                </Box>
              ) : (
                <Typography color="textSecondary">Loading interview readiness data...</Typography>
              )}
              <Button variant="text" href="/analytics" fullWidth sx={{ mt: 2 }}>
                View Detailed Analysis
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Algorithm Relevance */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🧮 Algorithm Relevance
              </Typography>
              {algorithmRelevance ? (
                <Box>
                  <Box display="flex" gap={2} mb={2}>
                    <Box textAlign="center">
                      <Typography variant="h6" color="success.main" fontWeight="bold">
                        {algorithmRelevance.summary?.high_priority_tags || 0}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        High Priority
                      </Typography>
                    </Box>
                    <Box textAlign="center">
                      <Typography variant="h6" color="warning.main" fontWeight="bold">
                        {algorithmRelevance.summary?.medium_priority_tags || 0}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Medium Priority
                      </Typography>
                    </Box>
                    <Box textAlign="center">
                      <Typography variant="h6" color="info.main" fontWeight="bold">
                        {algorithmRelevance.summary?.total_unique_tags || 0}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Total Tags
                      </Typography>
                    </Box>
                  </Box>

                  {algorithmRelevance.algorithm_analysis && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Top Interview Algorithms:
                      </Typography>
                      {algorithmRelevance.algorithm_analysis.slice(0, 4).map((alg: any, index: number) => (
                        <Box key={index} display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                            {alg.algorithm_tag}
                          </Typography>
                          <Box display="flex" alignItems="center" gap={1}>
                            <Chip 
                              label={alg.interview_priority}
                              size="small"
                              color={alg.interview_priority === 'High' ? 'success' : alg.interview_priority === 'Medium' ? 'warning' : 'default'}
                            />
                            <Typography variant="caption" color="textSecondary">
                              {alg.problem_count} problems
                            </Typography>
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  )}
                </Box>
              ) : (
                <Typography color="textSecondary">Loading algorithm relevance data...</Typography>
              )}
              <Button variant="text" href="/problems" fullWidth sx={{ mt: 2 }}>
                Browse by Algorithm
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* ML Recommendations */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🤖 ML Recommendations for You
              </Typography>
              {recommendations.length > 0 ? (
                recommendations.map((rec, index) => (
                  <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {rec.title}
                    </Typography>
                    <Box display="flex" gap={1} my={1}>
                      <Chip label={rec.difficulty} size="small" color="primary" />
                      <Chip 
                        label={`Score: ${rec.recommendation_score?.toFixed(2) || 'N/A'}`} 
                        size="small" 
                        variant="outlined" 
                      />
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      {rec.recommendation_reasoning || 'No reasoning available'}
                    </Typography>
                  </Box>
                ))
              ) : (
                <Typography>No personalized recommendations available yet.</Typography>
              )}
              <Button variant="text" href="/recommendations" fullWidth>
                View All Recommendations
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Problems */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Problems
              </Typography>
              {recentProblems.length > 0 ? (
                recentProblems.map((problem, index) => (
                  <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {problem.title}
                    </Typography>
                    <Box display="flex" gap={1} my={1}>
                      <Chip label={problem.difficulty} size="small" color="primary" />
                      <Chip label={problem.platform} size="small" variant="outlined" />
                      {problem.algorithm_tags?.slice(0, 2).map((tag: string, i: number) => (
                        <Chip key={i} label={tag} size="small" variant="outlined" />
                      ))}
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      Quality: {problem.quality_score?.toFixed(1) || 'N/A'} | 
                      Google Relevance: {problem.google_interview_relevance?.toFixed(1) || 'N/A'}
                    </Typography>
                  </Box>
                ))
              ) : (
                <Typography>No problems available.</Typography>
              )}
              <Button variant="text" href="/problems" fullWidth>
                Browse All Problems
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* User Info */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Your Learning Journey
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                <Timeline color="primary" />
                <Box>
                  <Typography variant="body1">
                    User ID: <code>{userId}</code>
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Track your progress and get personalized recommendations based on your activity.
                  </Typography>
                </Box>
              </Box>
              <Box mt={2}>
                <Button variant="outlined" href="/analytics">
                  View Your Analytics
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
