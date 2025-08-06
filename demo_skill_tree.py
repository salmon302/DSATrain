"""
Comprehensive Skill Tree Demo
Shows the complete skill tree system in action
"""

from fastapi.testclient import TestClient
from fastapi import FastAPI
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.skill_tree_api import skill_tree_router

def create_demo_app():
    """Create demo FastAPI app with skill tree router"""
    app = FastAPI(title="Skill Tree Demo")
    app.include_router(skill_tree_router)
    return TestClient(app)

def demo_skill_tree_overview(client):
    """Demo the skill tree overview"""
    print("🎯 SKILL TREE OVERVIEW")
    print("=" * 60)
    
    response = client.get("/skill-tree/overview")
    if response.status_code == 200:
        data = response.json()
        
        print(f"📊 Total Skill Areas: {data['total_skill_areas']}")
        print(f"📚 Total Problems: {data['total_problems']}")
        print(f"🕐 Last Updated: {data['last_updated']}")
        print()
        
        print("🏗️  SKILL TREE COLUMNS:")
        for i, column in enumerate(data['skill_tree_columns'], 1):
            print(f"\n{i}. {column['skill_area'].replace('_', ' ').title()}")
            print(f"   📈 Total Problems: {column['total_problems']}")
            print(f"   🎯 Mastery: {column['mastery_percentage']:.1f}%")
            
            # Show problems by difficulty
            for difficulty in ['Easy', 'Medium', 'Hard']:
                problems = column['difficulty_levels'][difficulty]
                if problems:
                    print(f"   🔸 {difficulty}: {len(problems)} problems")
                    # Show first 2 problems as examples
                    for j, problem in enumerate(problems[:2]):
                        print(f"      • {problem['title']} (Sub-level: {problem['sub_difficulty_level']})")
    else:
        print(f"❌ Failed to get overview: {response.status_code}")

def demo_problem_clusters(client):
    """Demo problem clustering"""
    print("\n\n🔗 PROBLEM CLUSTERS")
    print("=" * 60)
    
    response = client.get("/skill-tree/clusters")
    if response.status_code == 200:
        clusters = response.json()
        
        print(f"📦 Total Clusters: {len(clusters)}")
        
        for i, cluster in enumerate(clusters, 1):
            print(f"\n{i}. {cluster['cluster_name']}")
            print(f"   🎯 Skill Area: {cluster['primary_skill_area']}")
            print(f"   📊 Difficulty: {cluster['difficulty_level']}")
            print(f"   👥 Size: {cluster['cluster_size']} problems")
            print(f"   ⭐ Quality: {cluster['avg_quality_score']:.1f}")
            print(f"   📋 Tags: {', '.join(cluster['algorithm_tags'][:5])}")
            print(f"   🎲 Representative: {', '.join(cluster['representative_problems'][:3])}")
    else:
        print(f"❌ Failed to get clusters: {response.status_code}")

def demo_similarity_engine(client):
    """Demo similarity detection"""
    print("\n\n🔍 SIMILARITY ENGINE")
    print("=" * 60)
    
    # Get a problem ID first
    overview = client.get("/skill-tree/overview")
    if overview.status_code == 200:
        data = overview.json()
        problem_id = None
        
        # Find first available problem
        for column in data['skill_tree_columns']:
            for difficulty in ['Easy', 'Medium', 'Hard']:
                if column['difficulty_levels'][difficulty]:
                    problem_id = column['difficulty_levels'][difficulty][0]['id']
                    problem_title = column['difficulty_levels'][difficulty][0]['title']
                    break
            if problem_id:
                break
        
        if problem_id:
            print(f"🎯 Finding problems similar to: '{problem_title}' ({problem_id})")
            
            response = client.get(f"/skill-tree/similar/{problem_id}")
            if response.status_code == 200:
                similar = response.json()
                
                print(f"🔍 Found {len(similar)} similar problems:")
                for i, sim in enumerate(similar, 1):
                    print(f"\n{i}. Problem ID: {sim['problem_id']}")
                    print(f"   🎯 Similarity Score: {sim['similarity_score']:.3f}")
                    print(f"   📊 Algorithm Similarity: {sim['algorithm_similarity']:.3f}")
                    print(f"   🧩 Pattern Similarity: {sim['pattern_similarity']:.3f}")
                    print(f"   📈 Difficulty Similarity: {sim['difficulty_similarity']:.3f}")
                    print(f"   💡 Explanation: {sim['explanation']}")
            else:
                print(f"❌ Failed to get similar problems: {response.status_code}")

