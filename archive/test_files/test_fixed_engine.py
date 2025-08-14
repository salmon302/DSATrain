from src.models.database import DatabaseConfig, Problem
from src.ml.learning_path_engine import LearningPathEngine, UserProfile

db_config = DatabaseConfig()
db = db_config.get_session()
engine = LearningPathEngine(db)

try:
    # Test array-focused learning path for beginners
    print("Testing array-focused learning path for beginners:")
    profile = UserProfile(
        user_id=1,
        current_skill_levels={"array": "beginner", "overall": "beginner"},
        learning_goals=["array"],
        available_hours_per_week=10,
        preferred_difficulty_curve="gradual",
        target_completion_weeks=4,
        weak_areas=["array"],
        strong_areas=[]
    )
    
    path = engine.generate_personalized_path(profile, template_id=None)
    
    if path:
        path_dict = path.to_dict()
        print(f"Generated path with {len(path_dict['weekly_plan'])} weeks")
        week1 = path_dict['weekly_plan'][0]
        print(f"Week 1 has {len(week1['problems'])} problems:")
        for p_id in week1['problems'][:3]:  # Show first 3
            problem = db.query(Problem).filter_by(id=p_id).first()
            if problem:
                print(f"  - {problem.title} [{problem.difficulty}] - {problem.algorithm_tags}")
    else:
        print("No path generated!")
    
    print("\n" + "="*50 + "\n")
    
    # Test greedy-focused learning path for beginners
    print("Testing greedy-focused learning path for beginners:")
    profile = UserProfile(
        user_id=2,
        current_skill_levels={"greedy": "beginner", "overall": "beginner"},
        learning_goals=["greedy"],
        available_hours_per_week=10,
        preferred_difficulty_curve="gradual",
        target_completion_weeks=4,
        weak_areas=["greedy"],
        strong_areas=[]
    )
    
    path = engine.generate_personalized_path(profile, template_id=None)
    
    if path:
        path_dict = path.to_dict()
        print(f"Generated path with {len(path_dict['weekly_plan'])} weeks")
        week1 = path_dict['weekly_plan'][0]
        print(f"Week 1 has {len(week1['problems'])} problems:")
        for p_id in week1['problems'][:3]:  # Show first 3
            problem = db.query(Problem).filter_by(id=p_id).first()
            if problem:
                print(f"  - {problem.title} [{problem.difficulty}] - {problem.algorithm_tags}")
    else:
        print("No path generated!")
        
finally:
    db.close()
