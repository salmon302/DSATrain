"""
Real Code Execution Engine
Secure subprocess-based code execution without Docker
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import subprocess
import tempfile
import os
import time
import signal
import threading
import shutil
import psutil
from pathlib import Path
import json
import re
from datetime import datetime

router = APIRouter(prefix="/execution", tags=["Code Execution"])

class CodeSubmission(BaseModel):
    code: str
    language: str
    test_inputs: Optional[List[str]] = []
    timeout_seconds: Optional[int] = 10
    memory_limit_mb: Optional[int] = 128

class TestCase(BaseModel):
    name: str
    input: str
    expected_output: Optional[str] = None
    description: Optional[str] = None

class ExecutionResult(BaseModel):
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time_ms: int
    memory_usage_mb: float
    timeout: bool
    error: Optional[str] = None

class TestResult(BaseModel):
    test_case: TestCase
    result: ExecutionResult
    passed: bool
    output_match: bool

class CodeAnalysisResult(BaseModel):
    execution_results: List[ExecutionResult]
    test_results: List[TestResult]
    performance_metrics: Dict[str, Any]
    code_quality: Dict[str, Any]
    suggestions: List[str]

class SafeCodeExecutor:
    """Secure code executor using subprocess with resource limits"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "dsatrain_execution"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Language configurations
        self.language_configs = {
            'python': {
                'extension': '.py',
                'command': ['python', '-u', '{file}'],  # -u for unbuffered output
                'timeout': 10,
                'encoding': 'utf-8',
                'security_patterns': [
                    r'import\s+os',
                    r'import\s+subprocess',
                    r'import\s+sys',
                    r'__import__',
                    r'eval\s*\(',
                    r'exec\s*\(',
                    r'open\s*\(',
                    r'file\s*\(',
                ]
            },
            'javascript': {
                'extension': '.js',
                'command': ['node', '{file}'],
                'timeout': 10,
                'encoding': 'utf-8',
                'security_patterns': [
                    r'require\s*\(\s*["\']fs["\']',
                    r'require\s*\(\s*["\']child_process["\']',
                    r'eval\s*\(',
                    r'Function\s*\(',
                    r'process\.exit',
                ]
            },
            'java': {
                'extension': '.java',
                'command': ['java', '--source', '11', '{file}'],  # Java 11+ single file execution
                'timeout': 15,
                'encoding': 'utf-8',
                'security_patterns': [
                    r'import\s+java\.io',
                    r'import\s+java\.nio',
                    r'Runtime\.getRuntime',
                    r'ProcessBuilder',
                    r'System\.exit',
                ]
            },
            'cpp': {
                'extension': '.cpp',
                'compile_command': ['g++', '-o', '{executable}', '{file}', '-std=c++17'],
                'run_command': ['{executable}'],
                'timeout': 15,
                'encoding': 'utf-8',
                'security_patterns': [
                    r'#include\s*<cstdlib>',
                    r'#include\s*<fstream>',
                    r'system\s*\(',
                    r'exec\s*\(',
                ]
            }
        }
    
    def check_security(self, code: str, language: str) -> List[str]:
        """Check code for security issues"""
        issues = []
        config = self.language_configs.get(language, {})
        patterns = config.get('security_patterns', [])
        
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(f"Potentially unsafe code detected: {pattern}")
        
        # Check for very long code (potential DoS)
        if len(code) > 50000:  # 50KB limit
            issues.append("Code too long - potential resource abuse")
        
        # Check for too many loops (potential infinite loop)
        loop_count = len(re.findall(r'\b(for|while)\b', code, re.IGNORECASE))
        if loop_count > 10:
            issues.append("Too many loops detected - potential infinite loop risk")
        
        return issues
    
    async def execute_code(self, submission: CodeSubmission) -> ExecutionResult:
        """Execute code safely with resource limits"""
        language = submission.language.lower()
        config = self.language_configs.get(language)
        
        if not config:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Language {language} not supported",
                return_code=-1,
                execution_time_ms=0,
                memory_usage_mb=0,
                timeout=False,
                error=f"Unsupported language: {language}"
            )
        
        # Security check
        security_issues = self.check_security(submission.code, language)
        if security_issues:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="Security check failed",
                return_code=-1,
                execution_time_ms=0,
                memory_usage_mb=0,
                timeout=False,
                error=f"Security issues: {'; '.join(security_issues)}"
            )
        
        # Create temporary files
        temp_id = f"exec_{int(time.time() * 1000)}_{os.getpid()}"
        temp_file = self.temp_dir / f"{temp_id}{config['extension']}"
        
        try:
            # Write code to file
            temp_file.write_text(submission.code, encoding=config['encoding'])
            
            # Handle compilation for compiled languages
            if language == 'cpp':
                executable = self.temp_dir / f"{temp_id}.exe"
                compile_result = await self._compile_code(temp_file, executable, config)
                if not compile_result.success:
                    return compile_result
                run_command = [str(executable)]
            else:
                run_command = [
                    part.format(file=str(temp_file)) 
                    for part in config['command']
                ]
            
            # Execute with monitoring
            result = await self._execute_with_monitoring(
                run_command,
                submission.test_inputs[0] if submission.test_inputs else "",
                submission.timeout_seconds or config['timeout'],
                submission.memory_limit_mb or 128,
                config['encoding']
            )
            
            return result
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time_ms=0,
                memory_usage_mb=0,
                timeout=False,
                error=f"Execution error: {str(e)}"
            )
        finally:
            # Cleanup
            self._cleanup_files([temp_file])
            if language == 'cpp':
                executable = self.temp_dir / f"{temp_id}.exe"
                self._cleanup_files([executable])
    
    async def _compile_code(self, source_file: Path, executable: Path, config: Dict) -> ExecutionResult:
        """Compile code for compiled languages"""
        try:
            compile_command = [
                part.format(file=str(source_file), executable=str(executable))
                for part in config['compile_command']
            ]
            
            start_time = time.time()
            result = subprocess.run(
                compile_command,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second compile timeout
                cwd=str(source_file.parent)
            )
            compile_time = int((time.time() - start_time) * 1000)
            
            if result.returncode != 0:
                return ExecutionResult(
                    success=False,
                    stdout=result.stdout,
                    stderr=f"Compilation failed: {result.stderr}",
                    return_code=result.returncode,
                    execution_time_ms=compile_time,
                    memory_usage_mb=0,
                    timeout=False,
                    error="Compilation error"
                )
            
            return ExecutionResult(
                success=True,
                stdout="Compilation successful",
                stderr="",
                return_code=0,
                execution_time_ms=compile_time,
                memory_usage_mb=0,
                timeout=False
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="Compilation timeout",
                return_code=-1,
                execution_time_ms=30000,
                memory_usage_mb=0,
                timeout=True,
                error="Compilation timeout"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time_ms=0,
                memory_usage_mb=0,
                timeout=False,
                error=f"Compilation error: {str(e)}"
            )
    
    async def _execute_with_monitoring(
        self, 
        command: List[str], 
        input_data: str, 
        timeout: int,
        memory_limit_mb: int,
        encoding: str
    ) -> ExecutionResult:
        """Execute command with resource monitoring"""
        
        start_time = time.time()
        max_memory_mb = 0.0
        process = None
        
        try:
            # Start process
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding=encoding,
                cwd=str(self.temp_dir)
            )
            
            # Memory monitoring thread
            def monitor_memory():
                nonlocal max_memory_mb
                try:
                    psutil_process = psutil.Process(process.pid)
                    while process.poll() is None:
                        try:
                            memory_info = psutil_process.memory_info()
                            current_memory_mb = memory_info.rss / (1024 * 1024)
                            max_memory_mb = max(max_memory_mb, current_memory_mb)
                            
                            # Kill if memory limit exceeded
                            if current_memory_mb > memory_limit_mb:
                                process.terminate()
                                break
                                
                            time.sleep(0.1)  # Check every 100ms
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            break
                except Exception:
                    pass  # Ignore monitoring errors
            
            # Start monitoring
            monitor_thread = threading.Thread(target=monitor_memory, daemon=True)
            monitor_thread.start()
            
            # Execute with timeout
            try:
                stdout, stderr = process.communicate(input=input_data, timeout=timeout)
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                return ExecutionResult(
                    success=process.returncode == 0,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=process.returncode,
                    execution_time_ms=execution_time_ms,
                    memory_usage_mb=round(max_memory_mb, 2),
                    timeout=False
                )
                
            except subprocess.TimeoutExpired:
                process.kill()
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                return ExecutionResult(
                    success=False,
                    stdout="",
                    stderr="Execution timed out",
                    return_code=-1,
                    execution_time_ms=execution_time_ms,
                    memory_usage_mb=round(max_memory_mb, 2),
                    timeout=True,
                    error=f"Execution timed out after {timeout} seconds"
                )
                
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time_ms=execution_time_ms,
                memory_usage_mb=round(max_memory_mb, 2),
                timeout=False,
                error=f"Execution error: {str(e)}"
            )
        finally:
            # Ensure process cleanup
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except Exception:
                    try:
                        process.kill()
                    except Exception:
                        pass
    
    def _cleanup_files(self, files: List[Path]):
        """Clean up temporary files"""
        for file_path in files:
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass  # Ignore cleanup errors
    
    def generate_test_cases(self, code: str, language: str, problem_type: Optional[str] = None) -> List[TestCase]:
        """Generate intelligent test cases based on code analysis"""
        test_cases = []
        
        # Basic functionality test
        test_cases.append(TestCase(
            name="Basic Case",
            input=self._generate_basic_input(code, problem_type),
            description="Tests core functionality"
        ))
        
        # Edge cases based on code analysis
        if self._has_array_operations(code):
            test_cases.extend([
                TestCase(
                    name="Empty Array",
                    input="[]",
                    description="Tests empty input handling"
                ),
                TestCase(
                    name="Single Element",
                    input="[1]",
                    description="Tests minimal input"
                ),
                TestCase(
                    name="Large Array",
                    input=str(list(range(1000))),
                    description="Tests performance with large input"
                )
            ])
        
        # Numeric boundary tests
        if self._has_numeric_operations(code):
            test_cases.extend([
                TestCase(
                    name="Zero Value",
                    input="0",
                    description="Tests zero handling"
                ),
                TestCase(
                    name="Negative Values",
                    input="-100",
                    description="Tests negative number handling"
                ),
                TestCase(
                    name="Large Numbers",
                    input="1000000",
                    description="Tests large number handling"
                )
            ])
        
        # String tests
        if self._has_string_operations(code):
            test_cases.extend([
                TestCase(
                    name="Empty String",
                    input='""',
                    description="Tests empty string handling"
                ),
                TestCase(
                    name="Single Character",
                    input='"a"',
                    description="Tests minimal string"
                ),
                TestCase(
                    name="Long String",
                    input='"' + 'a' * 1000 + '"',
                    description="Tests long string performance"
                )
            ])
        
        return test_cases[:8]  # Limit to 8 test cases
    
    def _generate_basic_input(self, code: str, problem_type: Optional[str]) -> str:
        """Generate basic input based on code analysis"""
        if problem_type == "array":
            return "[1, 2, 3, 4, 5]"
        elif problem_type == "string":
            return '"hello"'
        elif problem_type == "number":
            return "42"
        
        # Auto-detect based on code
        if "list" in code.lower() or "array" in code.lower() or "[" in code:
            return "[1, 2, 3, 4, 5]"
        elif "str" in code.lower() or '"' in code or "'" in code:
            return '"test"'
        else:
            return "42"
    
    def _has_array_operations(self, code: str) -> bool:
        """Check if code has array operations"""
        array_indicators = ["[", "]", "list", "array", "append", "pop", "len("]
        return any(indicator in code.lower() for indicator in array_indicators)
    
    def _has_numeric_operations(self, code: str) -> bool:
        """Check if code has numeric operations"""
        numeric_indicators = ["+", "-", "*", "/", "int(", "float(", "math."]
        return any(indicator in code for indicator in numeric_indicators)
    
    def _has_string_operations(self, code: str) -> bool:
        """Check if code has string operations"""
        string_indicators = ['"', "'", "str(", ".split", ".join", ".strip", ".lower", ".upper"]
        return any(indicator in code for indicator in string_indicators)

