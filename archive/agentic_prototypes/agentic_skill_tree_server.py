#!/usr/bin/env python3
"""
Persistent Flask server optimized for agentic development.
Features auto-restart, health monitoring, and VS Code integration.
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('skill_tree_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Global variables for server management
SERVER_PORT = 8007
SERVER_HOST = '127.0.0.1'
HEALTH_CHECK_INTERVAL = 30
server_start_time = time.time()

def determine_primary_skill_area(algorithm_tags):
    """Determine primary skill area from algorithm tags"""
    if not algorithm_tags:
        return "general"
    
    tags_str = str(algorithm_tags).lower()
    
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
    """Health check with server status"""
    uptime = time.time() - server_start_time
    return jsonify({
        "status": "healthy",
        "service": "DSA Skill Tree API",
        "version": "1.0.0",
        "uptime_seconds": round(uptime, 2),
        "port": SERVER_PORT,
        "agentic_ready": True
    })

@app.route('/skill-tree/overview')
def skill_tree_overview():
    """Get complete skill tree overview with robust error handling"""
    try:
        logger.info("🔍 Processing skill tree overview request...")
        
        # Import with fallback
        try:
            from src.models.database import DatabaseConfig, Problem
            use_database = True
        except ImportError as e:
            logger.warning(f"Database import failed, using cached data: {e}")
            use_database = False
        
        if use_database:
            try:
                # Get database session
                db_config = DatabaseConfig()
                db = db_config.get_session()
                
                # Query problems with enhanced data
                problems = db.query(Problem).filter(
                    Problem.algorithm_tags.isnot(None),
                    Problem.algorithm_tags != "[]",
                    Problem.algorithm_tags != ""
                ).all()
                
                logger.info(f"📊 Found {len(problems)} problems with algorithm tags")
                
                # Organize by skill areas
                skill_areas = {}
                
                for problem in problems:
                    if not problem.algorithm_tags:
                        continue
                        
                    primary_skill = determine_primary_skill_area(problem.algorithm_tags)
                    
                    if primary_skill not in skill_areas:
                        skill_areas[primary_skill] = {"Easy": [], "Medium": [], "Hard": []}
                    
                    problem_info = {
                        "id": problem.id,
                        "title": problem.title,
                        "difficulty": problem.difficulty,
                        "sub_difficulty_level": getattr(problem, 'sub_difficulty_level', 1) or 1,
                        "conceptual_difficulty": getattr(problem, 'conceptual_difficulty', 50) or 50,
                        "implementation_complexity": getattr(problem, 'implementation_complexity', 50) or 50,
                        "algorithm_tags": problem.algorithm_tags or [],
                        "prerequisite_skills": [],
                        "quality_score": getattr(problem, 'quality_score', 0.0) or 0.0,
                        "google_interview_relevance": getattr(problem, 'google_interview_relevance', 0.0) or 0.0,
                        "skill_tree_position": {}
                    }
                    
                    skill_areas[primary_skill][problem.difficulty].append(problem_info)
                
                # Create skill tree columns
                columns = []
                for skill_area, difficulties in skill_areas.items():
                    total_problems = sum(len(probs) for probs in difficulties.values())
                    
                    for difficulty in difficulties:
                        difficulties[difficulty].sort(key=lambda p: p['sub_difficulty_level'])
                    
                    columns.append({
                        "skill_area": skill_area,
                        "total_problems": total_problems,
                        "difficulty_levels": difficulties,
                        "mastery_percentage": 0.0
                    })
                
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
                    "last_updated": "2025-07-31T22:30:00Z",
                    "data_source": "database"
                }
                
                logger.info(f"✅ Returning {len(columns)} skill areas with {len(problems)} total problems")
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"❌ Database error: {e}")
                use_database = False
        
        # Fallback to cached data
        if not use_database:
            cache_file = project_root / "skill_tree_test_data.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                cached_data["data_source"] = "cached_file"
                logger.info("✅ Returning cached skill tree data")
                return jsonify(cached_data)
        
        # Final fallback
        fallback_data = {
            "skill_tree_columns": [{
                "skill_area": "array_processing",
                "total_problems": 1,
                "difficulty_levels": {
                    "Easy": [{
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
                    }],
                    "Medium": [],
                    "Hard": []
                },
                "mastery_percentage": 0.0
            }],
            "total_problems": 1,
            "total_skill_areas": 1,
            "user_id": request.args.get('user_id'),
            "last_updated": "2025-07-31T22:30:00Z",
            "data_source": "fallback"
        }
        
        logger.info("⚠️ Using fallback data")
        return jsonify(fallback_data)
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Internal server error",
            "total_problems": 0,
            "total_skill_areas": 0,
            "skill_tree_columns": [],
            "data_source": "error"
        })

@app.route('/skill-tree/server/status')
def server_status():
    """Agentic server status endpoint"""
    uptime = time.time() - server_start_time
    return jsonify({
        "status": "running",
        "uptime_seconds": round(uptime, 2),
        "port": SERVER_PORT,
        "host": SERVER_HOST,
        "endpoints": [
            "/health",
            "/skill-tree/overview",
            "/skill-tree/server/status",
            "/skill-tree/server/restart"
        ],
        "agentic_features": {
            "auto_restart": True,
            "health_monitoring": True,
            "fallback_data": True,
            "external_process": True
        }
    })

@app.route('/skill-tree/server/restart', methods=['POST'])
def restart_server():
    """Endpoint for agentic server restart"""
    logger.info("🔄 Server restart requested via API")
    
    def restart():
        time.sleep(1)
        os._exit(0)  # Force exit to trigger restart script
    
    thread = threading.Thread(target=restart)
    thread.start()
    
    return jsonify({"status": "restarting", "message": "Server will restart in 1 second"})

def create_server_launcher():
    """Create a launcher script for external terminal"""
    launcher_script = f"""@echo off
