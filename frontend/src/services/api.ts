import axios from 'axios';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
export const apiService = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
apiService.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
apiService.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      // Redirect to login if needed
    }
    return Promise.reject(error);
  }
);

// API endpoints interface
export interface Problem {
  id: string;
  platform: string;
  platform_id: string;
  title: string;
  description?: string;
  difficulty: string;
  category?: string;
  algorithm_tags: string[];
  data_structures?: string[];
  google_interview_relevance: number;
  difficulty_rating?: number;
  quality_score: number;
  popularity_score?: number;
  acceptance_rate?: number;
  companies?: string[];
  solution_count?: number;
  created_at?: string;
}

export interface Recommendation {
  id: string;
  title: string;
  difficulty: string;
  recommendation_score: number;
  // Backend returns `recommendation_reason`; keep both for compatibility
  recommendation_reason?: string;
  recommendation_reasoning?: string;
  algorithm_tags: string[];
  google_interview_relevance: number;
  quality_score: number;
}

export interface LearningPath {
  id: string;
  user_id: string;
  target_goal: string;
  current_level: string;
  duration_weeks: number;
  total_problems: number;
  weekly_plan: WeeklyPlan[];
  estimated_completion_time: {
    total_hours: number;
    hours_per_week: number;
    easy_problems: number;
    medium_problems: number;
    hard_problems: number;
  };
  created_at: string;
}

export interface WeeklyPlan {
  week: number;
  problems: Problem[];
  focus_areas: string[];
  estimated_hours: number;
}

export interface UserAnalytics {
  user_id: string;
  total_interactions: number;
  activity_summary: {
    actions: Record<string, number>;
    most_common_action: string;
    unique_problems: number;
    unique_sessions: number;
  };
  problem_solving_stats: {
    solved: number;
    attempted: number;
    success_rate: number;
    average_solve_time: number;
  };
  learning_patterns: {
    active_days: number;
    total_days_period: number;
    consistency_score: number;
    average_daily_interactions: number;
  };
}

// API service methods
export const problemsAPI = {
  // Get all problems with filtering
  getProblems: async (params?: {
    difficulty?: string;
    platform?: string;
    category?: string;
    limit?: number;
    offset?: number;
    // Extended filters supported by backend
    min_quality?: number;
    min_relevance?: number;
    interview_ready?: boolean;
    algorithm_priority?: string;
    order_by?: string;
  }) => {
    const response = await apiService.get('/problems', { params });
    return response.data;
  },

  // Get single problem by ID
  getProblem: async (problemId: string) => {
    const response = await apiService.get(`/problems/${problemId}`);
    return response.data;
  },

  // Search problems
  searchProblems: async (query: string) => {
    const response = await apiService.get('/search', {
      params: { query, limit: 20 }
    });
    return response.data;
  },
};

export const recommendationsAPI = {
  // Get personalized recommendations
  getRecommendations: async (params?: {
    user_id?: string;
    difficulty_level?: string;
    focus_area?: string;
    limit?: number;
  }) => {
    const response = await apiService.get('/recommendations', { params });
    return response.data;
  },

  // Get similar problems
  getSimilarProblems: async (problemId: string, limit = 5) => {
    const response = await apiService.get(`/recommendations/similar/${problemId}`, {
      params: { limit }
    });
    return response.data;
  },

  // Train ML models
  trainModels: async () => {
    const response = await apiService.post('/ml/train');
    return response.data;
  },
};

