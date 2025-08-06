"""
Database Migration for Learning Paths Feature
Adds new tables for advanced learning path functionality
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy.orm import Session
from src.models.database import DatabaseConfig, Base
from src.ml.learning_path_templates import LearningPathTemplateManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database():
    """
    Migrate database to include learning paths tables and initialize templates
    """
    try:
        logger.info("🔄 Starting learning paths database migration...")
        
        # Initialize database config
        db_config = DatabaseConfig()
        
        # Create all new tables
        logger.info("📊 Creating new database tables...")
        Base.metadata.create_all(bind=db_config.engine)
        logger.info("✅ Database tables created successfully")
        
        # Initialize learning path templates
        logger.info("📝 Initializing learning path templates...")
        db_session = db_config.get_session()
        
        template_manager = LearningPathTemplateManager(db_session)
        templates = template_manager.create_all_templates()
        
        logger.info(f"✅ Created {len(templates)} learning path templates:")
        for template in templates:
            logger.info(f"   - {template.name} ({template.category}, {template.estimated_duration_weeks} weeks)")
        
        db_session.close()
        
        # Verify migration
        logger.info("🔍 Verifying migration...")
        db_session = db_config.get_session()
        
        from src.models.database import (
            LearningPathTemplate, UserLearningPath, 
            LearningMilestone, UserSkillAssessment
        )
        
        template_count = db_session.query(LearningPathTemplate).count()
        logger.info(f"✅ Verification complete: {template_count} templates in database")
        
        db_session.close()
        
        logger.info("🚀 Learning paths migration completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    migrate_database()
