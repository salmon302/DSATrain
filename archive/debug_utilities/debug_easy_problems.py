from src.models.database import DatabaseConfig, Problem
from sqlalchemy import text

db_config = DatabaseConfig()
db = db_config.get_session()

try:
    # Check Easy problems with different tags
    test_tags = ['array', 'hash_table', 'string', 'two_pointers', 'greedy', 'math']
    
    print("Easy problems by algorithm tag:")
    for tag in test_tags:
        count = db.query(Problem).filter(
            Problem.algorithm_tags.contains([tag])
        ).filter(
            Problem.difficulty == 'Easy'
        ).count()
        print(f"  {tag}: {count} problems")
    
    # Get some sample Easy problems to see what tags they actually have
    easy_problems = db.query(Problem).filter(Problem.difficulty == 'Easy').limit(5).all()
    print("\nSample Easy problems:")
    for p in easy_problems:
        print(f"  {p.title}: {p.algorithm_tags}")
    
finally:
    db.close()
