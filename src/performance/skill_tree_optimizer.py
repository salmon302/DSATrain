"""
Database Performance Optimizations for Skill Tree
Optimized queries and caching strategies for handling hundreds of problems
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, Text, JSON, DateTime, Index, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Optional, Tuple
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SkillTreePerformanceOptimizer:
    """Performance optimization utilities for Skill Tree queries"""
    
    def __init__(self, db_session):
        self.db = db_session
        self._cache = {}
        self._cache_ttl = timedelta(minutes=15)  # 15-minute cache
    
    def get_skill_area_summary_optimized(self) -> List[Dict]:
        """
        OPTIMIZATION 1: Single query for all skill area summaries
        Instead of N+1 queries, use aggregation
        """
        cache_key = "skill_area_summary"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]['data']
        
        try:
            from src.models.database import Problem
            from src.api.skill_tree_api import _determine_primary_skill_area
            
            # Single query to get all problems with needed fields
            problems = self.db.query(
                Problem.id,
                Problem.title,
                Problem.difficulty,
                Problem.sub_difficulty_level,
                Problem.algorithm_tags,
                Problem.quality_score,
                Problem.google_interview_relevance
            ).filter(
                Problem.sub_difficulty_level.isnot(None)
            ).all()
            
            # Group by skill area in memory (faster than multiple DB queries)
            skill_areas = {}
            
            for problem in problems:
                if not problem.algorithm_tags:
                    continue
                    
                primary_skill = _determine_primary_skill_area(problem.algorithm_tags)
                
                if primary_skill not in skill_areas:
                    skill_areas[primary_skill] = {
                        'total_problems': 0,
                        'difficulty_distribution': {'Easy': 0, 'Medium': 0, 'Hard': 0},
                        'problems': []
                    }
                
                skill_areas[primary_skill]['total_problems'] += 1
                skill_areas[primary_skill]['difficulty_distribution'][problem.difficulty] += 1
                skill_areas[primary_skill]['problems'].append(problem)
            
            # Sort problems by relevance + quality and take top N
            for skill_area in skill_areas.values():
                skill_area['problems'].sort(
                    key=lambda p: (p.quality_score or 0) + (p.google_interview_relevance or 0),
                    reverse=True
                )
            
            # Cache result
            self._cache[cache_key] = {
                'data': skill_areas,
                'timestamp': datetime.now()
            }
            
            return skill_areas
            
        except Exception as e:
            logger.error(f"Error in get_skill_area_summary_optimized: {str(e)}")
            return {}
    
    def get_paginated_problems_optimized(
        self, 
        skill_area: str, 
        page: int = 1, 
        page_size: int = 20,
        difficulty: Optional[str] = None,
        sort_by: str = "quality"
    ) -> Tuple[List, int, bool]:
        """
        OPTIMIZATION 2: Efficient pagination with proper indexing
        """
        try:
            from src.models.database import Problem
            from src.api.skill_tree_api import _determine_primary_skill_area
            
            # Build base query with minimal fields for better performance
            base_query = self.db.query(
                Problem.id,
                Problem.title,
                Problem.difficulty,
                Problem.sub_difficulty_level,
                Problem.quality_score,
                Problem.google_interview_relevance,
                Problem.algorithm_tags
            ).filter(
                Problem.sub_difficulty_level.isnot(None)
            )
            
            # Apply difficulty filter early
            if difficulty:
                base_query = base_query.filter(Problem.difficulty == difficulty)
            
            # Get all matching problems (we need to filter by skill area in Python)
            # This could be optimized with a materialized view or denormalized field
            all_problems = base_query.all()
            
            # Filter by skill area
            filtered_problems = [
                p for p in all_problems 
                if p.algorithm_tags and _determine_primary_skill_area(p.algorithm_tags) == skill_area
            ]
            
            # Apply sorting
            if sort_by == "quality":
                filtered_problems.sort(key=lambda p: p.quality_score or 0, reverse=True)
            elif sort_by == "relevance":
                filtered_problems.sort(key=lambda p: p.google_interview_relevance or 0, reverse=True)
            elif sort_by == "difficulty":
                difficulty_order = {"Easy": 1, "Medium": 2, "Hard": 3}
                filtered_problems.sort(
                    key=lambda p: (difficulty_order.get(p.difficulty, 4), p.sub_difficulty_level or 1)
                )
            elif sort_by == "title":
                filtered_problems.sort(key=lambda p: p.title)
            
            # Calculate pagination
            total_count = len(filtered_problems)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_problems = filtered_problems[start_idx:end_idx]
            has_next = end_idx < total_count
            
            return page_problems, total_count, has_next
            
        except Exception as e:
            logger.error(f"Error in get_paginated_problems_optimized: {str(e)}")
            return [], 0, False
    
    def search_problems_optimized(
        self,
        search_term: str,
        skill_areas: Optional[List[str]] = None,
        difficulties: Optional[List[str]] = None,
        min_quality: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List, int, bool]:
        """
        OPTIMIZATION 3: Full-text search with proper indexing
        """
        try:
            from src.models.database import Problem
            from src.api.skill_tree_api import _determine_primary_skill_area
            
            # Build query with database-level filtering
            query = self.db.query(
                Problem.id,
                Problem.title,
                Problem.difficulty,
                Problem.sub_difficulty_level,
                Problem.quality_score,
                Problem.google_interview_relevance,
                Problem.algorithm_tags
            ).filter(
                Problem.sub_difficulty_level.isnot(None),
                Problem.title.contains(search_term)  # Use database index
            )
            
            # Apply filters
            if difficulties:
                query = query.filter(Problem.difficulty.in_(difficulties))
                
            if min_quality is not None:
                query = query.filter(Problem.quality_score >= min_quality)
            
            all_results = query.all()
            
            # Filter by skill areas if specified
            if skill_areas:
                filtered_results = [
                    p for p in all_results
                    if p.algorithm_tags and _determine_primary_skill_area(p.algorithm_tags) in skill_areas
                ]
            else:
                filtered_results = all_results
            
            # Sort by relevance (quality + search relevance)
            filtered_results.sort(
                key=lambda p: (p.quality_score or 0) + (p.google_interview_relevance or 0),
                reverse=True
            )
            
            # Pagination
            total_count = len(filtered_results)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_results = filtered_results[start_idx:end_idx]
            has_next = end_idx < total_count
            
            return page_results, total_count, has_next
            
        except Exception as e:
            logger.error(f"Error in search_problems_optimized: {str(e)}")
            return [], 0, False
    
    def get_cached_statistics(self) -> Dict:
        """
        OPTIMIZATION 4: Pre-computed statistics with caching
        """
        cache_key = "statistics"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]['data']
        
        try:
            from src.models.database import Problem
            
            # Use aggregate queries for better performance
            total_problems = self.db.query(Problem).filter(
                Problem.sub_difficulty_level.isnot(None)
            ).count()
            
            # Single query for difficulty distribution
            difficulty_stats = self.db.query(
                Problem.difficulty,
                func.count(Problem.id).label('count')
            ).filter(
                Problem.sub_difficulty_level.isnot(None)
            ).group_by(Problem.difficulty).all()
            
            difficulty_distribution = {stat.difficulty: stat.count for stat in difficulty_stats}
            
            # Quality statistics
            quality_stats = self.db.query(
                func.avg(Problem.quality_score).label('avg_quality'),
                func.count().filter(Problem.google_interview_relevance >= 70).label('high_relevance')
            ).filter(
                Problem.sub_difficulty_level.isnot(None)
            ).first()
            
            stats = {
                'total_problems': total_problems,
                'difficulty_distribution': difficulty_distribution,
                'avg_quality_score': float(quality_stats.avg_quality or 0),
                'high_relevance_problems': quality_stats.high_relevance or 0,
                'last_updated': datetime.now().isoformat(),
                'cache_status': 'fresh'
            }
            
            # Cache result
            self._cache[cache_key] = {
                'data': stats,
                'timestamp': datetime.now()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error in get_cached_statistics: {str(e)}")
            return {}
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self._cache:
            return False
        
        cache_entry = self._cache[cache_key]
        return datetime.now() - cache_entry['timestamp'] < self._cache_ttl
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()


# OPTIMIZATION 5: Database Index Recommendations
def create_performance_indexes(engine):
    """
    Create additional indexes for skill tree performance
    Run this as a migration
    """
    
    index_statements = [
        # Composite index for skill tree queries
        "CREATE INDEX IF NOT EXISTS idx_problems_skill_tree ON problems(sub_difficulty_level, difficulty, quality_score)",
        
        # Index for search functionality
        "CREATE INDEX IF NOT EXISTS idx_problems_title_search ON problems(title)",
        
        # Index for quality and relevance filtering
        "CREATE INDEX IF NOT EXISTS idx_problems_quality_relevance ON problems(quality_score, google_interview_relevance)",
        
        # Partial index for high-quality problems
        "CREATE INDEX IF NOT EXISTS idx_problems_high_quality ON problems(quality_score) WHERE quality_score >= 7.0",
        
        # Index for algorithm tags (if using PostgreSQL)
        # "CREATE INDEX IF NOT EXISTS idx_problems_algorithm_tags_gin ON problems USING gin(algorithm_tags)",
    ]
    
    try:
        with engine.connect() as conn:
            for statement in index_statements:
                logger.info(f"Creating index: {statement}")
                conn.execute(statement)
            conn.commit()
        logger.info("Performance indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating performance indexes: {str(e)}")


# OPTIMIZATION 6: Query Batch Processing
class BatchQueryProcessor:
    """Process multiple queries efficiently"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def get_multiple_skill_areas_data(self, skill_areas: List[str]) -> Dict:
        """
        Get data for multiple skill areas in a single optimized query batch
        """
        try:
            from src.models.database import Problem
            from src.api.skill_tree_api import _determine_primary_skill_area
            
            # Single query to get all needed data
            problems = self.db.query(Problem).filter(
                Problem.sub_difficulty_level.isnot(None)
            ).all()
            
            # Group by skill areas
            skill_area_data = {}
            
            for problem in problems:
                if not problem.algorithm_tags:
                    continue
                    
                primary_skill = _determine_primary_skill_area(problem.algorithm_tags)
                
                if primary_skill in skill_areas:
                    if primary_skill not in skill_area_data:
                        skill_area_data[primary_skill] = []
                    skill_area_data[primary_skill].append(problem)
            
            return skill_area_data
            
        except Exception as e:
            logger.error(f"Error in get_multiple_skill_areas_data: {str(e)}")
            return {}


# Usage Example:
"""
# Initialize optimizer
optimizer = SkillTreePerformanceOptimizer(db_session)

# Get optimized skill area summaries
skill_areas = optimizer.get_skill_area_summary_optimized()

# Get paginated problems
problems, total, has_next = optimizer.get_paginated_problems_optimized(
    skill_area="array_processing",
    page=1,
    page_size=20,
    difficulty="Medium",
    sort_by="quality"
)

# Search with optimization
search_results, total, has_next = optimizer.search_problems_optimized(
    search_term="two sum",
    skill_areas=["array_processing", "mathematical"],
    difficulties=["Easy", "Medium"],
    min_quality=7.0,
    page=1,
    page_size=20
)

# Get cached statistics
stats = optimizer.get_cached_statistics()
"""
