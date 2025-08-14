#!/usr/bin/env python3
"""
Simple test to check database and imports
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    print("Testing imports...")
    
    # Test basic imports
    from src.models.database import DatabaseConfig
    print("✅ DatabaseConfig imported")
    
    from src.ml.learning_path_engine import LearningPathEngine
    print("✅ LearningPathEngine imported")
    
    from src.ml.learning_path_templates import LearningPathTemplateManager
    print("✅ LearningPathTemplateManager imported")
    
    # Test database connection
    print("\nTesting database connection...")
    db_config = DatabaseConfig()
    db_session = db_config.get_session()
    print("✅ Database session created")
    
    # Test tables exist
    from src.models.database import LearningPathTemplate, UserLearningPath
    template_count = db_session.query(LearningPathTemplate).count()
    print(f"✅ Found {template_count} learning path templates")
    
    if template_count == 0:
        print("⚠️  No templates found - need to initialize")
        template_manager = LearningPathTemplateManager(db_session)
        templates = template_manager.create_all_templates()
        print(f"✅ Created {len(templates)} templates")
    
    db_session.close()
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
