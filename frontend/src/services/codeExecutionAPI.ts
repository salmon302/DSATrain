/**
 * Enhanced Code Execution API Service
 * Real code execution with comprehensive testing and analysis
 */

const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8000') + '/execution';

export interface CodeSubmission {
  code: string;
  language: string;
  test_inputs?: string[];
  timeout_seconds?: number;
  memory_limit_mb?: number;
}

export interface TestCase {
  name: string;
  input: string;
  expected_output?: string;
  description?: string;
}

export interface ExecutionResult {
  success: boolean;
  stdout: string;
  stderr: string;
  return_code: number;
  execution_time_ms: number;
  memory_usage_mb: number;
  timeout: boolean;
  error?: string;
}

export interface TestResult {
  test_case: TestCase;
  result: ExecutionResult;
  passed: boolean;
  output_match: boolean;
}

export interface PerformanceMetrics {
  average_execution_time_ms: number;
  max_execution_time_ms: number;
  min_execution_time_ms: number;
  average_memory_usage_mb: number;
  max_memory_usage_mb: number;
  success_rate: number;
  total_test_cases: number;
  performance_grade: 'A' | 'B' | 'C' | 'D';
}

export interface CodeQuality {
  total_lines: number;
  code_lines: number;
  comment_lines: number;
  average_line_length: number;
  complexity_indicators: {
    nested_loops: number;
    conditional_statements: number;
    function_definitions: number;
  };
}

export interface CodeAnalysisResult {
  execution_results: ExecutionResult[];
  test_results: TestResult[];
  performance_metrics: PerformanceMetrics;
  code_quality: CodeQuality;
  suggestions: string[];
}

export interface LanguageInfo {
  extension: string;
  timeout: number;
  description: string;
}

export interface SupportedLanguages {
  supported_languages: string[];
  language_details: Record<string, LanguageInfo>;
}

class CodeExecutionAPI {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
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
   * Execute code with real execution environment
   */
  async executeCode(submission: CodeSubmission): Promise<ExecutionResult> {
  return this.request<ExecutionResult>('/run', {
      method: 'POST',
      body: JSON.stringify(submission),
    });
  }

  /**
   * Test code against multiple test cases
   */
  async testCode(
    code: string,
    language: string,
    testCases: TestCase[],
    timeoutSeconds: number = 10
  ): Promise<TestResult[]> {
    const params = new URLSearchParams({
      code,
      language,
      timeout_seconds: timeoutSeconds.toString(),
    });

  return this.request<TestResult[]>(`/test?${params}`, {
      method: 'POST',
      body: JSON.stringify(testCases),
    });
  }

  /**
   * Comprehensive code analysis with execution and testing
   */
  async analyzeCode(
    code: string,
    language: string,
    problemType?: string,
    customTestCases?: TestCase[]
  ): Promise<CodeAnalysisResult> {
    const params = new URLSearchParams({
      code,
      language,
    });

    if (problemType) {
      params.append('problem_type', problemType);
    }

    const body = customTestCases ? JSON.stringify(customTestCases) : undefined;

  return this.request<CodeAnalysisResult>(`/analyze?${params}`, {
      method: 'POST',
      body,
    });
  }

  /**
   * Get supported programming languages
   */
  async getSupportedLanguages(): Promise<SupportedLanguages> {
  return this.request<SupportedLanguages>('/languages');
  }

  /**
   * Quick code execution with basic input
   */
  async runCode(code: string, language: string, input: string = ''): Promise<ExecutionResult> {
    const submission: CodeSubmission = {
      code,
      language,
      test_inputs: input ? [input] : [],
      timeout_seconds: 10,
      memory_limit_mb: 128,
    };

    return this.executeCode(submission);
  }

