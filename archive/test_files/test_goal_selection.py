from src.models.database import DatabaseConfig
from src.ml.learning_path_engine import LearningPathEngine, UserProfile

# Test the direct engine to ensure functionality is working
db_config = DatabaseConfig()
db = db_config.get_session()
engine = LearningPathEngine(db)

print('Testing different learning goals with fixed engine:')

try:
    # Test array goal
    print('1. Array goal:')
    array_profile = UserProfile(
        user_id=1,
        current_skill_levels={'array': 'beginner'},
        learning_goals=['array'],
        available_hours_per_week=10,
        preferred_difficulty_curve='gradual',
        target_completion_weeks=4,
        weak_areas=['array'],
        strong_areas=[]
    )
    path = engine.generate_personalized_path(array_profile, None)
    if path:
        week1 = path.to_dict()['weekly_plan'][0]
        print(f'Week 1: {len(week1["problems"])} problems')
        for p_id in week1["problems"][:1]:  # Show first problem
            from src.models.database import Problem
            problem = db.query(Problem).filter_by(id=p_id).first()
            if problem:
                print(f'  First problem: {problem.title} - {problem.algorithm_tags}')
    else:
        print('Failed to generate path')

    # Test greedy goal
    print('2. Greedy goal:')
    greedy_profile = UserProfile(
        user_id=2,
        current_skill_levels={'greedy': 'beginner'},
        learning_goals=['greedy'],
        available_hours_per_week=10,
        preferred_difficulty_curve='gradual',
        target_completion_weeks=4,
        weak_areas=['greedy'],
        strong_areas=[]
    )
    path = engine.generate_personalized_path(greedy_profile, None)
    if path:
        week1 = path.to_dict()['weekly_plan'][0]
        print(f'Week 1: {len(week1["problems"])} problems')
        for p_id in week1["problems"][:1]:  # Show first problem
            from src.models.database import Problem
            problem = db.query(Problem).filter_by(id=p_id).first()
            if problem:
                print(f'  First problem: {problem.title} - {problem.algorithm_tags}')
    else:
        print('Failed to generate path')

finally:
    db.close()
    print('Direct engine test completed.')
