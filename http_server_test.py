#!/usr/bin/env python3
"""
HTTP server using Python's built-in http.server module.
This should be more stable than Flask in this environment.
"""

import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillTreeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            logger.info(f"📡 Received request: {path}")
            
            # CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if path == '/health':
                response = {
                    "status": "healthy",
                    "server": "Python HTTP Server",
                    "message": "Built-in HTTP server working"
                }
                
            elif path == '/skill-tree/overview':
                response = self.get_skill_tree_data()
                
            else:
                response = {"error": "Not found", "path": path}
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            logger.info(f"✅ Response sent for {path}")
            
        except Exception as e:
            logger.error(f"❌ Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def get_skill_tree_data(self):
        """Get skill tree data - try database first, fallback to test data"""
        try:
            # Try to get real data from database
            from src.models.database import DatabaseConfig, Problem
            
            db_config = DatabaseConfig()
            db = db_config.get_session()
            
            problems = db.query(Problem).filter(
                Problem.algorithm_tags.isnot(None),
                Problem.algorithm_tags != "[]",
                Problem.algorithm_tags != ""
            ).limit(10).all()  # Limit for testing
            
            db.close()
            
            # Simple data structure
            test_data = {
                "skill_tree_columns": [
                    {
                        "skill_area": "array_processing",
                        "total_problems": len(problems),
                        "difficulty_levels": {
                            "Easy": [
                                {
                                    "id": p.id,
                                    "title": p.title,
                                    "difficulty": p.difficulty,
                                    "algorithm_tags": p.algorithm_tags
                                } for p in problems[:3] if p.difficulty == "Easy"
                            ],
                            "Medium": [],
                            "Hard": []
                        },
                        "mastery_percentage": 0.0
                    }
                ],
                "total_problems": len(problems),
                "total_skill_areas": 1,
                "user_id": None,
                "last_updated": "2025-07-31T22:30:00Z"
            }
            
            logger.info(f"✅ Returning real data with {len(problems)} problems")
            return test_data
            
        except Exception as e:
            logger.warning(f"⚠️ Database failed, using fallback data: {e}")
            
            # Fallback test data
            return {
                "skill_tree_columns": [
                    {
                        "skill_area": "array_processing",
                        "total_problems": 100,
                        "difficulty_levels": {
                            "Easy": [
                                {
                                    "id": 1,
                                    "title": "Two Sum",
                                    "difficulty": "Easy",
                                    "algorithm_tags": ["array", "hash_table"]
                                }
                            ],
                            "Medium": [],
                            "Hard": []
                        },
                        "mastery_percentage": 0.0
                    }
                ],
                "total_problems": 100,
                "total_skill_areas": 1,
                "user_id": None,
                "last_updated": "2025-07-31T22:30:00Z"
            }
    
    def log_message(self, format, *args):
        """Suppress default log messages"""
        pass

if __name__ == '__main__':
    port = 8006
    server = HTTPServer(('127.0.0.1', port), SkillTreeHandler)
    
    logger.info("🚀 Starting Python HTTP Server...")
    logger.info(f"❤️ Health: http://localhost:{port}/health")
    logger.info(f"🌳 Skill Tree: http://localhost:{port}/skill-tree/overview")
    logger.info("🔄 Server will run until manually stopped...")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
        server.shutdown()
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