  /**
   * Generate smart test cases based on code analysis
   */
  generateTestCases(code: string, language: string, problemType?: string): TestCase[] {
    const testCases: TestCase[] = [];

    // Basic functionality test
    testCases.push({
      name: 'Basic Case',
      input: this.generateBasicInput(code, problemType),
      description: 'Tests core functionality',
    });

    // Edge cases based on code analysis
    if (this.hasArrayOperations(code)) {
      testCases.push(
        {
          name: 'Empty Array',
          input: '[]',
          description: 'Tests empty input handling',
        },
        {
          name: 'Single Element',
          input: '[1]',
          description: 'Tests minimal input',
        },
        {
          name: 'Large Array',
          input: JSON.stringify(Array.from({ length: 100 }, (_, i) => i + 1)),
          description: 'Tests performance with large input',
        }
      );
    }

    // Numeric boundary tests
    if (this.hasNumericOperations(code)) {
      testCases.push(
        {
          name: 'Zero Value',
          input: '0',
          description: 'Tests zero handling',
        },
        {
          name: 'Negative Values',
          input: '-100',
          description: 'Tests negative number handling',
        },
        {
          name: 'Large Numbers',
          input: '1000000',
          description: 'Tests large number handling',
        }
      );
    }

    // String tests
    if (this.hasStringOperations(code)) {
      testCases.push(
        {
          name: 'Empty String',
          input: '""',
          description: 'Tests empty string handling',
        },
        {
          name: 'Single Character',
          input: '"a"',
          description: 'Tests minimal string',
        },
        {
          name: 'Long String',
          input: '"' + 'a'.repeat(100) + '"',
          description: 'Tests long string performance',
        }
      );
    }

    return testCases.slice(0, 8); // Limit to 8 test cases
  }

  private generateBasicInput(code: string, problemType?: string): string {
    if (problemType === 'array') {
      return '[1, 2, 3, 4, 5]';
    } else if (problemType === 'string') {
      return '"hello"';
    } else if (problemType === 'number') {
      return '42';
    }

    // Auto-detect based on code
    if (this.hasArrayOperations(code)) {
      return '[1, 2, 3, 4, 5]';
    } else if (this.hasStringOperations(code)) {
      return '"test"';
    } else {
      return '42';
    }
  }

  private hasArrayOperations(code: string): boolean {
    const arrayIndicators = ['[', ']', 'list', 'array', 'append', 'pop', 'len('];
    return arrayIndicators.some(indicator => code.toLowerCase().includes(indicator));
  }

  private hasNumericOperations(code: string): boolean {
    const numericIndicators = ['+', '-', '*', '/', 'int(', 'float(', 'math.'];
    return numericIndicators.some(indicator => code.includes(indicator));
  }

  private hasStringOperations(code: string): boolean {
    const stringIndicators = ['"', "'", 'str(', '.split', '.join', '.strip', '.lower', '.upper'];
    return stringIndicators.some(indicator => code.includes(indicator));
  }

  /**
   * Get performance grade color for UI display
   */
  getPerformanceGradeColor(grade: string): 'success' | 'warning' | 'error' {
    switch (grade) {
      case 'A':
        return 'success';
      case 'B':
        return 'success';
      case 'C':
        return 'warning';
      case 'D':
        return 'error';
      default:
        return 'warning';
    }
  }

  /**
   * Format execution time for display
   */
  formatExecutionTime(timeMs: number): string {
    if (timeMs < 1000) {
      return `${timeMs}ms`;
    } else {
      return `${(timeMs / 1000).toFixed(2)}s`;
    }
  }

  /**
   * Format memory usage for display
   */
  formatMemoryUsage(memoryMb: number): string {
    if (memoryMb < 1) {
      return `${(memoryMb * 1024).toFixed(1)}KB`;
    } else {
      return `${memoryMb.toFixed(1)}MB`;
    }
  }

  /**
   * Get execution status color for UI
   */
  getExecutionStatusColor(result: ExecutionResult): 'success' | 'warning' | 'error' {
    if (result.timeout) {
      return 'warning';
    } else if (result.success) {
      return 'success';
    } else {
      return 'error';
    }
  }

  /**
   * Get test result summary
   */
  getTestSummary(testResults: TestResult[]): {
    total: number;
    passed: number;
    failed: number;
    successRate: number;
  } {
    const total = testResults.length;
    const passed = testResults.filter(t => t.passed).length;
    const failed = total - passed;
    const successRate = total > 0 ? (passed / total) * 100 : 0;

    return { total, passed, failed, successRate };
  }

