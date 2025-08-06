import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Chip,
  LinearProgress,
  Card,
  CardContent,
  Button,
  IconButton,
  Collapse,
  Avatar,
  Switch,
  FormControlLabel,
  CircularProgress,
  Pagination,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Skeleton
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { FixedSizeList as List } from 'react-window';

// PERFORMANCE OPTIMIZATION: Virtualized Skill Tree Component
const OptimizedSkillTreeVisualization = () => {
  // State management
  const [skillAreas, setSkillAreas] = useState([]);
  const [expandedAreas, setExpandedAreas] = useState({});
  const [skillAreaProblems, setSkillAreaProblems] = useState({});
  const [currentPage, setCurrentPage] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [sortBy, setSortBy] = useState('quality');

  // API Configuration
  const API_BASE = 'http://localhost:8002';
  const USER_ID = 'demo_user_2025';
  const PROBLEMS_PER_PAGE = 20;

  // OPTIMIZATION 1: Load only skill area summaries initially
  useEffect(() => {
    loadSkillAreaSummaries();
  }, []);

  const loadSkillAreaSummaries = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/skill-tree-v2/overview-optimized?user_id=${USER_ID}&top_problems_per_area=5`);
      const data = await response.json();
      setSkillAreas(data.skill_areas);
      
      // Initialize pagination state
      const initialPages = {};
      data.skill_areas.forEach(area => {
        initialPages[area.skill_area] = 1;
      });
      setCurrentPage(initialPages);
      
    } catch (error) {
      console.error('Error loading skill areas:', error);
    } finally {
      setLoading(false);
    }
  };

  // OPTIMIZATION 2: Lazy load problems when skill area is expanded
  const loadSkillAreaProblems = useCallback(async (skillArea, page = 1, difficulty = '', sortBy = 'quality') => {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: PROBLEMS_PER_PAGE.toString(),
        sort_by: sortBy
      });
      
      if (difficulty) {
        params.append('difficulty', difficulty);
      }

      const response = await fetch(`${API_BASE}/skill-tree-v2/skill-area/${skillArea}/problems?${params}`);
      const data = await response.json();
      
      setSkillAreaProblems(prev => ({
        ...prev,
        [skillArea]: {
          ...data,
          problems: page === 1 ? data.problems : [...(prev[skillArea]?.problems || []), ...data.problems]
        }
      }));
      
    } catch (error) {
      console.error(`Error loading problems for ${skillArea}:`, error);
    }
  }, []);

  // OPTIMIZATION 3: Optimized toggle handler with lazy loading
  const toggleSkillArea = useCallback((skillArea) => {
    setExpandedAreas(prev => {
      const newExpanded = { ...prev, [skillArea]: !prev[skillArea] };
      
      // Load problems when expanding for the first time
      if (newExpanded[skillArea] && !skillAreaProblems[skillArea]) {
        loadSkillAreaProblems(skillArea, 1, selectedDifficulty, sortBy);
      }
      
      return newExpanded;
    });
  }, [skillAreaProblems, selectedDifficulty, sortBy, loadSkillAreaProblems]);

  // OPTIMIZATION 4: Memoized problem item renderer for virtualization
  const ProblemItem = React.memo(({ index, style, data }) => {
    const problem = data.problems[index];
    const { onProblemClick } = data;

    return (
      <div style={style}>
        <Card
          sx={{ 
            m: 1, 
            cursor: 'pointer',
            '&:hover': { bgcolor: 'action.hover' },
            minHeight: '80px'
          }}
          onClick={() => onProblemClick(problem)}
        >
          <CardContent sx={{ p: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 500, mb: 1 }}>
              {problem.title}
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Chip
                label={problem.difficulty}
                size="small"
                sx={{
                  bgcolor: problem.difficulty === 'Easy' ? '#4caf50' :
                          problem.difficulty === 'Medium' ? '#ff9800' : '#f44336',
                  color: 'white',
                  fontSize: '0.7rem'
                }}
              />
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  Quality: {problem.quality_score.toFixed(1)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Level: {problem.sub_difficulty_level}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </div>
    );
  });

  // OPTIMIZATION 5: Virtualized problem list component
  const VirtualizedProblemList = React.memo(({ skillArea, problems, onProblemClick }) => {
    const listHeight = Math.min(600, problems.length * 100); // Max 600px height
    
    return (
      <Box sx={{ height: listHeight, width: '100%' }}>
        <List
          height={listHeight}
          itemCount={problems.length}
          itemSize={100}
          itemData={{ problems, onProblemClick }}
        >
          {ProblemItem}
        </List>
      </Box>
    );
  });

  // OPTIMIZATION 6: Pagination with infinite scroll option
  const handleLoadMore = useCallback((skillArea) => {
    const currentProblems = skillAreaProblems[skillArea];
    if (currentProblems && currentProblems.has_next) {
      const nextPage = currentPage[skillArea] + 1;
      setCurrentPage(prev => ({ ...prev, [skillArea]: nextPage }));
      loadSkillAreaProblems(skillArea, nextPage, selectedDifficulty, sortBy);
    }
  }, [skillAreaProblems, currentPage, selectedDifficulty, sortBy, loadSkillAreaProblems]);

  // OPTIMIZATION 7: Debounced search
  const debouncedSearch = useMemo(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery.length >= 2) {
        // Implement search API call
        console.log('Searching for:', searchQuery);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  // Handle problem click
  const handleProblemClick = useCallback((problem) => {
    console.log('Problem clicked:', problem);
    // Implementation for problem detail view
  }, []);

  // Render loading state
  if (loading) {
    return (
      <Box sx={{ p: 3, maxWidth: '1400px', mx: 'auto' }}>
        <Skeleton variant="text" width="40%" height={60} sx={{ mb: 2 }} />
        <Grid container spacing={3}>
          {[1, 2, 3].map(i => (
            <Grid item xs={12} md={4} key={i}>
              <Skeleton variant="rectangular" height={200} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: '1400px', mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main', mb: 1 }}>
          🌳 DSA Skill Tree (Optimized)
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 2 }}>
          Efficiently browse {skillAreas.reduce((sum, area) => sum + area.total_problems, 0)} problems
        </Typography>
        
        {/* Search and Filters */}
        <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
          <TextField
            placeholder="Search problems..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 300 }}
          />
          
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Difficulty</InputLabel>
            <Select
              value={selectedDifficulty}
              label="Difficulty"
              onChange={(e) => setSelectedDifficulty(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="Easy">Easy</MenuItem>
              <MenuItem value="Medium">Medium</MenuItem>
              <MenuItem value="Hard">Hard</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Sort By</InputLabel>
            <Select
              value={sortBy}
              label="Sort By"
              onChange={(e) => setSortBy(e.target.value)}
            >
              <MenuItem value="quality">Quality</MenuItem>
              <MenuItem value="relevance">Relevance</MenuItem>
              <MenuItem value="difficulty">Difficulty</MenuItem>
              <MenuItem value="title">Title</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Skill Areas Grid */}
      <Grid container spacing={3}>
        {skillAreas.map((area, index) => {
          const isExpanded = expandedAreas[area.skill_area];
          const areaProblems = skillAreaProblems[area.skill_area];
          
          return (
            <Grid item xs={12} md={6} lg={4} key={area.skill_area}>
              <Paper sx={{ p: 2, height: '100%' }}>
                {/* Skill Area Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ 
                    bgcolor: `hsl(${index * 40}, 60%, 50%)`,
                    mr: 2,
                    width: 32,
                    height: 32
                  }}>
                    {area.skill_area.charAt(0).toUpperCase()}
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>
                      {area.skill_area.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {area.total_problems} problems
                    </Typography>
                  </Box>
                  <IconButton 
                    size="small" 
                    onClick={() => toggleSkillArea(area.skill_area)}
                  >
                    {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Box>

                {/* Difficulty Distribution */}
                <Box sx={{ mb: 2 }}>
                  {Object.entries(area.difficulty_distribution).map(([difficulty, count]) => 
                    count > 0 ? (
                      <Chip
                        key={difficulty}
                        label={`${difficulty}: ${count}`}
                        size="small"
                        sx={{ 
                          mr: 0.5, 
                          mb: 0.5,
                          bgcolor: difficulty === 'Easy' ? '#4caf50' :
                                  difficulty === 'Medium' ? '#ff9800' : '#f44336',
                          color: 'white',
                          fontSize: '0.75rem'
                        }}
                      />
                    ) : null
                  )}
                </Box>

                {/* Top Problems Preview */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                    Top Problems:
                  </Typography>
                  {area.top_problems.slice(0, 3).map(problem => (
                    <Typography 
                      key={problem.id}
                      variant="caption" 
                      sx={{ 
                        display: 'block',
                        cursor: 'pointer',
                        '&:hover': { color: 'primary.main' },
                        mb: 0.5
                      }}
                      onClick={() => handleProblemClick(problem)}
                    >
                      • {problem.title}
                    </Typography>
                  ))}
                </Box>

                {/* Expanded Problem List */}
                <Collapse in={isExpanded}>
                  <Box sx={{ mt: 2 }}>
                    {areaProblems ? (
                      <>
                        <VirtualizedProblemList
                          skillArea={area.skill_area}
                          problems={areaProblems.problems}
                          onProblemClick={handleProblemClick}
                        />
                        
                        {/* Load More Button */}
                        {areaProblems.has_next && (
                          <Box sx={{ mt: 2, textAlign: 'center' }}>
                            <Button
                              variant="outlined"
                              onClick={() => handleLoadMore(area.skill_area)}
                              size="small"
                            >
                              Load More ({areaProblems.total_count - areaProblems.problems.length} remaining)
                            </Button>
                          </Box>
                        )}
                        
                        {/* Progress indicator */}
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                          Showing {areaProblems.problems.length} of {areaProblems.total_count} problems
                        </Typography>
                      </>
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                        <CircularProgress size={24} />
                      </Box>
                    )}
                  </Box>
                </Collapse>
              </Paper>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
};

export default OptimizedSkillTreeVisualization;