def demo_user_interaction(client):
    """Demo user confidence tracking"""
    print("\n\n👤 USER INTERACTION DEMO")
    print("=" * 60)
    
    user_id = "demo_user_2025"
    
    # Get a problem to interact with
    overview = client.get("/skill-tree/overview")
    if overview.status_code == 200:
        data = overview.json()
        
        # Find first Easy problem
        for column in data['skill_tree_columns']:
            if column['difficulty_levels']['Easy']:
                problem = column['difficulty_levels']['Easy'][0]
                problem_id = problem['id']
                problem_title = problem['title']
                break
        
        print(f"🎯 Simulating user interaction with: '{problem_title}'")
        
        # Update confidence
        confidence_data = {
            "problem_id": problem_id,
            "confidence_level": 4,
            "solve_time_seconds": 900,
            "hints_used": 1
        }
        
        response = client.post(f"/skill-tree/confidence?user_id={user_id}", json=confidence_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            
            # Get user progress
            progress_response = client.get(f"/skill-tree/user/{user_id}/progress")
            if progress_response.status_code == 200:
                progress = progress_response.json()
                
                print(f"\n📈 USER PROGRESS SUMMARY:")
                print(f"   🎯 Total Problems Attempted: {progress['total_problems_attempted']}")
                print(f"   🏗️  Skill Areas Touched: {progress['skill_areas_touched']}")
                
                if progress['skill_progress']:
                    print(f"\n🎯 SKILL AREA PROGRESS:")
                    for skill_area, progress_data in progress['skill_progress'].items():
                        print(f"   📚 {skill_area.replace('_', ' ').title()}:")
                        print(f"      • Problems Attempted: {progress_data['problems_attempted']}")
                        print(f"      • Average Confidence: {progress_data['average_confidence']:.1f}/5")
                
                if progress['skill_mastery']:
                    print(f"\n🎖️  SKILL MASTERY:")
                    for skill_area, mastery_data in progress['skill_mastery'].items():
                        print(f"   🏆 {skill_area.replace('_', ' ').title()}:")
                        print(f"      • Mastery Level: {mastery_data['mastery_level']:.1f}%")
                        print(f"      • Problems Solved: {mastery_data['problems_solved']}")
        else:
            print(f"❌ Failed to update confidence: {response.status_code}")

def demo_user_preferences(client):
    """Demo user preferences"""
    print("\n\n⚙️  USER PREFERENCES DEMO")
    print("=" * 60)
    
    user_id = "demo_user_2025"
    
    # Set preferences
    preferences = {
        "preferred_view_mode": "columns",
        "show_confidence_overlay": True,
        "auto_expand_clusters": False,
        "highlight_prerequisites": True,
        "visible_skill_areas": ["array_processing", "string_algorithms", "dynamic_programming"]
    }
    
    response = client.post(f"/skill-tree/preferences/{user_id}", json=preferences)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        
        # Get preferences back
        get_response = client.get(f"/skill-tree/preferences/{user_id}")
        if get_response.status_code == 200:
            user_prefs = get_response.json()
            
            print(f"\n🎛️  USER PREFERENCES:")
            print(f"   🖼️  View Mode: {user_prefs['preferred_view_mode']}")
            print(f"   👁️  Show Confidence Overlay: {user_prefs['show_confidence_overlay']}")
            print(f"   📂 Auto Expand Clusters: {user_prefs['auto_expand_clusters']}")
            print(f"   🔍 Highlight Prerequisites: {user_prefs['highlight_prerequisites']}")
            print(f"   👀 Visible Skill Areas: {len(user_prefs['visible_skill_areas'])} selected")
            for area in user_prefs['visible_skill_areas']:
                print(f"      • {area.replace('_', ' ').title()}")

def main():
    """Run the complete skill tree demo"""
    print("🚀 DSA TRAIN SKILL TREE SYSTEM DEMO")
    print("🎯 Comprehensive Feature Showcase")
    print("=" * 80)
    
    # Create test client
    client = create_demo_app()
    
    # Run all demos
    demo_skill_tree_overview(client)
    demo_problem_clusters(client)
    demo_similarity_engine(client)
    demo_user_interaction(client)
    demo_user_preferences(client)
    
    print("\n\n🎉 DEMO COMPLETE!")
    print("=" * 80)
    print("💡 This demonstrates our full skill tree system:")
    print("   🏗️  Hierarchical skill organization")
    print("   📊 Enhanced difficulty analysis")  
    print("   🔗 Smart problem clustering")
    print("   🔍 Advanced similarity detection")
    print("   👤 User confidence tracking")
    print("   📈 Progress monitoring")
    print("   ⚙️  Personalized preferences")
    print("   🎯 Ready for frontend integration!")

if __name__ == "__main__":
    main()
