"""
Test script for the Skill Tree API endpoints
Validates the new skill tree functionality
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8001"

def print_response(response, title: str):
    """Print formatted response"""
    print(f"\n{'='*60}")
    print(f"🔸 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")
    print(f"{'='*60}")

def test_skill_tree_api():
    """Test all skill tree API endpoints"""
    
    print("🚀 Testing DSATrain Skill Tree API")
    print(f"Target: {BASE_URL}")
    
    # 1. Test root endpoint
    print("\n1️⃣  Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print_response(response, "Root Endpoint")
    except Exception as e:
        print(f"❌ Error connecting to {BASE_URL}: {e}")
        return
    
    # 2. Test skill tree overview
    print("\n2️⃣  Testing skill tree overview...")
    try:
        response = requests.get(f"{BASE_URL}/skill-tree/overview")
        print_response(response, "Skill Tree Overview")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Skill Tree Summary:")
            print(f"   • Total Skill Areas: {data.get('total_skill_areas', 0)}")
            print(f"   • Total Problems: {data.get('total_problems', 0)}")
            if 'skill_tree_columns' in data:
                for col in data['skill_tree_columns'][:3]:  # Show first 3
                    print(f"   • {col['skill_area']}: {col['total_problems']} problems")
    except Exception as e:
        print(f"❌ Error testing skill tree overview: {e}")
    
    # 3. Test problem clusters
    print("\n3️⃣  Testing problem clusters...")
    try:
        response = requests.get(f"{BASE_URL}/skill-tree/clusters")
        print_response(response, "Problem Clusters")
        
        if response.status_code == 200:
            clusters = response.json()
            print(f"\n🔗 Clusters Summary:")
            print(f"   • Total Clusters: {len(clusters)}")
            for cluster in clusters[:2]:  # Show first 2
                print(f"   • {cluster['cluster_name']}: {cluster['cluster_size']} problems")
    except Exception as e:
        print(f"❌ Error testing clusters: {e}")
    
    # 4. Test similar problems (need a valid problem ID first)
    print("\n4️⃣  Testing similar problems...")
    try:
        # First get a problem ID from the overview
        overview_response = requests.get(f"{BASE_URL}/skill-tree/overview")
        if overview_response.status_code == 200:
            data = overview_response.json()
            problem_id = None
            
            # Find a problem ID from the skill tree
            for column in data.get('skill_tree_columns', []):
                for difficulty in ['Easy', 'Medium', 'Hard']:
                    if column['difficulty_levels'][difficulty]:
                        problem_id = column['difficulty_levels'][difficulty][0]['id']
                        break
                if problem_id:
                    break
            
            if problem_id:
                print(f"   Using problem ID: {problem_id}")
                response = requests.get(f"{BASE_URL}/skill-tree/similar/{problem_id}")
                print_response(response, f"Similar Problems for {problem_id}")
                
                if response.status_code == 200:
                    similar = response.json()
                    print(f"\n🎯 Similar Problems Summary:")
                    print(f"   • Found {len(similar)} similar problems")
                    for sim in similar[:2]:  # Show first 2
                        print(f"   • {sim['problem_id']}: {sim['similarity_score']:.2f} similarity")
            else:
                print("   ⚠️  No problem ID found to test similarity")
        
    except Exception as e:
        print(f"❌ Error testing similar problems: {e}")
    
    # 5. Test user confidence update
    print("\n5️⃣  Testing user confidence update...")
    try:
        # Use same problem ID from above
        overview_response = requests.get(f"{BASE_URL}/skill-tree/overview")
        if overview_response.status_code == 200:
            data = overview_response.json()
            problem_id = None
            
            for column in data.get('skill_tree_columns', []):
                for difficulty in ['Easy', 'Medium', 'Hard']:
                    if column['difficulty_levels'][difficulty]:
                        problem_id = column['difficulty_levels'][difficulty][0]['id']
                        break
                if problem_id:
                    break
            
            if problem_id:
                confidence_data = {
                    "problem_id": problem_id,
                    "confidence_level": 4,
                    "solve_time_seconds": 1200,
                    "hints_used": 1
                }
                
                response = requests.post(
                    f"{BASE_URL}/skill-tree/confidence?user_id=test_user_123",
                    json=confidence_data
                )
                print_response(response, "Update User Confidence")
    except Exception as e:
        print(f"❌ Error testing confidence update: {e}")
    
    # 6. Test user progress
    print("\n6️⃣  Testing user progress...")
    try:
        response = requests.get(f"{BASE_URL}/skill-tree/user/test_user_123/progress")
        print_response(response, "User Progress")
        
        if response.status_code == 200:
            progress = response.json()
            print(f"\n📈 User Progress Summary:")
            print(f"   • Total Problems Attempted: {progress.get('total_problems_attempted', 0)}")
            print(f"   • Skill Areas Touched: {progress.get('skill_areas_touched', 0)}")
    except Exception as e:
        print(f"❌ Error testing user progress: {e}")
    
    # 7. Test user preferences
    print("\n7️⃣  Testing user preferences...")
    try:
        # Get preferences
        response = requests.get(f"{BASE_URL}/skill-tree/preferences/test_user_123")
        print_response(response, "Get User Preferences")
        
        # Update preferences
        preferences_data = {
            "preferred_view_mode": "columns",
            "show_confidence_overlay": True,
            "auto_expand_clusters": False,
            "highlight_prerequisites": True,
            "visible_skill_areas": ["array_processing", "dynamic_programming"]
        }
        
        response = requests.post(
            f"{BASE_URL}/skill-tree/preferences/test_user_123",
            json=preferences_data
        )
        print_response(response, "Update User Preferences")
        
    except Exception as e:
        print(f"❌ Error testing user preferences: {e}")
    
    # 8. Test with filters
    print("\n8️⃣  Testing filtered clusters...")
    try:
        # Test with skill area filter
        response = requests.get(f"{BASE_URL}/skill-tree/clusters?skill_area=array_processing")
        print_response(response, "Filtered Clusters (Array Processing)")
        
        # Test with difficulty filter
        response = requests.get(f"{BASE_URL}/skill-tree/clusters?difficulty=Easy")
        print_response(response, "Filtered Clusters (Easy)")
        
    except Exception as e:
        print(f"❌ Error testing filtered clusters: {e}")
    
    print("\n✅ Skill Tree API Testing Complete!")
    print("🎯 All endpoints have been tested.")
    print("📋 Check the responses above for any issues.")

if __name__ == "__main__":
    test_skill_tree_api()
