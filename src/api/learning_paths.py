"""
Learning Path API endpoints for DSATrain
Advanced learning path management and personalization
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from ..models.database import (
    DatabaseConfig, LearningPathTemplate, UserLearningPath, 
    LearningMilestone, UserSkillAssessment
)
from ..ml.learning_path_engine import LearningPathEngine, UserProfile
from ..ml.learning_path_templates import LearningPathTemplateManager

# Initialize router
router = APIRouter(prefix="/learning-paths", tags=["Learning Paths"])

# Database dependency
db_config = DatabaseConfig()

def get_db():
    """Get database session"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


# Pydantic models for API requests/responses
class UserProfileRequest(BaseModel):
    user_id: str
    current_skill_levels: Dict[str, float]
    learning_goals: List[str]
    available_hours_per_week: int
    preferred_difficulty_curve: str = "gradual"
    target_completion_weeks: Optional[int] = None
    weak_areas: Optional[List[str]] = None
    strong_areas: Optional[List[str]] = None


class PerformanceUpdateRequest(BaseModel):
    problem_id: str
    success: bool
    time_spent_seconds: int
    additional_metrics: Optional[Dict[str, Any]] = None


class SkillAssessmentRequest(BaseModel):
    user_id: str
    assessment_type: str = "comprehensive"
    specific_problems: Optional[List[str]] = None


