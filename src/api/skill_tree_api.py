"""
Skill Tree API Endpoints
Provides REST API for skill tree visualization and interaction
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from src.models.database import (
    DatabaseConfig, Problem, ProblemCluster, UserProblemConfidence, 
    UserSkillMastery, UserSkillTreePreferences
)
from src.ml.enhanced_difficulty_analyzer import EnhancedDifficultyAnalyzer
from src.ml.enhanced_similarity_engine import EnhancedSimilarityEngine
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/skill-tree", tags=["Skill Tree"])
skill_tree_router = router  # Alias for backward compatibility

# Database dependency
def get_db():
    db_config = DatabaseConfig("sqlite:///dsatrain_phase4.db")  # Use main database with enhanced data
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


# Response Models
class ProblemSkillTreeInfo(BaseModel):
    id: str
    title: str
    difficulty: str
    sub_difficulty_level: int
    conceptual_difficulty: int
    implementation_complexity: int
    algorithm_tags: List[str]
    prerequisite_skills: List[str]
    quality_score: float
    google_interview_relevance: float
    skill_tree_position: Dict[str, Any]


class SkillTreeColumn(BaseModel):
    skill_area: str
    total_problems: int
    difficulty_levels: Dict[str, List[ProblemSkillTreeInfo]]
    mastery_percentage: float
    recommended_next: Optional[List[str]] = None


class ProblemClusterInfo(BaseModel):
    id: str
    cluster_name: str
    primary_skill_area: str
    difficulty_level: str
    representative_problems: List[str]
    cluster_size: int
    avg_quality_score: float
    similarity_threshold: float
    algorithm_tags: List[str]


class SimilarityResult(BaseModel):
    problem_id: str
    similarity_score: float
    explanation: str
    algorithm_similarity: float
    pattern_similarity: float
    difficulty_similarity: float


class UserConfidenceUpdate(BaseModel):
    problem_id: str
    confidence_level: int  # 0-5
    solve_time_seconds: Optional[int] = None
    hints_used: Optional[int] = 0


class SkillTreePreferences(BaseModel):
    preferred_view_mode: str = "columns"
    show_confidence_overlay: bool = True
    auto_expand_clusters: bool = False
    highlight_prerequisites: bool = True
    visible_skill_areas: List[str] = []


# API Endpoints

@router.get("/overview", response_model=Dict[str, Any])
async def get_skill_tree_overview(
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get complete skill tree overview with problems organized by skill area and difficulty"""
    
    try:
        # Get all problems with enhanced difficulty metrics
        problems = db.query(Problem).filter(Problem.sub_difficulty_level.isnot(None)).all()
        
        if not problems:
            raise HTTPException(status_code=404, detail="No problems with skill tree data found")
        
        # Organize problems by skill area
        skill_areas = {}
        
        for problem in problems:
            if not problem.algorithm_tags:
                continue
                
            # Determine primary skill area
            primary_skill = _determine_primary_skill_area(problem.algorithm_tags)
            
            if primary_skill not in skill_areas:
                skill_areas[primary_skill] = {
                    "Easy": [], "Medium": [], "Hard": []
                }
            
            # Add to appropriate difficulty level
            problem_info = ProblemSkillTreeInfo(
                id=problem.id,
                title=problem.title,
                difficulty=problem.difficulty,
                sub_difficulty_level=problem.sub_difficulty_level or 1,
                conceptual_difficulty=problem.conceptual_difficulty or 50,
                implementation_complexity=problem.implementation_complexity or 50,
                algorithm_tags=problem.algorithm_tags or [],
                prerequisite_skills=problem.prerequisite_skills or [],
                quality_score=problem.quality_score or 0.0,
                google_interview_relevance=problem.google_interview_relevance or 0.0,
                skill_tree_position=problem.skill_tree_position or {}
            )
            
            skill_areas[primary_skill][problem.difficulty].append(problem_info)
        
        # Create skill tree columns
        columns = []
        for skill_area, difficulties in skill_areas.items():
            # Calculate total problems
            total_problems = sum(len(probs) for probs in difficulties.values())
            
            # Get user mastery (if user_id provided)
            mastery_percentage = 0.0
            if user_id:
                mastery = db.query(UserSkillMastery).filter(
                    UserSkillMastery.user_id == user_id,
                    UserSkillMastery.skill_area == skill_area
                ).first()
                if mastery:
                    mastery_percentage = mastery.mastery_level
            
            # Sort problems by sub-difficulty within each level
            for difficulty in difficulties:
                difficulties[difficulty].sort(key=lambda p: p.sub_difficulty_level)
            
            column = SkillTreeColumn(
                skill_area=skill_area,
                total_problems=total_problems,
                difficulty_levels=difficulties,
                mastery_percentage=mastery_percentage
            )
            
            columns.append(column)
        
        # Sort columns by complexity (easy skills first)
        skill_complexity_order = {
            "array_processing": 1, "string_algorithms": 2, "mathematical": 3,
            "sorting_searching": 4, "tree_algorithms": 5, "dynamic_programming": 6,
            "graph_algorithms": 7, "advanced_structures": 8
        }
        
        columns.sort(key=lambda c: skill_complexity_order.get(c.skill_area, 99))
        
        return {
            "skill_tree_columns": [col.dict() for col in columns],
            "total_problems": len(problems),
            "total_skill_areas": len(skill_areas),
            "user_id": user_id,
            "last_updated": "2025-07-31T10:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting skill tree overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters", response_model=List[ProblemClusterInfo])
