"""
Data schemas for the DSA Training Platform
Based on Technical_Coding_Data_Strategy.md specifications
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SourcePlatform(str, Enum):
    CODEFORCES = "codeforces"
    LEETCODE = "leetcode"
    HACKERRANK = "hackerrank"
    ATCODER = "atcoder"
    CODECHEF = "codechef"


class SolutionType(str, Enum):
    OPTIMAL = "optimal"
    BRUTE_FORCE = "brute_force"
    ALTERNATIVE = "alternative"


class ProgrammingLanguage(str, Enum):
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    CSHARP = "csharp"
    GO = "go"


class AcquisitionMethod(str, Enum):
    API = "api"
    STATIC_DATASET = "static_dataset"
    SCRAPING = "scraping"


class Difficulty(BaseModel):
    level: DifficultyLevel
    rating: Optional[int] = None
    source_scale: Optional[str] = None


class Constraints(BaseModel):
    time_limit: Optional[str] = None
    memory_limit: Optional[str] = None
    input_size: Optional[str] = None


class TestCase(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None


class Complexity(BaseModel):
    time: str = Field(..., description="Time complexity in Big O notation")
    space: str = Field(..., description="Space complexity in Big O notation")
    verified: bool = False


class Editorial(BaseModel):
    approach: Optional[str] = None
    complexity: Optional[Complexity] = None


class ProblemMetadata(BaseModel):
    created_date: datetime
    last_updated: datetime
    source_url: Optional[HttpUrl] = None
    acquisition_method: AcquisitionMethod


class Problem(BaseModel):
    id: str = Field(..., description="Unique identifier")
    source: SourcePlatform
    title: str
    description: str
    difficulty: Difficulty
    tags: List[str] = Field(default_factory=list)
    company_tags: List[str] = Field(default_factory=list)
    constraints: Optional[Constraints] = None
    test_cases: List[TestCase] = Field(default_factory=list)
    editorial: Optional[Editorial] = None
    metadata: ProblemMetadata

    # Pydantic v2 serializes datetime to ISO 8601 by default; no custom Config needed.


class QualityMetrics(BaseModel):
    readability_score: Optional[float] = Field(None, ge=0, le=10)
    maintainability_score: Optional[float] = Field(None, ge=0, le=10)
    follows_best_practices: Optional[bool] = None


class SolutionMetadata(BaseModel):
    author: Optional[str] = None
    verification_status: Optional[Literal["tested", "verified", "community_approved"]] = None
    created_date: datetime
    last_updated: datetime


class Solution(BaseModel):
    problem_id: str
    language: ProgrammingLanguage
    solution_type: SolutionType
    code: str
    explanation: Optional[str] = None
    complexity: Optional[Complexity] = None
    quality_metrics: Optional[QualityMetrics] = None
    metadata: SolutionMetadata

    # Pydantic v2 default serialization is sufficient.


class Tag(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    parent_tag: Optional[str] = None


class Company(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    problem_count: int = 0


class AcquisitionLog(BaseModel):
    source: SourcePlatform
    acquisition_method: AcquisitionMethod
    timestamp: datetime
    records_collected: int
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    # Pydantic v2 default serialization is sufficient.


# Response models for APIs
class ProblemListResponse(BaseModel):
    problems: List[Problem]
    total_count: int
    page: int
    page_size: int


class SolutionListResponse(BaseModel):
    solutions: List[Solution]
    total_count: int
    page: int
    page_size: int


# Search and filter models
class ProblemFilter(BaseModel):
    source: Optional[SourcePlatform] = None
    difficulty_level: Optional[DifficultyLevel] = None
    tags: Optional[List[str]] = None
    company_tags: Optional[List[str]] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None


class SolutionFilter(BaseModel):
    language: Optional[ProgrammingLanguage] = None
    solution_type: Optional[SolutionType] = None
    min_readability_score: Optional[float] = None
    verified_only: bool = False


# ==================== PHASE 3B: SOLUTION ANALYSIS SCHEMAS ====================

class SolutionComplexity(BaseModel):
    """Time and space complexity information"""
    time_complexity: str  # e.g., "O(n log n)"
    space_complexity: str  # e.g., "O(n)"
    time_complexity_explanation: Optional[str] = None
    space_complexity_explanation: Optional[str] = None
    best_case: Optional[str] = None
    worst_case: Optional[str] = None
    average_case: Optional[str] = None


class CodeQualityMetrics(BaseModel):
    """Code quality assessment metrics"""
    overall_score: float  # 0-100
    readability_score: float  # 0-100
    structure_score: float  # 0-100
    style_score: float  # 0-100
    documentation_score: float  # 0-100
    efficiency_score: float  # 0-100
    maintainability_score: float  # 0-100
    
    # Specific metrics
    lines_of_code: int
    cyclomatic_complexity: Optional[int] = None
    comment_ratio: float  # percentage of lines that are comments
    function_count: int
    variable_naming_score: float
    
    # Issues found
    style_issues: List[str] = []
    potential_bugs: List[str] = []
    performance_warnings: List[str] = []


class PerformanceMetrics(BaseModel):
    """Runtime and memory performance data"""
    runtime_ms: Optional[int] = None
    memory_mb: Optional[float] = None
    runtime_percentile: Optional[float] = None  # Compared to other solutions
    memory_percentile: Optional[float] = None
    test_cases_passed: Optional[int] = None
    total_test_cases: Optional[int] = None
    
    # Benchmarking data
    benchmark_runtime: Optional[Dict[str, float]] = None  # Different input sizes
    benchmark_memory: Optional[Dict[str, float]] = None


class SolutionApproach(str, Enum):
    """Types of solution approaches"""
    OPTIMAL = "optimal"
    BRUTE_FORCE = "brute_force"
    EDUCATIONAL = "educational"
    ALTERNATIVE = "alternative"
    CREATIVE = "creative"
    INTERVIEW_STYLE = "interview_style"
    COMPETITIVE = "competitive"
    RECURSIVE = "recursive"
    ITERATIVE = "iterative"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    GREEDY = "greedy"
    DIVIDE_CONQUER = "divide_conquer"


class SolutionSource(str, Enum):
    """Sources where solutions were collected"""
    LEETCODE_EDITORIAL = "leetcode_editorial"
    LEETCODE_DISCUSSION = "leetcode_discussion"
    CODEFORCES_SUBMISSION = "codeforces_submission"
    CODEFORCES_TUTORIAL = "codeforces_tutorial"
    GITHUB_REPOSITORY = "github_repository"
    GEEKSFORGEEKS = "geeksforgeeks"
    HACKERRANK_EDITORIAL = "hackerrank_editorial"
    ATCODER_EDITORIAL = "atcoder_editorial"
    CODECHEF_EDITORIAL = "codechef_editorial"
    MANUAL_CREATION = "manual_creation"
    COMMUNITY_CONTRIBUTION = "community_contribution"


class EnhancedSolution(BaseModel):
    """Enhanced solution data structure for Phase 3B"""
    # Basic identification
    id: str  # Unique solution identifier
    problem_id: str  # Reference to problem from Phase 2
    title: str  # Solution title/name
    
    # Code and implementation
    language: ProgrammingLanguage
    code: str  # Complete solution code
    entry_point: Optional[str] = None  # Main function/method name
    
    # Approach and methodology
    approach_type: SolutionApproach
    algorithm_tags: List[str] = []  # Specific algorithm techniques used
    data_structures_used: List[str] = []  # Data structures in solution
    design_patterns: List[str] = []  # Programming patterns used
    
    # Complexity analysis
    complexity: SolutionComplexity
    
    # Quality and performance metrics
    code_quality: CodeQualityMetrics
    performance: PerformanceMetrics
    
    # Educational content
    explanation: str  # Algorithm explanation
    step_by_step: List[str] = []  # Step-by-step solution breakdown
    key_insights: List[str] = []  # Important insights/tricks
    common_mistakes: List[str] = []  # Things to avoid
    alternative_approaches: List[str] = []  # Other ways to solve
    
    # Difficulty and learning
    implementation_difficulty: int  # 1-10 scale
    conceptual_difficulty: int  # 1-10 scale
    interview_frequency: Optional[int] = None  # How often asked in interviews
    google_interview_relevance: float = 0.0  # 0-100 score
    
    # Source and attribution
    source: SolutionSource
    source_url: Optional[str] = None
    author: Optional[str] = None
    author_profile: Optional[str] = None
    collection_date: datetime
    verification_status: str = "unverified"  # verified/unverified/flagged
    
    # Learning and progression
    prerequisites: List[str] = []  # Concepts needed to understand
    follow_up_problems: List[str] = []  # Related problems to practice
    difficulty_progression: Optional[str] = None  # beginner/intermediate/advanced
    
    # Metadata
    metadata: Dict[str, Any] = {}
    
    # Pydantic v2 default serialization is sufficient.


class SolutionCollection(BaseModel):
    """Collection of solutions for a single problem"""
    problem_id: str
    problem_title: str
    total_solutions: int
    solutions: List[EnhancedSolution]
    
    # Analysis of the solution set
    language_distribution: Dict[str, int] = {}
    approach_distribution: Dict[str, int] = {}
    quality_stats: Dict[str, float] = {}
    performance_stats: Dict[str, float] = {}
    
    # Best solutions by category
    optimal_solution_id: Optional[str] = None
    most_educational_id: Optional[str] = None
    cleanest_code_id: Optional[str] = None
    fastest_runtime_id: Optional[str] = None
    lowest_memory_id: Optional[str] = None
    
    # Collection metadata
    collection_date: datetime
    last_updated: datetime
    metadata: Dict[str, Any] = {}
    
    # Pydantic v2 default serialization is sufficient.


class SolutionAnalytics(BaseModel):
    """Analytics for solution collections"""
    total_solutions: int
    total_problems_covered: int
    coverage_percentage: float
    
    # Language analysis
    language_distribution: Dict[str, int]
    most_popular_language: str
    
    # Approach analysis
    approach_distribution: Dict[str, int]
    algorithm_frequency: Dict[str, int]
    
    # Quality metrics
    average_code_quality: float
    average_performance_score: float
    high_quality_solutions: int  # Quality score > 80
    
    # Complexity analysis
    time_complexity_distribution: Dict[str, int]
    space_complexity_distribution: Dict[str, int]
    
    # Educational value
    average_explanation_length: float
    solutions_with_steps: int
    solutions_with_insights: int
    
    # Source analysis
    source_distribution: Dict[str, int]
    verified_solutions: int
    community_contributions: int
    
    # Performance insights
    fastest_languages: Dict[str, float]  # Average runtime by language
    memory_efficient_languages: Dict[str, float]
    
    # Collection metadata
    analysis_date: datetime
    metadata: Dict[str, Any] = {}
    
    # Pydantic v2 default serialization is sufficient.