# Initialize the executor
executor = SafeCodeExecutor()

@router.post("/run", response_model=ExecutionResult)
async def execute_code(submission: CodeSubmission):
    """Execute code and return results"""
    try:
        result = await executor.execute_code(submission)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@router.post("/test", response_model=List[TestResult])
async def test_code(
    code: str,
    language: str,
    test_cases: List[TestCase],
    timeout_seconds: int = 10
):
    """Run code against multiple test cases"""
    try:
        results = []
        
        for test_case in test_cases:
            submission = CodeSubmission(
                code=code,
                language=language,
                test_inputs=[test_case.input],
                timeout_seconds=timeout_seconds
            )
            
            execution_result = await executor.execute_code(submission)
            
            # Check if output matches expected (if provided)
            output_match = True
            if test_case.expected_output is not None:
                actual_output = execution_result.stdout.strip()
                expected_output = test_case.expected_output.strip()
                output_match = actual_output == expected_output
            
            test_result = TestResult(
                test_case=test_case,
                result=execution_result,
                passed=execution_result.success and output_match,
                output_match=output_match
            )
            
            results.append(test_result)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Testing failed: {str(e)}")

@router.post("/analyze", response_model=CodeAnalysisResult)
async def analyze_code(
    code: str,
    language: str,
    problem_type: Optional[str] = None,
    custom_test_cases: Optional[List[TestCase]] = None
):
    """Comprehensive code analysis with execution and testing"""
    try:
        # Generate or use provided test cases
        if custom_test_cases:
            test_cases = custom_test_cases
        else:
            test_cases = executor.generate_test_cases(code, language, problem_type)
        
        # Run tests
        test_results = []
        execution_results = []
        
        for test_case in test_cases:
            submission = CodeSubmission(
                code=code,
                language=language,
                test_inputs=[test_case.input],
                timeout_seconds=10
            )
            
            execution_result = await executor.execute_code(submission)
            execution_results.append(execution_result)
            
            # Check output match
            output_match = True
            if test_case.expected_output is not None:
                actual_output = execution_result.stdout.strip()
                expected_output = test_case.expected_output.strip()
                output_match = actual_output == expected_output
            
            test_result = TestResult(
                test_case=test_case,
                result=execution_result,
                passed=execution_result.success and output_match,
                output_match=output_match
            )
            test_results.append(test_result)
        
        # Analyze performance metrics
        performance_metrics = _analyze_performance(execution_results)
        
        # Analyze code quality
        code_quality = _analyze_code_quality(code, language)
        
        # Generate suggestions
        suggestions = _generate_suggestions(code, language, test_results, performance_metrics)
        
        return CodeAnalysisResult(
            execution_results=execution_results,
            test_results=test_results,
            performance_metrics=performance_metrics,
            code_quality=code_quality,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    return {
        "supported_languages": list(executor.language_configs.keys()),
        "language_details": {
            lang: {
                "extension": config["extension"],
                "timeout": config["timeout"],
                "description": f"{lang.title()} execution support"
            }
            for lang, config in executor.language_configs.items()
        }
    }

def _analyze_performance(execution_results: List[ExecutionResult]) -> Dict[str, Any]:
    """Analyze performance metrics from execution results"""
    if not execution_results:
        return {}
    
    successful_results = [r for r in execution_results if r.success]
    
    if not successful_results:
        return {"error": "No successful executions to analyze"}
    
    execution_times = [r.execution_time_ms for r in successful_results]
    memory_usages = [r.memory_usage_mb for r in successful_results]
    
    return {
        "average_execution_time_ms": sum(execution_times) / len(execution_times),
        "max_execution_time_ms": max(execution_times),
        "min_execution_time_ms": min(execution_times),
        "average_memory_usage_mb": sum(memory_usages) / len(memory_usages),
        "max_memory_usage_mb": max(memory_usages),
        "success_rate": len(successful_results) / len(execution_results),
        "total_test_cases": len(execution_results),
        "performance_grade": _calculate_performance_grade(execution_times, memory_usages)
    }

def _calculate_performance_grade(execution_times: List[int], memory_usages: List[float]) -> str:
    """Calculate performance grade based on execution metrics"""
    avg_time = sum(execution_times) / len(execution_times)
    avg_memory = sum(memory_usages) / len(memory_usages)
    
    # Simple grading logic
    if avg_time < 100 and avg_memory < 10:
        return "A"
    elif avg_time < 500 and avg_memory < 50:
        return "B"
    elif avg_time < 1000 and avg_memory < 100:
        return "C"
    else:
        return "D"

def _analyze_code_quality(code: str, language: str) -> Dict[str, Any]:
    """Basic code quality analysis"""
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    
    return {
        "total_lines": len(lines),
        "code_lines": len([line for line in lines if not line.startswith('#') and not line.startswith('//')]),
        "comment_lines": len([line for line in lines if line.startswith('#') or line.startswith('//')]),
        "average_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0,
        "complexity_indicators": {
            "nested_loops": len(re.findall(r'for.*for|while.*while', code, re.IGNORECASE)),
            "conditional_statements": len(re.findall(r'\bif\b', code, re.IGNORECASE)),
            "function_definitions": len(re.findall(r'\bdef\b|\bfunction\b', code, re.IGNORECASE))
        }
    }

def _generate_suggestions(
    code: str, 
    language: str, 
    test_results: List[TestResult], 
    performance_metrics: Dict[str, Any]
) -> List[str]:
    """Generate improvement suggestions based on analysis"""
    suggestions = []
    
    # Performance suggestions
    if performance_metrics.get("performance_grade", "A") in ["C", "D"]:
        suggestions.append("Consider optimizing your algorithm for better performance")
    
    if performance_metrics.get("max_memory_usage_mb", 0) > 50:
        suggestions.append("High memory usage detected - consider more memory-efficient data structures")
    
    # Test result suggestions
    failed_tests = [t for t in test_results if not t.passed]
    if failed_tests:
        suggestions.append(f"{len(failed_tests)} test case(s) failed - check edge case handling")
    
    # Code quality suggestions
    if "TODO" in code or "FIXME" in code:
        suggestions.append("Complete TODO/FIXME items in your code")
    
    # Language-specific suggestions
    if language == "python":
        if "range(len(" in code:
            suggestions.append("Consider using enumerate() instead of range(len()) for better Pythonic code")
        if "+=" in code and "str" in code.lower():
            suggestions.append("For string concatenation, consider using join() for better performance")
    
    return suggestions
