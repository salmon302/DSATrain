import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Chip,
  LinearProgress,
  Card,
  CardContent,
  CardActions,
  Button,
  Tooltip,
  IconButton,
  Collapse,
  Badge,
  Avatar,
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  TrendingUp as TrendingUpIcon,
  Stars as StarsIcon,
  Psychology as PsychologyIcon,
  Group as GroupIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

// Skill Tree Component
const SkillTreeVisualization = () => {
  const [skillTreeData, setSkillTreeData] = useState(null);
  const [userProgress, setUserProgress] = useState(null);
  const [expandedColumns, setExpandedColumns] = useState({});
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [similarProblems, setSimilarProblems] = useState([]);
  const [showConfidenceOverlay, setShowConfidenceOverlay] = useState(true);
  const [loading, setLoading] = useState(true);

  // API Base URL
  const API_BASE = 'http://localhost:8001';
  const USER_ID = 'demo_user_2025';

  useEffect(() => {
    loadSkillTreeData();
    loadUserProgress();
  }, []);

  const loadSkillTreeData = async () => {
    try {
      const response = await fetch(`${API_BASE}/skill-tree/overview?user_id=${USER_ID}`);
      const data = await response.json();
      setSkillTreeData(data);
    } catch (error) {
      console.error('Error loading skill tree:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserProgress = async () => {
    try {
      const response = await fetch(`${API_BASE}/skill-tree/user/${USER_ID}/progress`);
      const data = await response.json();
      setUserProgress(data);
    } catch (error) {
      console.error('Error loading user progress:', error);
    }
  };

  const loadSimilarProblems = async (problemId) => {
    try {
      const response = await fetch(`${API_BASE}/skill-tree/similar/${problemId}`);
      const data = await response.json();
      setSimilarProblems(data);
    } catch (error) {
      console.error('Error loading similar problems:', error);
    }
  };

  const updateConfidence = async (problemId, confidenceLevel) => {
    try {
      await fetch(`${API_BASE}/skill-tree/confidence?user_id=${USER_ID}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: problemId,
          confidence_level: confidenceLevel,
          solve_time_seconds: Math.floor(Math.random() * 3600) + 300,
          hints_used: Math.floor(Math.random() * 3)
        })
      });
      loadUserProgress(); // Refresh progress
    } catch (error) {
      console.error('Error updating confidence:', error);
    }
  };

  const toggleColumnExpansion = (skillArea) => {
    setExpandedColumns(prev => ({
      ...prev,
      [skillArea]: !prev[skillArea]
    }));
  };

  const handleProblemClick = (problem) => {
    setSelectedProblem(problem);
    loadSimilarProblems(problem.id);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy': return '#4caf50';
      case 'Medium': return '#ff9800';
      case 'Hard': return '#f44336';
      default: return '#757575';
    }
  };

  const getConfidenceLevel = (problemId) => {
    if (!userProgress?.skill_progress) return 0;
    
    for (const skillArea of Object.values(userProgress.skill_progress)) {
      if (skillArea.confidence_levels && skillArea.confidence_levels[problemId]) {
        return skillArea.confidence_levels[problemId].confidence_level;
      }
    }
    return 0;
  };

  const renderSkillColumn = (column, index) => {
    const isExpanded = expandedColumns[column.skill_area];
    const userSkillProgress = userProgress?.skill_progress?.[column.skill_area];
    
    return (
      <Grid item xs={12} sm={6} md={4} lg={3} key={column.skill_area}>
        <Paper 
          elevation={3} 
          sx={{ 
            height: '100%', 
            p: 2, 
            borderTop: `4px solid ${index % 4 === 0 ? '#1976d2' : index % 4 === 1 ? '#4caf50' : index % 4 === 2 ? '#ff9800' : '#9c27b0'}`,
            transition: 'transform 0.2s',
            '&:hover': { transform: 'translateY(-2px)' }
          }}
        >
          {/* Column Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ 
              bgcolor: index % 4 === 0 ? '#1976d2' : index % 4 === 1 ? '#4caf50' : index % 4 === 2 ? '#ff9800' : '#9c27b0',
              mr: 1, 
              width: 32, 
              height: 32 
            }}>
              {column.skill_area.charAt(0).toUpperCase()}
            </Avatar>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>
                {column.skill_area.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {column.total_problems} problems
              </Typography>
            </Box>
            <IconButton 
              size="small" 
              onClick={() => toggleColumnExpansion(column.skill_area)}
            >
              {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>

          {/* Mastery Progress */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <TrendingUpIcon sx={{ fontSize: 16, mr: 1, color: 'primary.main' }} />
              <Typography variant="body2">
                Mastery: {column.mastery_percentage.toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={column.mastery_percentage} 
              sx={{ height: 6, borderRadius: 3 }}
            />
            {userSkillProgress && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                Attempted: {userSkillProgress.problems_attempted} | 
                Avg Confidence: {userSkillProgress.average_confidence.toFixed(1)}/5
              </Typography>
            )}
          </Box>

          {/* Difficulty Overview */}
          <Box sx={{ mb: 2 }}>
            {['Easy', 'Medium', 'Hard'].map(difficulty => {
              const count = column.difficulty_levels[difficulty].length;
              return count > 0 ? (
                <Chip
                  key={difficulty}
                  label={`${difficulty}: ${count}`}
                  size="small"
                  sx={{ 
                    mr: 0.5, 
                    mb: 0.5,
                    bgcolor: getDifficultyColor(difficulty),
                    color: 'white',
                    fontSize: '0.75rem'
                  }}
                />
              ) : null;
            })}
          </Box>

          {/* Expanded Problem List */}
          <Collapse in={isExpanded}>
            <Box sx={{ maxHeight: '400px', overflow: 'auto' }}>
              {['Easy', 'Medium', 'Hard'].map(difficulty => {
                const problems = column.difficulty_levels[difficulty];
                return problems.length > 0 ? (
                  <Box key={difficulty} sx={{ mb: 2 }}>
                    <Typography 
                      variant="subtitle2" 
                      sx={{ 
                        color: getDifficultyColor(difficulty),
                        fontWeight: 600,
                        mb: 1
                      }}
                    >
                      {difficulty} Problems
                    </Typography>
                    {problems.map(problem => {
                      const confidenceLevel = getConfidenceLevel(problem.id);
                      return (
                        <Card
                          key={problem.id}
                          sx={{ 
                            mb: 1, 
                            cursor: 'pointer',
                            '&:hover': { bgcolor: 'action.hover' },
                            border: confidenceLevel > 0 && showConfidenceOverlay ? 
                              `2px solid ${confidenceLevel >= 4 ? '#4caf50' : confidenceLevel >= 3 ? '#ff9800' : '#f44336'}` : 
                              '1px solid #e0e0e0'
                          }}
                          onClick={() => handleProblemClick(problem)}
                        >
                          <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                            <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                              <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                                <Typography 
                                  variant="body2" 
                                  sx={{ 
                                    fontWeight: 500,
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    whiteSpace: 'nowrap'
                                  }}
                                >
                                  {problem.title}
                                </Typography>
                                <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                                  <Typography variant="caption" color="text.secondary">
                                    Sub-level: {problem.sub_difficulty_level}
                                  </Typography>
                                  {problem.google_interview_relevance > 70 && (
                                    <Tooltip title="High Google Interview Relevance">
                                      <StarsIcon sx={{ fontSize: 14, ml: 1, color: 'warning.main' }} />
                                    </Tooltip>
                                  )}
                                </Box>
                              </Box>
                              {showConfidenceOverlay && confidenceLevel > 0 && (
                                <Badge 
                                  badgeContent={confidenceLevel} 
                                  color={confidenceLevel >= 4 ? 'success' : confidenceLevel >= 3 ? 'warning' : 'error'}
                                  sx={{ ml: 1 }}
                                >
                                  <PsychologyIcon sx={{ fontSize: 16 }} />
                                </Badge>
                              )}
                            </Box>
                            <Box sx={{ mt: 1 }}>
                              {problem.algorithm_tags.slice(0, 3).map(tag => (
                                <Chip
                                  key={tag}
                                  label={tag}
                                  size="small"
                                  variant="outlined"
                                  sx={{ fontSize: '0.7rem', height: 20, mr: 0.5 }}
                                />
                              ))}
                            </Box>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </Box>
                ) : null;
              })}
            </Box>
          </Collapse>
        </Paper>
      </Grid>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <LinearProgress sx={{ width: '200px' }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: '1400px', mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main', mb: 1 }}>
          🌳 DSA Skill Tree
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 2 }}>
          Master coding interviews through organized skill progression
        </Typography>
        
        {/* Controls */}
        <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch 
                checked={showConfidenceOverlay} 
                onChange={(e) => setShowConfidenceOverlay(e.target.checked)} 
              />
            }
            label="Show Confidence Overlay"
          />
          <Chip 
            icon={<AssessmentIcon />}
            label={`${skillTreeData?.total_problems || 0} Total Problems`}
            color="primary"
            variant="outlined"
          />
          <Chip 
            icon={<GroupIcon />}
            label={`${skillTreeData?.total_skill_areas || 0} Skill Areas`}
            color="secondary"
            variant="outlined"
          />
          {userProgress && (
            <Chip 
              icon={<TrendingUpIcon />}
              label={`${userProgress.total_problems_attempted} Attempted`}
              color="success"
              variant="outlined"
            />
          )}
        </Box>
      </Box>

      {/* Skill Tree Grid */}
      <Grid container spacing={3}>
        {skillTreeData?.skill_tree_columns?.map((column, index) => 
          renderSkillColumn(column, index)
        )}
      </Grid>

      {/* Problem Detail Dialog */}
      <Dialog 
        open={!!selectedProblem} 
        onClose={() => setSelectedProblem(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedProblem && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="h6">{selectedProblem.title}</Typography>
                <Chip 
                  label={selectedProblem.difficulty}
                  sx={{ 
                    bgcolor: getDifficultyColor(selectedProblem.difficulty),
                    color: 'white'
                  }}
                />
              </Box>
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Problem ID: {selectedProblem.id}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Sub-difficulty Level:</strong> {selectedProblem.sub_difficulty_level}/5
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Conceptual Difficulty:</strong> {selectedProblem.conceptual_difficulty}/100
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Implementation Complexity:</strong> {selectedProblem.implementation_complexity}/100
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Google Interview Relevance:</strong> {selectedProblem.google_interview_relevance.toFixed(1)}%
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* Confidence Rating */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>Rate Your Confidence:</Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {[1, 2, 3, 4, 5].map(level => (
                    <Button
                      key={level}
                      variant={getConfidenceLevel(selectedProblem.id) === level ? 'contained' : 'outlined'}
                      size="small"
                      onClick={() => updateConfidence(selectedProblem.id, level)}
                    >
                      {level}
                    </Button>
                  ))}
                </Box>
                <Typography variant="caption" color="text.secondary">
                  1: No idea → 5: Completely confident
                </Typography>
              </Box>

              {/* Algorithm Tags */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>Algorithm Tags:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selectedProblem.algorithm_tags.map(tag => (
                    <Chip key={tag} label={tag} size="small" variant="outlined" />
                  ))}
                </Box>
              </Box>

              {/* Similar Problems */}
              {similarProblems.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>Similar Problems:</Typography>
                  <List dense>
                    {similarProblems.slice(0, 5).map(similar => (
                      <ListItem key={similar.problem_id}>
                        <ListItemText
                          primary={similar.problem_id}
                          secondary={
                            <Box>
                              <Typography variant="caption" component="div">
                                Similarity: {(similar.similarity_score * 100).toFixed(1)}%
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {similar.explanation}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </DialogContent>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default SkillTreeVisualization;
