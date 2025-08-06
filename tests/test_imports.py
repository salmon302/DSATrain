#!/usr/bin/env python3
"""
Test FastAPI imports and routes
"""

try:
    import uvicorn
    print("✅ uvicorn imported")
    
    from src.api.main import app
    print("✅ FastAPI app imported")
    
    print("\n📋 Available routes:")
    for route in app.routes:
        print(f"  {route.path}")
        
    print("\n🔍 Checking Google routes:")
    google_routes = [route for route in app.routes if '/google' in str(route.path)]
    for route in google_routes:
        print(f"  ✅ {route.path}")
        
    if not google_routes:
        print("  ❌ No Google routes found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
