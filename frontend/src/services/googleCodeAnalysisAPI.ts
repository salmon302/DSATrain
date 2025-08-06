/**
 * Google-style Code Analysis API Service
 * Provides analysis using Google's interview evaluation criteria
 */

export interface CodeSubmission {
  code: string;
  language: string;
  problem_id?: string;
  time_spent_seconds?: number;
  thinking_out_loud?: boolean;
  communication_notes?: string[];
}

export interface ComplexityAnalysis {
  time_complexity: string;
  space_complexity: string;
  confidence: number;
  explanation: string;
}

export interface CodeQualityMetrics {
  overall_score: number;
  readability: number;
  naming_conventions: number;
  code_structure: number;
  documentation: number;
  best_practices: number;
}

export interface GoogleCriteriaEvaluation {
  gca_score: number; // General Cognitive Ability
  rrk_score: number; // Role-Related Knowledge
  communication_score: number;
  googleyness_score: number;
  overall_score: number;
  detailed_feedback: Record<string, string>;
}

export interface CodeAnalysisResult {
  complexity: ComplexityAnalysis;
  quality: CodeQualityMetrics;
  google_criteria: GoogleCriteriaEvaluation;
  suggestions: string[];
  test_results: Array<{
    test_name: string;
    input: string;
    expected: string;
    actual: string;
    passed: boolean;
    execution_time_ms: number;
  }>;
  execution_successful: boolean;
  security_issues: string[];
  performance_insights: string[];
}

export interface GoogleCodingStandards {
  evaluation_criteria: {
    gca: {
      name: string;
      description: string;
      key_indicators: string[];
    };
    rrk: {
      name: string;
      description: string;
      key_indicators: string[];
    };
    communication: {
      name: string;
      description: string;
      key_indicators: string[];
    };
    googleyness: {
      name: string;
      description: string;
      key_indicators: string[];
    };
  };
  code_quality_standards: {
    readability: string[];
    documentation: string[];
    best_practices: string[];
  };
  interview_tips: string[];
}

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class GoogleCodeAnalysisAPI {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${url}:`, error);
      throw error;
    }
  }

  /**
   * Analyze code using Google's evaluation criteria
   */
  async analyzeCode(submission: CodeSubmission): Promise<CodeAnalysisResult> {
    return this.request<CodeAnalysisResult>('/code-analysis/analyze', {
      method: 'POST',
      body: JSON.stringify(submission),
    });
  }

  /**
   * Get Google's coding standards and interview criteria
   */
  async getGoogleStandards(): Promise<GoogleCodingStandards> {
    return this.request<GoogleCodingStandards>('/code-analysis/google-standards');
  }

  /**
   * Get complexity analysis guide
   */
  async getComplexityGuide(): Promise<{
    time_complexity: Record<string, {
      description: string;
      examples: string[];
      code_patterns: string[];
    }>;
    space_complexity: Record<string, string>;
    optimization_strategies: string[];
  }> {
    return this.request('/code-analysis/complexity-guide');
  }

  /**
   * Analyze code complexity only (lighter analysis)
   */
  async analyzeComplexity(code: string, language: string): Promise<ComplexityAnalysis> {
    const submission: CodeSubmission = {
      code,
      language,
      thinking_out_loud: false,
      communication_notes: []
    };
    
    const result = await this.analyzeCode(submission);
    return result.complexity;
  }

  /**
   * Get code quality metrics only
   */
  async analyzeCodeQuality(code: string, language: string): Promise<CodeQualityMetrics> {
    const submission: CodeSubmission = {
      code,
      language,
      thinking_out_loud: false,
      communication_notes: []
    };
    
    const result = await this.analyzeCode(submission);
    return result.quality;
  }

  /**
   * Evaluate against Google's interview criteria
   */
  async evaluateGoogleCriteria(
    code: string, 
    language: string, 
    timeSpent: number, 
    thinkingOutLoud: boolean = false,
    communicationNotes: string[] = []
  ): Promise<GoogleCriteriaEvaluation> {
    const submission: CodeSubmission = {
      code,
      language,
      time_spent_seconds: timeSpent,
      thinking_out_loud: thinkingOutLoud,
      communication_notes: communicationNotes
    };
    
    const result = await this.analyzeCode(submission);
    return result.google_criteria;
  }

  /**
   * Get improvement suggestions for code
   */
  async getImprovementSuggestions(code: string, language: string): Promise<string[]> {
    const submission: CodeSubmission = {
      code,
      language,
      thinking_out_loud: false,
      communication_notes: []
    };
    
    const result = await this.analyzeCode(submission);
    return result.suggestions;
  }
}

// Export singleton instance
export const googleCodeAnalysisAPI = new GoogleCodeAnalysisAPI();

// Utility functions for code analysis
export const analysisUtils = {
  /**
   * Get complexity color based on efficiency
   */
  getComplexityColor(complexity: string): 'success' | 'warning' | 'error' {
    const excellent = ['O(1)', 'O(log n)'];
    const good = ['O(n)', 'O(n log n)'];
    
    if (excellent.includes(complexity)) return 'success';
    if (good.includes(complexity)) return 'warning';
    return 'error';
  },

  /**
   * Get score color based on value
   */
  getScoreColor(score: number): 'success' | 'warning' | 'error' {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  },

  /**
   * Format time for display
   */
  formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  },

  /**
   * Get Google criteria description
   */
  getGoogleCriteriaDescription(criteria: 'gca_score' | 'rrk_score' | 'communication_score' | 'googleyness_score' | 'overall_score'): string {
    const descriptions: Record<string, string> = {
      gca_score: 'General Cognitive Ability: Problem-solving skills and algorithmic thinking',
      rrk_score: 'Role-Related Knowledge: Technical competency and programming skills',
      communication_score: 'Communication: Ability to explain thought process clearly',
      googleyness_score: 'Googleyness: Cultural fit and engineering best practices',
      overall_score: 'Overall evaluation based on all Google criteria'
    };
    
    return descriptions[criteria] || '';
  },

  /**
   * Generate practice recommendations based on analysis
   */
  generatePracticeRecommendations(analysis: CodeAnalysisResult): string[] {
    const recommendations = [];
    
    if (analysis.google_criteria.gca_score < 70) {
      recommendations.push('Practice algorithmic problem-solving on LeetCode or HackerRank');
      recommendations.push('Study time and space complexity analysis');
    }
    
    if (analysis.google_criteria.rrk_score < 70) {
      recommendations.push('Review programming language fundamentals and best practices');
      recommendations.push('Practice writing clean, readable code');
    }
    
    if (analysis.google_criteria.communication_score < 70) {
      recommendations.push('Practice explaining your thought process out loud');
      recommendations.push('Record yourself solving problems and review your communication');
    }
    
    if (analysis.google_criteria.googleyness_score < 70) {
      recommendations.push('Study Google\'s engineering practices and code review guidelines');
      recommendations.push('Focus on writing maintainable and documented code');
    }
    
    if (analysis.complexity.time_complexity.includes('n²') || analysis.complexity.time_complexity.includes('2^n')) {
      recommendations.push('Study optimization techniques and advanced data structures');
    }
    
    return recommendations;
  }
};

export default googleCodeAnalysisAPI;
