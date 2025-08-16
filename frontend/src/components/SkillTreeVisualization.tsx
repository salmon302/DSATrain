import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
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
import { FixedSizeList, ListChildComponentProps } from 'react-window';
import { favoritesAPI, getCurrentUserId } from '../services/api';
import { Bookmark, BookmarkBorder, PlayArrow } from '@mui/icons-material';

// TypeScript interfaces
interface Problem {
  id: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  sub_difficulty_level: number;
  conceptual_difficulty: number;
  implementation_complexity: number;
  algorithm_tags: string[];
  prerequisite_skills: string[];
  quality_score: number;
  google_interview_relevance: number;
  skill_tree_position: Record<string, any>;
}

// Problem summary shape used by optimized endpoints
interface ProblemSummaryLite {
  id: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  sub_difficulty_level: number;
  quality_score: number;
  google_interview_relevance: number;
}

interface SkillTreeColumn {
  skill_area: string;
  total_problems: number;
  difficulty_levels: {
    [key in 'Easy' | 'Medium' | 'Hard']: Problem[];
  };
  mastery_percentage: number;
  recommended_next?: string[];
}

interface SkillTreeData {
  skill_tree_columns: SkillTreeColumn[];
  total_problems: number;
  total_skill_areas: number;
  user_id?: string;
  last_updated: string;
}

// Tag overview models (from optimized API)
interface TagSummary {
  tag: string;
  total_problems: number;
  difficulty_distribution: Record<'Easy'|'Medium'|'Hard', number>;
  top_problems: ProblemSummaryLite[];
}

interface TagsOverview {
  tags: TagSummary[];
  total_tags: number;
  total_problems: number;
  last_updated: string;
}

interface SimilarProblem {
  problem_id: string;
  similarity_score: number;
  explanation: string;
  algorithm_similarity: number;
  pattern_similarity: number;
  difficulty_similarity: number;
}

interface UserProgress {
  user_id: string;
  skill_progress: Record<string, {
    problems_attempted: number;
    average_confidence: number;
    confidence_levels: Record<string, {
      confidence_level: number;
      last_attempted: string | null;
      attempts_count: number;
    }>;
  }>;
  skill_mastery: Record<string, {
    mastery_level: number;
    problems_attempted: number;
    problems_solved: number;
    mastery_trend: string;
    last_activity: string | null;
  }>;
  total_problems_attempted: number;
  skill_areas_touched: number;
}

