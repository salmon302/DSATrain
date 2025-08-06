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
  difficulty: string;
  category: string;
  algorithm_tags: string[];
  data_structures: string[];
  google_interview_relevance: number;
  difficulty_rating: number;
  quality_score: number;
  popularity_score: number;
  acceptance_rate?: number;
  companies?: string[];
  solution_count: number;
  created_at: string;
}

export interface Recommendation {
  id: string;
  title: string;
  difficulty: string;
  recommendation_score: number;
  recommendation_reasoning: string;
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

// Utility functions
export const generateSessionId = (): string => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const getCurrentUserId = (): string => {
  // Get user ID from localStorage or generate a demo user ID
  let userId = localStorage.getItem('userId');
  if (!userId) {
    userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('userId', userId);
  }
  return userId;
};

export default apiService;
