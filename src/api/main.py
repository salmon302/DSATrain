"""
Phase 4 FastAPI Backend
RESTful API for DSA Training Platform
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

# Database imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.database import DatabaseConfig, Problem, Solution, get_database_stats, get_quality_metrics
from src.ml.recommendation_engine_simple import RecommendationEngine
from src.models.user_tracking import UserBehaviorTracker
from src.api.enhanced_stats import stats_router
from src.api.google_code_analysis import router as google_analysis_router
from src.api.learning_paths import router as learning_paths_router
from src.api.code_execution import router as execution_router
# from src.api.skill_tree_api import skill_tree_router  # Temporarily disabled due to schema differences

# Initialize FastAPI app
app = FastAPI(
    title="DSA Training Platform API",
    description="Phase 4 scalable API for coding interview preparation",
    version="4.0.0"
)

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
db_config = DatabaseConfig()

# Include enhanced statistics router
app.include_router(stats_router)

# Include Google-style code analysis router
app.include_router(google_analysis_router)

# Include learning paths router
app.include_router(learning_paths_router)

# Include code execution router
app.include_router(execution_router)

# Include skill tree router
# app.include_router(skill_tree_router)  # Temporarily disabled due to schema differences

def get_db():
    """Dependency to get database session"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

# Initialize ML components (will be recreated for each request)
def get_recommendation_engine(db: Session = Depends(get_db)) -> RecommendationEngine:
    """Dependency to get ML recommendation engine"""
    return RecommendationEngine(db)

