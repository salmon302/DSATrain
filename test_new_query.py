from src.models.database import DatabaseConfig, Problem
from sqlalchemy import cast, String

db_config = DatabaseConfig()
db = db_config.get_session()

try:
    # Test the new query approach
    skill_area = 'array'
    
    # Test text search approach
    count = db.query(Problem).filter(
        cast(Problem.algorithm_tags, String).contains(f'"{skill_area}"')
    ).filter(
        Problem.quality_score >= 60.0
    ).filter(
        Problem.difficulty == 'Easy'
    ).count()
    
    print(f"Easy '{skill_area}' problems with new query: {count}")
    
    # Get some samples
    problems = db.query(Problem).filter(
        cast(Problem.algorithm_tags, String).contains(f'"{skill_area}"')
    ).filter(
        Problem.quality_score >= 60.0
    ).filter(
        Problem.difficulty == 'Easy'
    ).limit(3).all()
    
    print("Sample problems found:")
    for p in problems:
        print(f"  {p.title} [{p.difficulty}] - {p.algorithm_tags}")
    
    # Test other skills too
    for skill in ['hash_table', 'greedy', 'math']:
        count = db.query(Problem).filter(
            cast(Problem.algorithm_tags, String).contains(f'"{skill}"')
        ).filter(
            Problem.quality_score >= 60.0
        ).filter(
            Problem.difficulty == 'Easy'
        ).count()
        print(f"Easy '{skill}' problems: {count}")
        
finally:
    db.close()