title DSA Skill Tree Server
echo Starting DSA Skill Tree Server...
echo Port: {SERVER_PORT}
echo Health: http://localhost:{SERVER_PORT}/health
echo Skill Tree: http://localhost:{SERVER_PORT}/skill-tree/overview
echo.

:restart
"{sys.executable}" "{__file__}"
if %ERRORLEVEL% EQU 0 goto end
echo Server crashed, restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto restart

:end
echo Server stopped normally.
pause
"""
    
    launcher_path = project_root / "start_skill_tree_server.bat"
    with open(launcher_path, 'w') as f:
        f.write(launcher_script)
    
    logger.info(f"✅ Launcher script created: {launcher_path}")
    return launcher_path

def create_agentic_client():
    """Create a client for agentic interaction with the server"""
    client_code = '''#!/usr/bin/env python3
"""
Agentic client for interacting with the skill tree server.
"""

import requests
import time
import subprocess
import os
from pathlib import Path

class SkillTreeClient:
    def __init__(self, host="127.0.0.1", port=8007):
        self.base_url = f"http://{host}:{port}"
        self.host = host
        self.port = port
    
    def is_server_running(self):
        """Check if server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_server_if_needed(self):
        """Start server if not running"""
        if not self.is_server_running():
            launcher = Path("start_skill_tree_server.bat")
            if launcher.exists():
                subprocess.Popen(str(launcher), shell=True)
                time.sleep(3)  # Wait for startup
                return self.is_server_running()
        return True
    
    def get_skill_tree_data(self):
        """Get skill tree data with auto-start"""
        if not self.start_server_if_needed():
            raise Exception("Could not start or connect to server")
        
        response = requests.get(f"{self.base_url}/skill-tree/overview", timeout=10)
        return response.json()
    
    def restart_server(self):
        """Restart the server"""
        try:
            requests.post(f"{self.base_url}/skill-tree/server/restart", timeout=5)
            time.sleep(3)
            return self.is_server_running()
        except:
            return False

# Example usage for agents
if __name__ == "__main__":
    client = SkillTreeClient()
    
    print("🤖 Agentic Skill Tree Client")
    print("=" * 40)
    
    if client.start_server_if_needed():
        print("✅ Server is running")
        data = client.get_skill_tree_data()
        print(f"📊 Total problems: {data.get('total_problems', 0)}")
        print(f"🎯 Skill areas: {data.get('total_skill_areas', 0)}")
    else:
        print("❌ Could not start server")
'''
    
    client_path = project_root / "agentic_skill_tree_client.py"
    with open(client_path, 'w') as f:
        f.write(client_code)
    
    logger.info(f"✅ Agentic client created: {client_path}")
    return client_path

if __name__ == '__main__':
    logger.info("🚀 Starting Agentic-Ready Skill Tree Server...")
    logger.info(f"🌳 Skill tree: http://{SERVER_HOST}:{SERVER_PORT}/skill-tree/overview")
    logger.info(f"❤️ Health: http://{SERVER_HOST}:{SERVER_PORT}/health")
    logger.info(f"🤖 Status: http://{SERVER_HOST}:{SERVER_PORT}/skill-tree/server/status")
    
    # Create launcher and client for agentic use
    launcher_path = create_server_launcher()
    client_path = create_agentic_client()
    
    logger.info(f"📁 Launcher: {launcher_path}")
    logger.info(f"🤖 Client: {client_path}")
    
    try:
        app.run(
            host=SERVER_HOST,
            port=SERVER_PORT,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        raise
