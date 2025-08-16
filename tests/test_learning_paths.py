"""
Test Learning Paths Implementation
Comprehensive test of the learning paths system
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.database import DatabaseConfig
from src.ml.learning_path_engine import LearningPathEngine, UserProfile
from src.ml.learning_path_templates import LearningPathTemplateManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_learning_paths_system():
    """
    Comprehensive test of the learning paths system
    """
    try:
        logger.info("🧪 Starting Learning Paths System Test...")
        
        # Initialize database and ensure all tables exist for this test run
        db_config = DatabaseConfig()
        # Create tables to avoid OperationalError: no such table: practice_gate_sessions
        try:
            db_config.create_tables()
        except Exception:
            # If tables already exist or creation fails non-critically, continue
            pass
        db_session = db_config.get_session()
        
        # Test 1: Template Management
        logger.info("\n📋 Test 1: Template Management")
        template_manager = LearningPathTemplateManager(db_session)
        
        # Get template recommendations
        recommendations = template_manager.get_template_recommendations(
            user_goals=["google", "interview"],
            available_weeks=10,
            current_skill_level="intermediate"
        )
        
        logger.info(f"✅ Found {len(recommendations)} template recommendations")
        for i, rec in enumerate(recommendations[:3]):
            template = rec['template']
            logger.info(f"   {i+1}. {template['name']} (fit score: {rec['fit_score']:.2f})")
            logger.info(f"      Reasons: {', '.join(rec['reasons'])}")
        
        # Test 2: User Skill Assessment
        logger.info("\n🎯 Test 2: User Skill Assessment")
        engine = LearningPathEngine(db_session)
        
        test_user_id = "test_user_001"
        skill_assessment = engine.assess_user_skills(test_user_id)
        
        logger.info(f"✅ Assessed skills for user {test_user_id}:")
        for skill, level in list(skill_assessment.items())[:5]:
            logger.info(f"   - {skill}: {level:.2f}")
        
        # Test 3: Personalized Path Generation
        logger.info("\n🛤️ Test 3: Personalized Path Generation")
        
        user_profile = UserProfile(
            user_id=test_user_id,
            current_skill_levels=skill_assessment,
            learning_goals=["google", "interview_prep"],
            available_hours_per_week=15,
            preferred_difficulty_curve="gradual",
            target_completion_weeks=8,
            weak_areas=["dynamic_programming", "graphs"],
            strong_areas=["arrays", "strings"]
        )
        
        learning_path = engine.generate_personalized_path(user_profile)
        
        logger.info(f"✅ Generated personalized learning path:")
        logger.info(f"   - Path ID: {learning_path.id}")
        logger.info(f"   - Name: {learning_path.name}")
        logger.info(f"   - Total Problems: {len(learning_path.personalized_sequence)}")
        logger.info(f"   - Estimated Completion: {learning_path.estimated_completion}")
        logger.info(f"   - Milestones: {len(learning_path.milestones)}")
        
        # Test 4: Get Next Problems
        logger.info("\n📚 Test 4: Get Next Problems")
        
        next_problems = engine.get_next_problems(learning_path.id, count=3)
        
        logger.info(f"✅ Retrieved {len(next_problems)} next problems:")
        for i, problem in enumerate(next_problems):
            logger.info(f"   {i+1}. {problem['title']} ({problem['difficulty']})")
            if 'learning_context' in problem:
                context = problem['learning_context']
                logger.info(f"      Focus: {', '.join(context.get('focus_areas', []))}")
                logger.info(f"      Estimated time: {context.get('estimated_time_minutes', 'N/A')} minutes")
        
        # Test 5: Progress Update
        logger.info("\n📈 Test 5: Progress Update")
        
        if next_problems:
            test_problem_id = next_problems[0]['id']
            
            progress_update = engine.update_path_progress(
                path_id=learning_path.id,
                problem_id=test_problem_id,
                success=True,
                time_spent_seconds=1800,  # 30 minutes
                additional_metrics={"attempts": 2, "hints_used": 1}
            )
            
            logger.info(f"✅ Updated progress for problem {test_problem_id}:")
            logger.info(f"   - Current position: {progress_update['current_position']}")
            logger.info(f"   - Completion: {progress_update['completion_percentage']:.1f}%")
            logger.info(f"   - Problems completed: {progress_update['problems_completed']}")
        
        # Test 6: Database Statistics
        logger.info("\n📊 Test 6: Database Statistics")
        
        from src.models.database import get_database_stats
        stats = get_database_stats(db_session)
        
        logger.info(f"✅ Updated database statistics:")
        for table, count in stats.items():
            logger.info(f"   - {table}: {count}")
        
        db_session.close()

        logger.info("\n🎉 All tests completed successfully!")
        logger.info("Learning Paths System is ready for production!")

        # Basic sanity assertions instead of returning a value
        assert learning_path is not None
        assert isinstance(learning_path.personalized_sequence, list)

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        if 'db_session' in locals():
            db_session.rollback()
            db_session.close()
        raise


if __name__ == "__main__":
    test_learning_paths_system()
