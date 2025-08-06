"""
Code Quality Analysis Tools for Phase 3B Solution Analysis
Provides automated assessment of solution code quality, style, and best practices
"""

import ast
import re
import keyword
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import textwrap

from src.models.schemas import CodeQualityMetrics, ProgrammingLanguage


@dataclass
class CodeMetrics:
    """Raw code metrics before scoring"""
    lines_of_code: int
    lines_of_comments: int
    blank_lines: int
    function_count: int
    class_count: int
    variable_count: int
    max_line_length: int
    avg_line_length: float
    cyclomatic_complexity: int


class PythonCodeAnalyzer:
    """Analyzes Python code quality and generates quality metrics"""
    
    def __init__(self):
        self.reserved_words = set(keyword.kwlist)
        self.good_variable_patterns = [
            r'^[a-z][a-z0-9_]*$',  # snake_case
            r'^[A-Z][A-Z0-9_]*$',  # CONSTANTS
            r'^[A-Z][a-zA-Z0-9]*$'  # PascalCase for classes
        ]
        
    def analyze_code(self, code: str, language: ProgrammingLanguage = ProgrammingLanguage.PYTHON) -> CodeQualityMetrics:
        """Main analysis function that returns complete quality metrics"""
        
        if language != ProgrammingLanguage.PYTHON:
            # For now, only Python analysis is implemented
            return self._create_default_metrics(code)
        
        try:
            # Parse the code
            tree = ast.parse(code)
            
            # Calculate raw metrics
            raw_metrics = self._calculate_raw_metrics(code, tree)
            
            # Analyze code structure and style
            structure_analysis = self._analyze_structure(tree)
            style_analysis = self._analyze_style(code)
            documentation_analysis = self._analyze_documentation(code, tree)
            naming_analysis = self._analyze_naming(tree)
            efficiency_analysis = self._analyze_efficiency(tree, code)
            
            # Calculate individual scores
            readability_score = self._calculate_readability_score(raw_metrics, style_analysis, naming_analysis)
            structure_score = self._calculate_structure_score(structure_analysis)
            style_score = self._calculate_style_score(style_analysis)
            documentation_score = self._calculate_documentation_score(documentation_analysis, raw_metrics)
            efficiency_score = self._calculate_efficiency_score(efficiency_analysis)
            maintainability_score = self._calculate_maintainability_score(raw_metrics, structure_analysis)
            
            # Calculate overall score (weighted average)
            overall_score = (
                readability_score * 0.25 +
                structure_score * 0.20 +
                style_score * 0.15 +
                documentation_score * 0.15 +
                efficiency_score * 0.15 +
                maintainability_score * 0.10
            )
            
            # Collect issues
            style_issues = style_analysis.get('issues', [])
            potential_bugs = efficiency_analysis.get('potential_bugs', [])
            performance_warnings = efficiency_analysis.get('performance_warnings', [])
            
            return CodeQualityMetrics(
                overall_score=round(overall_score, 2),
                readability_score=round(readability_score, 2),
                structure_score=round(structure_score, 2),
                style_score=round(style_score, 2),
                documentation_score=round(documentation_score, 2),
                efficiency_score=round(efficiency_score, 2),
                maintainability_score=round(maintainability_score, 2),
                lines_of_code=raw_metrics.lines_of_code,
                cyclomatic_complexity=raw_metrics.cyclomatic_complexity,
                comment_ratio=(raw_metrics.lines_of_comments / max(raw_metrics.lines_of_code, 1)) * 100,
                function_count=raw_metrics.function_count,
                variable_naming_score=naming_analysis.get('score', 70.0),
                style_issues=style_issues,
                potential_bugs=potential_bugs,
                performance_warnings=performance_warnings
            )
            
        except SyntaxError as e:
            return self._create_error_metrics(code, f"Syntax Error: {str(e)}")
        except Exception as e:
            return self._create_error_metrics(code, f"Analysis Error: {str(e)}")
    
    def _calculate_raw_metrics(self, code: str, tree: ast.AST) -> CodeMetrics:
        """Calculate basic code metrics"""
        lines = code.split('\n')
        
        # Count different types of lines
        lines_of_code = 0
        lines_of_comments = 0
        blank_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#'):
                lines_of_comments += 1
            else:
                lines_of_code += 1
                # Check for inline comments
                if '#' in line:
                    lines_of_comments += 1
        
        # Count functions and classes
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        
        # Count variables (approximate)
        variable_count = len([node for node in ast.walk(tree) if isinstance(node, ast.Name)])
        
        # Line length metrics
        line_lengths = [len(line) for line in lines]
        max_line_length = max(line_lengths) if line_lengths else 0
        avg_line_length = sum(line_lengths) / len(line_lengths) if line_lengths else 0
        
        # Calculate cyclomatic complexity
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(tree)
        
        return CodeMetrics(
            lines_of_code=lines_of_code,
            lines_of_comments=lines_of_comments,
            blank_lines=blank_lines,
            function_count=function_count,
            class_count=class_count,
            variable_count=variable_count,
            max_line_length=max_line_length,
            avg_line_length=avg_line_length,
            cyclomatic_complexity=cyclomatic_complexity
        )
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _analyze_structure(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze code structure"""
        analysis = {
            'functions': [],
            'classes': [],
            'nesting_depth': 0,
            'function_lengths': [],
            'issues': []
        }
        
        # Analyze functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'args_count': len(node.args.args),
                    'has_docstring': ast.get_docstring(node) is not None,
                    'line_count': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 1
                }
                analysis['functions'].append(func_info)
                analysis['function_lengths'].append(func_info['line_count'])
                
                # Check for issues
                if func_info['args_count'] > 5:
                    analysis['issues'].append(f"Function '{func_info['name']}' has too many parameters ({func_info['args_count']})")
                if func_info['line_count'] > 50:
                    analysis['issues'].append(f"Function '{func_info['name']}' is too long ({func_info['line_count']} lines)")
        
        return analysis
    
    def _analyze_style(self, code: str) -> Dict[str, Any]:
        """Analyze code style"""
        lines = code.split('\n')
        issues = []
        
        # Check line lengths
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 88]
        if long_lines:
            issues.append(f"Lines too long (>88 chars): {long_lines[:5]}")
        
        # Check indentation consistency
        indentations = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indentations.append(indent)
        
        if indentations:
            # Check if using 4-space indentation
            non_four_space = [ind for ind in indentations if ind % 4 != 0]
            if non_four_space:
                issues.append("Inconsistent indentation (not 4-space)")
        
        # Check for trailing whitespace
        trailing_whitespace_lines = [i+1 for i, line in enumerate(lines) if line.rstrip() != line]
        if trailing_whitespace_lines:
            issues.append(f"Trailing whitespace on lines: {trailing_whitespace_lines[:3]}")
        
        return {
            'issues': issues,
            'long_lines_count': len(long_lines),
            'indentation_consistent': len(non_four_space) == 0 if indentations else True
        }
    
    def _analyze_documentation(self, code: str, tree: ast.AST) -> Dict[str, Any]:
        """Analyze documentation quality"""
        analysis = {
            'has_module_docstring': False,
            'functions_with_docstrings': 0,
            'total_functions': 0,
            'comment_quality': 0,
            'docstring_quality': 0
        }
        
        # Check for module docstring
        if isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Str):
            analysis['has_module_docstring'] = True
        
        # Check function docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis['total_functions'] += 1
                if ast.get_docstring(node):
                    analysis['functions_with_docstrings'] += 1
        
        # Analyze comments
        comment_lines = [line for line in code.split('\n') if line.strip().startswith('#')]
        if comment_lines:
            # Simple heuristic for comment quality
            avg_comment_length = sum(len(line.strip()) for line in comment_lines) / len(comment_lines)
            analysis['comment_quality'] = min(100, avg_comment_length * 2)  # Longer comments = better quality
        
        return analysis
    
    def _analyze_naming(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze variable and function naming conventions"""
        analysis = {
            'good_names': 0,
            'bad_names': 0,
            'total_names': 0,
            'issues': []
        }
        
        # Collect all names
        names_to_check = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                names_to_check.append(('function', node.name))
            elif isinstance(node, ast.ClassDef):
                names_to_check.append(('class', node.name))
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                names_to_check.append(('variable', node.id))
        
        # Check naming conventions
        for name_type, name in names_to_check:
            analysis['total_names'] += 1
            
            # Skip certain names
            if name in ['_', '__', '___'] or name in self.reserved_words:
                continue
            
            is_good = False
            
            if name_type == 'class':
                # Classes should be PascalCase
                if re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
                    is_good = True
            else:
                # Functions and variables should be snake_case
                if re.match(r'^[a-z][a-z0-9_]*$', name) or re.match(r'^[A-Z][A-Z0-9_]*$', name):
                    is_good = True
            
            if is_good:
                analysis['good_names'] += 1
            else:
                analysis['bad_names'] += 1
                analysis['issues'].append(f"Poor naming: {name_type} '{name}'")
        
        # Calculate score
        if analysis['total_names'] > 0:
            analysis['score'] = (analysis['good_names'] / analysis['total_names']) * 100
        else:
            analysis['score'] = 100
        
        return analysis
    
    def _analyze_efficiency(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Analyze code efficiency and potential performance issues"""
        analysis = {
            'potential_bugs': [],
            'performance_warnings': [],
            'efficiency_score': 80  # Default score
        }
        
        # Check for common performance issues
        for node in ast.walk(tree):
            # Nested loops (potential O(n²) or worse)
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child != node and isinstance(child, (ast.For, ast.While)):
                        analysis['performance_warnings'].append("Nested loops detected - consider optimization")
                        analysis['efficiency_score'] -= 10
                        break
            
            # List comprehensions in loops
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.ListComp):
                        analysis['performance_warnings'].append("List comprehension in loop - consider optimization")
                        analysis['efficiency_score'] -= 5
        
        # Check for potential bugs
        if 'except:' in code or 'except Exception:' in code:
            analysis['potential_bugs'].append("Bare except clause - consider specific exceptions")
        
        if '== True' in code or '== False' in code:
            analysis['potential_bugs'].append("Explicit boolean comparison - use 'if condition:' instead")
        
        return analysis
    
    def _calculate_readability_score(self, metrics: CodeMetrics, style: Dict, naming: Dict) -> float:
        """Calculate readability score"""
        score = 100
        
        # Penalize long lines
        if metrics.max_line_length > 88:
            score -= min(20, (metrics.max_line_length - 88) * 0.5)
        
        # Penalize poor naming
        score = score * (naming.get('score', 100) / 100)
        
        # Penalize style issues
        score -= len(style.get('issues', [])) * 5
        
        return max(0, score)
    
    def _calculate_structure_score(self, structure: Dict) -> float:
        """Calculate structure score"""
        score = 100
        
        # Penalize structural issues
        score -= len(structure.get('issues', [])) * 10
        
        # Bonus for good function count
        func_count = len(structure.get('functions', []))
        if 1 <= func_count <= 10:
            score += 5
        elif func_count > 20:
            score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_style_score(self, style: Dict) -> float:
        """Calculate style score"""
        score = 100
        
        # Penalize style issues
        score -= len(style.get('issues', [])) * 8
        
        # Bonus for consistent indentation
        if style.get('indentation_consistent', True):
            score += 5
        
        return max(0, min(100, score))
    
    def _calculate_documentation_score(self, doc: Dict, metrics: CodeMetrics) -> float:
        """Calculate documentation score"""
        score = 50  # Base score
        
        # Bonus for module docstring
        if doc.get('has_module_docstring', False):
            score += 20
        
        # Bonus for function docstrings
        total_funcs = doc.get('total_functions', 0)
        if total_funcs > 0:
            docstring_ratio = doc.get('functions_with_docstrings', 0) / total_funcs
            score += docstring_ratio * 30
        
        # Comment quality
        score += doc.get('comment_quality', 0) * 0.2
        
        return max(0, min(100, score))
    
    def _calculate_efficiency_score(self, efficiency: Dict) -> float:
        """Calculate efficiency score"""
        score = efficiency.get('efficiency_score', 80)
        return max(0, min(100, score))
    
    def _calculate_maintainability_score(self, metrics: CodeMetrics, structure: Dict) -> float:
        """Calculate maintainability score"""
        score = 100
        
        # Penalize high complexity
        if metrics.cyclomatic_complexity > 10:
            score -= (metrics.cyclomatic_complexity - 10) * 5
        
        # Penalize very long functions
        avg_func_length = sum(structure.get('function_lengths', [10])) / max(len(structure.get('function_lengths', [1])), 1)
        if avg_func_length > 30:
            score -= (avg_func_length - 30) * 2
        
        return max(0, min(100, score))
    
    def _create_default_metrics(self, code: str) -> CodeQualityMetrics:
        """Create default metrics for unsupported languages"""
        lines = code.split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
        
        return CodeQualityMetrics(
            overall_score=75.0,  # Default reasonable score
            readability_score=75.0,
            structure_score=75.0,
            style_score=75.0,
            documentation_score=60.0,
            efficiency_score=80.0,
            maintainability_score=70.0,
            lines_of_code=loc,
            cyclomatic_complexity=None,
            comment_ratio=10.0,  # Estimated
            function_count=1,  # Estimated
            variable_naming_score=75.0,
            style_issues=["Language not fully supported for analysis"],
            potential_bugs=[],
            performance_warnings=[]
        )
    
    def _create_error_metrics(self, code: str, error_msg: str) -> CodeQualityMetrics:
        """Create metrics when analysis fails"""
        lines = code.split('\n')
        loc = len([line for line in lines if line.strip()])
        
        return CodeQualityMetrics(
            overall_score=20.0,  # Low score due to errors
            readability_score=20.0,
            structure_score=20.0,
            style_score=20.0,
            documentation_score=20.0,
            efficiency_score=20.0,
            maintainability_score=20.0,
            lines_of_code=loc,
            cyclomatic_complexity=None,
            comment_ratio=0.0,
            function_count=0,
            variable_naming_score=0.0,
            style_issues=[error_msg],
            potential_bugs=[],
            performance_warnings=[]
        )


def analyze_solution_code(code: str, language: ProgrammingLanguage = ProgrammingLanguage.PYTHON) -> CodeQualityMetrics:
    """
    Main function to analyze solution code quality
    
    Args:
        code: The solution code to analyze
        language: Programming language of the code
        
    Returns:
        CodeQualityMetrics with comprehensive quality assessment
    """
    analyzer = PythonCodeAnalyzer()
    return analyzer.analyze_code(code, language)


def batch_analyze_solutions(solutions: List[Tuple[str, str, ProgrammingLanguage]]) -> List[CodeQualityMetrics]:
    """
    Analyze multiple solutions in batch
    
    Args:
        solutions: List of (solution_id, code, language) tuples
        
    Returns:
        List of CodeQualityMetrics for each solution
    """
    analyzer = PythonCodeAnalyzer()
    results = []
    
    for solution_id, code, language in solutions:
        try:
            metrics = analyzer.analyze_code(code, language)
            results.append(metrics)
        except Exception as e:
            # Create error metrics for failed analysis
            error_metrics = analyzer._create_error_metrics(code, f"Batch analysis error: {str(e)}")
            results.append(error_metrics)
    
    return results


if __name__ == "__main__":
    # Test the analyzer with a sample solution
    sample_code = """
def two_sum(nums, target):
    \"\"\"
    Find two numbers in the array that add up to target.
    
    Args:
        nums: List of integers
        target: Target sum
        
    Returns:
        List of two indices that sum to target
    \"\"\"
    num_map = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    
    return []
"""
    
    metrics = analyze_solution_code(sample_code)
    print(f"Overall Score: {metrics.overall_score}")
    print(f"Readability: {metrics.readability_score}")
    print(f"Structure: {metrics.structure_score}")
    print(f"Documentation: {metrics.documentation_score}")
    print(f"Issues found: {len(metrics.style_issues + metrics.potential_bugs)}")
