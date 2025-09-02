/**
 * Advanced State Management for Skill Tree Performance
 * Using React Context + Reducer pattern with optimizations
 */

import React, { createContext, useContext, useReducer, useCallback, useMemo, useEffect } from 'react';

// Action Types
const ACTION_TYPES = {
  // Data loading
  SET_LOADING: 'SET_LOADING',
  SET_SKILL_AREAS: 'SET_SKILL_AREAS',
  SET_SKILL_AREA_PROBLEMS: 'SET_SKILL_AREA_PROBLEMS',
  APPEND_SKILL_AREA_PROBLEMS: 'APPEND_SKILL_AREA_PROBLEMS',
  SET_SEARCH_RESULTS: 'SET_SEARCH_RESULTS',
  SET_USER_PROGRESS: 'SET_USER_PROGRESS',
  
  // UI state
  TOGGLE_SKILL_AREA: 'TOGGLE_SKILL_AREA',
  SET_FILTERS: 'SET_FILTERS',
  SET_SELECTED_PROBLEM: 'SET_SELECTED_PROBLEM',
  SET_PAGINATION: 'SET_PAGINATION',
  
  // Performance
  SET_CACHE: 'SET_CACHE',
  CLEAR_CACHE: 'CLEAR_CACHE',
  SET_ERROR: 'SET_ERROR'
};

// Initial State
const initialState = {
  // Data
  skillAreas: [],
  skillAreaProblems: {}, // { skillArea: { problems: [], page: 1, hasNext: true, totalCount: 0 } }
  searchResults: { problems: [], totalCount: 0, query: '' },
  userProgress: null,
  
  // UI State
  expandedAreas: {},
  selectedProblem: null,
  filters: {
    difficulty: '',
    sortBy: 'quality',
    sortOrder: 'desc',
    searchQuery: ''
  },
  
  // Performance
  loading: {
    overview: false,
    skillAreas: {},
    search: false
  },
  cache: new Map(), // In-memory cache for API responses
  errors: {},
  
  // Statistics
  statistics: null
};

// Reducer
function skillTreeReducer(state, action) {
  switch (action.type) {
    case ACTION_TYPES.SET_LOADING:
      return {
        ...state,
        loading: {
          ...state.loading,
          [action.payload.type]: action.payload.value
        }
      };
      
    case ACTION_TYPES.SET_SKILL_AREAS:
      return {
        ...state,
        skillAreas: action.payload,
        loading: { ...state.loading, overview: false }
      };
      
    case ACTION_TYPES.SET_SKILL_AREA_PROBLEMS:
      return {
        ...state,
        skillAreaProblems: {
          ...state.skillAreaProblems,
          [action.payload.skillArea]: {
            problems: action.payload.problems,
            page: action.payload.page,
            hasNext: action.payload.hasNext,
            totalCount: action.payload.totalCount,
            lastUpdated: Date.now()
          }
        },
        loading: {
          ...state.loading,
          skillAreas: {
            ...state.loading.skillAreas,
            [action.payload.skillArea]: false
          }
        }
      };
      
    case ACTION_TYPES.APPEND_SKILL_AREA_PROBLEMS:
      const existingData = state.skillAreaProblems[action.payload.skillArea] || { problems: [] };
      return {
        ...state,
        skillAreaProblems: {
          ...state.skillAreaProblems,
          [action.payload.skillArea]: {
            ...existingData,
            problems: [...existingData.problems, ...action.payload.problems],
            page: action.payload.page,
            hasNext: action.payload.hasNext,
            totalCount: action.payload.totalCount,
            lastUpdated: Date.now()
          }
        },
        loading: {
          ...state.loading,
          skillAreas: {
            ...state.loading.skillAreas,
            [action.payload.skillArea]: false
          }
        }
      };
      
    case ACTION_TYPES.TOGGLE_SKILL_AREA:
      return {
        ...state,
        expandedAreas: {
          ...state.expandedAreas,
          [action.payload]: !state.expandedAreas[action.payload]
        }
      };
      
    case ACTION_TYPES.SET_FILTERS:
      return {
        ...state,
        filters: {
          ...state.filters,
          ...action.payload
        }
      };
      
    case ACTION_TYPES.SET_SELECTED_PROBLEM:
      return {
        ...state,
        selectedProblem: action.payload
      };
      
    case ACTION_TYPES.SET_SEARCH_RESULTS:
      return {
        ...state,
        searchResults: action.payload,
        loading: { ...state.loading, search: false }
      };
      
    case ACTION_TYPES.SET_USER_PROGRESS:
      return {
        ...state,
        userProgress: action.payload
      };
      
    case ACTION_TYPES.SET_CACHE:
      const newCache = new Map(state.cache);
      newCache.set(action.payload.key, {
        data: action.payload.data,
        timestamp: Date.now(),
        ttl: action.payload.ttl || 300000 // 5 minutes default
      });
      return {
        ...state,
        cache: newCache
      };
      
    case ACTION_TYPES.CLEAR_CACHE:
      return {
        ...state,
        cache: new Map()
      };
      
    case ACTION_TYPES.SET_ERROR:
      return {
        ...state,
        errors: {
          ...state.errors,
          [action.payload.type]: action.payload.error
        }
      };
      
    default:
      return state;
  }
}

