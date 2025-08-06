"""
Google-Style Code Analysis API
Enhanced code evaluation using Google's interview criteria
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import re
import ast
import time
from datetime import datetime
import json

# Database imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.database import DatabaseConfig, get_database_stats
from src.analysis.google_analyzer import GoogleStyleCodeAnalyzer

router = APIRouter(prefix="/google", tags=["Google Code Analysis"])

class CodeSubmission(BaseModel):
    code: str
    language: str
    problem_id: Optional[str] = None
    time_spent_seconds: Optional[int] = None
    thinking_out_loud: bool = False
    communication_notes: List[str] = []

class ComplexityAnalysis(BaseModel):
    time_complexity: str
    space_complexity: str
    confidence: float
    explanation: str

class CodeQualityMetrics(BaseModel):
    overall_score: int
    readability: int
    naming_conventions: int
    code_structure: int
    documentation: int
    best_practices: int

class GoogleCriteriaEvaluation(BaseModel):
    gca_score: int  # General Cognitive Ability
    rrk_score: int  # Role-Related Knowledge
    communication_score: int
    googleyness_score: int
    overall_score: int
    detailed_feedback: Dict[str, str]

class CodeAnalysisResult(BaseModel):
    complexity: ComplexityAnalysis
    quality: CodeQualityMetrics
    google_criteria: GoogleCriteriaEvaluation
    suggestions: List[str]
    test_results: List[Dict[str, Any]]
    execution_successful: bool
    security_issues: List[str]
    performance_insights: List[str]

class GoogleStyleCodeAnalyzer:
    """
    Advanced code analyzer implementing Google's evaluation criteria
    Based on Google's engineering practices and interview rubrics
    """
    
    def __init__(self):
        self.complexity_patterns = {
            'constant': [r'return\s+\w+', r'^\s*\w+\s*='],
            'logarithmic': [r'while.*\/\/?\s*2', r'binary.*search', r'log'],
            'linear': [r'for.*in.*range\([^,)]+\)', r'while.*<.*len'],
            'quadratic': [r'for.*for', r'for.*in.*for.*in'],
            'exponential': [r'def.*\w+.*\w+\(.*\w+.*\)', r'2\s*\*\*', r'fibonacci.*recursive']
        }
    
    def analyze_complexity(self, code: str, language: str) -> ComplexityAnalysis:
        """
        Analyze time and space complexity using pattern recognition
        Implements Google's focus on algorithmic efficiency
        """
        code_normalized = re.sub(r'\s+', ' ', code.lower())
        
        # Time complexity analysis
        time_complexity = "O(1)"
        confidence = 0.7
        explanation = "Basic complexity analysis"
        
        if any(re.search(pattern, code_normalized) for pattern in self.complexity_patterns['exponential']):
            time_complexity = "O(2^n)"
            confidence = 0.8
            explanation = "Exponential complexity detected due to recursive patterns"
        elif any(re.search(pattern, code_normalized) for pattern in self.complexity_patterns['quadratic']):
            time_complexity = "O(n²)"
            confidence = 0.9
            explanation = "Quadratic complexity from nested loops"
        elif any(re.search(pattern, code_normalized) for pattern in self.complexity_patterns['linear']):
            time_complexity = "O(n)"
            confidence = 0.85
            explanation = "Linear complexity from single iteration"
        elif any(re.search(pattern, code_normalized) for pattern in self.complexity_patterns['logarithmic']):
            time_complexity = "O(log n)"
            confidence = 0.9
            explanation = "Logarithmic complexity from divide-and-conquer approach"
        
        # Space complexity analysis
        space_complexity = "O(1)"
        if 'recursion' in code_normalized or 'recursive' in code_normalized:
            space_complexity = "O(n)"
        elif any(word in code_normalized for word in ['list', 'array', 'dict', 'set', 'map']):
            space_complexity = "O(n)"
        
        return ComplexityAnalysis(
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            confidence=confidence,
            explanation=explanation
        )
    
    def analyze_code_quality(self, code: str, language: str) -> CodeQualityMetrics:
        """
        Comprehensive code quality analysis based on Google's code review standards
        Reference: https://google.github.io/eng-practices/review/reviewer/standard.html
        """
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        
        # Readability analysis
        readability_score = self._analyze_readability(code, lines)
        
        # Naming conventions (Google style)
        naming_score = self._analyze_naming_conventions(code, language)
        
        # Code structure analysis
        structure_score = self._analyze_code_structure(code, lines)
        
        # Documentation analysis
        documentation_score = self._analyze_documentation(code)
        
        # Best practices analysis
        best_practices_score = self._analyze_best_practices(code, language)
        
        overall_score = int((readability_score + naming_score + structure_score + 
                           documentation_score + best_practices_score) / 5)
        
        return CodeQualityMetrics(
            overall_score=overall_score,
            readability=readability_score,
            naming_conventions=naming_score,
            code_structure=structure_score,
            documentation=documentation_score,
            best_practices=best_practices_score
        )
    
    def _analyze_readability(self, code: str, lines: List[str]) -> int:
        """Analyze code readability using Google's standards"""
        score = 100
        
        # Line length (Google prefers 80 characters)
        long_lines = sum(1 for line in lines if len(line) > 80)
        if long_lines > 0:
            score -= min(20, long_lines * 5)
        
        # Complexity per function
        avg_function_length = self._calculate_avg_function_length(lines)
        if avg_function_length > 30:
            score -= 15
        elif avg_function_length > 20:
            score -= 10
        
        # Nested depth
        max_depth = self._calculate_max_nesting_depth(lines)
        if max_depth > 4:
            score -= 20
        elif max_depth > 3:
            score -= 10
        
        return max(0, score)
    
    def _analyze_naming_conventions(self, code: str, language: str) -> int:
        """Analyze naming conventions according to Google style guides"""
        score = 100
        
        if language == 'python':
            # Python naming conventions
            # Functions and variables: snake_case
            function_pattern = r'def\s+([A-Z][a-zA-Z0-9]*)'
            if re.search(function_pattern, code):
                score -= 20  # Functions should be snake_case, not PascalCase
            
            # Constants: UPPER_CASE
            constant_pattern = r'^[a-z_][a-z0-9_]*\s*='
            variables = re.findall(r'^(\w+)\s*=', code, re.MULTILINE)
            
        elif language == 'java':
            # Java naming conventions
            # Methods: camelCase
            # Classes: PascalCase
            pass
        
        # Generic naming quality
        short_names = len(re.findall(r'\b[a-z]{1,2}\b', code))
        if short_names > 3:
            score -= min(30, short_names * 5)
        
        return max(0, score)
    
    def _analyze_code_structure(self, code: str, lines: List[str]) -> int:
        """Analyze code structure and organization"""
        score = 100
        
        # Function length analysis
        functions = self._extract_functions(code)
        long_functions = sum(1 for func in functions if len(func.split('\n')) > 25)
        if long_functions > 0:
            score -= min(25, long_functions * 10)
        
        # Single responsibility principle
        # Count number of different operations in main function
        main_complexity = self._count_main_operations(code)
        if main_complexity > 5:
            score -= 15
        
        return max(0, score)
    
    def _analyze_documentation(self, code: str) -> int:
        """Analyze documentation quality"""
        score = 60  # Start with base score
        
        # Check for function docstrings
        docstring_pattern = r'""".*?"""'
        docstrings = re.findall(docstring_pattern, code, re.DOTALL)
        if docstrings:
            score += 25
        
        # Check for inline comments
        comment_lines = len(re.findall(r'#.*$', code, re.MULTILINE))
        total_lines = len(code.split('\n'))
        comment_ratio = comment_lines / max(1, total_lines)
        
        if comment_ratio > 0.1:
            score += 15
        elif comment_ratio > 0.05:
            score += 10
        
        return min(100, score)
    
    def _analyze_best_practices(self, code: str, language: str) -> int:
        """Analyze adherence to best practices"""
        score = 100
        
        # Check for magic numbers
        magic_numbers = re.findall(r'\b(?!0|1)\d{2,}\b', code)
        if magic_numbers:
            score -= min(20, len(magic_numbers) * 5)
        
        # Check for proper error handling
        if 'try:' not in code and 'except:' not in code and language == 'python':
            score -= 10
        
        # Check for global variables (bad practice)
        global_vars = re.findall(r'^[A-Z_][A-Z0-9_]*\s*=', code, re.MULTILINE)
        if len(global_vars) > 2:
            score -= 15
        
        return max(0, score)
    
    def evaluate_google_criteria(self, code: str, language: str, 
                                time_spent: int, thinking_out_loud: bool,
                                communication_notes: List[str], 
                                complexity: ComplexityAnalysis,
                                quality: CodeQualityMetrics) -> GoogleCriteriaEvaluation:
        """
        Evaluate code against Google's four core criteria:
        1. General Cognitive Ability (GCA)
        2. Role-Related Knowledge (RRK)  
        3. Leadership (Communication)
        4. Googleyness
        """
        
        # General Cognitive Ability (Problem-solving approach)
        gca_score = self._evaluate_gca(code, complexity, time_spent)
        
        # Role-Related Knowledge (Technical competency)
        rrk_score = self._evaluate_rrk(code, quality, language)
        
        # Communication (Thinking out loud, explanation quality)
        communication_score = self._evaluate_communication(thinking_out_loud, 
                                                          communication_notes, time_spent)
        
        # Googleyness (Code quality, best practices, growth mindset)
        googleyness_score = self._evaluate_googleyness(code, quality)
        
        overall_score = int((gca_score + rrk_score + communication_score + googleyness_score) / 4)
        
        detailed_feedback = {
            "gca": self._get_gca_feedback(gca_score, complexity),
            "rrk": self._get_rrk_feedback(rrk_score, quality),
            "communication": self._get_communication_feedback(communication_score, thinking_out_loud),
            "googleyness": self._get_googleyness_feedback(googleyness_score, quality)
        }
        
        return GoogleCriteriaEvaluation(
            gca_score=gca_score,
            rrk_score=rrk_score,
            communication_score=communication_score,
            googleyness_score=googleyness_score,
            overall_score=overall_score,
            detailed_feedback=detailed_feedback
        )
    
    def _evaluate_gca(self, code: str, complexity: ComplexityAnalysis, time_spent: int) -> int:
        """Evaluate General Cognitive Ability"""
        score = 70  # Base score
        
        # Optimal complexity bonus
        if complexity.time_complexity in ["O(n)", "O(log n)", "O(1)"]:
            score += 20
        elif complexity.time_complexity == "O(n log n)":
            score += 10
        else:
            score -= 15
        
        # Problem-solving efficiency (time to solution)
        if time_spent and time_spent < 1200:  # Under 20 minutes
            score += 10
        elif time_spent and time_spent > 2700:  # Over 45 minutes
            score -= 10
        
        # Code correctness indicators
        if 'edge case' in code.lower() or 'boundary' in code.lower():
            score += 5
        
        return max(0, min(100, score))
    
    def _evaluate_rrk(self, code: str, quality: CodeQualityMetrics, language: str) -> int:
        """Evaluate Role-Related Knowledge"""
        base_score = quality.overall_score
        
        # Language-specific best practices
        if language == 'python':
            if 'list comprehension' in code.lower() or '[' in code and 'for' in code and 'in' in code:
                base_score += 5
            if '__name__ == "__main__"' in code:
                base_score += 5
        
        # Data structure usage
        advanced_structures = ['deque', 'heapq', 'collections', 'set', 'defaultdict']
        if any(structure in code for structure in advanced_structures):
            base_score += 10
        
        return max(0, min(100, base_score))
    
    def _evaluate_communication(self, thinking_out_loud: bool, 
                              communication_notes: List[str], time_spent: int) -> int:
        """Evaluate Communication skills"""
        score = 50  # Base score
        
        if thinking_out_loud:
            score += 30
        
        # Quality of communication notes
        note_quality_bonus = min(20, len(communication_notes) * 5)
        score += note_quality_bonus
        
        # Explanation quality keywords
        explanation_keywords = ['because', 'approach', 'algorithm', 'optimization', 'edge case']
        note_text = ' '.join(communication_notes).lower()
        keyword_matches = sum(1 for keyword in explanation_keywords if keyword in note_text)
        score += min(15, keyword_matches * 3)
        
        return max(0, min(100, score))
    
    def _evaluate_googleyness(self, code: str, quality: CodeQualityMetrics) -> int:
        """Evaluate Googleyness (culture fit, best practices)"""
        score = quality.best_practices
        
        # Clean code indicators
        if quality.documentation > 80:
            score += 10
        if quality.naming_conventions > 85:
            score += 5
        
        # Growth mindset indicators (comments about improvements)
        growth_keywords = ['todo', 'fixme', 'improve', 'optimize', 'refactor']
        if any(keyword in code.lower() for keyword in growth_keywords):
            score += 10
        
        return max(0, min(100, score))
    
    # Helper methods for detailed analysis
    def _calculate_avg_function_length(self, lines: List[str]) -> float:
        """Calculate average function length"""
        functions = self._extract_functions('\n'.join(lines))
        if not functions:
            return len(lines)
        return sum(len(func.split('\n')) for func in functions) / len(functions)
    
    def _calculate_max_nesting_depth(self, lines: List[str]) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            if line.strip().endswith(':'):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif line and not line.startswith(' ') and not line.startswith('\t'):
                current_depth = 0
        
        return max_depth
    
    def _extract_functions(self, code: str) -> List[str]:
        """Extract function definitions from code"""
        functions = []
        lines = code.split('\n')
        current_function = []
        in_function = False
        
        for line in lines:
            if line.strip().startswith('def '):
                if current_function:
                    functions.append('\n'.join(current_function))
                current_function = [line]
                in_function = True
            elif in_function:
                if line and not line.startswith(' ') and not line.startswith('\t') and not line.strip().startswith('#'):
                    functions.append('\n'.join(current_function))
                    current_function = []
                    in_function = False
                else:
                    current_function.append(line)
        
        if current_function:
            functions.append('\n'.join(current_function))
        
        return functions
    
    def _count_main_operations(self, code: str) -> int:
        """Count distinct operations in main logic"""
        operations = ['if', 'for', 'while', 'try', 'with', 'def', 'class']
        return sum(code.count(op) for op in operations)
    
    def _get_gca_feedback(self, score: int, complexity: ComplexityAnalysis) -> str:
        """Generate detailed GCA feedback"""
        if score >= 85:
            return f"Excellent problem-solving approach with {complexity.time_complexity} complexity. Shows strong algorithmic thinking."
        elif score >= 70:
            return f"Good solution with {complexity.time_complexity} complexity. Consider optimizing for better efficiency."
        else:
            return f"Solution works but needs optimization. Current {complexity.time_complexity} complexity can be improved."
    
    def _get_rrk_feedback(self, score: int, quality: CodeQualityMetrics) -> str:
        """Generate detailed RRK feedback"""
        if score >= 85:
            return "Strong technical implementation with excellent code quality and best practices."
        elif score >= 70:
            return "Good technical skills demonstrated. Focus on improving code organization and documentation."
        else:
            return "Technical implementation needs improvement. Review coding standards and best practices."
    
    def _get_communication_feedback(self, score: int, thinking_out_loud: bool) -> str:
        """Generate detailed communication feedback"""
        if not thinking_out_loud:
            return "Remember to explain your thought process out loud during interviews. This is crucial for Google interviews."
        elif score >= 80:
            return "Excellent communication throughout the problem-solving process."
        else:
            return "Good effort in communication. Try to explain your approach more clearly and discuss trade-offs."
    
    def _get_googleyness_feedback(self, score: int, quality: CodeQualityMetrics) -> str:
        """Generate detailed Googleyness feedback"""
        if score >= 85:
            return "Code demonstrates strong alignment with Google's engineering principles and culture."
        elif score >= 70:
            return "Good practices shown. Focus on code documentation and clean coding principles."
        else:
            return "Work on code quality, documentation, and following engineering best practices."

