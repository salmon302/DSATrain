"""
Reading Materials API
Provides endpoints for accessing and managing educational content
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

import os
from ..models.database import DatabaseConfig
from ..models.reading_materials import (
    ReadingMaterial, UserReadingProgress, MaterialRecommendation, 
    ContentCollection, MaterialAnalytics
)

router = APIRouter(prefix="/reading-materials", tags=["reading-materials"])

# Local DB dependency (avoid importing get_db from main)
# IMPORTANT: Respect DSATRAIN_DATABASE_URL possibly set at runtime (e.g., in tests)
_db_cache: dict[str, DatabaseConfig] = {}

def _get_db_config_for_current_env() -> DatabaseConfig:
    url = (
        os.getenv("DSATRAIN_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or "sqlite:///./dsatrain_phase4.db"
    )
    cfg = _db_cache.get(url)
    if cfg is None:
        cfg = DatabaseConfig(url)
        _db_cache[url] = cfg
    return cfg

def get_db():
    cfg = _get_db_config_for_current_env()
    db = cfg.get_session()
    try:
        yield db
    finally:
        db.close()


# Pydantic models for API requests/responses
class MaterialSearchRequest(BaseModel):
    query: str
    content_types: Optional[List[str]] = None
    difficulty_levels: Optional[List[str]] = None
    concept_ids: Optional[List[str]] = None
    competency_ids: Optional[List[str]] = None
    target_personas: Optional[List[str]] = None
    max_read_time: Optional[int] = None


class ReadingProgressUpdate(BaseModel):
    progress_percentage: float
    reading_time_seconds: int
    sections_read: Optional[List[str]] = None
    notes: Optional[str] = None
    bookmarked_sections: Optional[List[str]] = None


class MaterialRating(BaseModel):
    user_rating: int  # 1-5
    difficulty_rating: Optional[int] = None
    usefulness_rating: Optional[int] = None
    feedback_text: Optional[str] = None
    would_recommend: Optional[bool] = None


@router.get("/search")
async def search_materials(
    query: str = Query(..., description="Search query"),
    content_type: Optional[str] = Query(None),
    difficulty_level: Optional[str] = Query(None),
    concept_ids: Optional[str] = Query(None, description="Comma-separated concept IDs"),
    user_id: Optional[str] = Query(None, description="User ID for personalization"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search reading materials with optional filtering and personalization
    """
    try:
        # Build base query
        query_obj = db.query(ReadingMaterial).filter(
            ReadingMaterial.status == 'published'
        )
        
        # Apply filters
        if content_type:
            query_obj = query_obj.filter(ReadingMaterial.content_type == content_type)
        
        if difficulty_level:
            query_obj = query_obj.filter(ReadingMaterial.difficulty_level == difficulty_level)
        
        if concept_ids:
            concept_list = concept_ids.split(',')
            # Filter materials that contain any of the specified concepts
            for concept_id in concept_list:
                query_obj = query_obj.filter(
                    ReadingMaterial.concept_ids.contains([concept_id])
                )
        
        # Text search in title, subtitle, and summary
        if query:
            search_term = f"%{query}%"
            query_obj = query_obj.filter(
                (ReadingMaterial.title.ilike(search_term)) |
                (ReadingMaterial.subtitle.ilike(search_term)) |
                (ReadingMaterial.summary.ilike(search_term))
            )
        
        # Order by relevance and quality
        query_obj = query_obj.order_by(
            ReadingMaterial.effectiveness_score.desc(),
            ReadingMaterial.user_ratings.desc(),
            ReadingMaterial.view_count.desc()
        )
        
        materials = query_obj.limit(limit).all()
        
        results = []
        for material in materials:
            material_dict = material.to_dict()
            
            # Add personalization if user_id provided
            if user_id:
                # Check if user has read this material
                progress = db.query(UserReadingProgress).filter(
                    UserReadingProgress.user_id == user_id,
                    UserReadingProgress.material_id == material.id
                ).first()
                
                if progress:
                    material_dict['user_progress'] = progress.to_dict()
                else:
                    material_dict['user_progress'] = None
            
            results.append(material_dict)
        
        return {
            "materials": results,
            "total_found": len(results),
            "query": query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/recommendations/{user_id}")
async def get_user_recommendations(
    user_id: str,
    context: Optional[str] = Query(None, description="Context: pre_problem, post_problem, milestone, general"),
    problem_id: Optional[str] = Query(None, description="Related problem ID"),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get personalized reading material recommendations for a user
    """
    try:
        # Get active recommendations for user
        recommendations = db.query(MaterialRecommendation).filter(
            MaterialRecommendation.user_id == user_id,
            MaterialRecommendation.user_dismissed == False
        ).order_by(
            MaterialRecommendation.priority_level.desc(),
            MaterialRecommendation.recommendation_score.desc()
        ).limit(limit).all()
        
        # If context specified, filter by recommendation type
        if context:
            recommendations = [r for r in recommendations if r.recommendation_type == context]
        
        results = []
        for rec in recommendations:
            material = db.query(ReadingMaterial).filter(
                ReadingMaterial.id == rec.material_id
            ).first()
            
            if material:
                material_dict = material.to_dict()
                material_dict['recommendation'] = {
                    'type': rec.recommendation_type,
                    'reason': rec.recommendation_reason,
                    'score': rec.recommendation_score,
                    'priority': rec.priority_level,
                    'recommended_at': rec.recommended_at.isoformat()
                }
                results.append(material_dict)
        
        return {
            "recommendations": results,
            "user_id": user_id,
            "context": context
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@router.get("/material/{material_id}")
async def get_material(
    material_id: str,
    user_id: Optional[str] = Query(None),
    include_content: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Get a specific reading material with optional user context
    """
    try:
        material = db.query(ReadingMaterial).filter(
            ReadingMaterial.id == material_id,
            ReadingMaterial.status == 'published'
        ).first()
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        material_dict = material.to_dict(include_content=include_content)
        
        # Add user-specific data if user_id provided
        if user_id:
            progress = db.query(UserReadingProgress).filter(
                UserReadingProgress.user_id == user_id,
                UserReadingProgress.material_id == material_id
            ).first()
            
            if progress:
                material_dict['user_progress'] = progress.to_dict()
            else:
                material_dict['user_progress'] = None
            
            # Record view if this is a new view
            if not progress or progress.last_accessed < datetime.now():
                # Update view count and last accessed time
                material.view_count += 1
                if progress:
                    progress.last_accessed = datetime.now()
                db.commit()
        
        return material_dict
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving material: {str(e)}")


@router.post("/material/{material_id}/progress")
async def update_reading_progress(
    material_id: str,
    user_id: str,
    progress_update: ReadingProgressUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user's reading progress for a material
    """
    try:
        # Check if material exists
        material = db.query(ReadingMaterial).filter(
            ReadingMaterial.id == material_id
        ).first()
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        # Get or create progress record
        progress = db.query(UserReadingProgress).filter(
            UserReadingProgress.user_id == user_id,
            UserReadingProgress.material_id == material_id
        ).first()
        
        if not progress:
            progress = UserReadingProgress(
                user_id=user_id,
                material_id=material_id,
                started_at=datetime.now()
            )
            db.add(progress)
        
        # Update progress
        progress.progress_percentage = progress_update.progress_percentage
        progress.reading_time_seconds = progress_update.reading_time_seconds
        progress.last_accessed = datetime.now()
        
        if progress_update.sections_read:
            progress.sections_read = progress_update.sections_read
        
        if progress_update.notes:
            progress.notes = progress_update.notes
        
        if progress_update.bookmarked_sections:
            progress.bookmarked_sections = progress_update.bookmarked_sections
        
        # Mark as completed if 100% progress
        if progress_update.progress_percentage >= 100.0 and not progress.completed_at:
            progress.completed_at = datetime.now()
            material.completion_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "progress": progress.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating progress: {str(e)}")


@router.post("/material/{material_id}/rating")
async def rate_material(
    material_id: str,
    user_id: str,
    rating: MaterialRating,
    db: Session = Depends(get_db)
):
    """
    Submit user rating and feedback for a material
    """
    try:
        # Check if material exists
        material = db.query(ReadingMaterial).filter(
            ReadingMaterial.id == material_id
        ).first()
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        # Get or create progress record
        progress = db.query(UserReadingProgress).filter(
            UserReadingProgress.user_id == user_id,
            UserReadingProgress.material_id == material_id
        ).first()
        
        if not progress:
            progress = UserReadingProgress(
                user_id=user_id,
                material_id=material_id,
                started_at=datetime.now()
            )
            db.add(progress)
        
        # Update rating information
        old_rating = progress.user_rating
        progress.user_rating = rating.user_rating
        progress.difficulty_rating = rating.difficulty_rating
        progress.usefulness_rating = rating.usefulness_rating
        progress.feedback_text = rating.feedback_text
        progress.would_recommend = rating.would_recommend
        
        # Update material aggregate ratings
        if old_rating is None:
            # New rating
            material.total_ratings += 1
            total_score = (material.user_ratings * (material.total_ratings - 1)) + rating.user_rating
            material.user_ratings = total_score / material.total_ratings
        else:
            # Updated rating
            total_score = (material.user_ratings * material.total_ratings) - old_rating + rating.user_rating
            material.user_ratings = total_score / material.total_ratings
        
        db.commit()
        
        return {
            "success": True,
            "material_rating": material.user_ratings,
            "total_ratings": material.total_ratings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting rating: {str(e)}")


@router.get("/collections")
async def get_content_collections(
    collection_type: Optional[str] = Query(None),
    difficulty_level: Optional[str] = Query(None),
    target_persona: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get curated content collections
    """
    try:
        query_obj = db.query(ContentCollection).filter(
            ContentCollection.status == 'active'
        )
        
        if collection_type:
            query_obj = query_obj.filter(ContentCollection.collection_type == collection_type)
        
        if difficulty_level:
            query_obj = query_obj.filter(ContentCollection.difficulty_level == difficulty_level)
        
        if target_persona:
            query_obj = query_obj.filter(
                ContentCollection.target_personas.contains([target_persona])
            )
        
        collections = query_obj.order_by(
            ContentCollection.effectiveness_score.desc(),
            ContentCollection.user_ratings.desc()
        ).limit(limit).all()
        
        return {
            "collections": [collection.to_dict() for collection in collections]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving collections: {str(e)}")


@router.get("/collection/{collection_id}")
async def get_collection_materials(
    collection_id: str,
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get materials in a specific collection with user progress
    """
    try:
        collection = db.query(ContentCollection).filter(
            ContentCollection.id == collection_id
        ).first()
        
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        # Get materials in order
        materials = []
        for material_id in collection.material_ids:
            material = db.query(ReadingMaterial).filter(
                ReadingMaterial.id == material_id,
                ReadingMaterial.status == 'published'
            ).first()
            
            if material:
                material_dict = material.to_dict()
                
                # Add user progress if user_id provided
                if user_id:
                    progress = db.query(UserReadingProgress).filter(
                        UserReadingProgress.user_id == user_id,
                        UserReadingProgress.material_id == material_id
                    ).first()
                    
                    material_dict['user_progress'] = progress.to_dict() if progress else None
                
                materials.append(material_dict)
        
        collection_dict = collection.to_dict()
        collection_dict['materials'] = materials
        
        return collection_dict
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving collection: {str(e)}")


@router.get("/analytics/{material_id}")
async def get_material_analytics(
    material_id: str,
    period: str = Query("last_30_days", description="Analytics period"),
    db: Session = Depends(get_db)
):
    """
    Get analytics for a specific material (admin/author access)
    """
    try:
        material = db.query(ReadingMaterial).filter(
            ReadingMaterial.id == material_id
        ).first()
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        # Get latest analytics for the period
        analytics = db.query(MaterialAnalytics).filter(
            MaterialAnalytics.material_id == material_id,
            MaterialAnalytics.period_type == period.split('_')[-1]  # daily/weekly/monthly
        ).order_by(MaterialAnalytics.period_start.desc()).first()
        
        if not analytics:
            return {
                "material_id": material_id,
                "analytics": None,
                "message": "No analytics data available for this period"
            }
        
        return {
            "material_id": material_id,
            "period": period,
            "analytics": {
                "unique_viewers": analytics.unique_viewers,
                "total_views": analytics.total_views,
                "completion_count": analytics.completion_count,
                "completion_rate": analytics.completion_count / analytics.total_views if analytics.total_views > 0 else 0,
                "average_reading_time": analytics.average_reading_time,
                "average_rating": analytics.average_rating,
                "average_difficulty_rating": analytics.average_difficulty_rating,
                "average_usefulness_rating": analytics.average_usefulness_rating,
                "recommendation_rate": analytics.recommendation_rate,
                "problem_solving_improvement": analytics.problem_solving_improvement,
                "device_breakdown": analytics.device_breakdown,
                "persona_engagement": analytics.persona_engagement
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")


@router.post("/recommendation/{recommendation_id}/dismiss")
async def dismiss_recommendation(
    recommendation_id: int,
    reason: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Dismiss a material recommendation
    """
    try:
        recommendation = db.query(MaterialRecommendation).filter(
            MaterialRecommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        recommendation.user_dismissed = True
        recommendation.dismissal_reason = reason
        
        db.commit()
        
        return {"success": True, "message": "Recommendation dismissed"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error dismissing recommendation: {str(e)}")
