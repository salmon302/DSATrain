import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Alert,
  Card,
  CardContent,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Button,
  LinearProgress,
  Pagination,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Search,
  FilterList,
  Star,
  TrendingUp,
  Code,
  BusinessCenter,
  ExpandMore,
  Refresh,
  ViewList,
  ViewModule,
  CheckCircle,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { problemsAPI, enhancedStatsAPI, Problem, trackingAPI, getCurrentUserId, generateSessionId } from '../services/api';

const ProblemBrowser: React.FC = () => {
  const navigate = useNavigate();
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    platform: '',
    difficulty: '',
    minQuality: '',
    minRelevance: '',
    interviewReady: false,
    algorithmPriority: ''
  });
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
  const [problemDetails, setProblemDetails] = useState<any>(null);
  const [showFilters, setShowFilters] = useState(false);

  const userId = getCurrentUserId();
  const sessionId = generateSessionId();
  const pageSize = 12;

  // Load problems
  const loadProblems = async (page = 1, resetPage = false) => {
    try {
      setLoading(true);
      
      const params: any = {
        limit: pageSize,
        offset: resetPage ? 0 : (page - 1) * pageSize
      };

      // Apply filters
      if (filters.platform) params.platform = filters.platform;
      if (filters.difficulty) params.difficulty = filters.difficulty;
      if (filters.minQuality) params.min_quality = parseFloat(filters.minQuality);
      if (filters.minRelevance) params.min_relevance = parseFloat(filters.minRelevance);

      let response;
      if (searchQuery.trim()) {
        response = await problemsAPI.searchProblems(searchQuery);
      } else {
        response = await problemsAPI.getProblems(params);
      }

      setProblems(response.problems || []);
      setTotalPages(Math.ceil((response.total_available || response.count) / pageSize));
      setError(null);

      if (resetPage) {
        setCurrentPage(1);
      }
    } catch (err: any) {
      console.error('Error loading problems:', err);
      setError('Failed to load problems. Please check if the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  // Track problem view
  const trackProblemView = async (problemId: string) => {
    try {
      await trackingAPI.trackInteraction({
        user_id: userId,
        problem_id: problemId,
        action: 'viewed',
        session_id: sessionId
      });
    } catch (error) {
      console.error('Failed to track problem view:', error);
    }
  };

  // Handle problem click
  const handleProblemClick = async (problem: Problem) => {
    setSelectedProblem(problem);
    setLoading(true);
    
    try {
      // Track the view
      await trackProblemView(problem.id);
      
      // Load problem details and solutions
      const [problemDetail, solutionsData] = await Promise.all([
        problemsAPI.getProblem(problem.id),
        problemsAPI.getProblem(problem.id).then(() => 
          fetch(`http://localhost:8000/problems/${problem.id}/solutions`).then(r => r.json())
        ).catch(() => ({ solutions: [] }))
      ]);
      
      setProblemDetails({
        ...problemDetail,
        solutions: solutionsData.solutions || []
      });
    } catch (error) {
      console.error('Error loading problem details:', error);
      setProblemDetails(problem);
    } finally {
      setLoading(false);
    }
  };

  // Handle search
  const handleSearch = () => {
    loadProblems(1, true);
  };

  // Handle filter change
  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Apply filters
  const applyFilters = () => {
    loadProblems(1, true);
    setShowFilters(false);
  };

  // Reset filters
  const resetFilters = () => {
    setFilters({
      platform: '',
      difficulty: '',
      minQuality: '',
      minRelevance: '',
      interviewReady: false,
      algorithmPriority: ''
    });
    setSearchQuery('');
    loadProblems(1, true);
  };

  // Difficulty color mapping
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  // Get algorithm priority (simplified version based on common interview algorithms)
  const getAlgorithmPriority = (tags: string[]): string => {
    if (!tags || tags.length === 0) return 'Low';
    
    const highPriorityAlgorithms = [
      'array', 'string', 'hash_table', 'dynamic_programming', 'tree', 'graph',
      'binary_search', 'two_pointers', 'sliding_window', 'breadth_first_search',
      'depth_first_search', 'backtracking', 'greedy'
    ];
    
    const mediumPriorityAlgorithms = [
      'linked_list', 'stack', 'queue', 'heap', 'sort', 'binary_tree',
      'recursion', 'divide_and_conquer', 'trie'
    ];

    const tagString = tags.join(',').toLowerCase();
    
    for (const alg of highPriorityAlgorithms) {
      if (tagString.includes(alg)) return 'High';
    }
    
    for (const alg of mediumPriorityAlgorithms) {
      if (tagString.includes(alg)) return 'Medium';
    }
    
    return 'Low';
  };

  // Platform color mapping
  const getPlatformColor = (platform: string) => {
    switch (platform?.toLowerCase()) {
      case 'leetcode': return '#FFA116';
      case 'codeforces': return '#1976D2';
      case 'hackerrank': return '#2EC866';
      case 'atcoder': return '#000000';
      case 'codechef': return '#5B4638';
      default: return '#757575';
    }
  };

  useEffect(() => {
    loadProblems();
  }, []);

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Problem Browser
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            Explore {problems.length} coding problems with ML-powered insights
          </Typography>
        </Box>
        
        <Box display="flex" gap={1}>
          <Tooltip title="Toggle View Mode">
            <IconButton onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}>
              {viewMode === 'grid' ? <ViewList /> : <ViewModule />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton onClick={() => loadProblems(currentPage)}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Search problems by title or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Box display="flex" gap={1}>
                <Button
                  variant="contained"
                  onClick={handleSearch}
                  startIcon={<Search />}
                >
                  Search
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => setShowFilters(!showFilters)}
                  startIcon={<FilterList />}
                >
                  Filters
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={2}>
              <Typography variant="body2" color="textSecondary" textAlign="right">
                {problems.length} problems found
              </Typography>
            </Grid>
          </Grid>

          {/* Advanced Filters */}
          {showFilters && (
            <Box mt={2}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Platform</InputLabel>
                    <Select
                      value={filters.platform}
                      onChange={(e) => handleFilterChange('platform', e.target.value)}
                    >
                      <MenuItem value="">All Platforms</MenuItem>
                      <MenuItem value="leetcode">LeetCode</MenuItem>
                      <MenuItem value="codeforces">Codeforces</MenuItem>
                      <MenuItem value="hackerrank">HackerRank</MenuItem>
                      <MenuItem value="atcoder">AtCoder</MenuItem>
                      <MenuItem value="codechef">CodeChef</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Difficulty</InputLabel>
                    <Select
                      value={filters.difficulty}
                      onChange={(e) => handleFilterChange('difficulty', e.target.value)}
                    >
                      <MenuItem value="">All Difficulties</MenuItem>
                      <MenuItem value="Easy">Easy</MenuItem>
                      <MenuItem value="Medium">Medium</MenuItem>
                      <MenuItem value="Hard">Hard</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <TextField
                    fullWidth
                    label="Min Quality Score"
                    type="number"
                    value={filters.minQuality}
                    onChange={(e) => handleFilterChange('minQuality', e.target.value)}
                    inputProps={{ min: 0, max: 100, step: 0.1 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <TextField
                    fullWidth
                    label="Min Google Relevance"
                    type="number"
                    value={filters.minRelevance}
                    onChange={(e) => handleFilterChange('minRelevance', e.target.value)}
                    inputProps={{ min: 0, max: 100, step: 0.1 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Algorithm Priority</InputLabel>
                    <Select
                      value={filters.algorithmPriority}
                      onChange={(e) => handleFilterChange('algorithmPriority', e.target.value)}
                    >
                      <MenuItem value="">All Priorities</MenuItem>
                      <MenuItem value="High">High Priority</MenuItem>
                      <MenuItem value="Medium">Medium Priority</MenuItem>
                      <MenuItem value="Low">Low Priority</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box display="flex" alignItems="center" height="100%">
                    <label>
                      <input
                        type="checkbox"
                        checked={filters.interviewReady}
                        onChange={(e) => handleFilterChange('interviewReady', e.target.checked.toString())}
                        style={{ marginRight: 8 }}
                      />
                      Interview Ready Only
                    </label>
                  </Box>
                </Grid>
              </Grid>
              <Box mt={2} display="flex" gap={1} justifyContent="flex-end">
                <Button onClick={resetFilters}>Reset</Button>
                <Button variant="contained" onClick={applyFilters}>Apply Filters</Button>
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && <LinearProgress sx={{ mb: 3 }} />}

      {/* Problems Display */}
      {viewMode === 'grid' ? (
        <Grid container spacing={3}>
          {problems.map((problem) => (
            <Grid item xs={12} sm={6} md={4} key={problem.id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  cursor: 'pointer',
                  '&:hover': { 
                    boxShadow: 6,
                    transform: 'translateY(-2px)',
                    transition: 'all 0.2s ease-in-out'
                  }
                }}
                onClick={() => handleProblemClick(problem)}
              >
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                    <Typography 
                      variant="h6" 
                      component="h3" 
                      sx={{ 
                        fontWeight: 'bold',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        minHeight: '3rem'
                      }}
                    >
                      {problem.title}
                    </Typography>
                    <Box display="flex" alignItems="center" gap={0.5}>
                      <Star sx={{ fontSize: 16, color: 'gold' }} />
                      <Typography variant="caption" color="textSecondary">
                        {problem.quality_score?.toFixed(1) || 'N/A'}
                      </Typography>
                    </Box>
                  </Box>

                  <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                    <Chip 
                      label={problem.platform}
                      size="small"
                      sx={{ backgroundColor: getPlatformColor(problem.platform), color: 'white' }}
                    />
                    <Chip 
                      label={problem.difficulty}
                      size="small"
                      color={getDifficultyColor(problem.difficulty) as any}
                    />
                    <Chip 
                      label={`${problem.google_interview_relevance?.toFixed(0) || 0}% Google`}
                      size="small"
                      variant="outlined"
                      icon={<BusinessCenter sx={{ fontSize: 14 }} />}
                    />
                    {problem.google_interview_relevance && problem.google_interview_relevance >= 6 && (
                      <Chip 
                        label="Interview Ready"
                        size="small"
                        color="success"
                        icon={<CheckCircle sx={{ fontSize: 14 }} />}
                      />
                    )}
                  </Box>

                  <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                    {problem.algorithm_tags?.slice(0, 3).map((tag, index) => (
                      <Chip key={index} label={tag} size="small" variant="outlined" />
                    ))}
                    {problem.algorithm_tags && problem.algorithm_tags.length > 3 && (
                      <Chip 
                        label={`+${problem.algorithm_tags.length - 3} more`} 
                        size="small" 
                        variant="outlined" 
                      />
                    )}
                    {problem.algorithm_tags && (
                      <Chip 
                        label={`${getAlgorithmPriority(problem.algorithm_tags)} Priority`}
                        size="small"
                        color={
                          getAlgorithmPriority(problem.algorithm_tags) === 'High' ? 'success' :
                          getAlgorithmPriority(problem.algorithm_tags) === 'Medium' ? 'warning' : 'default'
                        }
                        variant="outlined"
                      />
                    )}
                  </Box>

                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box display="flex" alignItems="center" gap={1}>
                      <TrendingUp sx={{ fontSize: 16, color: 'text.secondary' }} />
                      <Typography variant="caption" color="textSecondary">
                        Relevance: {problem.google_interview_relevance?.toFixed(1) || 'N/A'}%
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="textSecondary">
                      {problem.solution_count || 0} solutions
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : (
        // List View
        <Box>
          {problems.map((problem) => (
            <Card 
              key={problem.id} 
              sx={{ 
                mb: 2, 
                cursor: 'pointer',
                '&:hover': { backgroundColor: 'action.hover' }
              }}
              onClick={() => handleProblemClick(problem)}
            >
              <CardContent>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" fontWeight="bold">
                      {problem.title}
                    </Typography>
                    <Box display="flex" gap={1} mt={1}>
                      <Chip 
                        label={problem.platform}
                        size="small"
                        sx={{ backgroundColor: getPlatformColor(problem.platform), color: 'white' }}
                      />
                      <Chip 
                        label={problem.difficulty}
                        size="small"
                        color={getDifficultyColor(problem.difficulty) as any}
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box display="flex" gap={1} flexWrap="wrap">
                      {problem.algorithm_tags?.slice(0, 2).map((tag, index) => (
                        <Chip key={index} label={tag} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box textAlign="right">
                      <Typography variant="body2">
                        Quality: {problem.quality_score?.toFixed(1) || 'N/A'}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Google: {problem.google_interview_relevance?.toFixed(1) || 'N/A'}%
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={4}>
          <Pagination
            count={totalPages}
            page={currentPage}
            onChange={(_, page) => {
              setCurrentPage(page);
              loadProblems(page);
            }}
            color="primary"
            size="large"
          />
        </Box>
      )}

      {/* Problem Details Dialog */}
      <Dialog 
        open={!!selectedProblem} 
        onClose={() => setSelectedProblem(null)}
        maxWidth="lg"
        fullWidth
      >
        {selectedProblem && (
          <>
            <DialogTitle>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="h5" fontWeight="bold">
                  {selectedProblem.title}
                </Typography>
                <Box display="flex" gap={1}>
                  <Chip 
                    label={selectedProblem.platform}
                    sx={{ backgroundColor: getPlatformColor(selectedProblem.platform), color: 'white' }}
                  />
                  <Chip 
                    label={selectedProblem.difficulty}
                    color={getDifficultyColor(selectedProblem.difficulty) as any}
                  />
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent>
              {problemDetails && (
                <Box>
                  {/* Problem Info */}
                  <Grid container spacing={2} mb={3}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>Problem Metrics</Typography>
                      <Box display="flex" flexDirection="column" gap={1}>
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
                        <Box display="flex" justifyContent="space-between">
                          <Typography>Solutions Available:</Typography>
                          <Typography fontWeight="bold">
                            {problemDetails.solutions?.length || 0}
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

                  {/* Problem Description */}
                  {problemDetails.description && (
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="h6">Problem Description</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography style={{ whiteSpace: 'pre-wrap' }}>
                          {problemDetails.description}
                        </Typography>
                      </AccordionDetails>
                    </Accordion>
                  )}

                  {/* Solutions */}
                  {problemDetails.solutions && problemDetails.solutions.length > 0 && (
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="h6">
                          Solutions ({problemDetails.solutions.length})
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        {problemDetails.solutions.map((solution: any, index: number) => (
                          <Box key={index} mb={3}>
                            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                              Solution {index + 1} - Quality: {solution.overall_quality_score?.toFixed(1) || 'N/A'}/100
                            </Typography>
                            {solution.code && (
                              <SyntaxHighlighter 
                                language="python" 
                                style={tomorrow}
                                customStyle={{ fontSize: '14px', borderRadius: '4px' }}
                              >
                                {solution.code}
                              </SyntaxHighlighter>
                            )}
                            {solution.explanation && (
                              <Typography variant="body2" color="textSecondary" mt={1}>
                                <strong>Explanation:</strong> {solution.explanation}
                              </Typography>
                            )}
                          </Box>
                        ))}
                      </AccordionDetails>
                    </Accordion>
                  )}
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedProblem(null)}>Close</Button>
              <Button 
                variant="contained" 
                startIcon={<Code />}
                onClick={() => {
                  // Track attempt action
                  trackingAPI.trackInteraction({
                    user_id: userId,
                    problem_id: selectedProblem.id,
                    action: 'attempted',
                    session_id: sessionId
                  });
                  
                  // Navigate to code practice with the selected problem
                  navigate('/practice', { 
                    state: { problemId: selectedProblem.id } 
                  });
                }}
              >
                Start Solving
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Empty State */}
      {!loading && problems.length === 0 && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No problems found
            </Typography>
            <Typography variant="body2" color="textSecondary" mb={2}>
              Try adjusting your search query or filters
            </Typography>
            <Button variant="outlined" onClick={resetFilters}>
              Clear All Filters
            </Button>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ProblemBrowser;
