"""
Codeforces API Client
Implementation of Priority 1.1 from Technical_Coding_Data_Strategy.md

Official API documentation: https://codeforces.com/apiHelp
Rate limit: 1 request per 2 seconds
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
from tqdm import tqdm

from ..models.schemas import (
    Problem, Solution, Difficulty, DifficultyLevel, SourcePlatform,
    ProblemMetadata, AcquisitionMethod, TestCase, Constraints
)


class CodeforcesAPIClient:
    """
    Client for Codeforces API with rate limiting and error handling
    """
    
    BASE_URL = "https://codeforces.com/api"
    RATE_LIMIT_DELAY = 2.1  # Slightly more than 2 seconds to be safe
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.problems_dir = data_dir / "raw" / "codeforces" / "problems"
        self.submissions_dir = data_dir / "raw" / "codeforces" / "submissions"
        self.contests_dir = data_dir / "raw" / "codeforces" / "contests"
        
        # Ensure directories exist
        self.problems_dir.mkdir(parents=True, exist_ok=True)
        self.submissions_dir.mkdir(parents=True, exist_ok=True)
        self.contests_dir.mkdir(parents=True, exist_ok=True)
        
        self.last_request_time = 0
        
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a rate-limited request to Codeforces API
        """
        # Enforce rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - time_since_last)
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params or {})
                response.raise_for_status()
                
                self.last_request_time = time.time()
                
                data = response.json()
                if data.get("status") != "OK":
                    raise Exception(f"API Error: {data.get('comment', 'Unknown error')}")
                
                return data.get("result", {})
                
            except httpx.TimeoutException:
                raise Exception(f"Timeout while accessing {url}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"HTTP {e.response.status_code} error: {e.response.text}")
    
    async def get_problemset_problems(self) -> Dict[str, Any]:
        """
        Get all problems from problemset
        API: /problemset.problems
        """
        print("Fetching Codeforces problemset...")
        return await self._make_request("problemset.problems")
    
    async def get_contest_list(self, gym: bool = False) -> List[Dict[str, Any]]:
        """
        Get list of contests
        API: /contest.list
        """
        print("Fetching Codeforces contests...")
        params = {"gym": "true" if gym else "false"}
        return await self._make_request("contest.list", params)
    
    async def get_user_status(self, handle: str, from_index: int = 1, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get user submissions
        API: /user.status
        """
        params = {
            "handle": handle,
            "from": from_index,
            "count": count
        }
        return await self._make_request("user.status", params)
    
    def _convert_to_difficulty_level(self, rating: Optional[int]) -> DifficultyLevel:
        """
        Convert Codeforces rating to standard difficulty level
        """
        if rating is None:
            return DifficultyLevel.MEDIUM
        
        if rating <= 1200:
            return DifficultyLevel.EASY
        elif rating <= 2000:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.HARD
    
    def _extract_tags(self, problem_data: Dict[str, Any]) -> List[str]:
        """
        Extract and normalize tags from Codeforces problem
        """
        tags = problem_data.get("tags", [])
        # Normalize tags (lowercase, replace spaces with underscores)
        return [tag.lower().replace(" ", "_") for tag in tags]
    
    def _create_problem_from_api_data(self, problem_data: Dict[str, Any], 
                                    problemstat_data: Dict[str, Any] = None) -> Problem:
        """
        Convert Codeforces API data to our Problem schema
        """
        contest_id = problem_data.get("contestId")
        index = problem_data.get("index")
        problem_id = f"cf_{contest_id}_{index}" if contest_id and index else f"cf_{problem_data.get('name', 'unknown')}"
        
        rating = problem_data.get("rating")
        difficulty = Difficulty(
            level=self._convert_to_difficulty_level(rating),
            rating=rating,
            source_scale="codeforces_rating"
        )
        
        # Extract problem statement parts
        name = problem_data.get("name", "")
        statement_parts = []
        
        # Create constraints from problem data
        constraints = None
        time_limit = problem_data.get("timeLimit")
        memory_limit = problem_data.get("memoryLimit")
        if time_limit or memory_limit:
            constraints = Constraints(
                time_limit=f"{time_limit}ms" if time_limit else None,
                memory_limit=f"{memory_limit}KB" if memory_limit else None
            )
        
        # Create source URL
        source_url = None
        if contest_id and index:
            source_url = f"https://codeforces.com/contest/{contest_id}/problem/{index}"
        
        metadata = ProblemMetadata(
            created_date=datetime.now(),
            last_updated=datetime.now(),
            source_url=source_url,
            acquisition_method=AcquisitionMethod.API
        )
        
        return Problem(
            id=problem_id,
            source=SourcePlatform.CODEFORCES,
            title=name,
            description=name,  # We'll need to scrape full descriptions separately
            difficulty=difficulty,
            tags=self._extract_tags(problem_data),
            company_tags=[],  # Codeforces doesn't provide company tags
            constraints=constraints,
            test_cases=[],  # Would need to scrape these separately
            editorial=None,  # Would need to scrape these separately
            metadata=metadata
        )
    
    async def collect_all_problems(self) -> List[Problem]:
        """
        Collect all problems from Codeforces and convert to our schema
        """
        print("Starting Codeforces problem collection...")
        
        # Get problemset data
        problemset_data = await self.get_problemset_problems()
        problems_api = problemset_data.get("problems", [])
        problemstats_api = problemset_data.get("problemStatistics", [])
        
        # Create mapping of problem stats for faster lookup
        stats_map = {}
        for stat in problemstats_api:
            contest_id = stat.get("contestId")
            index = stat.get("index")
            if contest_id and index:
                stats_map[f"{contest_id}_{index}"] = stat
        
        problems = []
        print(f"Processing {len(problems_api)} problems...")
        
        for problem_data in tqdm(problems_api, desc="Converting problems"):
            try:
                contest_id = problem_data.get("contestId")
                index = problem_data.get("index")
                stat_key = f"{contest_id}_{index}" if contest_id and index else None
                
                problem_stat = stats_map.get(stat_key) if stat_key else None
                problem = self._create_problem_from_api_data(problem_data, problem_stat)
                problems.append(problem)
                
            except Exception as e:
                print(f"Error processing problem {problem_data.get('name', 'unknown')}: {e}")
                continue
        
        print(f"Successfully converted {len(problems)} problems")
        return problems
    
    async def save_problems_to_files(self, problems: List[Problem]):
        """
        Save problems to JSON files for later processing
        """
        print("Saving problems to files...")
        
        # Save raw data
        raw_file = self.problems_dir / "problems_raw.json"
        problems_data = [problem.dict() for problem in problems]
        
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(problems_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Saved {len(problems)} problems to {raw_file}")
        
        # Save summary statistics
        summary = {
            "total_problems": len(problems),
            "by_difficulty": {},
            "by_rating_range": {},
            "top_tags": {},
            "collection_date": datetime.now().isoformat()
        }
        
        # Calculate statistics
        for problem in problems:
            # Difficulty distribution
            difficulty = problem.difficulty.level.value
            summary["by_difficulty"][difficulty] = summary["by_difficulty"].get(difficulty, 0) + 1
            
            # Rating distribution
            rating = problem.difficulty.rating
            if rating:
                rating_range = f"{(rating // 200) * 200}-{(rating // 200 + 1) * 200 - 1}"
                summary["by_rating_range"][rating_range] = summary["by_rating_range"].get(rating_range, 0) + 1
            
            # Tag frequency
            for tag in problem.tags:
                summary["top_tags"][tag] = summary["top_tags"].get(tag, 0) + 1
        
        # Sort top tags
        summary["top_tags"] = dict(sorted(summary["top_tags"].items(), key=lambda x: x[1], reverse=True)[:20])
        
        summary_file = self.problems_dir / "collection_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Saved collection summary to {summary_file}")
        print(f"Summary: {summary['total_problems']} problems, "
              f"{len(summary['by_difficulty'])} difficulty levels, "
              f"{len(summary['top_tags'])} unique tags")


async def main():
    """
    Main function to run Codeforces data collection
    """
    data_dir = Path(__file__).parent.parent.parent / "data"
    client = CodeforcesAPIClient(data_dir)
    
    try:
        # Collect all problems
        problems = await client.collect_all_problems()
        
        # Save to files
        await client.save_problems_to_files(problems)
        
        print("Codeforces data collection completed successfully!")
        
    except Exception as e:
        print(f"Error during collection: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
