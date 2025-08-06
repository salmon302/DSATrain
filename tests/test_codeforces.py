"""
Simple test script for Codeforces API collection
Tests the basic functionality without complex imports
"""

import asyncio
import json
import time
import httpx
from datetime import datetime
from pathlib import Path


class SimpleCodeforcesClient:
    """Simplified Codeforces client for testing"""
    
    BASE_URL = "https://codeforces.com/api"
    RATE_LIMIT = 2.1
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.problems_dir = self.data_dir / "raw" / "codeforces" / "problems"
        self.problems_dir.mkdir(parents=True, exist_ok=True)
        self.last_request_time = 0
    
    async def _make_request(self, endpoint, params=None):
        """Make rate-limited API request"""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.RATE_LIMIT:
            await asyncio.sleep(self.RATE_LIMIT - time_since_last)
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params or {})
            response.raise_for_status()
            
            self.last_request_time = time.time()
            
            data = response.json()
            if data.get("status") != "OK":
                raise Exception(f"API Error: {data.get('comment', 'Unknown error')}")
            
            return data.get("result", {})
    
    async def get_problems(self):
        """Get problems from problemset"""
        print("Fetching Codeforces problems...")
        return await self._make_request("problemset.problems")
    
    async def collect_and_save(self):
        """Collect problems and save to file"""
        try:
            data = await self.get_problems()
            
            problems = data.get("problems", [])
            print(f"Retrieved {len(problems)} problems")
            
            # Save raw data
            output_file = self.problems_dir / "problems_simple.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "collection_date": datetime.now().isoformat(),
                    "total_problems": len(problems),
                    "problems": problems[:100]  # Save first 100 for testing
                }, f, indent=2, ensure_ascii=False)
            
            print(f"Saved problems to: {output_file}")
            
            # Print some stats
            if problems:
                print("\nSample problems:")
                for i, problem in enumerate(problems[:5]):
                    name = problem.get("name", "Unknown")
                    rating = problem.get("rating", "Unrated")
                    tags = problem.get("tags", [])
                    print(f"{i+1}. {name} (Rating: {rating}, Tags: {tags[:3]})")
            
            return len(problems)
            
        except Exception as e:
            print(f"Error: {e}")
            return 0


async def main():
    """Main test function"""
    print("Simple Codeforces API Test")
    print("=" * 40)
    
    data_dir = Path("data")
    client = SimpleCodeforcesClient(data_dir)
    
    count = await client.collect_and_save()
    
    if count > 0:
        print(f"\n✅ Successfully collected {count} problems!")
        print("Basic API connection working.")
    else:
        print("\n❌ Failed to collect problems.")
    
    print("\nTest completed.")


if __name__ == "__main__":
    asyncio.run(main())
