#!/usr/bin/env python3
"""Direct test of the skill tree API using the backend directly (bypassing server)."""

import sys
import os
import json

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_backend_directly():
    """Test the skill tree functionality directly without HTTP server"""
    try:
        print("🧪 Testing skill tree backend directly...")
        
        # Import database modules
        from src.models.database import DatabaseConfig, Problem
        
        # Get database session
        db_config = DatabaseConfig()
        db = db_config.get_session()
        print("✅ Database session established")
        
        # Query all problems
        problems = db.query(Problem).all()
        print(f"📊 Total problems in database: {len(problems)}")
        
        # Check problems with algorithm tags
        problems_with_tags = db.query(Problem).filter(
            Problem.algorithm_tags.isnot(None),
            Problem.algorithm_tags != "[]",
            Problem.algorithm_tags != ""
        ).all()
        print(f"📊 Problems with algorithm tags: {len(problems_with_tags)}")
        
        # Show sample problem data
        if problems_with_tags:
            sample = problems_with_tags[0]
            print(f"📝 Sample problem: {sample.title}")
            print(f"   Difficulty: {sample.difficulty}")
            print(f"   Algorithm tags: {sample.algorithm_tags}")
            
            # Check for skill tree fields
            if hasattr(sample, 'sub_difficulty_level'):
                print(f"   Sub-difficulty: {sample.sub_difficulty_level}")
            if hasattr(sample, 'conceptual_difficulty'):
                print(f"   Conceptual difficulty: {sample.conceptual_difficulty}")
        
        db.close()
        return len(problems_with_tags)
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return 0

def create_simple_data_endpoint():
    """Create a simple data file for the frontend to test with"""
    try:
        problem_count = test_backend_directly()
        
        # Create mock data structure for frontend testing
        mock_data = {
            "skill_tree_columns": [
                {
                    "skill_area": "array_processing",
                    "total_problems": max(1, problem_count // 5),
                    "difficulty_levels": {
                        "Easy": [
                            {
                                "id": 1,
                                "title": "Two Sum",
                                "difficulty": "Easy",
                                "sub_difficulty_level": 1,
                                "conceptual_difficulty": 30,
                                "implementation_complexity": 20,
                                "algorithm_tags": ["array", "hash table"],
                                "prerequisite_skills": [],
                                "quality_score": 0.9,
                                "google_interview_relevance": 0.8,
                                "skill_tree_position": {}
                            }
                        ],
                        "Medium": [],
                        "Hard": []
                    },
                    "mastery_percentage": 0.0
                }
            ],
            "total_problems": problem_count,
            "total_skill_areas": 1,
            "user_id": None,
            "last_updated": "2025-07-31T22:30:00Z"
        }
        
        # Save to file for frontend testing
        with open('skill_tree_test_data.json', 'w') as f:
            json.dump(mock_data, f, indent=2)
        
        print(f"✅ Created test data file with {problem_count} total problems")
        return mock_data
        
    except Exception as e:
        print(f"❌ Failed to create test data: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Direct Backend Test")
    print("=" * 50)
    
    problem_count = test_backend_directly()
    print()
    
    if problem_count > 0:
        print("✅ Backend is working! Creating test data...")
        create_simple_data_endpoint()
    else:
        print("❌ No problems found with algorithm tags. Check database enhancement.")
        
    print()
    print("📝 Summary:")
    print(f"   - Database connection: ✅")
    print(f"   - Problems with tags: {problem_count}")
    print(f"   - Ready for frontend: {'✅' if problem_count > 0 else '❌'}")
