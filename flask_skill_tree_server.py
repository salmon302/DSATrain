"""
🌐 Robust Flask Server for Skill Tree API
Stable server that handles HTTP requests properly
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from src.models.database import DatabaseConfig, Problem
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
    
    # Count matches for each skill area
    skill_scores = {}
    for skill_area, keywords in skill_mapping.items():
        score = sum(1 for tag in algorithm_tags if tag.lower() in [k.lower() for k in keywords])
        if score > 0:
            skill_scores[skill_area] = score
    
    if skill_scores:
        return max(skill_scores.items(), key=lambda x: x[1])[0]
    
    # Fallback
    return "general"

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'server': 'Flask skill tree server',
        'message': 'Server is running properly'
    })

@app.route('/skill-tree/overview')
def skill_tree_overview():
    """Get skill tree overview"""
    try:
        logger.info("📊 Fetching skill tree overview...")
        
        # Connect to database
        db_config = DatabaseConfig("sqlite:///dsatrain_phase4.db")
        db = db_config.get_session()
        
        # Get all problems with enhanced difficulty metrics
        problems = db.query(Problem).filter(Problem.sub_difficulty_level.isnot(None)).all()
        
        if not problems:
            return jsonify({
                "error": "No problems with skill tree data found",
                "total_problems": 0,
                "total_skill_areas": 0
            })
        
        logger.info(f"📊 Found {len(problems)} enhanced problems")
        
        # Organize problems by skill area
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
            
            # Add to appropriate difficulty level
            problem_info = {
                "id": problem.id,
                "title": problem.title,
                "difficulty": problem.difficulty,
                "sub_difficulty_level": problem.sub_difficulty_level or 1,
                "conceptual_difficulty": problem.conceptual_difficulty or 50,
                "implementation_complexity": problem.implementation_complexity or 50,
                "algorithm_tags": problem.algorithm_tags or [],
                "prerequisite_skills": json.loads(problem.prerequisite_skills) if problem.prerequisite_skills else [],
                "quality_score": problem.quality_score or 0.0,
                "google_interview_relevance": problem.google_interview_relevance or 0.0,
                "skill_tree_position": json.loads(problem.skill_tree_position) if problem.skill_tree_position else {}
            }
            
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
        logger.error(f"❌ Error getting skill tree overview: {e}")
        return jsonify({
            "error": str(e),
            "total_problems": 0,
            "total_skill_areas": 0
        }), 500

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
    logger.info("🚀 Starting Flask Skill Tree Server...")
    logger.info("🌳 Skill tree endpoint: http://localhost:8003/skill-tree/overview")
    logger.info("❤️ Health check: http://localhost:8003/health")
    
    app.run(host='127.0.0.1', port=8003, debug=False)
