"""
Simple test for API functionality
"""

import requests
import time

def test_api():
    try:
        print("Testing API health check...")
        response = requests.get("http://localhost:8000/")
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health check response: {response.json()}")
        
        print("\nTesting basic problems endpoint...")
        response = requests.get("http://localhost:8000/problems?limit=2")
        print(f"Problems status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['count']} problems")
        else:
            print(f"Problems error: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api()
