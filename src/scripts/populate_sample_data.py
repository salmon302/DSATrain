"""
Sample Data Population for Skill Tree Testing
Creates sample problems to test the enhanced difficulty analysis and similarity engine
"""

from src.models.database import Problem, DatabaseConfig
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

def create_sample_problems(db_session: Session):
    """Create sample problems for testing the skill tree system"""
    
    sample_problems = [
        # Easy Array Problems
        {
            "id": "easy_array_1",
            "platform": "leetcode",
            "platform_id": "1",
            "title": "Two Sum",
            "difficulty": "Easy",
            "algorithm_tags": ["arrays", "hash_table", "two_pointers"],
            "data_structures": ["array", "hash_table"],
            "quality_score": 85.0,
            "google_interview_relevance": 90.0
        },
        {
            "id": "easy_array_2", 
            "platform": "leetcode",
            "platform_id": "26",
            "title": "Remove Duplicates from Sorted Array",
            "difficulty": "Easy",
            "algorithm_tags": ["arrays", "two_pointers"],
            "data_structures": ["array"],
            "quality_score": 75.0,
            "google_interview_relevance": 70.0
        },
        {
            "id": "easy_string_1",
            "platform": "leetcode", 
            "platform_id": "242",
            "title": "Valid Anagram",
            "difficulty": "Easy",
            "algorithm_tags": ["strings", "hash_table", "sorting"],
            "data_structures": ["string", "hash_table"],
            "quality_score": 80.0,
            "google_interview_relevance": 65.0
        },
        
        # Medium Problems
        {
            "id": "medium_array_1",
            "platform": "leetcode",
            "platform_id": "3",
            "title": "Longest Substring Without Repeating Characters", 
            "difficulty": "Medium",
            "algorithm_tags": ["strings", "sliding_window", "hash_set"],
            "data_structures": ["string", "hash_set"],
            "quality_score": 90.0,
            "google_interview_relevance": 95.0
        },
        {
            "id": "medium_dp_1",
            "platform": "leetcode",
            "platform_id": "322",
            "title": "Coin Change",
            "difficulty": "Medium", 
            "algorithm_tags": ["dynamic_programming", "arrays", "optimization"],
            "data_structures": ["array"],
            "quality_score": 95.0,
            "google_interview_relevance": 85.0
        },
        {
            "id": "medium_tree_1",
            "platform": "leetcode",
            "platform_id": "102", 
            "title": "Binary Tree Level Order Traversal",
            "difficulty": "Medium",
            "algorithm_tags": ["trees", "bfs", "queue"],
            "data_structures": ["tree", "queue"],
            "quality_score": 88.0,
            "google_interview_relevance": 80.0
        },
        
        # Hard Problems
        {
            "id": "hard_dp_1",
            "platform": "leetcode",
            "platform_id": "76",
            "title": "Minimum Window Substring",
            "difficulty": "Hard",
            "algorithm_tags": ["strings", "sliding_window", "hash_table", "optimization"],
            "data_structures": ["string", "hash_table"],
            "quality_score": 100.0,
            "google_interview_relevance": 100.0
        },
        {
            "id": "hard_graph_1", 
            "platform": "leetcode",
            "platform_id": "269",
            "title": "Alien Dictionary",
            "difficulty": "Hard",
            "algorithm_tags": ["graphs", "topological_sort", "dfs", "strings"],
            "data_structures": ["graph", "string"],
            "quality_score": 92.0,
            "google_interview_relevance": 90.0
        },
        {
            "id": "hard_tree_1",
            "platform": "leetcode", 
            "platform_id": "124",
            "title": "Binary Tree Maximum Path Sum",
            "difficulty": "Hard",
            "algorithm_tags": ["trees", "dfs", "dynamic_programming", "recursion"],
            "data_structures": ["tree"],
            "quality_score": 98.0,
            "google_interview_relevance": 88.0
        },
        
        # Codeforces Problems
        {
            "id": "cf_easy_1",
            "platform": "codeforces",
            "platform_id": "4A",
            "title": "Watermelon",
            "difficulty": "Easy",
            "algorithm_tags": ["math", "implementation", "modular_arithmetic"],
            "data_structures": ["integer"],
            "quality_score": 70.0,
            "google_interview_relevance": 30.0
        },
        {
            "id": "cf_medium_1",
            "platform": "codeforces",
            "platform_id": "1200C", 
            "title": "Round Corridor",
            "difficulty": "Medium",
            "algorithm_tags": ["math", "binary_search", "geometry"],
            "data_structures": ["array"],
            "quality_score": 85.0,
            "google_interview_relevance": 45.0
        }
    ]
    
    problems_created = 0
    
    for problem_data in sample_problems:
        # Check if problem already exists
        existing = db_session.query(Problem).filter(Problem.id == problem_data["id"]).first()
        if existing:
            continue
            
        problem = Problem(
            id=problem_data["id"],
            platform=problem_data["platform"],
            platform_id=problem_data["platform_id"], 
            title=problem_data["title"],
            difficulty=problem_data["difficulty"],
            algorithm_tags=problem_data["algorithm_tags"],
            data_structures=problem_data["data_structures"],
            quality_score=problem_data["quality_score"],
            google_interview_relevance=problem_data["google_interview_relevance"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db_session.add(problem)
        problems_created += 1
    
    db_session.commit()
    
    print(f"✅ Created {problems_created} sample problems")
    return problems_created


def main():
    """Main function to populate sample data"""
    
    # Use the new skill tree database
    db_config = DatabaseConfig("sqlite:///./dsatrain_skilltree.db")
    session = db_config.get_session()
    
    try:
        print("🌱 Populating sample data for skill tree testing...")
        
        # Create sample problems
        count = create_sample_problems(session)
        
        # Show final statistics
        from src.models.database import get_database_stats
        stats = get_database_stats(session)
        
        print(f"\n📊 Database Statistics:")
        for table, count in stats.items():
            if count > 0:
                print(f"   {table}: {count}")
        
        print(f"\n🎉 Sample data population completed!")
        
    finally:
        session.close()


if __name__ == "__main__":
    main()