// Skill Tree Component
const SkillTreeVisualization: React.FC = () => {
  const navigate = useNavigate();
  const [skillTreeData, setSkillTreeData] = useState<SkillTreeData | null>(null);
  const [userProgress, setUserProgress] = useState<UserProgress | null>(null);
  const [expandedColumns, setExpandedColumns] = useState<Record<string, boolean>>({});
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
  const [similarProblems, setSimilarProblems] = useState<SimilarProblem[]>([]);
  const [showConfidenceOverlay, setShowConfidenceOverlay] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [filterDifficulty, setFilterDifficulty] = useState<'' | 'Easy' | 'Medium' | 'Hard'>('');
  const [sortBy, setSortBy] = useState<'quality' | 'relevance' | 'difficulty' | 'title'>('quality');
  const [visibleCounts, setVisibleCounts] = useState<Record<string, number>>({});
  // View mode toggle: Skill Areas vs Tags
  const [viewMode, setViewMode] = useState<'areas'|'tags'>('areas');
  const [tagsOverview, setTagsOverview] = useState<TagsOverview | null>(null);
  const [loadingTags, setLoadingTags] = useState<boolean>(false);
  // Expanded dialog state for large lists
  const [expandedOpen, setExpandedOpen] = useState<boolean>(false);
  const [expandedType, setExpandedType] = useState<'area'|'tag'|null>(null);
  const [expandedKey, setExpandedKey] = useState<string>('');
  const [expandedTitle, setExpandedTitle] = useState<string>('');
  const [expandedProblems, setExpandedProblems] = useState<ProblemSummaryLite[]>([]);
  const [expandedTotal, setExpandedTotal] = useState<number>(0);
  const [expandedPage, setExpandedPage] = useState<number>(1);
  const [expandedPageSize, setExpandedPageSize] = useState<number>(50);
  const [expandedSortBy, setExpandedSortBy] = useState<'quality'|'relevance'|'difficulty'|'title'>('quality');
  const [expandedDifficulty, setExpandedDifficulty] = useState<''|'Easy'|'Medium'|'Hard'>('');
  const [loadingExpanded, setLoadingExpanded] = useState<boolean>(false);
  const [expandedQuery, setExpandedQuery] = useState<string>('');
  const [expandedQuickFilters, setExpandedQuickFilters] = useState<Record<string, boolean>>({
    Easy: false,
    Medium: false,
    Hard: false,
  });
  const [expandedPlatform, setExpandedPlatform] = useState<string>('');
  const [expandedTitleMatch, setExpandedTitleMatch] = useState<''|'prefix'|'exact'>('');
  // Favorites
  const [favoriteIds, setFavoriteIds] = useState<Set<string>>(new Set());
  const [favoritesOnly, setFavoritesOnly] = useState<boolean>(false);

  // API Base URL (feature-flag to consolidate to main API)
  const useMainApi = process.env.REACT_APP_FEATURE_SKILL_TREE_MAIN_API === 'on';
  const API_BASE = useMainApi
    ? (process.env.REACT_APP_API_URL || 'http://localhost:8000')
    : (process.env.REACT_APP_SKILL_TREE_URL || 'http://localhost:8002');
  const API_V2_BASE = useMainApi
    ? (process.env.REACT_APP_API_URL || 'http://localhost:8000') + '/skill-tree-proxy'
    : (process.env.REACT_APP_SKILL_TREE_URL || 'http://localhost:8002') + '/skill-tree-v2';
  const USER_ID = getCurrentUserId();

  useEffect(() => {
    loadSkillTreeData();
    loadUserProgress();
  void loadFavorites();
    // initialize favoritesOnly from localStorage
    try {
      const stored = localStorage.getItem('skillTree:favoritesOnly');
      if (stored === 'true') setFavoritesOnly(true);
    } catch {}
  }, []);

  // persist favoritesOnly to localStorage
  useEffect(() => {
    try {
      if (favoritesOnly) localStorage.setItem('skillTree:favoritesOnly', 'true');
      else localStorage.removeItem('skillTree:favoritesOnly');
    } catch {}
  }, [favoritesOnly]);

  useEffect(() => {
    if (viewMode === 'tags' && !tagsOverview && !loadingTags) {
      loadTagsOverview();
    }
    // eslint-disable-next-line
  }, [viewMode]);

  const loadSkillTreeData = async (): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE}/skill-tree/overview?user_id=${USER_ID}`);
      const data: SkillTreeData = await response.json();
      setSkillTreeData(data);
    } catch (error) {
      console.error('Error loading skill tree:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserProgress = async (): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE}/skill-tree/user/${USER_ID}/progress`);
      const data: UserProgress = await response.json();
      setUserProgress(data);
    } catch (error) {
      console.error('Error loading user progress:', error);
    }
  };

  const loadTagsOverview = async (): Promise<void> => {
    try {
      setLoadingTags(true);
      const response = await fetch(`${API_V2_BASE}/tags/overview?top_problems_per_tag=5`);
      const data: TagsOverview = await response.json();
      setTagsOverview(data);
    } catch (error) {
      console.error('Error loading tags overview:', error);
    } finally {
      setLoadingTags(false);
    }
  };

  const loadSimilarProblems = async (problemId: string): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE}/skill-tree/similar/${problemId}`);
      const data: SimilarProblem[] = await response.json();
      setSimilarProblems(data);
    } catch (error) {
      console.error('Error loading similar problems:', error);
    }
  };

  const loadFavorites = async (): Promise<void> => {
    try {
      const res = await favoritesAPI.list(USER_ID, false);
      const ids: string[] = res.problem_ids || [];
      setFavoriteIds(new Set(ids));
    } catch (e) {
      // non-blocking
      console.warn('Failed to load favorites', e);
    }
  };

  const toggleFavorite = async (problemId: string, makeFav?: boolean): Promise<void> => {
    const currentlyFav = favoriteIds.has(problemId);
    const next = typeof makeFav === 'boolean' ? makeFav : !currentlyFav;
    // optimistic update
    setFavoriteIds(prev => {
      const copy = new Set(prev);
      if (next) copy.add(problemId); else copy.delete(problemId);
      return copy;
    });
    try {
      await favoritesAPI.toggle({ user_id: USER_ID, problem_id: problemId, favorite: next });
    } catch (e) {
      // revert on error
      setFavoriteIds(prev => {
        const copy = new Set(prev);
        if (next) copy.delete(problemId); else copy.add(problemId);
        return copy;
      });
    }
  };

  const updateConfidence = async (problemId: string, confidenceLevel: number): Promise<void> => {
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

  const toggleColumnExpansion = (skillArea: string): void => {
    setExpandedColumns(prev => ({
      ...prev,
      [skillArea]: !prev[skillArea]
    }));
  };

  const handleProblemClick = (problem: Problem): void => {
    setSelectedProblem(problem);
    loadSimilarProblems(problem.id);
  };

  const goPractice = (problemId: string) => {
    navigate('/practice', { state: { problemId } });
  };

  const getDifficultyColor = (difficulty: string): string => {
    switch (difficulty) {
      case 'Easy': return '#4caf50';
      case 'Medium': return '#ff9800';
      case 'Hard': return '#f44336';
      default: return '#757575';
    }
  };

  const getConfidenceLevel = (problemId: string): number => {
    if (!userProgress?.skill_progress) return 0;
    
    for (const skillArea of Object.values(userProgress.skill_progress)) {
      if (skillArea.confidence_levels && skillArea.confidence_levels[problemId]) {
        return skillArea.confidence_levels[problemId].confidence_level;
      }
    }
    return 0;
  };

  // Expanded window logic for categories/tags
  const openExpanded = (type: 'area'|'tag', key: string, title: string) => {
    setExpandedType(type);
    setExpandedKey(key);
    setExpandedTitle(title);
    setExpandedPage(1);
    setExpandedProblems([]);
    setExpandedTotal(0);
    setExpandedOpen(true);
    void loadExpandedPage(1, expandedPageSize, expandedSortBy, expandedDifficulty, type, key);
  };

  const loadExpandedPage = async (
    page = 1,
    pageSize = expandedPageSize,
    sort: 'quality'|'relevance'|'difficulty'|'title' = expandedSortBy,
    difficulty: ''|'Easy'|'Medium'|'Hard' = expandedDifficulty,
    type: 'area'|'tag'|null = expandedType,
    key: string = expandedKey
  ) => {
    if (!type || !key) return;
    try {
      setLoadingExpanded(true);
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize), sort_by: sort });
      if (difficulty) params.append('difficulty', difficulty);
  if (expandedQuery.trim()) params.append('query', expandedQuery.trim());
      if (expandedPlatform) params.append('platform', expandedPlatform);
      if (expandedTitleMatch) params.append('title_match', expandedTitleMatch);
      if (useMainApi) {
        // Add favorites-only server-side filtering params
        params.append('favorites_only', String(favoritesOnly));
        params.append('user_id', USER_ID);
      }
      const url = type === 'area'
        ? `${API_V2_BASE}/skill-area/${encodeURIComponent(key)}/problems?${params.toString()}`
        : `${API_V2_BASE}/tag/${encodeURIComponent(key)}/problems?${params.toString()}`;
      const res = await fetch(url);
      const data = await res.json();
      setExpandedProblems(data.problems || []);
      setExpandedTotal(data.total_count || 0);
      setExpandedPage(data.page || page);
      setExpandedPageSize(data.page_size || pageSize);
    } catch (e) {
      console.error('Error loading expanded list:', e);
    } finally {
      setLoadingExpanded(false);
    }
  };

  // Expanded dialog favorites-only filtered list (client-side)
  const shownExpandedProblems = useMemo(() => {
    return expandedProblems && expandedProblems.length > 0
      ? (favoritesOnly ? expandedProblems.filter(p => favoriteIds.has(p.id)) : expandedProblems)
      : [] as ProblemSummaryLite[];
  }, [expandedProblems, favoritesOnly, favoriteIds]);

  // Quick filter chips logic
  const handleQuickFilterToggle = async (level: 'Easy'|'Medium'|'Hard') => {
    // Toggle chip state and set expandedDifficulty accordingly
    setExpandedQuickFilters(prev => {
      const next = { ...prev, [level]: !prev[level] } as Record<'Easy'|'Medium'|'Hard', boolean>;
      const active = (['Easy','Medium','Hard'] as const).filter(d => next[d]);
      // If exactly one difficulty active, apply it; otherwise clear to allow all
      const nextDifficulty = active.length === 1 ? (active[0] as any) : '';
      setExpandedDifficulty(nextDifficulty as any);
      void loadExpandedPage(1, expandedPageSize, expandedSortBy, nextDifficulty as any);
      return next;
    });
  };

  // Virtualized row renderer for expanded problems
  const Row = useCallback(({ index, style }: ListChildComponentProps) => {
    const p = shownExpandedProblems[index];
    if (!p) return null;
    const isFav = favoriteIds.has(p.id);
    return (
      <div style={style}>
        <Card key={p.id} sx={{ m: 0.5 }}>
          <CardContent sx={{ py: 1.0, px: 1.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box sx={{ minWidth: 0, mr: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{p.title}</Typography>
                <Typography variant="caption" color="text.secondary">{p.difficulty} • Sub-level {p.sub_difficulty_level}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                {p.google_interview_relevance > 70 && (
                  <Tooltip title="High Google Interview Relevance">
                    <StarsIcon sx={{ fontSize: 16, color: 'warning.main' }} />
                  </Tooltip>
                )}
                <Tooltip title={isFav ? 'Unfavorite' : 'Favorite'}>
                  <IconButton size="small" onClick={() => void toggleFavorite(p.id)}>
                    {isFav ? <Bookmark sx={{ fontSize: 18 }} color="primary" /> : <BookmarkBorder sx={{ fontSize: 18 }} />}
                  </IconButton>
                </Tooltip>
                <Tooltip title="Practice in editor">
                  <IconButton size="small" onClick={() => goPractice(p.id)}>
                    <PlayArrow sx={{ fontSize: 18 }} />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </div>
    );
  }, [shownExpandedProblems, favoriteIds]);

  const renderSkillColumn = (column: SkillTreeColumn, index: number): JSX.Element => {
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
            {(['Easy', 'Medium', 'Hard'] as const).map(difficulty => {
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
            <Box sx={{ maxHeight: '460px', overflow: 'auto' }}>
              {(['Easy', 'Medium', 'Hard'] as const).map(difficulty => {
                if (filterDifficulty && filterDifficulty !== difficulty) return null;
                let problems = column.difficulty_levels[difficulty];
                // Search filter
                if (searchQuery.trim()) {
                  const q = searchQuery.toLowerCase();
                  problems = problems.filter(p => p.title.toLowerCase().includes(q) || p.algorithm_tags.join(',').toLowerCase().includes(q));
                }
                // Favorites filter (global)
                if (favoritesOnly) {
                  problems = problems.filter(p => favoriteIds.has(p.id));
                }
                // Sorting
                problems = [...problems].sort((a, b) => {
                  switch (sortBy) {
                    case 'relevance':
                      return (b.google_interview_relevance || 0) - (a.google_interview_relevance || 0);
                    case 'difficulty':
                      return (b.sub_difficulty_level || 0) - (a.sub_difficulty_level || 0);
                    case 'title':
                      return a.title.localeCompare(b.title);
                    default:
                      return (b.quality_score || 0) - (a.quality_score || 0);
                  }
                });
                const key = `${column.skill_area}:${difficulty}`;
                const count = visibleCounts[key] ?? 20;
                const visible = problems.slice(0, count);
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
                    {visible.map((problem: Problem) => {
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
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                {showConfidenceOverlay && confidenceLevel > 0 && (
                                  <Badge 
                                    badgeContent={confidenceLevel} 
                                    color={confidenceLevel >= 4 ? 'success' : confidenceLevel >= 3 ? 'warning' : 'error'}
                                    sx={{ ml: 1 }}
                                  >
                                    <PsychologyIcon sx={{ fontSize: 16 }} />
                                  </Badge>
                                )}
                                <Tooltip title={favoriteIds.has(problem.id) ? 'Unfavorite' : 'Favorite'}>
                                  <IconButton size="small" onClick={(e) => { e.stopPropagation(); void toggleFavorite(problem.id); }}>
                                    {favoriteIds.has(problem.id) ? <Bookmark sx={{ fontSize: 18 }} color="primary" /> : <BookmarkBorder sx={{ fontSize: 18 }} />}
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Practice in editor">
                                  <IconButton size="small" onClick={(e) => { e.stopPropagation(); goPractice(problem.id); }}>
                                    <PlayArrow sx={{ fontSize: 18 }} />
                                  </IconButton>
                                </Tooltip>
                              </Box>
                            </Box>
                            <Box sx={{ mt: 1 }}>
                              {problem.algorithm_tags.slice(0, 3).map((tag: string) => (
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
                    {problems.length > visible.length && (
                      <Box sx={{ textAlign: 'center', mt: 1 }}>
                        <Button size="small" variant="outlined" onClick={() => setVisibleCounts(prev => ({ ...prev, [key]: (prev[key] ?? 20) + 20 }))}>
                          Load More ({problems.length - visible.length} remaining)
                        </Button>
                      </Box>
                    )}
                  </Box>
                ) : null;
              })}
              <Box sx={{ textAlign: 'right', mt: 1 }}>
                <Button size="small" onClick={() => openExpanded('area', column.skill_area, `${column.skill_area.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} — All Problems`)}>
                  View All in {column.skill_area.replace(/_/g, ' ')}
                </Button>
              </Box>
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
          <FormControlLabel
            control={
              <Switch
                checked={favoritesOnly}
                onChange={(e) => setFavoritesOnly(e.target.checked)}
              />
            }
            label="Favorites only"
          />
          <select value={viewMode} onChange={(e) => setViewMode(e.target.value as any)} style={{ padding: '8px', border: '1px solid #ddd', borderRadius: 4 }}>
            <option value="areas">View: Skill Areas</option>
            <option value="tags">View: Tags</option>
          </select>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <input
              placeholder="Search problems or tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ padding: '8px 10px', border: '1px solid #ddd', borderRadius: 4, minWidth: 240 }}
            />
            <select value={filterDifficulty} onChange={(e) => setFilterDifficulty(e.target.value as any)} style={{ padding: '8px', border: '1px solid #ddd', borderRadius: 4 }}>
              <option value="">All</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value as any)} style={{ padding: '8px', border: '1px solid #ddd', borderRadius: 4 }}>
              <option value="quality">Quality</option>
              <option value="relevance">Relevance</option>
              <option value="difficulty">Difficulty</option>
              <option value="title">Title</option>
            </select>
          </Box>
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

      {/* Main Grid: Areas or Tags */}
      {viewMode === 'areas' ? (
        <Grid container spacing={3}>
          {skillTreeData?.skill_tree_columns?.map((column, index) => 
            renderSkillColumn(column, index)
          )}
        </Grid>
      ) : (
        <Grid container spacing={3}>
          {loadingTags && (
            <Box sx={{ p: 2 }}><LinearProgress /></Box>
          )}
    {!loadingTags && tagsOverview && tagsOverview.tags.map((t: TagSummary, idx: number) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={t.tag}>
              <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Avatar sx={{ mr: 1 }}>{t.tag.charAt(0).toUpperCase()}</Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>{t.tag}</Typography>
                    <Typography variant="body2" color="text.secondary">{t.total_problems} problems</Typography>
                  </Box>
                  <IconButton size="small" onClick={() => openExpanded('tag', t.tag, `#${t.tag} — All Problems`)}>
                    <ExpandMoreIcon />
                  </IconButton>
                </Box>
                <Box sx={{ mb: 1 }}>
                  {(['Easy','Medium','Hard'] as const).map(d => (
                    t.difficulty_distribution[d] > 0 ? (
                      <Chip key={d} label={`${d}: ${t.difficulty_distribution[d]}`} size="small" sx={{ mr: 0.5, mb: 0.5, bgcolor: getDifficultyColor(d), color: 'white' }} />
                    ) : null
                  ))}
                </Box>
                <Box>
      {(favoritesOnly ? t.top_problems.filter(p => favoriteIds.has(p.id)) : t.top_problems).slice(0,5).map((p: ProblemSummaryLite) => (
                    <Card key={p.id} sx={{ mb: 1 }}>
                      <CardContent sx={{ py: 1.0, px: 1.5 }}>
                        <Typography variant="body2" sx={{ fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{p.title}</Typography>
                        <Typography variant="caption" color="text.secondary">{p.difficulty} • Sub-level {p.sub_difficulty_level}</Typography>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
                <Box sx={{ textAlign: 'right', mt: 1 }}>
                  <Button size="small" onClick={() => openExpanded('tag', t.tag, `#${t.tag} — All Problems`)}>View All</Button>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}

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
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1 }}>
                <Typography variant="h6" sx={{ mr: 1, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{selectedProblem.title}</Typography>
                <Chip label={selectedProblem.difficulty} sx={{ bgcolor: getDifficultyColor(selectedProblem.difficulty), color: 'white' }} />
                <Tooltip title={favoriteIds.has(selectedProblem.id) ? 'Unfavorite' : 'Favorite'}>
                  <IconButton onClick={() => void toggleFavorite(selectedProblem.id)}>
                    {favoriteIds.has(selectedProblem.id) ? <Bookmark color="primary" /> : <BookmarkBorder />}
                  </IconButton>
                </Tooltip>
                <Button size="small" variant="contained" startIcon={<PlayArrow />} onClick={() => goPractice(selectedProblem.id)}>
                  Practice
                </Button>
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

      {/* Expanded Problems Dialog (for Areas/Tags) */}
      <Dialog open={expandedOpen} onClose={() => setExpandedOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6">{expandedTitle || 'All Problems'}</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', gap: 1, mb: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <input
              placeholder="Search within list..."
              value={expandedQuery}
              onChange={(e) => setExpandedQuery(e.target.value)}
              onKeyDown={async (e) => { if (e.key === 'Enter') await loadExpandedPage(1); }}
              style={{ padding: '6px 8px', border: '1px solid #ddd', borderRadius: 4, minWidth: 200 }}
            />
            <FormControlLabel
              control={<Switch checked={favoritesOnly} onChange={(e) => setFavoritesOnly(e.target.checked)} />}
              label="Favorites only"
            />
            {/* Quick filter chips */}
            {(['Easy','Medium','Hard'] as const).map((d) => (
              <Chip
                key={`chip-${d}`}
                label={d}
                size="small"
                onClick={() => handleQuickFilterToggle(d)}
                sx={{ bgcolor: expandedQuickFilters[d] ? getDifficultyColor(d) : 'transparent', color: expandedQuickFilters[d] ? 'white' : 'inherit' }}
                variant={expandedQuickFilters[d] ? 'filled' : 'outlined'}
              />
            ))}
            <select value={expandedDifficulty} onChange={async (e) => { const v = e.target.value as any; setExpandedDifficulty(v); await loadExpandedPage(1, expandedPageSize, expandedSortBy, v); }} style={{ padding: '6px', border: '1px solid #ddd', borderRadius: 4 }}>
              <option value="">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
            <select value={expandedSortBy} onChange={async (e) => { const v = e.target.value as any; setExpandedSortBy(v); await loadExpandedPage(1, expandedPageSize, v, expandedDifficulty); }} style={{ padding: '6px', border: '1px solid #ddd', borderRadius: 4 }}>
              <option value="quality">Quality</option>
              <option value="relevance">Relevance</option>
              <option value="difficulty">Difficulty</option>
              <option value="title">Title</option>
            </select>
            <select value={expandedPlatform} onChange={async (e) => { const v = e.target.value as any; setExpandedPlatform(v); await loadExpandedPage(1); }} style={{ padding: '6px', border: '1px solid #ddd', borderRadius: 4 }}>
              <option value="">All Platforms</option>
              <option value="leetcode">LeetCode</option>
              <option value="codeforces">Codeforces</option>
              <option value="custom">Custom</option>
            </select>
            <select value={expandedTitleMatch} onChange={async (e) => { const v = e.target.value as any; setExpandedTitleMatch(v); await loadExpandedPage(1); }} style={{ padding: '6px', border: '1px solid #ddd', borderRadius: 4 }}>
              <option value="">Title: Contains</option>
              <option value="prefix">Title: Starts With</option>
              <option value="exact">Title: Exact</option>
            </select>
      <Typography variant="caption" color="text.secondary">{shownExpandedProblems.length} shown (of {expandedTotal})</Typography>
          </Box>
          {loadingExpanded ? (
            <LinearProgress />
          ) : (
            <Box sx={{ maxHeight: 500, overflow: 'auto' }}>
              <FixedSizeList
                height={440}
                width={"100%" as any}
        itemCount={shownExpandedProblems.length}
                itemSize={76}
              >
                {Row}
              </FixedSizeList>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                <Button size="small" disabled={expandedPage <= 1 || loadingExpanded} onClick={() => loadExpandedPage(expandedPage - 1)}>
                  Previous
                </Button>
                <Typography variant="caption">Page {expandedPage} / {Math.max(1, Math.ceil(expandedTotal / expandedPageSize))}</Typography>
                <Button size="small" disabled={expandedPage * expandedPageSize >= expandedTotal || loadingExpanded} onClick={() => loadExpandedPage(expandedPage + 1)}>
                  Next
                </Button>
              </Box>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default SkillTreeVisualization;
