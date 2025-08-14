"""
🧪 Production API Test
Test the skill tree API with the enhanced database
"""

from fastapi.testclient import TestClient
from src.api.skill_tree_api import router
from fastapi import FastAPI
import json

# Create test app
app = FastAPI()
app.include_router(router)

# Create test client
client = TestClient(app)

def test_skill_tree_overview():
    """Test skill tree overview endpoint"""
    print("🧪 Testing skill tree overview...")
    
    response = client.get("/skill-tree/overview")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Overview API successful!")
        print(f"📊 Total problems: {data.get('total_problems', 0)}")
        print(f"🌳 Skill areas: {data.get('total_skill_areas', 0)}")
        
        # Show skill tree columns
        columns = data.get('skill_tree_columns', [])
        print(f"\n🎯 Skill Tree Structure:")
        for col in columns[:5]:  # Show first 5
            print(f"  {col['skill_area']}: {col['total_problems']} problems")
            for difficulty, problems in col['difficulty_levels'].items():
                if problems:
                    print(f"    {difficulty}: {len(problems)} problems")
        
        return True
    else:
        print(f"❌ Overview API failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def test_clusters():
    """Test problem clusters endpoint"""
    print("\n🧪 Testing problem clusters...")
    
    response = client.get("/skill-tree/clusters")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Clusters API successful!")
        print(f"🎯 Found {len(data)} clusters")
        
        for cluster in data[:3]:  # Show first 3
            print(f"  {cluster['cluster_name']}: {cluster['cluster_size']} problems")
        
        return True
    else:
        print(f"❌ Clusters API failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def main():
    print("🚀 Production API Test Suite")
    print("=" * 50)
    
    # Test overview
    overview_success = test_skill_tree_overview()
    
    # Test clusters
    clusters_success = test_clusters()
    
    print("\n📊 Test Results:")
    print(f"  Overview API: {'✅' if overview_success else '❌'}")
    print(f"  Clusters API: {'✅' if clusters_success else '❌'}")
    
    if overview_success and clusters_success:
        print("\n🎉 All tests passed! API is ready for production.")
    else:
        print("\n⚠️ Some tests failed. Check the API configuration.")

if __name__ == "__main__":
    main()
