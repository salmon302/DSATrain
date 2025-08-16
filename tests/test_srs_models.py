from src.models.database import DatabaseConfig, Base, ReviewCard, ReviewHistory, ProblemAttempt, UserCognitiveProfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta


def test_srs_tables_basic_insert(tmp_path):
    # Use a temporary sqlite file to exercise DDL
    db_path = tmp_path / "test_srs.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables in this temp DB
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Insert minimal rows
    # Need a Problem row to satisfy FKs; insert a minimal problem
    from src.models.database import Problem
    p = Problem(
        id="test_p1",
        platform="custom",
        platform_id="p1",
        title="Test Problem",
        difficulty="Easy",
        category="test",
        algorithm_tags=["arrays"],
        google_interview_relevance=10.0,
        quality_score=10.0,
    )
    session.add(p)
    session.commit()

    rc = ReviewCard(problem_id=p.id, interval_days=1, ease=2.5, reps=0, deck="problems")
    session.add(rc)
    session.commit()

    rh = ReviewHistory(problem_id=p.id, outcome="good", time_spent=60)
    session.add(rh)
    session.commit()

    pa = ProblemAttempt(problem_id=p.id, status="attempted", time_spent=120)
    session.add(pa)
    session.commit()

    ucp = UserCognitiveProfile(user_id="default_user", working_memory_capacity=7)
    session.add(ucp)
    session.commit()

    # Assertions
    assert session.query(ReviewCard).count() == 1
    assert session.query(ReviewHistory).count() == 1
    assert session.query(ProblemAttempt).count() == 1
    assert session.query(UserCognitiveProfile).count() == 1

    session.close()
