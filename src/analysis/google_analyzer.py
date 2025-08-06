"""
Standalone Google-Style Code Analyzer
Independent implementation without FastAPI dependencies
"""

import re
import ast
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class ComplexityAnalysis:
    time_complexity: str
    space_complexity: str
    confidence: float
    explanation: str

@dataclass
class CodeQualityMetrics:
    overall_score: int
    readability: int
    naming_conventions: int
    code_structure: int
    documentation: int
    best_practices: int

@dataclass
class GoogleCriteriaEvaluation:
    gca_score: int  # General Cognitive Ability
    rrk_score: int  # Role-Related Knowledge
    communication_score: int
    googleyness_score: int
    overall_score: int
    detailed_feedback: Dict[str, str]

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
