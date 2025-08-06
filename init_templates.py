#!/usr/bin/env python3
"""
Initialize learning path templates
"""

import requests
import json

def initialize_templates():
    try:
        print("Initializing learning path templates...")
        response = requests.post('http://127.0.0.1:8001/learning-paths/admin/initialize-templates', timeout=30)
        print(f"Initialize templates status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('message', 'Templates initialized')}")
            print(f"Templates created: {len(data.get('templates', []))}")
        else:
            print(f"❌ Error: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    initialize_templates()
