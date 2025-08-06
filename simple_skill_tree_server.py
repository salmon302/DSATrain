"""
🔧 Simple HTTP Server for Frontend Integration
Minimal server that stays running for frontend testing
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from src.models.database import DatabaseConfig, Problem
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillTreeHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            logger.info(f"GET request: {self.path}")
            
            if self.path == '/health':
                self.send_json_response({'status': 'healthy', 'server': 'simple HTTP server'})
            elif self.path == '/skill-tree/overview':
                data = self.get_skill_tree_overview()
                self.send_json_response(data)
            else:
                self.send_error(404, "Endpoint not found")
                
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_error(500, str(e))
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        response = json.dumps(data)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(response.encode('utf-8'))
    
    def get_skill_tree_overview(self):
        """Get skill tree overview data"""
        try:
            # Connect to database
            db_config = DatabaseConfig("sqlite:///dsatrain_phase4.db")
            db = db_config.get_session()
            
            # Get all problems with enhanced difficulty metrics
            problems = db.query(Problem).filter(Problem.sub_difficulty_level.isnot(None)).all()
            
            if not problems:
                return {
                    "error": "No problems with skill tree data found",
                    "total_problems": 0,
                    "total_skill_areas": 0
                }
            
            # Organize problems by skill area
            skill_areas = {}
            
            for problem in problems:
                if not problem.algorithm_tags:
                    continue
                    
                # Determine primary skill area
                primary_skill = self.determine_primary_skill_area(problem.algorithm_tags)
                
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
                    "prerequisite_skills": problem.prerequisite_skills or [],
                    "quality_score": problem.quality_score or 0.0,
                    "google_interview_relevance": problem.google_interview_relevance or 0.0
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
            
            return {
                "skill_tree_columns": columns,
                "total_problems": len(problems),
                "total_skill_areas": len(skill_areas),
                "user_id": None,
                "last_updated": "2025-07-31T22:00:00Z"
            }
            
        except Exception as e:
            logger.error(f"Error getting skill tree overview: {e}")
            return {
                "error": str(e),
                "total_problems": 0,
                "total_skill_areas": 0
            }
    
    def determine_primary_skill_area(self, algorithm_tags):
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

def main():
    """Start the simple HTTP server"""
    port = 8002
    server_address = ('127.0.0.1', port)
    
    logger.info(f"🚀 Starting Simple Skill Tree Server on http://127.0.0.1:{port}")
    logger.info(f"🌳 Skill tree endpoint: http://127.0.0.1:{port}/skill-tree/overview")
    logger.info(f"❤️ Health check: http://127.0.0.1:{port}/health")
    
    httpd = HTTPServer(server_address, SkillTreeHandler)
    
    try:
        logger.info("✅ Server is running and ready for requests...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
        httpd.server_close()

if __name__ == "__main__":
    main()