// Context
const SkillTreeContext = createContext();

// Provider Component
export const SkillTreeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(skillTreeReducer, initialState);
  
  // API Configuration
  const MAIN_API = (process.env.REACT_APP_API_URL || 'http://localhost:8000');
  const EXTERNAL = (process.env.REACT_APP_SKILL_TREE_URL || '');
  const USE_EXTERNAL = !!EXTERNAL && process.env.REACT_APP_FEATURE_SKILL_TREE_MAIN_API === 'off';
  const API_BASE = USE_EXTERNAL ? (EXTERNAL + '/skill-tree-v2') : (MAIN_API + '/skill-tree-proxy');
  const USER_ID = 'demo_user_2025';
  
  // OPTIMIZATION: Cache management
  const getCachedData = useCallback((key) => {
    const cached = state.cache.get(key);
    if (cached && Date.now() - cached.timestamp < cached.ttl) {
      return cached.data;
    }
    return null;
  }, [state.cache]);
  
  const setCachedData = useCallback((key, data, ttl) => {
    dispatch({
      type: ACTION_TYPES.SET_CACHE,
      payload: { key, data, ttl }
    });
  }, []);
  
  // OPTIMIZATION: Debounced API calls
  const debounce = useCallback((func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }, []);
  
  // API Methods
  const loadSkillAreas = useCallback(async () => {
    const cacheKey = 'skill-areas-overview';
    const cached = getCachedData(cacheKey);
    
    if (cached) {
      dispatch({ type: ACTION_TYPES.SET_SKILL_AREAS, payload: cached });
      return;
    }
    
    try {
      dispatch({ type: ACTION_TYPES.SET_LOADING, payload: { type: 'overview', value: true } });
      
  const response = await fetch(`${API_BASE}/overview-optimized?user_id=${USER_ID}&top_problems_per_area=5`);
  if (!response.ok) throw new Error(`Overview error ${response.status}`);
  const data = await response.json();
      
  dispatch({ type: ACTION_TYPES.SET_SKILL_AREAS, payload: data.skill_areas });
      setCachedData(cacheKey, data.skill_areas, 900000); // 15 minutes
      
    } catch (error) {
      dispatch({
        type: ACTION_TYPES.SET_ERROR,
        payload: { type: 'overview', error: error.message }
      });
    }
  }, [getCachedData, setCachedData]);
  
  const loadSkillAreaProblems = useCallback(async (skillArea, page = 1, append = false) => {
    const { difficulty, sortBy, sortOrder } = state.filters;
    const cacheKey = `skill-area-${skillArea}-${page}-${difficulty}-${sortBy}-${sortOrder}`;
    const cached = getCachedData(cacheKey);
    
    if (cached && !append) {
      const actionType = append ? ACTION_TYPES.APPEND_SKILL_AREA_PROBLEMS : ACTION_TYPES.SET_SKILL_AREA_PROBLEMS;
      dispatch({
        type: actionType,
        payload: { skillArea, ...cached }
      });
      return;
    }
    
    try {
      dispatch({
        type: ACTION_TYPES.SET_LOADING,
        payload: { type: 'skillAreas', value: { ...state.loading.skillAreas, [skillArea]: true } }
      });
      
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '20',
        sort_by: sortBy,
        sort_order: sortOrder
      });
      
      if (difficulty) {
        params.append('difficulty', difficulty);
      }
      
      const response = await fetch(`${API_BASE}/skill-area/${skillArea}/problems?${params}`);
      const data = await response.json();
      
      const actionType = append ? ACTION_TYPES.APPEND_SKILL_AREA_PROBLEMS : ACTION_TYPES.SET_SKILL_AREA_PROBLEMS;
      const payload = {
        skillArea,
        problems: data.problems,
        page: data.page,
        hasNext: data.has_next,
        totalCount: data.total_count
      };
      
      dispatch({ type: actionType, payload });
      setCachedData(cacheKey, payload, 600000); // 10 minutes
      
    } catch (error) {
      dispatch({
        type: ACTION_TYPES.SET_ERROR,
        payload: { type: 'skillArea', error: error.message }
      });
    }
  }, [state.filters, state.loading.skillAreas, getCachedData, setCachedData]);
  
  const searchProblems = useCallback(async (query, filters = {}) => {
    if (query.length < 2) return;
    
    const cacheKey = `search-${query}-${JSON.stringify(filters)}`;
    const cached = getCachedData(cacheKey);
    
    if (cached) {
      dispatch({ type: ACTION_TYPES.SET_SEARCH_RESULTS, payload: cached });
      return;
    }
    
    try {
      dispatch({ type: ACTION_TYPES.SET_LOADING, payload: { type: 'search', value: true } });
      
      const params = new URLSearchParams({
        query: query,
        page: '1',
        page_size: '50'
      });
      
      // Add filters
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value.length > 0) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
          } else {
            params.append(key, value);
          }
        }
      });
      
      const response = await fetch(`${API_BASE}/search?${params}`);
      const data = await response.json();
      
      const payload = {
        problems: data.problems,
        totalCount: data.total_count,
        query: query
      };
      
      dispatch({ type: ACTION_TYPES.SET_SEARCH_RESULTS, payload });
      setCachedData(cacheKey, payload, 300000); // 5 minutes
      
    } catch (error) {
      dispatch({
        type: ACTION_TYPES.SET_ERROR,
        payload: { type: 'search', error: error.message }
      });
    }
  }, [getCachedData, setCachedData]);
  
  // Debounced search
  const debouncedSearch = useMemo(
    () => debounce(searchProblems, 300),
    [searchProblems, debounce]
  );
  
  // Actions
  const actions = {
    loadSkillAreas,
    loadSkillAreaProblems,
    searchProblems: debouncedSearch,
    
    toggleSkillArea: useCallback((skillArea) => {
      dispatch({ type: ACTION_TYPES.TOGGLE_SKILL_AREA, payload: skillArea });
      
      // Load problems if expanding for the first time
      if (!state.expandedAreas[skillArea] && !state.skillAreaProblems[skillArea]) {
        loadSkillAreaProblems(skillArea, 1);
      }
    }, [state.expandedAreas, state.skillAreaProblems, loadSkillAreaProblems]),
    
    loadMoreProblems: useCallback((skillArea) => {
      const currentData = state.skillAreaProblems[skillArea];
      if (currentData && currentData.hasNext) {
        loadSkillAreaProblems(skillArea, currentData.page + 1, true);
      }
    }, [state.skillAreaProblems, loadSkillAreaProblems]),
    
    setFilters: useCallback((filters) => {
      dispatch({ type: ACTION_TYPES.SET_FILTERS, payload: filters });
      
      // Clear relevant caches when filters change
      const newCache = new Map();
      for (const [key, value] of state.cache.entries()) {
        if (!key.includes('skill-area-') && !key.includes('search-')) {
          newCache.set(key, value);
        }
      }
      dispatch({ type: ACTION_TYPES.CLEAR_CACHE });
      state.cache = newCache;
      
    }, [state.cache]),
    
    selectProblem: useCallback((problem) => {
      dispatch({ type: ACTION_TYPES.SET_SELECTED_PROBLEM, payload: problem });
    }, []),
    
    clearCache: useCallback(() => {
      dispatch({ type: ACTION_TYPES.CLEAR_CACHE });
    }, [])
  };
  
  // OPTIMIZATION: Initialize data on mount
  useEffect(() => {
    loadSkillAreas();
  }, [loadSkillAreas]);
  
  // OPTIMIZATION: Cache cleanup interval
  useEffect(() => {
    const cleanup = setInterval(() => {
      const now = Date.now();
      const newCache = new Map();
      
      for (const [key, value] of state.cache.entries()) {
        if (now - value.timestamp < value.ttl) {
          newCache.set(key, value);
        }
      }
      
      if (newCache.size !== state.cache.size) {
        dispatch({ type: ACTION_TYPES.CLEAR_CACHE });
        state.cache = newCache;
      }
    }, 60000); // Cleanup every minute
    
    return () => clearInterval(cleanup);
  }, [state.cache]);
  
  // Memoized context value
  const contextValue = useMemo(() => ({
    state,
    actions
  }), [state, actions]);
  
  return (
    <SkillTreeContext.Provider value={contextValue}>
      {children}
    </SkillTreeContext.Provider>
  );
};

