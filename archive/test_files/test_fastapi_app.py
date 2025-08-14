#!/usr/bin/env python3
"""
Simple FastAPI test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    print("Testing FastAPI app import...")
    from src.api.main import app
    print("✅ FastAPI app imported successfully")
    
    # Test routes
    print("Available routes:")
    for route in app.routes:
        print(f"  {route.path}")
    
    print("✅ App seems OK")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