export const learningPathsAPI = {
  // Generate learning path
  generateLearningPath: async (params: {
    user_id: string;
    goal?: string;
    level?: string;
    duration_weeks?: number;
  }) => {
    // Convert params to the format expected by the POST endpoint
    // Using skill names that actually exist in the database
    const requestData = {
      user_id: params.user_id,
      current_skill_levels: {
        'array': 0.3,           // matches database algorithm_tags
        'hash_table': 0.2,      // matches database algorithm_tags
        'binary_search': 0.1,   // matches database algorithm_tags
        'two_pointers': 0.2,    // matches database algorithm_tags
        'sliding_window': 0.1,  // matches database algorithm_tags
        'greedy': 0.2,          // matches database algorithm_tags
        'sorting': 0.2,         // matches database algorithm_tags
        'string': 0.2           // matches database algorithm_tags
      },
      learning_goals: [params.goal || 'google_interview'],
      available_hours_per_week: 10,
      preferred_difficulty_curve: 'gradual',
      target_completion_weeks: params.duration_weeks || 8,
      weak_areas: ['binary_search', 'sliding_window'],  // Use actual algorithm tags
      strong_areas: ['array', 'hash_table']            // Use actual algorithm tags
    };

    const response = await apiService.post('/learning-paths/generate', requestData);
    return response.data;
  },
  
  // Quick start beginner preset
  quickStart: async (payload: { user_id: string; preset_id?: string; hours_per_week?: number; duration_weeks?: number; goals?: string[] }) => {
    const response = await apiService.post('/learning-paths/quick-start', payload);
    return response.data;
  },
  
  // Retrieve a specific learning path
  getPath: async (pathId: string) => {
    const response = await apiService.get(`/learning-paths/${pathId}`);
    return response.data;
  },

  // Get next problems
  getNextProblems: async (pathId: string, count?: number) => {
    const params = typeof count === 'number' ? { count } : {};
    const response = await apiService.get(`/learning-paths/${pathId}/next-problems`, { params });
    return response.data;
  },

  // Update progress
  updateProgress: async (pathId: string, payload: any) => {
    const response = await apiService.post(`/learning-paths/${pathId}/progress`, payload);
    return response.data;
  },

  // Adapt path
  adaptPath: async (pathId: string, payload: any) => {
    const response = await apiService.post(`/learning-paths/${pathId}/adapt`, payload);
    return response.data;
  },

  // List by user
  listUserPaths: async (userId: string, status?: string) => {
    const params = status ? { status } : {};
    const response = await apiService.get(`/learning-paths/user/${userId}`, { params });
    return response.data;
  },

  // Milestones
  listMilestones: async (pathId: string, excludeCompleted?: boolean) => {
    const params = typeof excludeCompleted === 'boolean' ? { exclude_completed: excludeCompleted } : {};
    const response = await apiService.get(`/learning-paths/${pathId}/milestones`, { params });
    return response.data;
  },
  completeMilestone: async (pathId: string, milestoneId: string, payload?: any) => {
    const response = await apiService.post(`/learning-paths/${pathId}/milestones/${milestoneId}/complete`, payload || {});
    return response.data;
  },
};

export const trackingAPI = {
  // Track user interaction
  trackInteraction: async (params: {
    user_id: string;
    problem_id: string;
    action: string;
    time_spent?: number;
    success?: boolean;
    session_id?: string;
    metadata?: string;
  }) => {
    const response = await apiService.post('/interactions/track', null, { params });
    return response.data;
  },

  // Get user analytics
  getUserAnalytics: async (userId: string, daysBack = 30) => {
    const response = await apiService.get(`/analytics/user/${userId}`, {
      params: { days_back: daysBack }
    });
    return response.data;
  },

  // Get platform trends
  getTrends: async (daysBack = 7) => {
    const response = await apiService.get('/analytics/trends', {
      params: { days_back: daysBack }
    });
    return response.data;
  },
};

export const statsAPI = {
  // Get platform statistics
  getStats: async () => {
    const response = await apiService.get('/stats');
    return response.data;
  },

  // Get platform analytics
  getPlatformAnalytics: async () => {
    const response = await apiService.get('/analytics/platforms');
    return response.data;
  },
};

// Favorites API
export const favoritesAPI = {
  list: async (userId: string, includeDetails = false) => {
    const response = await apiService.get('/favorites', {
      params: { user_id: userId, include_details: includeDetails },
    });
    return response.data;
  },
  toggle: async (payload: { user_id: string; problem_id: string; favorite: boolean }) => {
    const response = await apiService.post('/favorites/toggle', payload);
    return response.data;
  },
};

