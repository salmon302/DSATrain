#!/usr/bin/env python3
"""
Test learning path generation directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    print("Testing learning path generation directly...")
    
    from src.models.database import DatabaseConfig
    from src.ml.learning_path_engine import LearningPathEngine, UserProfile
    
    # Create database session
    db_config = DatabaseConfig()
    db_session = db_config.get_session()
    
    # Create learning path engine
    engine = LearningPathEngine(db_session)
    
    # Create user profile
    user_profile = UserProfile(
        user_id='test_user_direct',
        current_skill_levels={
            'arrays': 0.3,
            'strings': 0.2,
            'hash_tables': 0.1,
            'trees': 0.1,
            'dynamic_programming': 0.1
        },
        learning_goals=['google_interview'],
        available_hours_per_week=10,
        preferred_difficulty_curve='gradual',
        target_completion_weeks=8,
        weak_areas=['dynamic_programming', 'trees'],
        strong_areas=['arrays']
    )
    
    print("User profile created, generating learning path...")
    
    # Generate learning path
    learning_path = engine.generate_personalized_path(user_profile)
    
    print(f"✅ Learning path generated successfully!")
    print(f"   - ID: {learning_path.id}")
    print(f"   - Name: {learning_path.name}")
    print(f"   - Problems: {len(learning_path.personalized_sequence)}")
    print(f"   - Status: {learning_path.status}")
    
    # Convert to dict for API response
    path_dict = learning_path.to_dict()
    print(f"   - API Response keys: {list(path_dict.keys())}")
    
    db_session.close()
    print("✅ Direct test passed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
