"""
Full Codeforces data collection script
Collects ALL problems from Codeforces API
"""

import asyncio
import json
import time
import httpx
from datetime import datetime
from pathlib import Path


class FullCodeforcesClient:
    """Full Codeforces client for complete data collection"""
    
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
    
    async def get_all_problems(self):
        """Get ALL problems from problemset"""
        print("Fetching ALL Codeforces problems...")
        return await self._make_request("problemset.problems")
    
    async def collect_all_and_save(self):
        """Collect ALL problems and save to file"""
        try:
            print("Starting full collection...")
            data = await self.get_all_problems()
            
            problems = data.get("problems", [])
            problem_stats = data.get("problemStatistics", [])
            
            print(f"Retrieved {len(problems)} problems")
            print(f"Retrieved {len(problem_stats)} problem statistics")
            
            # Save complete raw data
            output_file = self.problems_dir / "problems_full.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "collection_date": datetime.now().isoformat(),
                    "total_problems": len(problems),
                    "total_statistics": len(problem_stats),
                    "problems": problems,  # ALL problems, not just first 100
                    "problemStatistics": problem_stats
                }, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(problems)} problems to: {output_file}")
            
            # Create summary statistics
            self._create_collection_summary(problems, problem_stats)
            
            return len(problems)
            
        except Exception as e:
            print(f"Error during collection: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def _create_collection_summary(self, problems, problem_stats):
        """Create summary of collected data"""
        print("\nCreating collection summary...")
        
        # Basic statistics
        total_problems = len(problems)
        rated_problems = sum(1 for p in problems if p.get("rating"))
        unrated_problems = total_problems - rated_problems
        
        # Rating distribution
        ratings = [p.get("rating") for p in problems if p.get("rating")]
        rating_stats = {
            "count": len(ratings),
            "min": min(ratings) if ratings else None,
            "max": max(ratings) if ratings else None,
            "avg": sum(ratings) / len(ratings) if ratings else None
        }
        
        # Tag frequency
        tag_counts = {}
        for problem in problems:
            for tag in problem.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Difficulty distribution (based on rating)
        difficulty_dist = {"easy": 0, "medium": 0, "hard": 0, "unrated": 0}
        for problem in problems:
            rating = problem.get("rating")
            if rating is None:
                difficulty_dist["unrated"] += 1
            elif rating <= 1200:
                difficulty_dist["easy"] += 1
            elif rating <= 2000:
                difficulty_dist["medium"] += 1
            else:
                difficulty_dist["hard"] += 1
        
        summary = {
            "collection_date": datetime.now().isoformat(),
            "total_problems": total_problems,
            "rated_problems": rated_problems,
            "unrated_problems": unrated_problems,
            "rating_statistics": rating_stats,
            "difficulty_distribution": difficulty_dist,
            "top_tags": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]),
            "unique_tags": len(tag_counts),
            "total_problem_statistics": len(problem_stats)
        }
        
        # Save summary
        summary_file = self.problems_dir / "collection_full_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Saved summary to: {summary_file}")
        
        # Print key statistics
        print(f"\n📊 Collection Summary:")
        print(f"  Total problems: {total_problems:,}")
        print(f"  Rated problems: {rated_problems:,}")
        print(f"  Unrated problems: {unrated_problems:,}")
        if rating_stats["avg"]:
            print(f"  Average rating: {rating_stats['avg']:.1f}")
            print(f"  Rating range: {rating_stats['min']} - {rating_stats['max']}")
        
        print(f"\n📈 Difficulty Distribution:")
        for level, count in difficulty_dist.items():
            percentage = (count / total_problems) * 100
            print(f"  {level.capitalize()}: {count:,} ({percentage:.1f}%)")
        
        print(f"\n🏷️  Top 10 Tags:")
        for tag, count in list(summary["top_tags"].items())[:10]:
            print(f"  {tag}: {count:,}")


async def main():
    """Main collection function"""
    print("Full Codeforces Data Collection")
    print("=" * 50)
    print("This will collect ALL problems from Codeforces API")
    print("Estimated time: ~20-30 seconds (due to rate limiting)")
    print()
    
    data_dir = Path("data")
    client = FullCodeforcesClient(data_dir)
    
    start_time = time.time()
    count = await client.collect_all_and_save()
    end_time = time.time()
    
    print(f"\n{'='*50}")
    if count > 0:
        print(f"✅ FULL COLLECTION SUCCESSFUL!")
        print(f"Collected: {count:,} problems")
        print(f"Time taken: {end_time - start_time:.1f} seconds")
        print("Ready for processing!")
    else:
        print("❌ Collection failed.")
    
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
