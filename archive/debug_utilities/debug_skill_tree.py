"""
Debug skill tree API issue
"""

import requests
import time
import subprocess
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_skill_tree_data():
    """Test skill tree data access directly"""
    try:
        from src.api.skill_tree_api import get_db
        from src.models.database import Problem
        
        db = next(get_db())
        problems = db.query(Problem).filter(Problem.sub_difficulty_level.isnot(None)).all()
        print(f"✅ Direct DB access: Found {len(problems)} problems with skill tree data")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Direct DB access failed: {e}")
        return False

def test_skill_tree_endpoint_direct():
    """Test skill tree endpoint using FastAPI TestClient"""
    try:
        from fastapi.testclient import TestClient
        from src.api.skill_tree_server import app
        
        client = TestClient(app)
        response = client.get("/skill-tree/overview")
        print(f"✅ TestClient: Status {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Total skill areas: {data.get('total_skill_areas', 0)}")
            print(f"   📚 Total problems: {data.get('total_problems', 0)}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ TestClient failed: {e}")
        return False

def test_http_connection():
    """Test if there are any HTTP connection issues"""
    try:
        # Try to connect to a simple endpoint first
        response = requests.get("http://httpbin.org/get", timeout=5)
        print(f"✅ HTTP connection works: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ HTTP connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Debugging Skill Tree API Issues")
    print("=" * 50)
    
    # Test 1: Direct database access
    print("\n1️⃣  Testing direct database access...")
    db_ok = test_skill_tree_data()
    
    # Test 2: Direct API testing
    print("\n2️⃣  Testing API with TestClient...")
    api_ok = test_skill_tree_endpoint_direct()
    
    # Test 3: HTTP connection
    print("\n3️⃣  Testing HTTP connection...")
    http_ok = test_http_connection()
    
    print("\n" + "=" * 50)
    print("📋 Results:")
    print(f"   Database: {'✅' if db_ok else '❌'}")
    print(f"   API Logic: {'✅' if api_ok else '❌'}")
    print(f"   HTTP: {'✅' if http_ok else '❌'}")
    
    if all([db_ok, api_ok, http_ok]):
        print("🎯 All components work! Issue might be with server lifecycle.")
        print("💡 Recommendation: Use FastAPI TestClient or try different port/host.")
    else:
        print("⚠️  Found issues that need to be resolved.")
