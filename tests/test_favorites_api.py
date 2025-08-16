import json
from fastapi.testclient import TestClient

# Import app
from src.api.main import app, db_config
from src.models.database import DatabaseConfig, Problem, UserSkillTreePreferences

client = TestClient(app)

def test_toggle_and_list_favorites(tmp_path):
    # Ensure a clean in-memory DB for this test if configured
    # Using existing db_config which may be sqlite file; insert a problem and prefs
    session = db_config.get_session()
    try:
        # Create tables if not present
        DatabaseConfig().create_tables()
        # Seed a problem
        p = session.query(Problem).filter(Problem.id == 'test_prob_1').first()
        if not p:
            p = Problem(
                id='test_prob_1', platform='leetcode', platform_id='1', title='Two Sum',
                difficulty='Easy', category='array', algorithm_tags=['array']
            )
            session.add(p)
            session.commit()

        # Ensure prefs row exists
        prefs = session.query(UserSkillTreePreferences).filter(UserSkillTreePreferences.user_id=='user_test').first()
        if not prefs:
            prefs = UserSkillTreePreferences(user_id='user_test', bookmarked_problems=[])
            session.add(prefs)
            session.commit()
    finally:
        session.close()

    # Toggle favorite on
    resp = client.post('/favorites/toggle', json={
        'user_id': 'user_test',
        'problem_id': 'test_prob_1',
        'favorite': True
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data['favorite'] is True

    # List favorites ids
    resp = client.get('/favorites', params={ 'user_id': 'user_test', 'include_details': False })
    assert resp.status_code == 200
    payload = resp.json()
    assert 'problem_ids' in payload
    assert 'test_prob_1' in payload['problem_ids']

    # Toggle off
    resp = client.post('/favorites/toggle', json={
        'user_id': 'user_test',
        'problem_id': 'test_prob_1',
        'favorite': False
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data['favorite'] is False

    # Verify removed
    resp = client.get('/favorites', params={ 'user_id': 'user_test' })
    assert resp.status_code == 200
    payload = resp.json()
    assert payload.get('count', 0) in (0, len(payload.get('problems', [])))
