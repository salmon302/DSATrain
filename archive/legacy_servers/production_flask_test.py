#!/usr/bin/env python3
"""
Production-style Flask server to test deployment issue.
"""

import logging
from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

@app.route('/health')
def health():
    logger.info("🏥 Health check requested")
    return jsonify({"status": "healthy", "server": "production-style"})

@app.route('/skill-tree/overview')
def skill_tree_overview():
    """Test endpoint that mimics the skill tree data structure"""
    logger.info("🌳 Skill tree overview requested")
    
    # Return simple test data without database access
    test_data = {
        "skill_tree_columns": [
            {
                "skill_area": "array_processing",
                "total_problems": 50,
                "difficulty_levels": {
                    "Easy": [
                        {
                            "id": 1,
                            "title": "Two Sum",
                            "difficulty": "Easy",
                            "sub_difficulty_level": 1,
                            "conceptual_difficulty": 30,
                            "implementation_complexity": 20,
                            "algorithm_tags": ["array", "hash_table"],
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
        "total_problems": 50,
        "total_skill_areas": 1,
        "user_id": None,
        "last_updated": "2025-07-31T22:30:00Z"
    }
    
    logger.info("✅ Returning test skill tree data")
    return jsonify(test_data)

if __name__ == '__main__':
    logger.info("🚀 Starting Production-Style Flask Server...")
    logger.info("❤️ Health: http://localhost:8005/health")
    logger.info("🌳 Skill Tree: http://localhost:8005/skill-tree/overview")
    
    try:
        # Production-style configuration
        app.run(
            host='127.0.0.1', 
            port=8005, 
            debug=False,           # No debug mode
            use_reloader=False,    # No auto-reloader
            threaded=True          # Enable threading
        )
    except Exception as e:
        logger.error(f"❌ Server failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
