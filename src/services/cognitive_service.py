"""
CognitiveService: Manage cognitive profile, assessments, and adaptation recommendations.
"""
from __future__ import annotations

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from src.models.database import UserCognitiveProfile


class CognitiveService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user_id: str = "default_user") -> Dict[str, Any]:
        profile = self.db.query(UserCognitiveProfile).filter(UserCognitiveProfile.user_id == user_id).first()
        if not profile:
            profile = UserCognitiveProfile(user_id=user_id)
            self.db.add(profile)
            self.db.commit()
        return {
            "user_id": profile.user_id,
            "working_memory_capacity": profile.working_memory_capacity,
            "learning_style_preference": profile.learning_style_preference,
            "visual_vs_verbal": profile.visual_vs_verbal,
            "processing_speed": profile.processing_speed,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }

    def assess(self, data: Dict[str, Any], user_id: str = "default_user") -> Dict[str, Any]:
        """
        Heuristic assessment combining optional signals:
        - working_memory_quiz (0..10) -> working_memory_capacity (1..10)
        - style_preference (visual|verbal|balanced) and numeric visual_vs_verbal (0..1)
        - processing_speed_hint (slow|average|fast)
        """
        profile = self.db.query(UserCognitiveProfile).filter(UserCognitiveProfile.user_id == user_id).first()
        if not profile:
            profile = UserCognitiveProfile(user_id=user_id)
            self.db.add(profile)

        quiz = data.get("working_memory_quiz")
        if quiz is not None:
            try:
                quiz_val = float(quiz)
            except Exception:
                quiz_val = 5.0
            quiz_val = max(0.0, min(10.0, quiz_val))
            profile.working_memory_capacity = int(round(quiz_val))

        style = data.get("style_preference")
        if style in {"visual", "verbal", "balanced"}:
            profile.learning_style_preference = style

        vvv = data.get("visual_vs_verbal")
        if vvv is not None:
            try:
                vvv_val = float(vvv)
            except Exception:
                vvv_val = 0.5
            profile.visual_vs_verbal = max(0.0, min(1.0, vvv_val))

        speed = data.get("processing_speed_hint")
        if speed in {"slow", "average", "fast"}:
            profile.processing_speed = speed

        profile.updated_at = datetime.now()
        self.db.commit()
        return self.get_profile(user_id)

    def get_adaptation(self, user_id: str = "default_user") -> Dict[str, Any]:
        profile = self.db.query(UserCognitiveProfile).filter(UserCognitiveProfile.user_id == user_id).first()
        if not profile:
            return {
                "recommendations": [
                    "Take a brief working memory and learning style assessment to personalize your practice."
                ]
            }

        recs: List[str] = []
        if profile.learning_style_preference == "visual" or (profile.visual_vs_verbal or 0) >= 0.7:
            recs.append("Prefer diagrams, step-through visuals, and tracing tables.")
        elif profile.learning_style_preference == "verbal" or (profile.visual_vs_verbal or 0) <= 0.3:
            recs.append("Prefer verbal walkthroughs and written explanations.")
        else:
            recs.append("Use balanced visual + verbal explanations.")

        wmc = profile.working_memory_capacity or 5
        if wmc <= 4:
            recs.append("Use chunking scaffolds: break down DP states/recurrence/base cases explicitly.")
            recs.append("Reduce simultaneous constraints; solve a simpler variant first.")
        elif wmc >= 8:
            recs.append("Increase challenge: opt for interleaved sessions and hard problems.")

        speed = (profile.processing_speed or "average")
        if speed == "slow":
            recs.append("Extend timeboxes slightly; focus on correctness before optimization.")
        elif speed == "fast":
            recs.append("Tighten timeboxes and emphasize optimization and edge cases.")

        return {
            "user_id": profile.user_id,
            "recommendations": recs,
        }
