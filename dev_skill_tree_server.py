"""
Development Skill Tree Data Server
Serves skill tree data for frontend development
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.skill_tree_api import get_db
from src.models.database import Problem, ProblemCluster, UserProblemConfidence

app = FastAPI(title="Development Skill Tree Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-generate data
def get_skill_tree_data():
    """Get skill tree data and cache it"""
    try:
        db = next(get_db())
        
        # Get all problems with skill tree data
        problems = db.query(Problem).filter(Problem.sub_difficulty_level.isnot(None)).all()
        
        # Organize by skill area
        skill_areas = {}
        for problem in problems:
            if not problem.algorithm_tags:
                continue
                
            # Determine primary skill area
            primary_skill = determine_primary_skill_area(problem.algorithm_tags)
            
            if primary_skill not in skill_areas:
                skill_areas[primary_skill] = {"Easy": [], "Medium": [], "Hard": []}
            
            problem_data = {
                "id": problem.id,
                "title": problem.title,
                "difficulty": problem.difficulty,
                "sub_difficulty_level": problem.sub_difficulty_level or 1,
                "conceptual_difficulty": problem.conceptual_difficulty or 50,
                "implementation_complexity": problem.implementation_complexity or 50,
                "algorithm_tags": problem.algorithm_tags or [],
                "prerequisite_skills": problem.prerequisite_skills or [],
                "quality_score": problem.quality_score or 0.0,
                "google_interview_relevance": problem.google_interview_relevance or 0.0,
                "skill_tree_position": problem.skill_tree_position or {}
            }
            
            skill_areas[primary_skill][problem.difficulty].append(problem_data)
        
        # Create columns
        columns = []
        for skill_area, difficulties in skill_areas.items():
            total_problems = sum(len(probs) for probs in difficulties.values())
            
            # Sort problems by sub-difficulty
            for difficulty in difficulties:
                difficulties[difficulty].sort(key=lambda p: p["sub_difficulty_level"])
            
            column = {
                "skill_area": skill_area,
                "total_problems": total_problems,
                "difficulty_levels": difficulties,
                "mastery_percentage": 0.0
            }
            columns.append(column)
        
        # Sort columns
        skill_order = {
            "array_processing": 1, "string_algorithms": 2, "mathematical": 3,
            "sorting_searching": 4, "tree_algorithms": 5, "dynamic_programming": 6,
            "graph_algorithms": 7, "advanced_structures": 8
        }
        columns.sort(key=lambda c: skill_order.get(c["skill_area"], 99))
        
        db.close()
        
        return {
            "skill_tree_columns": columns,
            "total_problems": len(problems),
            "total_skill_areas": len(skill_areas),
            "user_id": None,
            "last_updated": "2025-07-31T10:00:00Z"
        }
        
    except Exception as e:
        print(f"Error getting skill tree data: {e}")
        return {"skill_tree_columns": [], "total_problems": 0, "total_skill_areas": 0}

def determine_primary_skill_area(algorithm_tags):
    """Determine primary skill area from algorithm tags"""
    skill_mapping = {
        "array_processing": ["arrays", "two_pointers", "sliding_window", "prefix_sum"],
        "string_algorithms": ["strings", "kmp", "rabin_karp", "manacher"],
        "tree_algorithms": ["trees", "binary_tree", "bst", "dfs", "bfs"],
        "graph_algorithms": ["graphs", "dijkstra", "floyd_warshall", "topological_sort"],
        "dynamic_programming": ["dynamic_programming", "dp", "memoization"],
        "sorting_searching": ["sorting", "binary_search", "quicksort", "mergesort"],
        "mathematical": ["math", "number_theory", "combinatorics", "geometry"],
        "advanced_structures": ["segment_tree", "fenwick_tree", "union_find", "trie"]
    }
    
    skill_scores = {}
    for skill_area, keywords in skill_mapping.items():
        score = sum(1 for tag in algorithm_tags if tag.lower() in [k.lower() for k in keywords])
        if score > 0:
            skill_scores[skill_area] = score
    
    if skill_scores:
        return max(skill_scores.items(), key=lambda x: x[1])[0]
    return "general"

# Cache the data
SKILL_TREE_DATA = get_skill_tree_data()

@app.get("/")
async def root():
    return {"message": "Development Skill Tree Server", "status": "active"}

@app.get("/skill-tree/overview")
async def get_skill_tree_overview():
    return SKILL_TREE_DATA

@app.get("/skill-tree/clusters")
async def get_clusters():
    return [
        {
            "id": "cluster_1",
            "cluster_name": "Array Processing - Easy",
            "primary_skill_area": "array_processing",
            "difficulty_level": "Easy",
            "representative_problems": ["easy_array_1", "easy_array_2"],
            "cluster_size": 2,
            "avg_quality_score": 80.0,
            "similarity_threshold": 0.7,
            "algorithm_tags": ["arrays", "two_pointers", "hash_table"]
        }
    ]

@app.get("/skill-tree/similar/{problem_id}")
async def get_similar_problems(problem_id: str):
    return [
        {
            "problem_id": "easy_array_2",
            "similarity_score": 0.668,
            "explanation": "Moderately similar problems with shared algorithms",
            "algorithm_similarity": 0.667,
            "pattern_similarity": 0.500,
            "difficulty_similarity": 1.000
        }
    ]

@app.post("/skill-tree/confidence")
async def update_confidence():
    return {"status": "success", "message": "Confidence updated (demo mode)"}

@app.get("/skill-tree/user/{user_id}/progress")
async def get_user_progress(user_id: str):
    return {
        "user_id": user_id,
        "skill_progress": {
            "array_processing": {
                "problems_attempted": 1,
                "average_confidence": 4.0,
                "confidence_levels": {}
            }
        },
        "skill_mastery": {},
        "total_problems_attempted": 1,
        "skill_areas_touched": 1
    }

@app.get("/skill-tree/preferences/{user_id}")
async def get_preferences(user_id: str):
    return {
        "preferred_view_mode": "columns",
        "show_confidence_overlay": True,
        "auto_expand_clusters": False,
        "highlight_prerequisites": True,
        "visible_skill_areas": []
    }

@app.post("/skill-tree/preferences/{user_id}")
async def update_preferences(user_id: str):
    return {"status": "success", "message": "Preferences updated"}

if __name__ == "__main__":
    import uvicorn
    print("🌳 Starting Development Skill Tree Server...")
    print(f"📊 Loaded {SKILL_TREE_DATA['total_problems']} problems in {SKILL_TREE_DATA['total_skill_areas']} skill areas")
    uvicorn.run(app, host="127.0.0.1", port=8002)
