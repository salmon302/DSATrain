"""
📊 Enhanced Data Population System
Addresses critical system need: scale from 11 → 1000+ problems with skill tree data
"""

import sqlite3
import logging
import random
from typing import List, Dict, Any, Tuple
import json
from datetime import datetime
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedDataPopulator:
    def __init__(self, database_path: str = "dsatrain_phase4.db"):
        self.database_path = database_path
        self.skill_areas = {
            "array_processing": {
                "keywords": ["arrays", "two_pointers", "sliding_window", "prefix_sum", "sorting"],
                "base_difficulty": 1,
                "complexity_range": (20, 60)
            },
            "string_algorithms": {
                "keywords": ["strings", "string_manipulation", "kmp", "rabin_karp"],
                "base_difficulty": 2,
                "complexity_range": (25, 65)
            },
            "mathematical": {
                "keywords": ["math", "number_theory", "combinatorics", "geometry", "modular"],
                "base_difficulty": 2,
                "complexity_range": (30, 70)
            },
            "sorting_searching": {
                "keywords": ["sorting", "binary_search", "quicksort", "mergesort", "search"],
                "base_difficulty": 3,
                "complexity_range": (35, 75)
            },
            "tree_algorithms": {
                "keywords": ["trees", "binary_tree", "bst", "dfs", "bfs", "tree_traversal"],
                "base_difficulty": 4,
                "complexity_range": (40, 80)
            },
            "dynamic_programming": {
                "keywords": ["dynamic_programming", "dp", "memoization", "recursion"],
                "base_difficulty": 5,
                "complexity_range": (50, 90)
            },
            "graph_algorithms": {
                "keywords": ["graphs", "dijkstra", "floyd_warshall", "topological_sort", "shortest_path"],
                "base_difficulty": 6,
                "complexity_range": (55, 95)
            },
            "advanced_structures": {
                "keywords": ["segment_tree", "fenwick_tree", "union_find", "trie", "heap"],
                "base_difficulty": 7,
                "complexity_range": (60, 100)
            }
        }
    
    def connect_database(self):
        """Connect to database"""
        return sqlite3.connect(self.database_path)
    
    def get_problems_summary(self):
        """Get summary of problems in database"""
        logger.info("📊 Analyzing current problem database...")
        
        conn = self.connect_database()
        cursor = conn.cursor()
        
        # Total problems
        cursor.execute("SELECT COUNT(*) FROM problems")
        total_problems = cursor.fetchone()[0]
        
        # Problems with skill tree data
        cursor.execute("SELECT COUNT(*) FROM problems WHERE sub_difficulty_level IS NOT NULL")
        enhanced_problems = cursor.fetchone()[0]
        
        # Problems by difficulty
        cursor.execute("SELECT difficulty, COUNT(*) FROM problems GROUP BY difficulty")
        difficulty_counts = dict(cursor.fetchall())
        
        # Problems by platform
        cursor.execute("SELECT platform, COUNT(*) FROM problems GROUP BY platform")
        platform_counts = dict(cursor.fetchall())
        
        conn.close()
        
        summary = {
            "total_problems": total_problems,
            "enhanced_problems": enhanced_problems,
            "enhancement_percentage": (enhanced_problems / total_problems * 100) if total_problems > 0 else 0,
            "difficulty_distribution": difficulty_counts,
            "platform_distribution": platform_counts
        }
        
        logger.info(f"📊 Database Summary:")
        logger.info(f"  Total problems: {total_problems:,}")
        logger.info(f"  Enhanced with skill tree: {enhanced_problems:,} ({summary['enhancement_percentage']:.1f}%)")
        logger.info(f"  Difficulty distribution: {difficulty_counts}")
        logger.info(f"  Platform distribution: {platform_counts}")
        
        return summary
    
    def analyze_problem_for_skill_area(self, problem: Dict[str, Any]) -> str:
        """Determine skill area for a problem based on its attributes"""
        
        # Combine all text fields for analysis
        text_content = " ".join([
            problem.get('title', '').lower(),
            problem.get('description', '').lower(),
            " ".join(problem.get('algorithm_tags', [])).lower(),
            " ".join(problem.get('data_structures', [])).lower(),
            problem.get('category', '').lower()
        ])
        
        # Score each skill area
        skill_scores = {}
        for skill_area, config in self.skill_areas.items():
            score = 0
            for keyword in config['keywords']:
                if keyword in text_content:
                    score += 1
            
            # Bonus for exact matches in key fields
            if any(keyword in problem.get('category', '').lower() for keyword in config['keywords']):
                score += 2
            
            if score > 0:
                skill_scores[skill_area] = score
        
        # Return skill area with highest score, or fallback
        if skill_scores:
            return max(skill_scores.items(), key=lambda x: x[1])[0]
        else:
            # Fallback based on difficulty
            difficulty = problem.get('difficulty', 'Easy').lower()
            if difficulty == 'easy':
                return 'array_processing'
            elif difficulty == 'medium':
                return 'tree_algorithms'
            else:
                return 'dynamic_programming'
    
    def calculate_enhanced_metrics(self, problem: Dict[str, Any], skill_area: str) -> Dict[str, Any]:
        """Calculate enhanced difficulty metrics for a problem"""
        
        difficulty = problem.get('difficulty', 'Easy').lower()
        skill_config = self.skill_areas[skill_area]
        
        # Base difficulty mapping
        difficulty_base = {
            'easy': 1,
            'medium': 3,
            'hard': 5
        }
        
        # Sub-difficulty level (1-10 within each difficulty)
        base_sub_difficulty = difficulty_base.get(difficulty, 3)
        random_variation = random.randint(-1, 2)
        sub_difficulty_level = max(1, min(10, base_sub_difficulty + skill_config['base_difficulty'] + random_variation))
        
        # Conceptual difficulty (10-100)
        concept_base = {
            'easy': random.randint(15, 35),
            'medium': random.randint(40, 70),
            'hard': random.randint(70, 95)
        }
        conceptual_difficulty = concept_base.get(difficulty, 50)
        
        # Implementation complexity (10-100)
        impl_min, impl_max = skill_config['complexity_range']
        implementation_complexity = random.randint(impl_min, impl_max)
        
        # Prerequisite skills
        prerequisite_skills = []
        if skill_area in ['dynamic_programming', 'graph_algorithms']:
            prerequisite_skills = ['recursion', 'basic_algorithms']
        elif skill_area in ['tree_algorithms']:
            prerequisite_skills = ['recursion', 'data_structures']
        elif skill_area in ['advanced_structures']:
            prerequisite_skills = ['trees', 'dynamic_programming']
        
        # Skill tree position (conceptual positioning)
        position_x = list(self.skill_areas.keys()).index(skill_area) * 100
        position_y = (sub_difficulty_level - 1) * 80 + random.randint(-20, 20)
        
        skill_tree_position = {
            "x": position_x,
            "y": position_y,
            "skill_area": skill_area,
            "difficulty_tier": difficulty
        }
        
        return {
            'sub_difficulty_level': sub_difficulty_level,
            'conceptual_difficulty': conceptual_difficulty,
            'implementation_complexity': implementation_complexity,
            'prerequisite_skills': json.dumps(prerequisite_skills),
            'skill_tree_position': json.dumps(skill_tree_position)
        }
    
    def enhance_problems_batch(self, batch_size: int = 100, max_problems: int = None):
        """Enhance problems with skill tree data in batches"""
        logger.info(f"🚀 Starting problem enhancement (batch size: {batch_size})")
        
        conn = self.connect_database()
        cursor = conn.cursor()
        
        # Get problems that need enhancement
        query = """
            SELECT id, title, difficulty, description, category, 
                   algorithm_tags, data_structures, quality_score,
                   google_interview_relevance
            FROM problems 
            WHERE sub_difficulty_level IS NULL
        """
        
        if max_problems:
            query += f" LIMIT {max_problems}"
        
        cursor.execute(query)
        problems_to_enhance = cursor.fetchall()
        
        logger.info(f"📊 Found {len(problems_to_enhance)} problems to enhance")
        
        if not problems_to_enhance:
            logger.info("✅ All problems already enhanced!")
            conn.close()
            return 0
        
        # Process in batches
        enhanced_count = 0
        total_problems = len(problems_to_enhance)
        
        for i in range(0, len(problems_to_enhance), batch_size):
            batch = problems_to_enhance[i:i + batch_size]
            batch_enhancements = []
            
            for row in batch:
                # Convert row to problem dict
                problem = {
                    'id': row[0],
                    'title': row[1] or '',
                    'difficulty': row[2] or 'Medium',
                    'description': row[3] or '',
                    'category': row[4] or '',
                    'algorithm_tags': json.loads(row[5]) if row[5] else [],
                    'data_structures': json.loads(row[6]) if row[6] else [],
                    'quality_score': row[7] or 0.5,
                    'google_interview_relevance': row[8] or 0.5
                }
                
                # Determine skill area
                skill_area = self.analyze_problem_for_skill_area(problem)
                
                # Calculate enhanced metrics
                metrics = self.calculate_enhanced_metrics(problem, skill_area)
                
                # Prepare update data
                batch_enhancements.append((
                    metrics['sub_difficulty_level'],
                    metrics['conceptual_difficulty'],
                    metrics['implementation_complexity'],
                    metrics['prerequisite_skills'],
                    metrics['skill_tree_position'],
                    problem['id']
                ))
            
            # Batch update
            update_sql = """
                UPDATE problems 
                SET sub_difficulty_level = ?,
                    conceptual_difficulty = ?,
                    implementation_complexity = ?,
                    prerequisite_skills = ?,
                    skill_tree_position = ?
                WHERE id = ?
            """
            
            cursor.executemany(update_sql, batch_enhancements)
            conn.commit()
            
            enhanced_count += len(batch_enhancements)
            progress = (enhanced_count / total_problems) * 100
            
            logger.info(f"📊 Enhanced batch {i//batch_size + 1}: {enhanced_count}/{total_problems} ({progress:.1f}%)")
        
        conn.close()
        
        logger.info(f"🎉 Successfully enhanced {enhanced_count} problems!")
        return enhanced_count
    
    def create_problem_clusters(self, max_clusters: int = 50):
        """Create meaningful problem clusters based on enhanced data"""
        logger.info(f"🎯 Creating problem clusters (max: {max_clusters})")
        
        conn = self.connect_database()
        cursor = conn.cursor()
        
        # Clear existing clusters
        cursor.execute("DELETE FROM problem_clusters")
        
        # Get enhanced problems grouped by skill area and difficulty
        cursor.execute("""
            SELECT skill_tree_position, id, title, difficulty, algorithm_tags, quality_score
            FROM problems 
            WHERE sub_difficulty_level IS NOT NULL 
            AND skill_tree_position IS NOT NULL
        """)
        
        problems = cursor.fetchall()
        logger.info(f"📊 Found {len(problems)} enhanced problems for clustering")
        
        # Group problems by skill area and difficulty
        clusters = {}
        for row in problems:
            try:
                position_data = json.loads(row[0])
                skill_area = position_data.get('skill_area', 'general')
                difficulty = position_data.get('difficulty_tier', 'medium')
                
                cluster_key = f"{skill_area}_{difficulty}"
                
                if cluster_key not in clusters:
                    clusters[cluster_key] = []
                
                clusters[cluster_key].append({
                    'id': row[1],
                    'title': row[2],
                    'difficulty': row[3],
                    'algorithm_tags': json.loads(row[4]) if row[4] else [],
                    'quality_score': row[5] or 0.5
                })
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"⚠️ Error processing problem {row[1]}: {e}")
        
        # Create cluster records
        cluster_inserts = []
        cluster_count = 0
        
        for cluster_key, cluster_problems in clusters.items():
            if len(cluster_problems) < 2:  # Skip small clusters
                continue
                
            skill_area, difficulty = cluster_key.split('_', 1)
            
            # Representative problems (top quality)
            sorted_problems = sorted(cluster_problems, key=lambda p: p['quality_score'], reverse=True)
            representative_problems = [p['id'] for p in sorted_problems[:min(5, len(sorted_problems))]]
            
            # Average quality score
            avg_quality = sum(p['quality_score'] for p in cluster_problems) / len(cluster_problems)
            
            # Common algorithm tags
            all_tags = []
            for problem in cluster_problems:
                all_tags.extend(problem['algorithm_tags'])
            
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            common_tags = [tag for tag, count in tag_counts.items() if count >= 2]
            
            cluster_insert = (
                f"cluster_{cluster_count + 1}",  # id
                f"{skill_area.replace('_', ' ').title()} - {difficulty.title()}",  # cluster_name
                skill_area,  # primary_skill_area
                difficulty,  # difficulty_level
                json.dumps(representative_problems),  # representative_problems
                len(cluster_problems),  # cluster_size
                avg_quality,  # avg_quality_score
                0.7,  # similarity_threshold
                json.dumps(common_tags[:10])  # algorithm_tags (top 10)
            )
            
            cluster_inserts.append(cluster_insert)
            cluster_count += 1
            
            if cluster_count >= max_clusters:
                break
        
        # Insert clusters
        if cluster_inserts:
            cursor.executemany("""
                INSERT INTO problem_clusters 
                (id, cluster_name, primary_skill_area, difficulty_level, 
                 representative_problems, cluster_size, avg_quality_score, 
                 similarity_threshold, algorithm_tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, cluster_inserts)
            
            conn.commit()
            logger.info(f"🎯 Created {len(cluster_inserts)} problem clusters")
        else:
            logger.warning("⚠️ No clusters created - insufficient data")
        
        conn.close()
        return len(cluster_inserts)
    
    def run_full_enhancement(self, max_problems: int = 1000, batch_size: int = 100):
        """Run complete data enhancement process"""
        logger.info("🚀 Starting full data enhancement process...")
        
        # Step 1: Get current status
        summary = self.get_problems_summary()
        
        # Step 2: Enhance problems
        enhanced_count = self.enhance_problems_batch(
            batch_size=batch_size,
            max_problems=max_problems
        )
        
        # Step 3: Create clusters
        cluster_count = self.create_problem_clusters()
        
        # Step 4: Final summary
        final_summary = self.get_problems_summary()
        
        logger.info("🎉 Enhancement process completed!")
        logger.info(f"📊 Enhanced {enhanced_count} problems")
        logger.info(f"🎯 Created {cluster_count} clusters")
        logger.info(f"📈 Enhancement coverage: {final_summary['enhancement_percentage']:.1f}%")
        
        return {
            'problems_enhanced': enhanced_count,
            'clusters_created': cluster_count,
            'final_coverage': final_summary['enhancement_percentage']
        }

def main():
    """Main enhancement execution"""
    print("📊 DSA Train Enhanced Data Population System")
    print("=" * 60)
    
    populator = EnhancedDataPopulator()
    
    # Get current status
    summary = populator.get_problems_summary()
    
    if summary['enhancement_percentage'] > 90:
        print(f"✅ Database already well enhanced ({summary['enhancement_percentage']:.1f}%)")
        response = input("🤔 Re-enhance anyway? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("❌ Enhancement cancelled")
            return
    
    # Configure enhancement
    print("\n⚙️ Enhancement Configuration:")
    max_problems = input("🔢 Max problems to enhance (default 1000, 'all' for all): ").strip()
    
    if max_problems.lower() == 'all':
        max_problems = None
    elif max_problems.isdigit():
        max_problems = int(max_problems)
    else:
        max_problems = 1000
    
    batch_size = input("📦 Batch size (default 100): ").strip()
    batch_size = int(batch_size) if batch_size.isdigit() else 100
    
    print(f"\n🚀 Will enhance up to {max_problems or 'ALL'} problems in batches of {batch_size}")
    response = input("🤔 Continue? (y/N): ").lower().strip()
    
    if response not in ['y', 'yes']:
        print("❌ Enhancement cancelled")
        return
    
    # Run enhancement
    try:
        results = populator.run_full_enhancement(max_problems, batch_size)
        
        print("\n🎉 Enhancement completed successfully!")
        print(f"✅ Enhanced {results['problems_enhanced']} problems")
        print(f"🎯 Created {results['clusters_created']} clusters")
        print(f"📈 Final coverage: {results['final_coverage']:.1f}%")
        
    except Exception as e:
        print(f"\n❌ Enhancement failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
