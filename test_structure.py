#!/usr/bin/env python3
"""
Test the learning path structure matches frontend expectations
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    print("Testing learning path structure...")
    
    from src.models.database import DatabaseConfig
    from src.ml.learning_path_engine import LearningPathEngine, UserProfile
    
    # Create database session
    db_config = DatabaseConfig()
    db_session = db_config.get_session()
    
    # Create learning path engine
    engine = LearningPathEngine(db_session)
    
    # Create user profile
    user_profile = UserProfile(
        user_id='test_structure',
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
    
    # Generate learning path
    learning_path = engine.generate_personalized_path(user_profile)
    
    # Convert to dict for API response
    path_dict = learning_path.to_dict()
    
    print(f"✅ Learning path generated!")
    print(f"Structure check:")
    
    # Check required fields
    required_fields = [
        'id', 'user_id', 'target_goal', 'current_level', 'duration_weeks', 
        'total_problems', 'weekly_plan', 'estimated_completion_time', 'created_at'
    ]
    
    for field in required_fields:
        if field in path_dict:
            print(f"  ✅ {field}: {type(path_dict[field])}")
        else:
            print(f"  ❌ {field}: MISSING")
    
    # Check estimated_completion_time structure
    if 'estimated_completion_time' in path_dict:
        ect = path_dict['estimated_completion_time']
        print(f"\nEstimated completion time structure:")
        for key in ['total_hours', 'hours_per_week', 'easy_problems', 'medium_problems', 'hard_problems']:
            if key in ect:
                print(f"  ✅ {key}: {ect[key]}")
            else:
                print(f"  ❌ {key}: MISSING")
    
    # Print sample of the structure
    print(f"\nSample data:")
    print(f"  Goal: {path_dict.get('target_goal')}")
    print(f"  Level: {path_dict.get('current_level')}")
    print(f"  Duration: {path_dict.get('duration_weeks')} weeks")
    print(f"  Total Problems: {path_dict.get('total_problems')}")
    print(f"  Weekly Plans: {len(path_dict.get('weekly_plan', []))}")
    
    ect = path_dict.get('estimated_completion_time', {})
    print(f"  Total Hours: {ect.get('total_hours')}")
    print(f"  Hours/Week: {ect.get('hours_per_week')}")
    
    db_session.close()
    print("\n✅ Structure test completed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