@router.get("/templates")
async def get_learning_path_templates(
    category: Optional[str] = None,
    skill_level: Optional[str] = None,
    max_weeks: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get available learning path templates
    
    Args:
        category: Filter by category (interview_prep, skill_mastery, foundations)
        skill_level: Filter by target skill level (beginner, intermediate, advanced)
        max_weeks: Filter by maximum duration in weeks
    """
    try:
        query = db.query(LearningPathTemplate).filter(
            LearningPathTemplate.status == 'active'
        )
        
        if category:
            query = query.filter(LearningPathTemplate.category == category)
        
        if skill_level:
            query = query.filter(LearningPathTemplate.target_skill_level == skill_level)
        
        if max_weeks:
            query = query.filter(LearningPathTemplate.estimated_duration_weeks <= max_weeks)
        
        templates = query.all()
        
        return {
            "templates": [template.to_dict() for template in templates],
            "total_count": len(templates)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")


@router.get("/templates/recommendations")
async def get_template_recommendations(
    user_goals: List[str] = Query(...),
    available_weeks: int = Query(...),
    current_skill_level: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get personalized template recommendations based on user criteria
    """
    try:
        template_manager = LearningPathTemplateManager(db)
        recommendations = template_manager.get_template_recommendations(
            user_goals=user_goals,
            available_weeks=available_weeks,
            current_skill_level=current_skill_level
        )
        
        return {
            "recommendations": recommendations,
            "criteria": {
                "user_goals": user_goals,
                "available_weeks": available_weeks,
                "current_skill_level": current_skill_level
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.post("/generate")
async def generate_personalized_path(
    user_profile: UserProfileRequest,
    template_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Generate a personalized learning path for a user
    """
    try:
        # Convert request to UserProfile
        profile = UserProfile(
            user_id=user_profile.user_id,
            current_skill_levels=user_profile.current_skill_levels,
            learning_goals=user_profile.learning_goals,
            available_hours_per_week=user_profile.available_hours_per_week,
            preferred_difficulty_curve=user_profile.preferred_difficulty_curve,
            target_completion_weeks=user_profile.target_completion_weeks,
            weak_areas=user_profile.weak_areas,
            strong_areas=user_profile.strong_areas
        )
        
        # Generate path
        engine = LearningPathEngine(db)
        learning_path = engine.generate_personalized_path(profile, template_id)
        
        # Get learning path as dict
        path_dict = learning_path.to_dict()
        
        # Enrich weekly plan with full problem objects
        if 'weekly_plan' in path_dict and path_dict['weekly_plan']:
            for week_plan in path_dict['weekly_plan']:
                if 'problems' in week_plan:
                    # Convert problem IDs to full problem objects
                    problem_ids = week_plan['problems']
                    problems_data = []
                    focus_areas = set()
                    
                    for problem_id in problem_ids:
                        from ..models.database import Problem
                        problem = db.query(Problem).filter(Problem.id == problem_id).first()
                        if problem:
                            problem_dict = problem.to_dict()
                            problems_data.append(problem_dict)
                            
                            # Extract focus areas from algorithm tags
                            if problem.algorithm_tags:
                                focus_areas.update(problem.algorithm_tags[:2])
                        else:
                            # Fallback for missing problems
                            problems_data.append({
                                'id': problem_id,
                                'title': f'Problem {problem_id}',
                                'difficulty': 'Unknown',
                                'platform': 'Unknown',
                                'algorithm_tags': [],
                                'quality_score': 0
                            })
                    
                    # Update week plan with full problem objects and real focus areas
                    week_plan['problems'] = problems_data
                    if focus_areas:
                        week_plan['focus_areas'] = list(focus_areas)
        
        return {
            "learning_path": path_dict,
            "message": f"Generated personalized learning path with {len(learning_path.personalized_sequence)} problems"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating learning path: {str(e)}")


@router.get("/{path_id}")
async def get_learning_path(
    path_id: str,
    include_milestones: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific learning path
    """
    try:
        path = db.query(UserLearningPath).filter(UserLearningPath.id == path_id).first()
        if not path:
            raise HTTPException(status_code=404, detail=f"Learning path {path_id} not found")
        
        response = path.to_dict()
        
        if include_milestones:
            milestones = db.query(LearningMilestone).filter(
                LearningMilestone.learning_path_id == path_id
            ).all()
            response["milestones"] = [milestone.to_dict() for milestone in milestones]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching learning path: {str(e)}")


@router.get("/{path_id}/next-problems")
async def get_next_problems(
    path_id: str,
    count: int = Query(5, ge=1, le=20),
    include_context: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get the next problems in a learning path with learning context
    """
    try:
        engine = LearningPathEngine(db)
        problems = engine.get_next_problems(path_id, count, include_context)
        
        return {
            "problems": problems,
            "path_id": path_id,
            "requested_count": count,
            "returned_count": len(problems)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting next problems: {str(e)}")


@router.post("/{path_id}/progress")
async def update_path_progress(
    path_id: str,
    progress_update: PerformanceUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update learning path progress when a user completes a problem
    """
    try:
        engine = LearningPathEngine(db)
        progress_info = engine.update_path_progress(
            path_id=path_id,
            problem_id=progress_update.problem_id,
            success=progress_update.success,
            time_spent_seconds=progress_update.time_spent_seconds,
            additional_metrics=progress_update.additional_metrics
        )
        
        return {
            "progress_update": progress_info,
            "message": "Progress updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating progress: {str(e)}")


@router.post("/{path_id}/adapt")
async def adapt_learning_path(
    path_id: str,
    performance_data: Dict[str, Any],
    force_adaptation: bool = False,
    db: Session = Depends(get_db)
):
    """
    Adapt an existing learning path based on user performance
    """
    try:
        engine = LearningPathEngine(db)
        adaptation_result = engine.adapt_learning_path(
            path_id=path_id,
            performance_data=performance_data,
            force_adaptation=force_adaptation
        )
        
        return adaptation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adapting learning path: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_learning_paths(
    user_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all learning paths for a specific user
    """
    try:
        query = db.query(UserLearningPath).filter(UserLearningPath.user_id == user_id)
        
        if status:
            query = query.filter(UserLearningPath.status == status)
        
        paths = query.order_by(UserLearningPath.created_at.desc()).all()
        
        return {
            "user_id": user_id,
            "learning_paths": [path.to_dict() for path in paths],
            "total_count": len(paths)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user learning paths: {str(e)}")


@router.post("/assess-skills")
async def assess_user_skills(
    assessment_request: SkillAssessmentRequest,
    db: Session = Depends(get_db)
):
    """
    Assess user's current skill levels across different areas
    """
    try:
        engine = LearningPathEngine(db)
        skill_assessment = engine.assess_user_skills(
            user_id=assessment_request.user_id,
            assessment_problems=assessment_request.specific_problems,
            assessment_type=assessment_request.assessment_type
        )
        
        return {
            "user_id": assessment_request.user_id,
            "skill_assessment": skill_assessment,
            "assessment_type": assessment_request.assessment_type,
            "assessed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing user skills: {str(e)}")


@router.get("/{path_id}/milestones")
async def get_learning_milestones(
    path_id: str,
    include_completed: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get learning milestones for a specific learning path
    """
    try:
        query = db.query(LearningMilestone).filter(
            LearningMilestone.learning_path_id == path_id
        )
        
        if not include_completed:
            query = query.filter(LearningMilestone.is_completed == False)
        
        milestones = query.order_by(LearningMilestone.created_at).all()
        
        return {
            "path_id": path_id,
            "milestones": [milestone.to_dict() for milestone in milestones],
            "total_count": len(milestones),
            "completed_count": len([m for m in milestones if m.is_completed])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching milestones: {str(e)}")


@router.post("/{path_id}/milestones/{milestone_id}/complete")
async def complete_milestone(
    path_id: str,
    milestone_id: str,
    completion_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Mark a milestone as completed with assessment results
    """
    try:
        milestone = db.query(LearningMilestone).filter(
            LearningMilestone.id == milestone_id,
            LearningMilestone.learning_path_id == path_id
        ).first()
        
        if not milestone:
            raise HTTPException(status_code=404, detail="Milestone not found")
        
        # Update milestone
        milestone.is_completed = True
        milestone.completed_at = datetime.now()
        milestone.assessment_results = completion_data
        milestone.completion_score = completion_data.get('score', 100.0)
        milestone.attempts += 1
        
        db.commit()
        
        return {
            "milestone": milestone.to_dict(),
            "message": "Milestone completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error completing milestone: {str(e)}")


@router.get("/analytics/overview")
async def get_learning_paths_analytics(
    time_period: str = Query("month", regex="^(week|month|quarter|year)$"),
    db: Session = Depends(get_db)
):
    """
    Get analytics overview for learning paths system
    """
    try:
        # Basic statistics
        total_templates = db.query(LearningPathTemplate).filter(
            LearningPathTemplate.status == 'active'
        ).count()
        
        total_user_paths = db.query(UserLearningPath).count()
        active_paths = db.query(UserLearningPath).filter(
            UserLearningPath.status == 'active'
        ).count()
        
        completed_paths = db.query(UserLearningPath).filter(
            UserLearningPath.status == 'completed'
        ).count()
        
        total_milestones = db.query(LearningMilestone).count()
        completed_milestones = db.query(LearningMilestone).filter(
            LearningMilestone.is_completed == True
        ).count()
        
        # Calculate completion rate
        completion_rate = (completed_paths / total_user_paths * 100) if total_user_paths > 0 else 0
        milestone_completion_rate = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
        
        return {
            "overview": {
                "total_templates": total_templates,
                "total_user_paths": total_user_paths,
                "active_paths": active_paths,
                "completed_paths": completed_paths,
                "completion_rate": round(completion_rate, 2),
                "total_milestones": total_milestones,
                "completed_milestones": completed_milestones,
                "milestone_completion_rate": round(milestone_completion_rate, 2)
            },
            "time_period": time_period,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")


# Initialize templates endpoint (for system setup)
@router.post("/admin/initialize-templates")
async def initialize_learning_path_templates(
    db: Session = Depends(get_db)
):
    """
    Initialize predefined learning path templates (admin endpoint)
    """
    try:
        template_manager = LearningPathTemplateManager(db)
        templates = template_manager.create_all_templates()
        
        return {
            "message": f"Successfully initialized {len(templates)} learning path templates",
            "templates": [template.to_dict() for template in templates]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing templates: {str(e)}")
