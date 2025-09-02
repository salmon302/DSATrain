import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { FixedSizeList as VirtualList, FixedSizeGrid } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import { useNavigate, useSearchParams } from 'react-router-dom';
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
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Menu,
  Snackbar,
  InputAdornment,
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
  BookmarkBorder,
  Bookmark,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { apiService, problemsAPI, Problem, trackingAPI, getCurrentUserId, generateSessionId, favoritesAPI } from '../services/api';
import SkeletonCard from '../components/SkeletonCard';

// Dual-coding content loader
const DualCodingContent: React.FC<{ problemId: string }> = ({ problemId }) => {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [data, setData] = React.useState<any>(null);

  React.useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const resp = await apiService.get(`/problems/${problemId}/dual-coding`);
        setData(resp.data);
      } catch (e: any) {
        setError('Dual-coding not available.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [problemId]);

  if (loading) return <LinearProgress sx={{ mb: 2 }} />;
  if (error) return <Alert severity="info">{error}</Alert>;
  if (!data) return null;

  return (
    <Box>
      {data.visual_summary && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1">Visual Summary</Typography>
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{data.visual_summary}</Typography>
        </Box>
      )}
      {data.verbal_summary && (
        <Box>
          <Typography variant="subtitle1">Verbal Summary</Typography>
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{data.verbal_summary}</Typography>
        </Box>
      )}
    </Box>
  );
};