async def get_problem_clusters(
    skill_area: Optional[str] = None,
    difficulty: Optional[str] = None,
    min_cluster_size: int = Query(2, ge=1),
    db: Session = Depends(get_db)
):
    """Get problem clusters for skill tree visualization"""
    
    try:
        query = db.query(ProblemCluster)
        
        if skill_area:
            query = query.filter(ProblemCluster.primary_skill_area == skill_area)
        if difficulty:
            query = query.filter(ProblemCluster.difficulty_level == difficulty)
        
        query = query.filter(ProblemCluster.cluster_size >= min_cluster_size)
        
        clusters = query.all()
        
        result = []
        for cluster in clusters:
            cluster_info = ProblemClusterInfo(
                id=cluster.id,
                cluster_name=cluster.cluster_name,
                primary_skill_area=cluster.primary_skill_area,
                difficulty_level=cluster.difficulty_level,
                representative_problems=cluster.representative_problems,
                cluster_size=cluster.cluster_size,
                avg_quality_score=cluster.avg_quality_score,
                similarity_threshold=cluster.similarity_threshold,
                algorithm_tags=cluster.algorithm_tags
            )
            result.append(cluster_info)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting problem clusters: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{problem_id}", response_model=List[SimilarityResult])
async def get_similar_problems(
    problem_id: str,
    limit: int = Query(5, ge=1, le=20),
    min_similarity: float = Query(0.3, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """Get problems similar to the specified problem"""
    
    try:
        # Check if problem exists
        problem = db.query(Problem).filter(Problem.id == problem_id).first()
        if not problem:
            raise HTTPException(status_code=404, detail=f"Problem {problem_id} not found")
        
        # Use similarity engine
        engine = EnhancedSimilarityEngine(db)
        similar_problems = engine.find_similar_problems(problem_id, limit, min_similarity)
        
        result = []
        for similar_problem, similarity_score in similar_problems:
            similarity_result = SimilarityResult(
                problem_id=similar_problem.id,
                similarity_score=similarity_score.combined_score,
                explanation=similarity_score.explanation,
                algorithm_similarity=similarity_score.algorithm_similarity,
                pattern_similarity=similarity_score.pattern_similarity,
                difficulty_similarity=similarity_score.difficulty_similarity
            )
            result.append(similarity_result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting similar problems: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confidence", response_model=Dict[str, str])
async def update_user_confidence(
    user_id: str,
    confidence_update: UserConfidenceUpdate,
    db: Session = Depends(get_db)
):
    """Update user confidence level for a problem"""
    
    try:
        # Check if problem exists
        problem = db.query(Problem).filter(Problem.id == confidence_update.problem_id).first()
        if not problem:
            raise HTTPException(status_code=404, detail=f"Problem {confidence_update.problem_id} not found")
        
        # Get or create confidence record
        confidence_record = db.query(UserProblemConfidence).filter(
            UserProblemConfidence.user_id == user_id,
            UserProblemConfidence.problem_id == confidence_update.problem_id
        ).first()
        
        if not confidence_record:
            confidence_record = UserProblemConfidence(
                user_id=user_id,
                problem_id=confidence_update.problem_id
            )
            db.add(confidence_record)
        
        # Update confidence data
        confidence_record.confidence_level = confidence_update.confidence_level
        if confidence_update.solve_time_seconds:
            confidence_record.solve_time_seconds = confidence_update.solve_time_seconds
        if confidence_update.hints_used is not None:
            confidence_record.hints_used = confidence_update.hints_used
        
        confidence_record.attempts_count = (confidence_record.attempts_count or 0) + 1
        
        from datetime import datetime
        confidence_record.last_attempted = datetime.now()
        confidence_record.updated_at = datetime.now()
        
        db.commit()
        
        # Update skill area mastery
        _update_skill_mastery(db, user_id, problem.algorithm_tags)
        
        return {
            "status": "success",
            "message": f"Confidence updated for problem {confidence_update.problem_id}"
        }
        
    except Exception as e:
        logger.error(f"Error updating confidence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/progress", response_model=Dict[str, Any])
async def get_user_progress(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's skill tree progress and confidence levels"""
    
    try:
        # Get user confidence records
        confidence_records = db.query(UserProblemConfidence).filter(
            UserProblemConfidence.user_id == user_id
        ).all()
        
        # Get skill mastery records
        skill_masteries = db.query(UserSkillMastery).filter(
            UserSkillMastery.user_id == user_id
        ).all()
        
        # Organize confidence by skill area
        skill_progress = {}
        
        for record in confidence_records:
            problem = db.query(Problem).filter(Problem.id == record.problem_id).first()
            if problem and problem.algorithm_tags:
                primary_skill = _determine_primary_skill_area(problem.algorithm_tags)
                
                if primary_skill not in skill_progress:
                    skill_progress[primary_skill] = {
                        "problems_attempted": 0,
                        "average_confidence": 0.0,
                        "confidence_levels": {}
                    }
                
                skill_progress[primary_skill]["problems_attempted"] += 1
                skill_progress[primary_skill]["confidence_levels"][record.problem_id] = {
                    "confidence_level": record.confidence_level,
                    "last_attempted": record.last_attempted.isoformat() if record.last_attempted else None,
                    "attempts_count": record.attempts_count or 0
                }
        
        # Calculate average confidence per skill
        for skill in skill_progress:
            confidence_levels = [
                conf["confidence_level"] 
                for conf in skill_progress[skill]["confidence_levels"].values()
            ]
            if confidence_levels:
                skill_progress[skill]["average_confidence"] = sum(confidence_levels) / len(confidence_levels)
        
        # Add skill mastery data
        mastery_data = {}
        for mastery in skill_masteries:
            mastery_data[mastery.skill_area] = {
                "mastery_level": mastery.mastery_level,
                "problems_attempted": mastery.problems_attempted,
                "problems_solved": mastery.problems_solved,
                "mastery_trend": mastery.mastery_trend,
                "last_activity": mastery.last_activity.isoformat() if mastery.last_activity else None
            }
        
        return {
            "user_id": user_id,
            "skill_progress": skill_progress,
            "skill_mastery": mastery_data,
            "total_problems_attempted": len(confidence_records),
            "skill_areas_touched": len(skill_progress)
        }
        
    except Exception as e:
        logger.error(f"Error getting user progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences/{user_id}", response_model=SkillTreePreferences)
async def get_user_preferences(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's skill tree visualization preferences"""
    
    try:
        preferences = db.query(UserSkillTreePreferences).filter(
            UserSkillTreePreferences.user_id == user_id
        ).first()
        
        if not preferences:
            # Return default preferences
            return SkillTreePreferences()
        
        return SkillTreePreferences(
            preferred_view_mode=preferences.preferred_view_mode,
            show_confidence_overlay=preferences.show_confidence_overlay,
            auto_expand_clusters=preferences.auto_expand_clusters,
            highlight_prerequisites=preferences.highlight_prerequisites,
            visible_skill_areas=preferences.visible_skill_areas or []
        )
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preferences/{user_id}", response_model=Dict[str, str])
async def update_user_preferences(
    user_id: str,
    preferences: SkillTreePreferences,
    db: Session = Depends(get_db)
):
    """Update user's skill tree visualization preferences"""
    
    try:
        # Get or create preferences record
        user_prefs = db.query(UserSkillTreePreferences).filter(
            UserSkillTreePreferences.user_id == user_id
        ).first()
        
        if not user_prefs:
            user_prefs = UserSkillTreePreferences(user_id=user_id)
            db.add(user_prefs)
        
        # Update preferences
        user_prefs.preferred_view_mode = preferences.preferred_view_mode
        user_prefs.show_confidence_overlay = preferences.show_confidence_overlay
        user_prefs.auto_expand_clusters = preferences.auto_expand_clusters
        user_prefs.highlight_prerequisites = preferences.highlight_prerequisites
        user_prefs.visible_skill_areas = preferences.visible_skill_areas
        
        from datetime import datetime
        user_prefs.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Preferences updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper Functions

def _determine_primary_skill_area(algorithm_tags: List[str]) -> str:
    """Determine primary skill area from algorithm tags"""
    
    skill_mapping = {
        "array_processing": ["arrays", "two_pointers", "sliding_window", "prefix_sum"],
        "string_algorithms": ["strings", "kmp", "rabin_karp", "manacher"],
        "tree_algorithms": ["trees", "binary_tree", "bst", "dfs", "bfs"],
        "graph_algorithms": ["graphs", "dijkstra", "floyd_warshall", "topological_sort"],
        "dynamic_programming": ["dynamic_programming", "dp", "memoization"],
        "sorting_searching": ["sorting", "binary_search", "quicksort", "mergesort"],
        "mathematical": ["math", "number_theory", "combinatorics", "geometry"],
        "advanced_structures": ["segment_tree", "fenwick_tree", "union_find", "trie"]
    }
    
    # Count matches for each skill area
    skill_scores = {}
    for skill_area, keywords in skill_mapping.items():
        score = sum(1 for tag in algorithm_tags if tag.lower() in [k.lower() for k in keywords])
        if score > 0:
            skill_scores[skill_area] = score
    
    if skill_scores:
        return max(skill_scores.items(), key=lambda x: x[1])[0]
    
    # Fallback
    return "general"


def _update_skill_mastery(db: Session, user_id: str, algorithm_tags: List[str]):
    """Update user skill mastery based on problem interaction"""
    
    if not algorithm_tags:
        return
    
    primary_skill = _determine_primary_skill_area(algorithm_tags)
    
    # Get or create skill mastery record
    mastery = db.query(UserSkillMastery).filter(
        UserSkillMastery.user_id == user_id,
        UserSkillMastery.skill_area == primary_skill
    ).first()
    
    if not mastery:
        mastery = UserSkillMastery(
            user_id=user_id,
            skill_area=primary_skill
        )
        db.add(mastery)
    
    # Update mastery metrics
    mastery.problems_attempted = (mastery.problems_attempted or 0) + 1
    
    # Calculate average confidence for this skill area
    confidences = db.query(UserProblemConfidence).join(Problem).filter(
        UserProblemConfidence.user_id == user_id,
        Problem.algorithm_tags.contains([primary_skill])  # Simplified for demo
    ).all()
    
    if confidences:
        avg_confidence = sum(c.confidence_level for c in confidences) / len(confidences)
        mastery.avg_confidence = avg_confidence
        mastery.mastery_level = min(100.0, avg_confidence * 20)  # Scale 0-5 to 0-100
    
    from datetime import datetime
    mastery.last_activity = datetime.now()
    mastery.updated_at = datetime.now()
    
    db.commit()
