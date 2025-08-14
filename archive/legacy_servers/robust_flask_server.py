#!/usr/bin/env python3
"""
Robust Flask server for DSA skill tree visualization.
Provides API endpoints for frontend integration.
"""

import json
import logging
import sys
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

def determine_primary_skill_area(algorithm_tags):
    """Determine primary skill area from algorithm tags"""
    if not algorithm_tags:
        return "general"
    
    tags_str = str(algorithm_tags).lower()
    
    # Define skill area mappings
    skill_mappings = {
        "array_processing": ["array", "prefix sum", "sliding window", "two pointers"],
        "string_algorithms": ["string", "palindrome", "substring", "kmp", "pattern"],
        "mathematical": ["math", "number theory", "probability", "combinatorics", "geometry"],
        "sorting_searching": ["sorting", "binary search", "search", "quicksort", "mergesort"],
        "tree_algorithms": ["tree", "binary tree", "bst", "heap", "trie"],
        "dynamic_programming": ["dp", "dynamic programming", "memoization", "knapsack"],
        "graph_algorithms": ["graph", "dfs", "bfs", "shortest path", "topological"],
        "advanced_structures": ["segment tree", "fenwick", "union find", "disjoint set"]
    }
    
    for skill_area, keywords in skill_mappings.items():
        if any(keyword in tags_str for keyword in keywords):
            return skill_area
    
    return "general"

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "DSA Skill Tree API",
        "version": "1.0.0"
    })

@app.route('/skill-tree/overview')
def skill_tree_overview():
    """Get complete skill tree overview with problems organized by skill areas"""
    try:
        logger.info("🔍 Processing skill tree overview request...")
        
        # Import database modules
        try:
            from src.models.database import DatabaseConfig, Problem
        except ImportError as e:
            logger.error(f"❌ Failed to import database modules: {e}")
            return jsonify({
                "error": "Database modules not available",
                "total_problems": 0,
                "total_skill_areas": 0,
                "skill_tree_columns": []
            })
        
        # Get database session
        try:
            db_config = DatabaseConfig()
            db = db_config.get_session()
            logger.info("✅ Database session established")
        except Exception as e:
            logger.error(f"❌ Failed to get database session: {e}")
            return jsonify({
                "error": "Database connection failed",
                "total_problems": 0,
                "total_skill_areas": 0,
                "skill_tree_columns": []
            })
        
        # Query all problems with enhanced skill tree data
        try:
            problems = db.query(Problem).filter(
                Problem.algorithm_tags.isnot(None),
                Problem.algorithm_tags != "[]",
                Problem.algorithm_tags != ""
            ).all()
            
            logger.info(f"📊 Found {len(problems)} problems with algorithm tags")
        except Exception as e:
            logger.error(f"❌ Failed to query problems: {e}")
            db.close()
            return jsonify({
                "error": "Failed to query problems",
                "total_problems": 0,
                "total_skill_areas": 0,
                "skill_tree_columns": []
            })
        
        # Organize by skill areas
        skill_areas = {}
        
        for problem in problems:
            if not problem.algorithm_tags:
                continue
                
            # Determine primary skill area
            primary_skill = determine_primary_skill_area(problem.algorithm_tags)
            
            if primary_skill not in skill_areas:
                skill_areas[primary_skill] = {
                    "Easy": [], "Medium": [], "Hard": []
                }
            
            # Add to appropriate difficulty level with safe attribute access
            problem_info = {
                "id": problem.id,
                "title": problem.title,
                "difficulty": problem.difficulty,
                "sub_difficulty_level": getattr(problem, 'sub_difficulty_level', 1) or 1,
                "conceptual_difficulty": getattr(problem, 'conceptual_difficulty', 50) or 50,
                "implementation_complexity": getattr(problem, 'implementation_complexity', 50) or 50,
                "algorithm_tags": problem.algorithm_tags or [],
                "prerequisite_skills": [],  # Simplified for now
                "quality_score": getattr(problem, 'quality_score', 0.0) or 0.0,
                "google_interview_relevance": getattr(problem, 'google_interview_relevance', 0.0) or 0.0,
                "skill_tree_position": {}  # Simplified for now
            }
            
            # Handle prerequisite_skills safely
            try:
                if hasattr(problem, 'prerequisite_skills') and problem.prerequisite_skills:
                    problem_info["prerequisite_skills"] = json.loads(problem.prerequisite_skills)
            except:
                problem_info["prerequisite_skills"] = []
            
            # Handle skill_tree_position safely
            try:
                if hasattr(problem, 'skill_tree_position') and problem.skill_tree_position:
                    problem_info["skill_tree_position"] = json.loads(problem.skill_tree_position)
            except:
                problem_info["skill_tree_position"] = {}
            
            skill_areas[primary_skill][problem.difficulty].append(problem_info)
        
        # Create skill tree columns
        columns = []
        for skill_area, difficulties in skill_areas.items():
            # Calculate total problems
            total_problems = sum(len(probs) for probs in difficulties.values())
            
            # Sort problems by sub-difficulty within each level
            for difficulty in difficulties:
                difficulties[difficulty].sort(key=lambda p: p['sub_difficulty_level'])
            
            column = {
                "skill_area": skill_area,
                "total_problems": total_problems,
                "difficulty_levels": difficulties,
                "mastery_percentage": 0.0
            }
            
            columns.append(column)
        
        # Sort columns by complexity
        skill_complexity_order = {
            "array_processing": 1, "string_algorithms": 2, "mathematical": 3,
            "sorting_searching": 4, "tree_algorithms": 5, "dynamic_programming": 6,
            "graph_algorithms": 7, "advanced_structures": 8, "general": 9
        }
        
        columns.sort(key=lambda c: skill_complexity_order.get(c['skill_area'], 99))
        
        db.close()
        
        result = {
            "skill_tree_columns": columns,
            "total_problems": len(problems),
            "total_skill_areas": len(skill_areas),
            "user_id": request.args.get('user_id'),
            "last_updated": "2025-07-31T22:30:00Z"
        }
        
        logger.info(f"✅ Returning {len(columns)} skill areas with {len(problems)} total problems")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in skill tree overview: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Internal server error",
            "total_problems": 0,
            "total_skill_areas": 0,
            "skill_tree_columns": []
        })

@app.route('/skill-tree/user/<user_id>/progress')
def user_progress(user_id):
    """Get user progress (mock data for now)"""
    return jsonify({
        "user_id": user_id,
        "skill_progress": {},
        "skill_mastery": {},
        "total_problems_attempted": 0,
        "skill_areas_touched": 0
    })

@app.route('/skill-tree/similar/<problem_id>')
def similar_problems(problem_id):
    """Get similar problems (mock data for now)"""
    return jsonify([])

@app.route('/skill-tree/confidence', methods=['POST'])
def update_confidence():
    """Update user confidence"""
    return jsonify({"status": "success", "message": "Confidence updated"})

if __name__ == '__main__':
    logger.info("🚀 Starting Robust Flask Skill Tree Server...")
    logger.info("🌳 Skill tree endpoint: http://localhost:8003/skill-tree/overview")
    logger.info("❤️ Health check: http://localhost:8003/health")
    
    try:
        app.run(host='127.0.0.1', port=8003, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        raise
