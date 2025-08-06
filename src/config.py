"""
Configuration settings for DSATrain data collection
"""

import os
from pathlib import Path

# Try to load environment variables, but don't fail if dotenv is not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, just use os.getenv defaults
    pass

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"

# Data directories
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ENRICHED_DATA_DIR = DATA_DIR / "enriched"
EXPORTS_DATA_DIR = DATA_DIR / "exports"

# Platform-specific data directories
CODEFORCES_RAW_DIR = RAW_DATA_DIR / "codeforces"
LEETCODE_RAW_DIR = RAW_DATA_DIR / "kaggle_leetcode"
HACKERRANK_RAW_DIR = RAW_DATA_DIR / "hackerrank"
ACADEMIC_RAW_DIR = RAW_DATA_DIR / "academic_datasets"

# API Configuration
CODEFORCES_API_BASE = "https://codeforces.com/api"
CODEFORCES_RATE_LIMIT = 2.1  # seconds between requests

# Collection settings
DEFAULT_BATCH_SIZE = 100
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# Database configuration (for future use)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dsatrain.db")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = PROJECT_ROOT / "logs" / "collection.log"

# Ensure log directory exists
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Quality thresholds
MIN_PROBLEM_DESCRIPTION_LENGTH = 50
MIN_SOLUTION_CODE_LENGTH = 20
QUALITY_SCORE_THRESHOLD = 6.0

# Google-relevance keywords (for tagging problems)
GOOGLE_RELEVANT_TAGS = [
    "algorithms", "data_structures", "dynamic_programming", "graphs", 
    "trees", "arrays", "strings", "binary_search", "sorting", "hashing",
    "greedy", "divide_and_conquer", "backtracking", "recursion", "math",
    "geometry", "implementation", "two_pointers", "sliding_window"
]

# Company tags that indicate Google relevance
GOOGLE_COMPANY_TAGS = ["google", "alphabet", "youtube", "android"]

# File naming conventions
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
JSON_INDENT = 2