def get_behavior_tracker(db: Session = Depends(get_db)) -> UserBehaviorTracker:
    """Dependency to get user behavior tracker"""
    return UserBehaviorTracker(db)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "DSA Training Platform API",
        "version": "4.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get overall platform statistics"""
    try:
        database_stats = get_database_stats(db)
        quality_metrics = get_quality_metrics(db)
        
        return {
            "database_stats": database_stats,
            "quality_metrics": quality_metrics,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@app.get("/problems")
async def get_problems(
    platform: Optional[str] = Query(None, description="Filter by platform (leetcode, codeforces)"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (Easy, Medium, Hard)"),
    min_quality: Optional[float] = Query(None, description="Minimum quality score (0-100)"),
    min_relevance: Optional[float] = Query(None, description="Minimum Google interview relevance (0-100)"),
    limit: int = Query(50, description="Maximum number of problems to return"),
    offset: int = Query(0, description="Number of problems to skip"),
    db: Session = Depends(get_db)
):
    """Get problems with optional filters"""
    try:
        query = db.query(Problem)
        
        # Apply filters
        if platform:
            query = query.filter(Problem.platform == platform)
        if difficulty:
            query = query.filter(Problem.difficulty == difficulty)
        if min_quality is not None:
            query = query.filter(Problem.quality_score >= min_quality)
        if min_relevance is not None:
            query = query.filter(Problem.google_interview_relevance >= min_relevance)
        
        # Apply pagination and ordering
        query = query.order_by(Problem.quality_score.desc(), Problem.google_interview_relevance.desc())
        problems = query.offset(offset).limit(limit).all()
        
        # Convert to dictionaries
        result = [problem.to_dict() for problem in problems]
        
        return {
            "problems": result,
            "count": len(result),
            "total_available": query.count(),
            "filters_applied": {
                "platform": platform,
                "difficulty": difficulty,
                "min_quality": min_quality,
                "min_relevance": min_relevance
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching problems: {str(e)}")


@app.get("/problems/{problem_id}")
async def get_problem(problem_id: str, db: Session = Depends(get_db)):
    """Get specific problem by ID"""
    try:
        problem = db.query(Problem).filter(Problem.id == problem_id).first()
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        return problem.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching problem: {str(e)}")


@app.get("/problems/{problem_id}/solutions")
async def get_problem_solutions(
    problem_id: str, 
    min_quality: Optional[float] = Query(None, description="Minimum solution quality score"),
    limit: int = Query(10, description="Maximum number of solutions to return"),
    db: Session = Depends(get_db)
):
    """Get solutions for a specific problem"""
    try:
        # Check if problem exists
        problem = db.query(Problem).filter(Problem.id == problem_id).first()
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Query solutions
        query = db.query(Solution).filter(Solution.problem_id == problem_id)
        
        if min_quality is not None:
            query = query.filter(Solution.overall_quality_score >= min_quality)
        
        solutions = query.order_by(Solution.overall_quality_score.desc()).limit(limit).all()
        
        return {
            "problem_id": problem_id,
            "problem_title": problem.title,
            "solutions": [solution.to_dict() for solution in solutions],
            "count": len(solutions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching solutions: {str(e)}")


@app.get("/solutions/{solution_id}")
async def get_solution(solution_id: str, db: Session = Depends(get_db)):
    """Get specific solution by ID"""
    try:
        solution = db.query(Solution).filter(Solution.id == solution_id).first()
        if not solution:
            raise HTTPException(status_code=404, detail="Solution not found")
        
        return solution.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching solution: {str(e)}")


@app.get("/recommendations")
async def get_recommendations(
    user_id: Optional[str] = Query(None, description="User ID for personalized recommendations"),
    difficulty_level: Optional[str] = Query(None, description="Target difficulty level"),
    focus_area: Optional[str] = Query(None, description="Algorithm focus area"),
    limit: int = Query(10, description="Number of recommendations"),
    recommendation_engine: RecommendationEngine = Depends(get_recommendation_engine),
    db: Session = Depends(get_db)
):
    """Get ML-powered personalized recommendations"""
    try:
        if user_id:
            # Get personalized recommendations using ML
            focus_areas = [focus_area] if focus_area else None
            recommendations = recommendation_engine.get_personalized_recommendations(
                user_id=user_id,
                num_recommendations=limit,
                difficulty_preference=difficulty_level,
                focus_areas=focus_areas
            )
            
            return {
                "recommendations": recommendations,
                "type": "personalized",
                "user_id": user_id,
                "criteria": {
                    "difficulty_level": difficulty_level,
                    "focus_area": focus_area
                },
                "count": len(recommendations),
                "ml_powered": True
            }
        else:
            # Fallback to basic recommendations for anonymous users
            query = db.query(Problem)
            
            # Filter by difficulty
            if difficulty_level:
                query = query.filter(Problem.difficulty == difficulty_level)
            
            # Filter by focus area if specified
            if focus_area:
                query = query.filter(Problem.algorithm_tags.contains([focus_area]))
            
            # Order by relevance and quality
            problems = query.order_by(
                Problem.google_interview_relevance.desc(),
                Problem.quality_score.desc()
            ).limit(limit).all()
            
            recommendations = []
            for problem in problems:
                rec = problem.to_dict()
                rec['recommendation_score'] = 0.8  # Static score for basic recommendations
                rec['recommendation_reason'] = f"High-quality problem"
                if difficulty_level:
                    rec['recommendation_reason'] += f" at {difficulty_level} level"
                if focus_area:
                    rec['recommendation_reason'] += f" focusing on {focus_area}"
                recommendations.append(rec)
            
            return {
                "recommendations": recommendations,
                "type": "basic",
                "criteria": {
                    "difficulty_level": difficulty_level,
                    "focus_area": focus_area
                },
                "count": len(recommendations),
                "ml_powered": False
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@app.get("/recommendations/similar/{problem_id}")
async def get_similar_problems(
    problem_id: str,
    limit: int = Query(5, description="Number of similar problems"),
    recommendation_engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """Get problems similar to a specific problem using content-based filtering"""
    try:
        similar_problems = recommendation_engine.get_content_based_recommendations(
            problem_id=problem_id,
            num_recommendations=limit
        )
        
        return {
            "similar_problems": similar_problems,
            "reference_problem_id": problem_id,
            "count": len(similar_problems),
            "algorithm": "content_based_filtering"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar problems: {str(e)}")


@app.post("/ml/train")
async def train_ml_models(
    recommendation_engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """Train ML recommendation models with current data"""
    try:
        recommendation_engine.train_models()
        
        return {
            "status": "success",
            "message": "ML models trained successfully",
            "trained_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training ML models: {str(e)}")


# Note: Learning paths generation is handled by the learning_paths_router
# which provides the POST /learning-paths/generate endpoint with sophisticated ML features


@app.post("/interactions/track")
async def track_user_interaction(
    user_id: str = Query(..., description="User ID"),
    problem_id: str = Query(..., description="Problem ID"),
    action: str = Query(..., description="Action type (viewed, solved, attempted, bookmarked)"),
    time_spent: Optional[int] = Query(None, description="Time spent in seconds"),
    success: Optional[bool] = Query(None, description="Whether action was successful"),
    session_id: Optional[str] = Query(None, description="Session ID"),
    metadata: Optional[str] = Query(None, description="Additional metadata as JSON string"),
    behavior_tracker: UserBehaviorTracker = Depends(get_behavior_tracker)
):
    """Track user interaction for ML model improvement"""
    try:
        # Parse metadata if provided
        interaction_metadata = None
        if metadata:
            try:
                interaction_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        # Track the interaction based on action type
        if action == "viewed":
            behavior_tracker.track_problem_view(
                user_id=user_id,
                problem_id=problem_id,
                time_spent_seconds=time_spent,
                session_id=session_id,
                metadata=interaction_metadata
            )
        elif action in ["solved", "attempted"]:
            behavior_tracker.track_problem_attempt(
                user_id=user_id,
                problem_id=problem_id,
                success=success if success is not None else (action == "solved"),
                time_spent_seconds=time_spent or 0,
                session_id=session_id,
                metadata=interaction_metadata
            )
        elif action == "bookmarked":
            behavior_tracker.track_bookmark_action(
                user_id=user_id,
                problem_id=problem_id,
                action="bookmarked",
                session_id=session_id,
                metadata=interaction_metadata
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported action type: {action}")
        
        return {
            "status": "success",
            "message": f"Interaction tracked: {user_id} {action} {problem_id}",
            "tracked_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking interaction: {str(e)}")


@app.get("/analytics/user/{user_id}")
async def get_user_analytics(
    user_id: str,
    days_back: int = Query(30, description="Number of days to analyze"),
    behavior_tracker: UserBehaviorTracker = Depends(get_behavior_tracker)
):
    """Get comprehensive analytics for a specific user"""
    try:
        analytics = behavior_tracker.get_user_analytics(
            user_id=user_id,
            days_back=days_back
        )
        
        return {
            "user_analytics": analytics,
            "period_days": days_back,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating user analytics: {str(e)}")


@app.get("/analytics/trends")
async def get_platform_trends(
    days_back: int = Query(7, description="Number of days to analyze for trends"),
    behavior_tracker: UserBehaviorTracker = Depends(get_behavior_tracker)
):
    """Get trending problems and platform usage patterns"""
    try:
        trends = behavior_tracker.get_popular_trends(days_back=days_back)
        
        return {
            "trends": trends,
            "period_days": days_back,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating trend analysis: {str(e)}")


@app.get("/analytics/algorithm-tags")
async def get_algorithm_tag_analytics(db: Session = Depends(get_db)):
    """Get analytics for algorithm tags"""
    try:
        from collections import Counter
        
        # Get all algorithm tags
        problems = db.query(Problem.algorithm_tags, Problem.quality_score, Problem.google_interview_relevance).all()
        
        tag_stats = Counter()
        tag_quality = {}
        tag_relevance = {}
        
        for problem in problems:
            if problem.algorithm_tags:
                for tag in problem.algorithm_tags:
                    tag_stats[tag] += 1
                    
                    # Track quality and relevance
                    if tag not in tag_quality:
                        tag_quality[tag] = []
                        tag_relevance[tag] = []
                    
                    tag_quality[tag].append(problem.quality_score or 0)
                    tag_relevance[tag].append(problem.google_interview_relevance or 0)
        
        # Calculate averages
        analytics = []
        for tag, count in tag_stats.most_common():
            avg_quality = sum(tag_quality[tag]) / len(tag_quality[tag]) if tag_quality[tag] else 0
            avg_relevance = sum(tag_relevance[tag]) / len(tag_relevance[tag]) if tag_relevance[tag] else 0
            
            analytics.append({
                'tag': tag,
                'problem_count': count,
                'average_quality': round(avg_quality, 2),
                'average_google_relevance': round(avg_relevance, 2),
                'learning_priority': round((avg_quality + avg_relevance) / 2, 2)
            })
        
        return {
            "algorithm_tag_analytics": analytics,
            "total_unique_tags": len(tag_stats),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating tag analytics: {str(e)}")


@app.get("/analytics/platforms")
async def get_platform_analytics(db: Session = Depends(get_db)):
    """Get analytics by platform"""
    try:
        from sqlalchemy import func
        
        platform_stats = db.query(
            Problem.platform,
            func.count(Problem.id).label('problem_count'),
            func.avg(Problem.quality_score).label('avg_quality'),
            func.avg(Problem.google_interview_relevance).label('avg_relevance')
        ).group_by(Problem.platform).all()
        
        analytics = []
        for stat in platform_stats:
            analytics.append({
                'platform': stat.platform,
                'problem_count': stat.problem_count,
                'average_quality_score': round(stat.avg_quality or 0, 2),
                'average_google_relevance': round(stat.avg_relevance or 0, 2)
            })
        
        return {
            "platform_analytics": analytics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")


@app.get("/analytics/difficulty")
async def get_difficulty_analytics(db: Session = Depends(get_db)):
    """Get analytics by difficulty level"""
    try:
        from sqlalchemy import func
        
        difficulty_stats = db.query(
            Problem.difficulty,
            func.count(Problem.id).label('problem_count'),
            func.avg(Problem.quality_score).label('avg_quality'),
            func.avg(Problem.google_interview_relevance).label('avg_relevance')
        ).group_by(Problem.difficulty).all()
        
        analytics = []
        for stat in difficulty_stats:
            analytics.append({
                'difficulty': stat.difficulty,
                'problem_count': stat.problem_count,
                'average_quality_score': round(stat.avg_quality or 0, 2),
                'average_google_relevance': round(stat.avg_relevance or 0, 2)
            })
        
        return {
            "difficulty_analytics": analytics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")


@app.get("/search")
async def enhanced_search_problems(
    query: str = Query(..., description="Search query for problem titles, descriptions, and tags"),
    algorithm_tags: Optional[List[str]] = Query(None, description="Filter by algorithm tags"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (Easy, Medium, Hard)"),
    company: Optional[str] = Query(None, description="Filter by company"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    min_quality: Optional[float] = Query(None, description="Minimum quality score"),
    min_relevance: Optional[float] = Query(None, description="Minimum Google interview relevance"),
    limit: int = Query(20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Enhanced search with multiple filters and ranking"""
    try:
        from sqlalchemy import or_, and_, func
        
        # Start with base query
        base_query = db.query(Problem)
        
        # Text search across title, description, and tags
        search_conditions = []
        if query:
            search_conditions.extend([
                Problem.title.contains(query),
                Problem.description.contains(query),
                Problem.algorithm_tags.contains([query.lower()])
            ])
        
        if search_conditions:
            base_query = base_query.filter(or_(*search_conditions))
        
        # Apply filters
        if algorithm_tags:
            for tag in algorithm_tags:
                base_query = base_query.filter(Problem.algorithm_tags.contains([tag]))
                
        if difficulty:
            base_query = base_query.filter(Problem.difficulty == difficulty)
            
        if company:
            base_query = base_query.filter(Problem.companies.contains([company]))
            
        if platform:
            base_query = base_query.filter(Problem.platform == platform)
            
        if min_quality is not None:
            base_query = base_query.filter(Problem.quality_score >= min_quality)
            
        if min_relevance is not None:
            base_query = base_query.filter(Problem.google_interview_relevance >= min_relevance)
        
        # Order by relevance (quality score + Google relevance)
        problems = base_query.order_by(
            (Problem.quality_score + Problem.google_interview_relevance).desc()
        ).limit(limit).all()
        
        # Calculate search relevance scores
        results = []
        for problem in problems:
            relevance_score = 0.0
            
            # Title match bonus
            if query and query.lower() in problem.title.lower():
                relevance_score += 50.0
                
            # Tag match bonus
            if query and any(query.lower() in tag.lower() for tag in problem.algorithm_tags):
                relevance_score += 30.0
                
            # Company match bonus
            if company and problem.companies and company in problem.companies:
                relevance_score += 20.0
                
            # Quality and Google relevance
            relevance_score += (problem.quality_score + problem.google_interview_relevance) / 2
            
            result = problem.to_dict()
            result['search_relevance_score'] = round(relevance_score, 2)
            results.append(result)
        
        # Sort by search relevance
        results.sort(key=lambda x: x['search_relevance_score'], reverse=True)
        
        return {
            "query": query,
            "filters": {
                "algorithm_tags": algorithm_tags,
                "difficulty": difficulty,
                "company": company,
                "platform": platform,
                "min_quality": min_quality,
                "min_relevance": min_relevance
            },
            "results": results,
            "count": len(results),
            "search_suggestions": _generate_search_suggestions(query, results, db)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


def _generate_search_suggestions(query: str, results: List[Dict], db: Session) -> List[str]:
    """Generate search suggestions based on query and results"""
    suggestions = []
    
    if len(results) < 5:  # If few results, suggest alternatives
        # Get popular algorithm tags
        popular_tags = db.query(Problem.algorithm_tags).limit(100).all()
        all_tags = set()
        for tag_list in popular_tags:
            all_tags.update(tag_list[0] if tag_list[0] else [])
        
        # Find similar tags
        if query:
            similar_tags = [tag for tag in all_tags if query.lower() in tag.lower() and tag.lower() != query.lower()]
            suggestions.extend(similar_tags[:3])
        
        # Add popular search terms
        suggestions.extend(["dynamic_programming", "binary_search", "two_pointers", "graph", "tree"])
    
    return list(set(suggestions))[:5]  # Remove duplicates and limit


@app.get("/search/suggestions")
async def get_search_suggestions(
    partial: str = Query(..., description="Partial search query"),
    db: Session = Depends(get_db)
):
    """Get search suggestions as user types"""
    try:
        suggestions = []
        
        # Get algorithm tags that match
        problems = db.query(Problem.algorithm_tags).limit(200).all()
        all_tags = set()
        for tag_list in problems:
            all_tags.update(tag_list[0] if tag_list[0] else [])
        
        matching_tags = [tag for tag in all_tags if partial.lower() in tag.lower()]
        suggestions.extend(matching_tags[:5])
        
        # Get problem titles that match
        matching_problems = db.query(Problem.title).filter(
            Problem.title.contains(partial)
        ).limit(5).all()
        
        suggestions.extend([p.title for p in matching_problems])
        
        return {
            "suggestions": list(set(suggestions))[:10],
            "query": partial
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion error: {str(e)}")


@app.get("/search")
async def search_problems(
    query: str = Query(..., description="Search query for problem titles and descriptions"),
    limit: int = Query(20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Search problems by title and description"""
    try:
        # Simple text search (can be enhanced with full-text search)
        problems = db.query(Problem).filter(
            Problem.title.contains(query) | 
            Problem.description.contains(query)
        ).order_by(
            Problem.quality_score.desc()
        ).limit(limit).all()
        
        return {
            "query": query,
            "results": [problem.to_dict() for problem in problems],
            "count": len(problems)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching problems: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