// Enhanced Statistics API for interview readiness and algorithm relevance
export const enhancedStatsAPI = {
  // Get algorithm relevance analysis
  getAlgorithmRelevance: async () => {
    const response = await apiService.get('/enhanced-stats/algorithm-relevance');
    return response.data;
  },

  // Get interview readiness statistics
  getInterviewReadiness: async () => {
    const response = await apiService.get('/enhanced-stats/interview-readiness');
    return response.data;
  },

  // Get enhanced overview (includes relevance distribution)
  getOverview: async () => {
    const response = await apiService.get('/enhanced-stats/overview');
    return response.data;
  },
};

// AI API for hints, reviews, and status
export const aiAPI = {
  // Get AI status
  getStatus: async (sessionId?: string) => {
    const params = sessionId ? { session_id: sessionId } : {};
    const response = await apiService.get('/ai/status', { params });
    return response.data;
  },

  // Get hint for a problem
  getHint: async (problemId: string, query?: string, sessionId?: string) => {
    const response = await apiService.post('/ai/hint', {
      problem_id: problemId,
      query,
      session_id: sessionId,
    });
    return response.data;
  },

  // Review code
  reviewCode: async (code: string, rubric?: any, problemId?: string) => {
    const response = await apiService.post('/ai/review', {
      code,
      rubric,
      problem_id: problemId,
    });
    return response.data;
  },

  // Elaborate on a problem
  elaborate: async (problemId: string) => {
    const response = await apiService.post('/ai/elaborate', {
      problem_id: problemId,
    });
    return response.data;
  },

  // Reset AI counters
  reset: async (sessionId?: string, resetGlobal = true) => {
    const response = await apiService.post('/ai/reset', {
      session_id: sessionId,
      reset_global: resetGlobal,
    });
    return response.data;
  },

  // Streamed Hint (SSE)
  streamHint: (
    problemId: string,
    opts: {
      query?: string;
      sessionId?: string;
      onMeta?: (meta: any) => void;
      onHint?: (hint: any) => void;
      onDone?: () => void;
      onError?: (err: any) => void;
    }
  ) => {
    const base = (process.env.REACT_APP_API_URL || 'http://localhost:8000').replace(/\/$/, '');
    const params = new URLSearchParams();
    params.set('problem_id', problemId);
    if (opts.query) params.set('query', opts.query);
    if (opts.sessionId) params.set('session_id', opts.sessionId);
    const url = `${base}/ai/hint/stream?${params.toString()}`;
    const es = new EventSource(url);
    const handleMessage = (ev: MessageEvent) => {
      try {
        const data = JSON.parse(ev.data);
        if (data?.type === 'meta' && opts.onMeta) opts.onMeta(data);
        else if (data?.type === 'hint' && opts.onHint) opts.onHint(data.hint);
        else if (data?.type === 'done') {
          if (opts.onDone) opts.onDone();
          es.close();
        } else if (data?.type === 'error') {
          if (opts.onError) opts.onError(data);
          es.close();
        }
      } catch (e) {
        // ignore parse errors
      }
    };
    es.onmessage = handleMessage;
    es.onerror = (err) => {
      if (opts.onError) opts.onError(err);
      try { es.close(); } catch {}
    };
    return { close: () => { try { es.close(); } catch {} } };
  },

  // Streamed Review (SSE over fetch)
  streamReview: (
    payload: { code: string; rubric?: any; problem_id?: string },
    opts: {
      onMeta?: (meta: any) => void;
      onStrength?: (text: string) => void;
      onSuggestion?: (text: string) => void;
      onDone?: () => void;
      onError?: (err: any) => void;
    }
  ) => {
    const controller = new AbortController();
    const base = (process.env.REACT_APP_API_URL || 'http://localhost:8000').replace(/\/$/, '');
    fetch(`${base}/ai/review/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    }).then(async (resp) => {
      if (!resp.body) throw new Error('No stream body');
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        // Parse SSE chunks split by double newlines
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';
        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith('data:')) continue;
          const jsonStr = line.replace(/^data:\s*/, '');
          try {
            const data = JSON.parse(jsonStr);
            if (data?.type === 'meta' && opts.onMeta) opts.onMeta(data);
            else if (data?.type === 'strength' && opts.onStrength) opts.onStrength(data.text);
            else if (data?.type === 'suggestion' && opts.onSuggestion) opts.onSuggestion(data.text);
            else if (data?.type === 'done') { if (opts.onDone) opts.onDone(); controller.abort(); }
            else if (data?.type === 'error') { if (opts.onError) opts.onError(data); controller.abort(); }
          } catch (e) {
            // ignore
          }
        }
      }
    }).catch((err) => {
      if (opts.onError) opts.onError(err);
    });
    return { abort: () => { try { controller.abort(); } catch {} } };
  },
};

// Practice API
export const practiceAPI = {
  // Create a practice session
  startSession: async (payload: {
    user_id?: string;
    size?: number;
    difficulty?: 'Easy' | 'Medium' | 'Hard' | string;
    focus_areas?: string[];
    interleaving?: boolean;
  }) => {
    const response = await apiService.post('/practice/session', payload);
    return response.data;
  },

  // Log a problem attempt
  logAttempt: async (payload: {
    user_id: string;
    problem_id: string;
    status: 'started' | 'attempted' | 'solved' | string;
    time_spent_seconds?: number;
    code?: string;
    language?: string;
    session_id?: string;
    metadata?: any;
  }) => {
    const response = await apiService.post('/practice/attempt', payload);
    return response.data;
  },

  // Elaborative interrogation entry
  elaborative: async (payload: {
    user_id?: string;
    problem_id?: string;
    question: string;
    context?: string;
  }) => {
    const response = await apiService.post('/practice/elaborative', payload);
    return response.data;
  },

  // Working memory check
  workingMemoryCheck: async (payload: {
    user_id?: string;
    problem_id?: string;
    metrics: Record<string, number>;
  }) => {
    const response = await apiService.post('/practice/working-memory-check', payload);
    return response.data;
  },

  // Gates namespace
  gates: {
    start: async (payload: { problem_id: string; session_id?: string }) => {
      const response = await apiService.post('/practice/gates/start', payload);
      return response.data;
    },
    progress: async (payload: { session_id: string; gate: 'dry_run' | 'pseudocode' | 'code'; value: boolean }) => {
      const response = await apiService.post('/practice/gates/progress', payload);
      return response.data;
    },
    status: async (sessionId: string) => {
      const response = await apiService.get('/practice/gates/status', { params: { session_id: sessionId } });
      return response.data;
    },
    list: async (problemId?: string) => {
      const params = problemId ? { problem_id: problemId } : {};
      const response = await apiService.get('/practice/gates', { params });
      return response.data;
    },
    get: async (sessionId: string) => {
      const response = await apiService.get(`/practice/gates/${sessionId}`);
      return response.data;
    },
    delete: async (sessionId: string) => {
      const response = await apiService.delete(`/practice/gates/${sessionId}`);
      return response.data;
    },
  },
};

// Cognitive API
export const cognitiveAPI = {
  getProfile: async (userId: string) => {
    const response = await apiService.get('/cognitive/profile', { params: { user_id: userId } });
    return response.data;
  },
  assess: async (payload: any) => {
    const response = await apiService.post('/cognitive/assess', payload);
    return response.data;
  },
  getAdaptation: async (userId: string) => {
    const response = await apiService.get('/cognitive/adaptation', { params: { user_id: userId } });
    return response.data;
  },
};

// Interview API
export const interviewAPI = {
  start: async (payload: { problem_id: string; duration_minutes?: number; constraints?: any; session_id?: string }) => {
    const response = await apiService.post('/interview/start', payload);
    return response.data;
  },
  complete: async (payload: { interview_id: string; code: string; language?: string; metrics?: any }) => {
    const response = await apiService.post('/interview/complete', payload);
    return response.data;
  },
};

// SRS (Spaced Repetition) API
export const srsAPI = {
  // Get next due review items (problems or patterns)
  getNextDue: async (params?: { user_id?: string; limit?: number }) => {
    const response = await apiService.get('/srs/next', { params });
    return response.data;
  },
  // Submit a review outcome
  submitReview: async (payload: {
    user_id?: string;
    item_id: string;
    item_type?: 'problem' | 'pattern' | string;
    rating: 0 | 1 | 2 | 3 | 4 | 5;
    time_spent_seconds?: number;
    notes?: string;
  }) => {
    const response = await apiService.post('/srs/review', payload);
    return response.data;
  },
  // Get SRS stats
  getStats: async (params?: { user_id?: string }) => {
    const response = await apiService.get('/srs/stats', { params });
    return response.data;
  },
};

// Settings API for configuration management
export const settingsAPI = {
  // Get settings
  getSettings: async (includeProviders = false, includeEffectiveFlags = false) => {
    const params: any = {};
    if (includeProviders) params.include_providers = true;
    if (includeEffectiveFlags) params.include_effective_flags = true;
    
    const response = await apiService.get('/settings', { params });
    return response.data;
  },

  // Update settings
  updateSettings: async (settings: any) => {
    const response = await apiService.put('/settings', settings);
    return response.data;
  },

  // Validate settings
  validateSettings: async (settings: any) => {
    const response = await apiService.post('/settings/validate', settings);
    return response.data;
  },

  // Get providers
  getProviders: async () => {
    const response = await apiService.get('/settings/providers');
    return response.data;
  },

  // Get effective settings
  getEffective: async () => {
    const response = await apiService.get('/settings/effective');
    return response.data;
  },

  // Get models for provider
  getModels: async (provider?: string) => {
    const params = provider ? { provider } : {};
    const response = await apiService.get('/settings/models', { params });
    return response.data;
  },

  // Update cognitive profile
  updateCognitiveProfile: async (profile: any) => {
    const response = await apiService.post('/settings/cognitive-profile', profile);
    return response.data;
  },
};

// Session management utilities
export const sessionManager = {
  // Generate a new session ID
  generateSessionId: (): string => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  },

  // Get current session ID or create one
  getCurrentSessionId: (): string => {
    let sessionId = sessionStorage.getItem('aiSessionId');
    if (!sessionId) {
      sessionId = sessionManager.generateSessionId();
      sessionStorage.setItem('aiSessionId', sessionId);
    }
    return sessionId;
  },

  // Clear current session
  clearCurrentSession: () => {
    sessionStorage.removeItem('aiSessionId');
  },

  // Set session ID
  setSessionId: (sessionId: string) => {
    sessionStorage.setItem('aiSessionId', sessionId);
  },
};

// Utility functions
export const generateSessionId = (): string => {
  return sessionManager.generateSessionId();
};

export const getCurrentUserId = (): string => {
  // Single-user mode: default to stable 'default_user'
  // If a userId is already set, keep it; otherwise set and return 'default_user'
  const existing = localStorage.getItem('userId');
  if (existing) return existing;
  localStorage.setItem('userId', 'default_user');
  return 'default_user';
};

export default apiService;

// Skill Tree API (preferences)
export interface SkillTreePreferences {
  preferred_view_mode: 'columns' | 'grid' | 'tree' | string;
  show_confidence_overlay: boolean;
  auto_expand_clusters: boolean;
  highlight_prerequisites: boolean;
  visible_skill_areas: string[];
}

export const skillTreeAPI = {
  getPreferences: async (userId: string): Promise<SkillTreePreferences> => {
    // When main API mounts skill-tree router (Option A), the base remains REACT_APP_API_URL
    const response = await apiService.get(`/skill-tree/preferences/${userId}`);
    return response.data;
  },
  updatePreferences: async (userId: string, prefs: SkillTreePreferences) => {
    const response = await apiService.post(`/skill-tree/preferences/${userId}`, prefs);
    return response.data;
  },
};