const ProblemBrowser: React.FC = () => {
  // Row height for virtualized list items (px)
  const ITEM_SIZE = 120;
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
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
    algorithmPriority: '',
    company: '',
    pattern: '',
    difficultyMin: '',
  difficultyMax: '',
  showFavorites: false
  });
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
  const [problemDetails, setProblemDetails] = useState<any>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [presetsAnchor, setPresetsAnchor] = useState<null | HTMLElement>(null);
  const [showSavePreset, setShowSavePreset] = useState(false);
  const [presetName, setPresetName] = useState('');
  const [sortBy, setSortBy] = useState<'relevance' | 'quality' | 'google' | 'difficulty' | 'newest'>('relevance');
  const searchInputRef = useRef<HTMLInputElement | null>(null);
  const initializedRef = useRef(false);
  const [favoriteIds, setFavoriteIds] = useState<Set<string>>(new Set());
  const lastFocusedCardIdRef = useRef<string | null>(null);
  const requestIdRef = useRef(0);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string }>({ open: false, message: '' });
  const [totalCount, setTotalCount] = useState<number | null>(null);

  const userId = getCurrentUserId();
  const sessionId = generateSessionId();
  const pageSize = 12;
  const GRID_GAP = 24; // px, roughly MUI Grid spacing={3}
  const CARD_HEIGHT = 260; // px, approximate card height in grid

  // Derived: number of active filters (excluding the free-text search)
  const activeFilterCount = useMemo(() => {
    const f = filters;
    return [
      f.platform,
      f.difficulty,
      f.minQuality,
      f.minRelevance,
      f.interviewReady ? '1' : '',
      f.algorithmPriority,
      f.company,
      f.pattern,
      f.difficultyMin,
      f.difficultyMax,
      f.showFavorites ? '1' : ''
    ].filter(Boolean).length;
  }, [filters]);

  // Helper to highlight matched search terms in titles
  const highlightText = (text: string, query: string) => {
    const q = (query || '').trim();
    if (!q || q.length < 2) return <>{text}</>;
    try {
      // Escape regex specials in query
      const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(escaped, 'ig');
      const parts: Array<string> = text.split(regex);
      const matches = text.match(regex) || [];
      const out: React.ReactNode[] = [];
      parts.forEach((p, i) => {
        out.push(<React.Fragment key={`p-${i}`}>{p}</React.Fragment>);
        if (i < matches.length) {
          out.push(
            <Box
              key={`m-${i}`}
              component="mark"
              sx={{
                px: 0.25,
                borderRadius: 0.5,
                backgroundColor: 'warning.light',
                color: 'inherit'
              }}
            >
              {matches[i]}
            </Box>
          );
        }
      });
      return <>{out}</>;
    } catch {
      return <>{text}</>;
    }
  };

  // Algorithm priority heuristic (hoisted above loadProblems to avoid TS2448)
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

  // Load problems
  const loadProblems = useCallback(async (page = 1, resetPage = false) => {
    const rid = ++requestIdRef.current;
    try {
      setLoading(true);
      // Favorites-only branch: fetch and filter client-side
      if (filters.showFavorites) {
        try {
          const favResp = await favoritesAPI.list(userId, true);
          let favItems: Problem[] = (favResp?.problems || favResp?.results || favResp?.items || []) as Problem[];
          if (!Array.isArray(favItems)) favItems = [];

          const q = searchQuery.trim().toLowerCase();
          const matchesFilters = (p: Problem) => {
            if (filters.platform && (p.platform || '').toLowerCase() !== filters.platform.toLowerCase()) return false;
            if (filters.difficulty && (p.difficulty || '') !== filters.difficulty) return false;
            if (filters.minQuality && typeof p.quality_score === 'number' && p.quality_score < parseFloat(filters.minQuality)) return false;
            if (filters.minRelevance && typeof p.google_interview_relevance === 'number' && p.google_interview_relevance < parseFloat(filters.minRelevance)) return false;
            if (filters.interviewReady && (p.google_interview_relevance || 0) < 6) return false;
            if (filters.algorithmPriority) {
              const pr = getAlgorithmPriority(p.algorithm_tags || []);
              if (pr !== filters.algorithmPriority) return false;
            }
            if (filters.company) {
              const companies = (p.companies || []).map((c: string) => (c || '').toLowerCase());
              if (!companies.includes(filters.company.toLowerCase())) return false;
            }
            if (filters.pattern) {
              const tags = (p.algorithm_tags || []).map((t: string) => (t || '').toLowerCase());
              if (!tags.includes(filters.pattern.toLowerCase())) return false;
            }
            if (filters.difficultyMin && typeof p.difficulty_rating === 'number' && p.difficulty_rating < parseFloat(filters.difficultyMin)) return false;
            if (filters.difficultyMax && typeof p.difficulty_rating === 'number' && p.difficulty_rating > parseFloat(filters.difficultyMax)) return false;
            if (q) {
              const hay = `${p.title || ''}\n${p.description || ''}`.toLowerCase();
              if (!hay.includes(q)) return false;
            }
            return true;
          };

          let items = favItems.filter(matchesFilters);
          const score = (p: Problem) => ((p.quality_score || 0) + (p.google_interview_relevance || 0)) / 2;
          if (sortBy === 'relevance') items = [...items].sort((a, b) => score(b) - score(a));
          else if (sortBy === 'quality') items = [...items].sort((a, b) => (b.quality_score || 0) - (a.quality_score || 0));
          else if (sortBy === 'google') items = [...items].sort((a, b) => (b.google_interview_relevance || 0) - (a.google_interview_relevance || 0));
          else if (sortBy === 'difficulty') {
            const order: Record<string, number> = { 'Easy': 1, 'Medium': 2, 'Hard': 3 };
            items = [...items].sort((a, b) => (order[a.difficulty] || 99) - (order[b.difficulty] || 99));
          } else if (sortBy === 'newest') {
            items = [...items].sort((a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime());
          }

          const total = items.length;
          const totalPagesCalc = Math.max(1, Math.ceil(total / pageSize));
          const pageNum = resetPage ? 1 : page;
          const start = (pageNum - 1) * pageSize;
          const paged = items.slice(start, start + pageSize);
          if (rid === requestIdRef.current) {
            setProblems(paged);
            setTotalPages(totalPagesCalc);
            setTotalCount(total);
            setError(null);
            if (resetPage) setCurrentPage(1);
          }
          return; // Done
        } catch (e) {
          console.warn('Failed to load favorites (details). Falling back to normal list.', e);
        }
      }
      
      const params: any = {
        limit: pageSize,
        offset: resetPage ? 0 : (page - 1) * pageSize
      };

      // Apply filters
      if (filters.platform) params.platform = filters.platform;
      if (filters.difficulty) params.difficulty = filters.difficulty;
      if (filters.minQuality) params.min_quality = parseFloat(filters.minQuality);
      if (filters.minRelevance) params.min_relevance = parseFloat(filters.minRelevance);
      if (filters.interviewReady) {
        (params as any).interview_ready = true;
      }
      if (filters.algorithmPriority) {
        (params as any).algorithm_priority = filters.algorithmPriority;
      }
      if (filters.company) (params as any).company = filters.company;
      if (filters.pattern) (params as any).algorithm_tag = filters.pattern;
      if (filters.difficultyMin) (params as any).difficulty_rating_min = parseFloat(filters.difficultyMin);
      if (filters.difficultyMax) (params as any).difficulty_rating_max = parseFloat(filters.difficultyMax);

  let response;
      if (searchQuery.trim()) {
        response = await problemsAPI.searchProblems(searchQuery);
      } else {
        // Send sort hint to backend (harmless if ignored)
        response = await problemsAPI.getProblems({ ...params, order_by: sortBy });
      }

      // Normalize and client-sort based on selected sort
      let items: Problem[] = (response.problems || response.results || []) as Problem[];
      const score = (p: Problem) => ((p.quality_score || 0) + (p.google_interview_relevance || 0)) / 2;
  if (sortBy === 'relevance') items = [...items].sort((a, b) => score(b) - score(a));
  else if (sortBy === 'quality') items = [...items].sort((a, b) => (b.quality_score || 0) - (a.quality_score || 0));
      else if (sortBy === 'google') items = [...items].sort((a, b) => (b.google_interview_relevance || 0) - (a.google_interview_relevance || 0));
      else if (sortBy === 'difficulty') {
        const order: Record<string, number> = { 'Easy': 1, 'Medium': 2, 'Hard': 3 };
        items = [...items].sort((a, b) => (order[a.difficulty] || 99) - (order[b.difficulty] || 99));
      } else if (sortBy === 'newest') {
        items = [...items].sort((a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime());
      }

  // Stale guard: only apply if this is the latest request
  if (rid === requestIdRef.current) {
  setProblems(items);
  const total = response.total_available || response.count || (response.results ? response.results.length : items.length);
  setTotalPages(Math.max(1, Math.ceil(total / pageSize)));
  setTotalCount(total ?? items.length);
        setError(null);
      }

      if (resetPage) {
        setCurrentPage(1);
      }
    } catch (err: any) {
      console.error('Error loading problems:', err);
      setError('Failed to load problems. Please check if the API server is running.');
    } finally {
      // Only clear loading for latest request to prevent flicker
      // Since rid is captured in this invocation, ensure this is still the latest request
      if (rid === requestIdRef.current) {
        setLoading(false);
      }
    }
  }, [filters, searchQuery, sortBy, pageSize, userId]);

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
          apiService.get(`/problems/${problem.id}/solutions`).then(r => r.data)
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

  // Close dialog and return focus to invoking card
  const handleCloseDialog = () => {
    setSelectedProblem(null);
    setTimeout(() => {
      if (lastFocusedCardIdRef.current) {
        const el = document.getElementById(lastFocusedCardIdRef.current);
        (el as HTMLElement | null)?.focus?.();
      }
    }, 0);
  };

  // Helper: push current state into URL (defined before first usage)
  const pushUrlState = useCallback((opts?: { page?: number; filtersOverride?: any; searchOverride?: string }) => {
    const f = opts?.filtersOverride || filters;
    const sp: Record<string, string> = {};
    if (searchQuery || opts?.searchOverride) sp.q = (opts?.searchOverride ?? searchQuery).trim();
    if (f.platform) sp.platform = f.platform;
    if (f.difficulty) sp.difficulty = f.difficulty;
    if (f.minQuality) sp.minQuality = String(f.minQuality);
    if (f.minRelevance) sp.minRelevance = String(f.minRelevance);
    if (f.interviewReady) sp.interviewReady = '1';
    if (f.algorithmPriority) sp.algorithmPriority = f.algorithmPriority;
    if (f.company) sp.company = f.company;
    if (f.pattern) sp.pattern = f.pattern;
    if (f.difficultyMin) sp.difficultyMin = String(f.difficultyMin);
    if (f.difficultyMax) sp.difficultyMax = String(f.difficultyMax);
    if (f.showFavorites) sp.favorites = '1';
    sp.view = viewMode;
    sp.sortBy = sortBy;
    sp.page = String(opts?.page ?? currentPage);
    setSearchParams(sp as any);
  }, [filters, searchQuery, viewMode, sortBy, currentPage, setSearchParams]);

  // Handle search
  const handleSearch = useCallback(() => {
    void loadProblems(1, true);
    // sync URL
    pushUrlState({ page: 1 });
  }, [loadProblems, pushUrlState]);

  // Share current URL to clipboard
  const handleShare = async () => {
    try {
      const url = window.location.href;
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(url);
      } else {
        // Fallback copy
        const ta = document.createElement('textarea');
        ta.value = url;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      setSnackbar({ open: true, message: 'Link copied to clipboard' });
    } catch (e) {
      setSnackbar({ open: true, message: 'Failed to copy link' });
    }
  };

  // Handle filter change
  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Apply filters
  const applyFilters = useCallback(() => {
    void loadProblems(1, true);
    setShowFilters(false);
    pushUrlState({ page: 1 });
  }, [loadProblems, pushUrlState]);

  // Reset filters
  const resetFilters = useCallback(() => {
    setFilters({
      platform: '',
      difficulty: '',
      minQuality: '',
      minRelevance: '',
      interviewReady: false,
      algorithmPriority: '',
      company: '',
      pattern: '',
      difficultyMin: '',
  difficultyMax: '',
  showFavorites: false
    });
    setSearchQuery('');
  setSortBy('relevance');
  setCurrentPage(1);
  void loadProblems(1, true);
  setSearchParams({});
  }, [loadProblems, setSearchParams]);

  // Presets
  const loadPresets = (): any[] => {
    try {
      return JSON.parse(localStorage.getItem('problemBrowserPresets') || '[]');
    } catch {
      return [];
    }
  };
  const savePresets = (presets: any[]) => localStorage.setItem('problemBrowserPresets', JSON.stringify(presets));
  const handleSavePreset = useCallback(() => {
    const presets = loadPresets();
    const existingIndex = presets.findIndex((p: any) => p.name === presetName);
    const entry = { name: presetName || `Preset ${presets.length + 1}`, filters, searchQuery };
    if (existingIndex >= 0) presets[existingIndex] = entry; else presets.push(entry);
    savePresets(presets);
    setShowSavePreset(false);
    setPresetName('');
  }, [presetName, filters, searchQuery]);
  const applyPreset = useCallback((preset: any) => {
    setFilters(preset.filters || filters);
    setSearchQuery(preset.searchQuery || '');
    setCurrentPage(1);
    void loadProblems(1, true);
    pushUrlState({ page: 1, filtersOverride: preset.filters, searchOverride: preset.searchQuery });
  }, [filters, loadProblems, pushUrlState]);

  // Difficulty color mapping
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
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

  // Favorites helpers
  const loadFavorites = useCallback(async () => {
    try {
      const data = await favoritesAPI.list(userId, false);
      const ids: string[] = data.problem_ids || [];
      setFavoriteIds(new Set(ids));
    } catch (e) {
      // Non-blocking
      console.warn('Failed to load favorites', e);
    }
  }, [userId]);

  const toggleFavorite = useCallback(async (problemId: string, desired: boolean) => {
    setFavoriteIds(prev => {
      const next = new Set(prev);
      if (desired) next.add(problemId); else next.delete(problemId);
      return next;
    });
    try {
      await favoritesAPI.toggle({ user_id: userId, problem_id: problemId, favorite: desired });
    } catch (e) {
      // revert if failed
      setFavoriteIds(prev => {
        const next = new Set(prev);
        if (desired) next.delete(problemId); else next.add(problemId);
        return next;
      });
    }
  }, [userId]);

  useEffect(() => {
    // Initialize state from URL only once
    if (initializedRef.current) return;
    initializedRef.current = true;
    const sp = Object.fromEntries(searchParams.entries());
    const initFilters = { ...filters };
    if (sp.platform) initFilters.platform = sp.platform;
    if (sp.difficulty) initFilters.difficulty = sp.difficulty;
    if (sp.minQuality) initFilters.minQuality = sp.minQuality;
    if (sp.minRelevance) initFilters.minRelevance = sp.minRelevance;
    if (sp.interviewReady) initFilters.interviewReady = sp.interviewReady === '1' || sp.interviewReady === 'true';
    if (sp.algorithmPriority) initFilters.algorithmPriority = sp.algorithmPriority;
    if (sp.company) initFilters.company = sp.company;
    if (sp.pattern) initFilters.pattern = sp.pattern;
    if (sp.difficultyMin) initFilters.difficultyMin = sp.difficultyMin;
    if (sp.difficultyMax) initFilters.difficultyMax = sp.difficultyMax;
  if (sp.favorites) initFilters.showFavorites = sp.favorites === '1' || sp.favorites === 'true';
    setFilters(initFilters);
    if (sp.q) setSearchQuery(sp.q);
    if (sp.view === 'list' || sp.view === 'grid') setViewMode(sp.view as any);
    if (sp.sortBy) setSortBy(sp.sortBy as any);
    const pageFromUrl = sp.page ? parseInt(sp.page, 10) : 1;
    setCurrentPage(Number.isFinite(pageFromUrl) && pageFromUrl > 0 ? pageFromUrl : 1);
    // If no URL state, apply default preset if available
    const hasUrlState = Boolean(Object.keys(sp).length);
    if (!hasUrlState) {
      try {
        const raw = localStorage.getItem('problemBrowserDefaultPreset');
        if (raw) {
          const preset = JSON.parse(raw);
          if (preset?.filters) setFilters(preset.filters);
          if (typeof preset?.searchQuery === 'string') setSearchQuery(preset.searchQuery);
          if (preset?.viewMode === 'list' || preset?.viewMode === 'grid') setViewMode(preset.viewMode);
          if (preset?.sortBy) setSortBy(preset.sortBy);
          // Push URL for shareability
          setTimeout(() => pushUrlState({ page: 1, filtersOverride: preset.filters, searchOverride: preset.searchQuery }), 0);
        }
      } catch {}
    }
    // Load with initialized filters (respect page if present)
    loadProblems(Number.isFinite(pageFromUrl) && pageFromUrl > 0 ? pageFromUrl : 1, true);
    loadFavorites();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Keyboard shortcut to focus search '/'
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const activeTag = (document.activeElement as HTMLElement)?.tagName?.toLowerCase();
      if (e.key === '/' && activeTag !== 'input' && activeTag !== 'textarea') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  // (pushUrlState defined above)

  // Debounce search input
  useEffect(() => {
    if (!initializedRef.current) return;
    const h = window.setTimeout(() => {
      setCurrentPage(1);
      void loadProblems(1, true);
      pushUrlState({ page: 1 });
    }, 300);
    return () => window.clearTimeout(h);
  }, [searchQuery, loadProblems, pushUrlState]);

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Problem Browser
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            {totalCount != null
              ? `Explore ${totalCount} coding problems with ML-powered insights`
              : `Explore coding problems with ML-powered insights`}
          </Typography>
          {/* Screen reader live region for updates */}
          <Box
            component="div"
            aria-live="polite"
            sx={{ position: 'absolute', width: 1, height: 1, p: 0, m: -1, overflow: 'hidden', clip: 'rect(0 0 0 0)', whiteSpace: 'nowrap', border: 0 }}
          >
            {totalCount != null ? `${totalCount} results. ${activeFilterCount} filters active.` : ''}
          </Box>
        </Box>
        
        <Box display="flex" gap={1}>
          <Tooltip title="Toggle View Mode">
            <IconButton 
              aria-label={viewMode === 'grid' ? 'Switch to list view' : 'Switch to grid view'}
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            >
              {viewMode === 'grid' ? <ViewList /> : <ViewModule />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton aria-label="Refresh problems" onClick={() => loadProblems(currentPage)}>
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
                onKeyDown={(e) => { if (e.key === 'Enter') handleSearch(); }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search sx={{ color: 'text.secondary' }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      {Boolean(searchQuery) && (
                        <Tooltip title="Clear">
                          <IconButton size="small" aria-label="Clear search" onClick={() => { setSearchQuery(''); pushUrlState({ page: 1, searchOverride: '' }); loadProblems(1, true); }}>
                            <span style={{ fontSize: 14, lineHeight: 1 }}>×</span>
                          </IconButton>
                        </Tooltip>
                      )}
                    </InputAdornment>
                  )
                }}
                inputRef={searchInputRef}
                aria-label="Search problems"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Box display="flex" gap={1} sx={{ flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  onClick={handleSearch}
                  startIcon={loading ? undefined : <Search />}
                  disabled={loading}
                >
                  {loading ? (
                    <Box display="flex" alignItems="center" gap={1}>
                      <CircularProgress size={16} thickness={5} />
                      Searching...
                    </Box>
                  ) : (
                    'Search'
                  )}
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => setShowFilters(!showFilters)}
                  startIcon={<FilterList />}
                >
                  {`Filters${activeFilterCount ? ` (${activeFilterCount})` : ''}`}
                </Button>
                <Button variant="outlined" onClick={(e) => setPresetsAnchor(e.currentTarget)}>Saved views</Button>
                <Button variant="outlined" onClick={handleShare}>Share</Button>
                <Chip
                  clickable
                  variant={filters.showFavorites ? 'filled' : 'outlined'}
                  color={filters.showFavorites ? 'primary' : 'default'}
                  icon={filters.showFavorites ? <Bookmark /> : <BookmarkBorder />}
                  label="Favorites only"
                  onClick={() => {
                    const v = !filters.showFavorites;
                    setFilters(prev => ({ ...prev, showFavorites: v }));
                    setCurrentPage(1);
                    loadProblems(1, true);
                    pushUrlState({ page: 1 });
                  }}
                />
                <Menu
                  anchorEl={presetsAnchor}
                  open={Boolean(presetsAnchor)}
                  onClose={() => setPresetsAnchor(null)}
                  // Ensure the menu renders into body to avoid clipping within containers
                  container={document.body}
                  slotProps={{ paper: { sx: { zIndex: (theme) => theme.zIndex.modal + 1 } } }}
                >
                  {loadPresets().length === 0 && (
                    <MenuItem disabled>No saved views</MenuItem>
                  )}
                  {loadPresets().map((p: any, idx: number) => (
                    <MenuItem key={idx} onClick={() => { applyPreset(p); setPresetsAnchor(null); }}>{p.name}</MenuItem>
                  ))}
                  <MenuItem onClick={() => { setShowSavePreset(true); setPresetsAnchor(null); }}>Save current as…</MenuItem>
                  <MenuItem onClick={() => { 
                    try {
                      localStorage.setItem('problemBrowserDefaultPreset', JSON.stringify({ filters, searchQuery, viewMode, sortBy }));
                      setSnackbar({ open: true, message: 'Set current filters as default' });
                    } catch {}
                    setPresetsAnchor(null);
                  }}>Set current as default</MenuItem>
                  <MenuItem onClick={() => { 
                    try { localStorage.removeItem('problemBrowserDefaultPreset'); setSnackbar({ open: true, message: 'Cleared default view' }); } catch {}
                    setPresetsAnchor(null);
                  }}>Clear default</MenuItem>
                </Menu>
              </Box>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Sort by</InputLabel>
                <Select
                  label="Sort by"
                  value={sortBy}
                  onChange={(e) => {
                    const v = e.target.value as typeof sortBy;
                    setSortBy(v);
                    // Re-sort current items and update URL
                    loadProblems(currentPage);
                    pushUrlState();
                  }}
                  MenuProps={{
                    container: () => document.body,
                    PaperProps: {
                      sx: { zIndex: (theme) => theme.zIndex.modal + 1 }
                    }
                  }}
                >
                  <MenuItem value="relevance">Relevance</MenuItem>
                  <MenuItem value="quality">Quality Score</MenuItem>
                  <MenuItem value="google">Google Relevance</MenuItem>
                  <MenuItem value="difficulty">Difficulty (Easy→Hard)</MenuItem>
                  <MenuItem value="newest">Newest</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {/* Active filter chips */}
          {(
            searchQuery ||
            filters.platform ||
            filters.difficulty ||
            filters.minQuality ||
            filters.minRelevance ||
            filters.interviewReady ||
            filters.algorithmPriority ||
            filters.company ||
            filters.pattern ||
            filters.difficultyMin ||
            filters.difficultyMax ||
            filters.showFavorites
          ) && (
            <Box mt={2} display="flex" gap={1} flexWrap="wrap" alignItems="center">
              {searchQuery && (
                <Chip label={`Search: ${searchQuery}`} onDelete={() => { setSearchQuery(''); pushUrlState({ page: 1, searchOverride: '' }); loadProblems(1, true); }} />
              )}
              {filters.platform && (
                <Chip label={`Platform: ${filters.platform}`} onDelete={() => { handleFilterChange('platform', ''); pushUrlState({ page: 1 }); loadProblems(1, true); }} />
              )}
              {filters.difficulty && (
                <Chip label={`Difficulty: ${filters.difficulty}`} onDelete={() => { handleFilterChange('difficulty', ''); pushUrlState({ page: 1 }); loadProblems(1, true); }} />
              )}
              {filters.minQuality && (
                <Chip label={`Min Quality: ${filters.minQuality}`} onDelete={() => { handleFilterChange('minQuality', ''); pushUrlState({ page: 1 }); loadProblems(1, true); }} />
              )}
              {filters.minRelevance && (
                <Chip label={`Min Relevance: ${filters.minRelevance}`} onDelete={() => { handleFilterChange('minRelevance', ''); pushUrlState({ page: 1 }); loadProblems(1, true); }} />
              )}
              {filters.interviewReady && (
                <Chip label="Interview Ready" onDelete={() => { handleFilterChange('interviewReady', false); pushUrlState({ page: 1 }); loadProblems(1, true); }} />
              )}
              {filters.algorithmPriority && (
                <Chip label={`Priority: ${filters.algorithmPriority}`} onDelete={() => { handleFilterChange('algorithmPriority', ''); pushUrlState({ page: 1 }); loadProblems(1, true); }} />
              )}
              {filters.company && (
                <Chip label={`Company: ${filters.company}`} onDelete={() => { handleFilterChange('company', ''); pushUrlState({ page: 1 }); loadProblems(1, true); }} />
              )}
              {filters.pattern && (
                <Chip label={`Tag: ${filters.pattern}`} onDelete={() => { handleFilterChange('pattern', ''); pushUrlState({ page: 1 }); loadProblems(1, true); }} />
              )}
              {filters.difficultyMin && (
                <Chip label={`Rating ≥ ${filters.difficultyMin}`} onDelete={() => { handleFilterChange('difficultyMin', ''); pushUrlState({ page: 1 }); loadProblems(1, true); }} />
              )}
              {filters.difficultyMax && (
                <Chip label={`Rating ≤ ${filters.difficultyMax}`} onDelete={() => { handleFilterChange('difficultyMax', ''); pushUrlState({ page: 1 }); loadProblems(1, true); }} />
              )}
              {filters.showFavorites && (
                <Chip label={`Favorites only`} onDelete={() => { handleFilterChange('showFavorites', false); pushUrlState({ page: 1 }); loadProblems(1, true); }} />
              )}
              <Button size="small" onClick={resetFilters}>Clear All</Button>
            </Box>
          )}

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
                  <TextField
                    fullWidth
                    label="Company"
                    value={filters.company}
                    onChange={(e) => handleFilterChange('company', e.target.value)}
                    placeholder="e.g., Google"
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <TextField
                    fullWidth
                    label="Pattern/Skill Tag"
                    value={filters.pattern}
                    onChange={(e) => handleFilterChange('pattern', e.target.value)}
                    placeholder="e.g., sliding_window"
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={6}>
                  <Typography variant="caption" color="textSecondary">Difficulty Rating Range</Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <TextField
                        fullWidth
                        label="Min"
                        type="number"
                        value={filters.difficultyMin}
                        onChange={(e) => handleFilterChange('difficultyMin', e.target.value)}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        fullWidth
                        label="Max"
                        type="number"
                        value={filters.difficultyMax}
                        onChange={(e) => handleFilterChange('difficultyMax', e.target.value)}
                      />
                    </Grid>
                  </Grid>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box display="flex" alignItems="center" height="100%">
                    <label>
                      <input
                        type="checkbox"
                        checked={Boolean(filters.interviewReady)}
                        onChange={(e) => handleFilterChange('interviewReady', e.target.checked)}
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

      {/* Save Preset Dialog */}
      <Dialog open={showSavePreset} onClose={() => setShowSavePreset(false)}>
        <DialogTitle>Save current filters as a view</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            autoFocus
            label="View name"
            value={presetName}
            onChange={(e) => setPresetName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSavePreset(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSavePreset} disabled={!presetName.trim()}>Save</Button>
        </DialogActions>
      </Dialog>

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
        <>
          {loading && problems.length === 0 && (
            <Grid container spacing={3}>
              {Array.from({ length: 6 }).map((_, i) => (
                <Grid item xs={12} sm={6} md={4} key={`skeleton-${i}`}>
                  <SkeletonCard variant="grid" />
                </Grid>
              ))}
            </Grid>
          )}
          {!loading && (
            <Box sx={{ height: 820 }}>
              <AutoSizer>
                {(size: { height?: number; width?: number }) => {
                  const { height = 820, width = 1200 } = size || {};
                  const safeHeight = height;
                  const safeWidth = width;
                  // Determine columns based on width (approximate MUI breakpoints)
                  const cols = safeWidth < 600 ? 1 : safeWidth < 900 ? 2 : safeWidth < 1200 ? 3 : 4;
                  const columnWidth = Math.floor((safeWidth - (cols + 1) * GRID_GAP) / cols);
                  const rowCount = Math.ceil(problems.length / cols);
                  return (
                    <FixedSizeGrid
                      height={safeHeight}
                      width={safeWidth}
                      columnCount={cols}
                      rowCount={rowCount}
                      columnWidth={columnWidth + GRID_GAP}
                      rowHeight={CARD_HEIGHT + GRID_GAP}
                    >
                      {({ columnIndex, rowIndex, style }) => {
                        const index = rowIndex * cols + columnIndex;
                        if (index >= problems.length) return <div style={style} />;
                        const problem = problems[index];
                        const adjustedStyle: React.CSSProperties = {
                          ...style,
                          left: (style as any).left + GRID_GAP,
                          top: (style as any).top + GRID_GAP,
                          width: columnWidth,
                          height: CARD_HEIGHT,
                        };
                        return (
                          <div style={adjustedStyle} key={problem.id}>
                            <Card
                              sx={{
                                height: '100%',
                                cursor: 'pointer',
                                '&:hover': {
                                  boxShadow: 6,
                                  transform: 'translateY(-2px)',
                                  transition: 'all 0.2s ease-in-out',
                                },
                              }}
                              onClick={() => {
                                lastFocusedCardIdRef.current = `problem-card-${problem.id}`;
                                handleProblemClick(problem);
                              }}
                              id={`problem-card-${problem.id}`}
                              role="button"
                              tabIndex={0}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                  e.preventDefault();
                                  lastFocusedCardIdRef.current = `problem-card-${problem.id}`;
                                  handleProblemClick(problem);
                                }
                              }}
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
                                      minHeight: '3rem',
                                    }}
                                  >
                                    {highlightText(problem.title || '', searchQuery)}
                                  </Typography>
                                  <Box display="flex" alignItems="center" gap={0.5}>
                                    <Tooltip title={favoriteIds.has(problem.id) ? 'Remove from favorites' : 'Add to favorites'}>
                                      <IconButton
                                        size="small"
                                        aria-label={`${favoriteIds.has(problem.id) ? 'Remove from favorites' : 'Add to favorites'}: ${problem.title}`}
                                        aria-pressed={favoriteIds.has(problem.id)}
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          toggleFavorite(problem.id, !favoriteIds.has(problem.id));
                                        }}
                                      >
                                        {favoriteIds.has(problem.id) ? (
                                          <Bookmark color="primary" fontSize="small" />
                                        ) : (
                                          <BookmarkBorder fontSize="small" />
                                        )}
                                      </IconButton>
                                    </Tooltip>
                                    <Star sx={{ fontSize: 16, color: 'gold' }} />
                                    <Typography variant="caption" color="text.secondary">
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
                                  <Chip label={problem.difficulty} size="small" color={getDifficultyColor(problem.difficulty) as any} />
                                  <Chip
                                    label={`${problem.google_interview_relevance?.toFixed(0) || 0}% Google`}
                                    size="small"
                                    variant="outlined"
                                    icon={<BusinessCenter sx={{ fontSize: 14 }} />}
                                  />
                                  {problem.google_interview_relevance && problem.google_interview_relevance >= 6 && (
                                    <Chip label="Interview Ready" size="small" color="success" icon={<CheckCircle sx={{ fontSize: 14 }} />} />
                                  )}
                                </Box>

                                <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                                  {problem.algorithm_tags?.slice(0, 3).map((tag, index) => (
                                    <Chip key={index} label={tag} size="small" variant="outlined" />
                                  ))}
                                  {problem.algorithm_tags && problem.algorithm_tags.length > 3 && (
                                    <Chip label={`+${problem.algorithm_tags.length - 3} more`} size="small" variant="outlined" />
                                  )}
                                  {problem.algorithm_tags && (
                                    <Chip
                                      label={`${getAlgorithmPriority(problem.algorithm_tags)} Priority`}
                                      size="small"
                                      color={
                                        getAlgorithmPriority(problem.algorithm_tags) === 'High'
                                          ? 'success'
                                          : getAlgorithmPriority(problem.algorithm_tags) === 'Medium'
                                          ? 'warning'
                                          : 'default'
                                      }
                                      variant="outlined"
                                    />
                                  )}
                                </Box>

                                <Box display="flex" justifyContent="space-between" alignItems="center">
                                  <Box display="flex" alignItems="center" gap={1}>
                                    <TrendingUp sx={{ fontSize: 16, color: 'text.secondary' }} />
                                    <Typography variant="caption" color="text.secondary">
                                      Relevance: {problem.google_interview_relevance?.toFixed(1) || 'N/A'}%
                                    </Typography>
                                  </Box>
                                  <Box display="flex" alignItems="center" gap={1}>
                                    <Typography variant="caption" color="textSecondary">
                                      {problem.solution_count || 0} solutions
                                    </Typography>
                                    <Button
                                      size="small"
                                      variant="outlined"
                                      aria-label={`Start solving: ${problem.title}`}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        trackingAPI.trackInteraction({ user_id: userId, problem_id: problem.id, action: 'attempted', session_id: sessionId });
                                        navigate('/practice', { state: { problemId: problem.id } });
                                      }}
                                    >
                                      Start
                                    </Button>
                                  </Box>
                                </Box>
                              </CardContent>
                            </Card>
                          </div>
                        );
                      }}
                    </FixedSizeGrid>
                  );
                }}
              </AutoSizer>
            </Box>
          )}
        </>
      ) : (
        // List View (virtualized)
        <Box>
          {loading && problems.length === 0 && (
            <Box>
              {Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={`ls-${i}`} variant="list" />
              ))}
            </Box>
          )}
          <VirtualList
            height={Math.min(600, Math.max(ITEM_SIZE, problems.length * ITEM_SIZE))}
            itemCount={problems.length}
            itemSize={ITEM_SIZE}
            width={'100%'}
          >
            {({ index, style }) => {
              const problem = problems[index];
              return (
                <div style={style} key={problem.id}>
                  <Card
                    sx={{ mb: 2, cursor: 'pointer', '&:hover': { backgroundColor: 'action.hover' } }}
                    onClick={() => { lastFocusedCardIdRef.current = `problem-card-${problem.id}`; handleProblemClick(problem); }}
                    id={`problem-card-${problem.id}`}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); lastFocusedCardIdRef.current = `problem-card-${problem.id}`; handleProblemClick(problem); } }}
                  >
                    <CardContent>
                      <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} md={6}>
                          <Typography variant="h6" fontWeight="bold">{highlightText(problem.title || '', searchQuery)}</Typography>
                          <Box display="flex" gap={1} mt={1}>
                            <Chip label={problem.platform} size="small" sx={{ backgroundColor: getPlatformColor(problem.platform), color: 'white' }} />
                            <Chip label={problem.difficulty} size="small" color={getDifficultyColor(problem.difficulty) as any} />
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={3}>
                          <Box display="flex" gap={1} flexWrap="wrap">
                            {problem.algorithm_tags?.slice(0, 2).map((tag, idx) => (
                              <Chip key={idx} label={tag} size="small" variant="outlined" />
                            ))}
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={3}>
                          <Box display="flex" gap={1} alignItems="center" justifyContent="flex-end">
                            <Tooltip title={favoriteIds.has(problem.id) ? 'Remove from favorites' : 'Add to favorites'}>
                                <IconButton 
                                  size="small"
                                  aria-label={`${favoriteIds.has(problem.id) ? 'Remove from favorites' : 'Add to favorites'}: ${problem.title}`}
                                  aria-pressed={favoriteIds.has(problem.id)}
                                  onClick={(e) => { e.stopPropagation(); toggleFavorite(problem.id, !favoriteIds.has(problem.id)); }}
                                >
                                {favoriteIds.has(problem.id) ? <Bookmark color="primary" fontSize="small" /> : <BookmarkBorder fontSize="small" />}
                              </IconButton>
                            </Tooltip>
                            <Typography variant="body2">Quality: {problem.quality_score?.toFixed(1) || 'N/A'}</Typography>
                            <Typography variant="body2" color="text.secondary">Google: {problem.google_interview_relevance?.toFixed(1) || 'N/A'}%</Typography>
                            <Button size="small" variant="outlined" aria-label={`Start solving: ${problem.title}`} onClick={(e) => { e.stopPropagation();
                              trackingAPI.trackInteraction({ user_id: userId, problem_id: problem.id, action: 'attempted', session_id: sessionId });
                              navigate('/practice', { state: { problemId: problem.id } });
                            }}>Start</Button>
                          </Box>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </div>
              );
            }}
          </VirtualList>
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
              pushUrlState({ page });
            }}
            color="primary"
            size="large"
          />
        </Box>
      )}

      {/* Problem Details Dialog */}
      <Dialog 
        open={!!selectedProblem} 
        onClose={handleCloseDialog}
        aria-labelledby={selectedProblem ? `problem-dialog-title-${selectedProblem.id}` : undefined}
        maxWidth="lg"
        fullWidth
      >
        {selectedProblem && (
          <>
            <DialogTitle id={`problem-dialog-title-${selectedProblem.id}`}>
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

                  {/* Dual-coding panel (feature-flagged) */}
                  {process.env.REACT_APP_FEATURE_DUAL_CODING !== 'off' && (
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="h6">Dual-Coding: Visuals + Verbal</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <DualCodingContent problemId={selectedProblem.id} />
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
              <Button onClick={handleCloseDialog}>Close</Button>
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
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No problems found
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Try adjusting your search query or filters
            </Typography>
            <Button variant="outlined" onClick={resetFilters}>
              Clear All Filters
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={2500}
        message={snackbar.message}
        onClose={() => setSnackbar({ open: false, message: '' })}
      />
    </Box>
  );
};

export default ProblemBrowser;