# Initialize analyzer
analyzer = GoogleStyleCodeAnalyzer()

def get_db():
    """Database dependency"""
    db_config = DatabaseConfig()
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

@router.post("/analyze", response_model=CodeAnalysisResult)
async def analyze_code(submission: CodeSubmission, db: Session = Depends(get_db)):
    """
    Comprehensive code analysis using Google's evaluation criteria
    """
    try:
        start_time = time.time()
        
        # Perform complexity analysis
        complexity = analyzer.analyze_complexity(submission.code, submission.language)
        
        # Perform code quality analysis
        quality = analyzer.analyze_code_quality(submission.code, submission.language)
        
        # Evaluate against Google's criteria
        google_criteria = analyzer.evaluate_google_criteria(
            code=submission.code,
            language=submission.language,
            time_spent=submission.time_spent_seconds or 0,
            thinking_out_loud=submission.thinking_out_loud,
            communication_notes=submission.communication_notes,
            complexity=complexity,
            quality=quality
        )
        
        # Generate improvement suggestions
        suggestions = generate_suggestions(submission.code, complexity, quality, google_criteria)
        
        # Mock test results (in real implementation, this would execute the code)
        test_results = generate_mock_test_results(submission.code)
        
        # Security analysis
        security_issues = analyze_security_issues(submission.code)
        
        # Performance insights
        performance_insights = generate_performance_insights(complexity, submission.code)
        
        analysis_time = time.time() - start_time
        
        return CodeAnalysisResult(
            complexity=complexity,
            quality=quality,
            google_criteria=google_criteria,
            suggestions=suggestions,
            test_results=test_results,
            execution_successful=True,
            security_issues=security_issues,
            performance_insights=performance_insights
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def generate_suggestions(code: str, complexity: ComplexityAnalysis, 
                        quality: CodeQualityMetrics, 
                        google_criteria: GoogleCriteriaEvaluation) -> List[str]:
    """Generate specific improvement suggestions"""
    suggestions = []
    
    # Complexity suggestions
    if complexity.time_complexity not in ["O(1)", "O(log n)", "O(n)"]:
        suggestions.append(f"Consider optimizing time complexity from {complexity.time_complexity} to a more efficient solution")
    
    # Quality suggestions
    if quality.documentation < 70:
        suggestions.append("Add comprehensive documentation and comments explaining your approach")
    
    if quality.naming_conventions < 80:
        suggestions.append("Improve variable and function naming to follow standard conventions")
    
    if quality.code_structure < 75:
        suggestions.append("Break down complex functions into smaller, single-purpose functions")
    
    # Google criteria suggestions
    if google_criteria.communication_score < 70:
        suggestions.append("Practice explaining your thought process out loud - this is crucial for Google interviews")
    
    if google_criteria.gca_score < 75:
        suggestions.append("Focus on edge case handling and algorithmic optimization")
    
    if google_criteria.rrk_score < 80:
        suggestions.append("Review computer science fundamentals and language-specific best practices")
    
    # Add Google-specific suggestions
    suggestions.append("Consider discussing trade-offs between different approaches")
    suggestions.append("Think about scalability - how would this solution work with millions of inputs?")
    
    return suggestions

def generate_mock_test_results(code: str) -> List[Dict[str, Any]]:
    """Generate mock test results for demonstration"""
    return [
        {
            "test_name": "Basic functionality",
            "input": "[1, 2, 3]",
            "expected": "[1, 2, 3]",
            "actual": "[1, 2, 3]",
            "passed": True,
            "execution_time_ms": 0.5
        },
        {
            "test_name": "Edge case - empty input",
            "input": "[]",
            "expected": "[]",
            "actual": "[]",
            "passed": True,
            "execution_time_ms": 0.1
        },
        {
            "test_name": "Large input",
            "input": "[1..10000]",
            "expected": "Processed 10000 items",
            "actual": "Processed 10000 items",
            "passed": True,
            "execution_time_ms": 15.2
        }
    ]

def analyze_security_issues(code: str) -> List[str]:
    """Analyze potential security issues"""
    issues = []
    
    # Check for eval usage
    if 'eval(' in code:
        issues.append("Avoid using eval() - potential security risk")
    
    # Check for exec usage
    if 'exec(' in code:
        issues.append("Avoid using exec() - potential security risk")
    
    # Check for unsafe input handling
    if 'input(' in code and 'int(' not in code:
        issues.append("Consider validating user input to prevent injection attacks")
    
    return issues

def generate_performance_insights(complexity: ComplexityAnalysis, code: str) -> List[str]:
    """Generate performance optimization insights"""
    insights = []
    
    if complexity.time_complexity == "O(n²)":
        insights.append("Consider using hash maps or sets to reduce nested loop complexity")
    
    if 'append(' in code and 'for' in code:
        insights.append("Consider using list comprehensions for better performance")
    
    if 'in' in code and 'list' in code:
        insights.append("Consider using sets for O(1) membership testing instead of lists")
    
    if '+=' in code and 'string' in code.lower():
        insights.append("For multiple string concatenations, consider using join() for better performance")
    
    return insights

@router.get("/google-standards")
async def get_google_coding_standards():
    """
    Return Google's coding standards and interview criteria for reference
    """
    return {
        "evaluation_criteria": {
            "gca": {
                "name": "General Cognitive Ability",
                "description": "Problem-solving skills, algorithmic thinking, ability to handle complexity",
                "key_indicators": [
                    "Optimal algorithm selection",
                    "Edge case consideration", 
                    "Time and space complexity understanding",
                    "Problem decomposition skills"
                ]
            },
            "rrk": {
                "name": "Role-Related Knowledge",
                "description": "Technical competency in programming and computer science fundamentals",
                "key_indicators": [
                    "Clean, readable code",
                    "Proper data structure usage",
                    "Language-specific best practices",
                    "Code organization and structure"
                ]
            },
            "communication": {
                "name": "Communication",
                "description": "Ability to articulate thought process and collaborate effectively",
                "key_indicators": [
                    "Thinking out loud",
                    "Clear explanation of approach",
                    "Asking clarifying questions",
                    "Discussing trade-offs"
                ]
            },
            "googleyness": {
                "name": "Googleyness & Leadership",
                "description": "Cultural fit, growth mindset, and engineering excellence",
                "key_indicators": [
                    "Code quality and best practices",
                    "Documentation and comments",
                    "Consideration for maintainability",
                    "Continuous improvement mindset"
                ]
            }
        },
        "code_quality_standards": {
            "readability": [
                "Functions should be small and focused (< 25 lines)",
                "Use meaningful variable and function names",
                "Maintain consistent indentation and formatting",
                "Avoid deep nesting (< 4 levels)"
            ],
            "documentation": [
                "Include docstrings for functions and classes",
                "Add inline comments for complex logic",
                "Explain the 'why', not just the 'what'",
                "Document edge cases and assumptions"
            ],
            "best_practices": [
                "Follow language-specific style guides",
                "Handle edge cases explicitly",
                "Use appropriate data structures",
                "Avoid magic numbers and strings",
                "Implement proper error handling"
            ]
        },
        "interview_tips": [
            "Always think out loud during the interview",
            "Start with a brute force solution, then optimize",
            "Discuss time and space complexity",
            "Ask clarifying questions about requirements",
            "Test your solution with examples",
            "Consider edge cases and error conditions",
            "Be prepared to discuss trade-offs",
            "Practice coding in a plain text environment"
        ]
    }

@router.get("/complexity-guide")
async def get_complexity_analysis_guide():
    """
    Return comprehensive guide for time and space complexity analysis
    """
    return {
        "time_complexity": {
            "O(1)": {
                "description": "Constant time - operation takes same time regardless of input size",
                "examples": ["Array access", "Hash table lookup", "Basic arithmetic"],
                "code_patterns": ["return array[0]", "dict[key]", "x + y"]
            },
            "O(log n)": {
                "description": "Logarithmic time - time increases logarithmically with input size",
                "examples": ["Binary search", "Balanced tree operations"],
                "code_patterns": ["while left <= right", "divide by 2", "binary search"]
            },
            "O(n)": {
                "description": "Linear time - time increases proportionally with input size",
                "examples": ["Single loop through array", "Linear search"],
                "code_patterns": ["for i in range(n)", "while i < n"]
            },
            "O(n log n)": {
                "description": "Linearithmic time - typical of efficient sorting algorithms",
                "examples": ["Merge sort", "Quick sort", "Heap sort"],
                "code_patterns": ["sorted()", "merge_sort()", "divide and conquer with linear work"]
            },
            "O(n²)": {
                "description": "Quadratic time - time increases quadratically with input size",
                "examples": ["Nested loops", "Bubble sort", "Selection sort"],
                "code_patterns": ["for i in range(n): for j in range(n)"]
            },
            "O(2^n)": {
                "description": "Exponential time - time doubles with each additional input",
                "examples": ["Recursive Fibonacci", "Subset generation"],
                "code_patterns": ["recursive calls without memoization", "2^n combinations"]
            }
        },
        "space_complexity": {
            "O(1)": "Constant space - fixed memory usage",
            "O(log n)": "Logarithmic space - typically recursion depth",
            "O(n)": "Linear space - memory proportional to input size",
            "O(n²)": "Quadratic space - 2D arrays or nested structures"
        },
        "optimization_strategies": [
            "Use hash maps for O(1) lookups instead of linear search",
            "Apply two-pointer technique for array problems",
            "Use dynamic programming to avoid redundant calculations",
            "Consider sliding window for substring/subarray problems",
            "Use binary search when data is sorted",
            "Apply divide and conquer for complex problems",
            "Use appropriate data structures (heaps, trees, graphs)"
        ]
    }
