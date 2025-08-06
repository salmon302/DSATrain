"""
Simple test to verify skill tree API functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import DatabaseConfig, Problem

def test_skill_tree_data():
    """Test if we have skill tree data in the database"""
    
    print("🔍 Testing Skill Tree Data...")
    
    # Connect to database
    db_config = DatabaseConfig("sqlite:///dsatrain_skilltree.db")
    db = db_config.get_session()
    
    try:
        # Check for problems with skill tree data
        problems_with_subtree = db.query(Problem).filter(
            Problem.sub_difficulty_level.isnot(None)
        ).all()
        
        print(f"📊 Found {len(problems_with_subtree)} problems with skill tree data")
        
        if problems_with_subtree:
            print("\n🎯 Sample Problems:")
            for i, problem in enumerate(problems_with_subtree[:3]):
                print(f"   {i+1}. {problem.title}")
                print(f"      • ID: {problem.id}")
                print(f"      • Difficulty: {problem.difficulty}")
                print(f"      • Sub-level: {problem.sub_difficulty_level}")
                print(f"      • Algorithm Tags: {problem.algorithm_tags}")
                print()
                
            return True
        else:
            print("❌ No problems with skill tree data found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing data: {e}")
        return False
    finally:
        db.close()

def test_skill_tree_router_direct():
    """Test skill tree router directly without server"""
    
    print("\n🧪 Testing Skill Tree Router Directly...")
    
    try:
        from src.api.skill_tree_api import skill_tree_router, get_db
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        # Create test app
        app = FastAPI()
        app.include_router(skill_tree_router)
        
        client = TestClient(app)
        
        # Test overview endpoint
        response = client.get("/skill-tree/overview")
        print(f"📈 Overview endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   • Total skill areas: {data.get('total_skill_areas', 0)}")
            print(f"   • Total problems: {data.get('total_problems', 0)}")
            
            # Test clusters endpoint
            response = client.get("/skill-tree/clusters")
            print(f"🔗 Clusters endpoint status: {response.status_code}")
            
            if response.status_code == 200:
                clusters = response.json()
                print(f"   • Found {len(clusters)} clusters")
                
            return True
        else:
            print(f"❌ Overview endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing router: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DSATrain Skill Tree Testing")
    print("=" * 50)
    
    # Test 1: Data availability
    data_ok = test_skill_tree_data()
    
    if data_ok:
        # Test 2: Router functionality  
        router_ok = test_skill_tree_router_direct()
        
        if router_ok:
            print("\n✅ All tests passed!")
            print("🎯 Skill Tree API is ready!")
        else:
            print("\n⚠️  Router tests failed")
    else:
        print("\n⚠️  No skill tree data available")
        print("💡 Run the enhanced analyzers first to populate data")
    
    print("=" * 50)