// Hook for using the context
export const useSkillTree = () => {
  const context = useContext(SkillTreeContext);
  if (!context) {
    throw new Error('useSkillTree must be used within a SkillTreeProvider');
  }
  return context;
};

// Selectors for optimized data access
export const useSkillTreeSelectors = () => {
  const { state } = useSkillTree();
  
  return useMemo(() => ({
    // Basic selectors
    skillAreas: state.skillAreas,
    isLoading: state.loading.overview,
    selectedProblem: state.selectedProblem,
    filters: state.filters,
    
    // Computed selectors
    totalProblems: state.skillAreas.reduce((sum, area) => sum + area.total_problems, 0),
    
    expandedSkillAreas: Object.entries(state.expandedAreas)
      .filter(([_, expanded]) => expanded)
      .map(([skillArea]) => skillArea),
    
    skillAreaProblemsCount: Object.entries(state.skillAreaProblems)
      .reduce((acc, [skillArea, data]) => {
        acc[skillArea] = data.problems.length;
        return acc;
      }, {}),
    
    // Performance selectors
    cacheSize: state.cache.size,
    errorCount: Object.keys(state.errors).length,
    
    // Search selectors
    hasSearchResults: state.searchResults.problems.length > 0,
    searchResultsCount: state.searchResults.totalCount
    
  }), [state]);
};

export default SkillTreeProvider;