  /**
   * Generate code improvement suggestions based on analysis
   */
  generateImprovementSuggestions(
    code: string,
    language: string,
    performanceMetrics: PerformanceMetrics,
    codeQuality: CodeQuality
  ): string[] {
    const suggestions: string[] = [];

    // Performance suggestions
    if (performanceMetrics.performance_grade === 'D') {
      suggestions.push('Algorithm performance needs significant improvement');
    } else if (performanceMetrics.performance_grade === 'C') {
      suggestions.push('Consider optimizing your algorithm for better performance');
    }

    if (performanceMetrics.max_memory_usage_mb > 100) {
      suggestions.push('High memory usage detected - consider more efficient data structures');
    }

    // Code quality suggestions
    if (codeQuality.comment_lines === 0 && codeQuality.code_lines > 10) {
      suggestions.push('Add comments to explain your approach');
    }

    if (codeQuality.average_line_length > 100) {
      suggestions.push('Consider breaking long lines for better readability');
    }

    if (codeQuality.complexity_indicators.nested_loops > 2) {
      suggestions.push('Multiple nested loops detected - consider optimizing complexity');
    }

    // Language-specific suggestions
    if (language === 'python') {
      if (code.includes('range(len(')) {
        suggestions.push('Use enumerate() instead of range(len()) for Pythonic code');
      }
      if (code.includes('+=') && code.toLowerCase().includes('str')) {
        suggestions.push('Use join() for string concatenation instead of += for better performance');
      }
    }

    if (language === 'javascript') {
      if (code.includes('==') && !code.includes('===')) {
        suggestions.push('Use strict equality (===) instead of loose equality (==)');
      }
    }

    return suggestions;
  }
}

// Export singleton instance
export const codeExecutionAPI = new CodeExecutionAPI();

// Utility functions
export const executionUtils = {
  /**
   * Check if execution result indicates timeout
   */
  isTimeout: (result: ExecutionResult): boolean => result.timeout,

  /**
   * Check if execution was successful
   */
  isSuccess: (result: ExecutionResult): boolean => result.success && !result.timeout,

  /**
   * Get dominant error type from multiple results
   */
  getDominantErrorType: (results: ExecutionResult[]): string => {
    const errors = results.filter(r => !r.success);
    if (errors.length === 0) return 'none';

    const timeouts = errors.filter(r => r.timeout).length;
    const runtime_errors = errors.filter(r => !r.timeout && r.return_code !== 0).length;
    const other_errors = errors.filter(r => !r.timeout && r.return_code === 0).length;

    if (timeouts > runtime_errors && timeouts > other_errors) return 'timeout';
    if (runtime_errors > other_errors) return 'runtime_error';
    return 'other';
  },

  /**
   * Calculate overall performance score
   */
  calculatePerformanceScore: (metrics: PerformanceMetrics): number => {
    const gradeScores = { A: 100, B: 85, C: 70, D: 50 };
    const gradeScore = gradeScores[metrics.performance_grade] || 50;
    const successRateScore = metrics.success_rate * 100;
    
    return Math.round((gradeScore + successRateScore) / 2);
  },

  /**
   * Get execution status color for UI
   */
  getExecutionStatusColor: (result: ExecutionResult): 'success' | 'error' | 'warning' => {
    if (result.success) return 'success';
    if (executionUtils.isTimeout(result)) return 'warning';
    return 'error';
  },

  /**
   * Get test summary statistics
   */
  getTestSummary: (results: ExecutionResult[] | TestResult[]) => {
    // Handle both ExecutionResult and TestResult arrays
    const isExecutionResults = results.length > 0 && 'success' in results[0];
    
    let passed: number;
    if (isExecutionResults) {
      passed = (results as ExecutionResult[]).filter(r => r.success).length;
    } else {
      passed = (results as TestResult[]).filter(r => r.passed).length;
    }
    
    const total = results.length;
    const successRate = total > 0 ? (passed / total) * 100 : 0;
    
    return {
      passed,
      total,
      successRate
    };
  }
};

export default codeExecutionAPI;
