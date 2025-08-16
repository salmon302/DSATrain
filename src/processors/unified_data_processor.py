"""
Cross-Platform Data Unification Processor
Unifies problem schemas across all data sources into a standardized format
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import hashlib


@dataclass
class UnifiedDataProcessor:
    """Processes and unifies data from multiple platforms into standardized schema"""
    
    data_dir: Path
    output_dir: Optional[Path] = None
    
    # Quality scoring weights
    GOOGLE_RELEVANCE_KEYWORDS = {
        "high_priority": ["dynamic programming", "graphs", "trees", "arrays", "strings", "binary search", "sorting"],
        "medium_priority": ["greedy", "hash tables", "stacks", "queues", "heaps"],
        "google_specific": ["system design", "scalability", "optimization"]
    }
    
    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = self.data_dir / "processed"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.raw_dir = self.data_dir / "raw"

    def _normalize_difficulty(self, problem: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Normalize difficulty across different platforms"""
        difficulty = {
            "level": "medium",
            "rating": 1500,
            "confidence": 0.5
        }
        
        if source == "codeforces":
            # Codeforces uses points system
            points = problem.get("points", 1000)
            if points <= 1000:
                difficulty["level"] = "easy"
                difficulty["rating"] = int(800 + points/5)
            elif points <= 2000:
                difficulty["level"] = "medium" 
                difficulty["rating"] = int(1200 + points/4)
            else:
                difficulty["level"] = "hard"
                difficulty["rating"] = int(1800 + points/8)
            difficulty["confidence"] = 0.9
            
        elif source == "hackerrank":
            # HackerRank difficulty from metadata
            hr_diff = problem.get("difficulty", {})
            if isinstance(hr_diff, dict):
                level = hr_diff.get("level", "medium").lower()
                rating = hr_diff.get("rating", 1500)
                difficulty = {
                    "level": level,
                    "rating": rating,
                    "confidence": 0.8
                }
            
        elif source == "leetcode":
            # LeetCode standard difficulty
            lc_diff = problem.get("difficulty", "Medium").lower()
            difficulty_map = {
                "easy": {"level": "easy", "rating": 1200, "confidence": 0.9},
                "medium": {"level": "medium", "rating": 1500, "confidence": 0.9},
                "hard": {"level": "hard", "rating": 1800, "confidence": 0.9}
            }
            difficulty = difficulty_map.get(lc_diff, difficulty)
            
        return difficulty

    def _extract_unified_tags(self, problem: Dict[str, Any], source: str) -> List[str]:
        """Extract and standardize tags across platforms"""
        tags = set()
        
        # Get tags from various sources
        raw_tags = problem.get("tags", [])
        if isinstance(raw_tags, list):
            tags.update(tag.lower().replace(" ", "_") for tag in raw_tags)
        
        # Add source-specific tag extraction
        if source == "codeforces":
            # Codeforces has good algorithmic tags
            cf_tags = problem.get("tags", [])
            tags.update(cf_tags)
            
        elif source == "hackerrank":
            # HackerRank metadata
            metadata = problem.get("metadata", {})
            topic = metadata.get("topic", "")
            if topic:
                tags.add(topic.lower().replace(" ", "_"))
                
        # Standardize common tag variations
        tag_mapping = {
            "dp": "dynamic_programming",
            "dfs": "depth_first_search", 
            "bfs": "breadth_first_search",
            "impl": "implementation",
            "ds": "data_structures",
            "math": "mathematics",
            "string": "strings",
            "graph": "graphs",
            "tree": "trees",
            "array": "arrays"
        }
        
        standardized_tags = []
        for tag in tags:
            standardized_tag = tag_mapping.get(tag, tag)
            standardized_tags.append(standardized_tag)
            
        return list(set(standardized_tags))

    def _calculate_google_relevance(self, problem: Dict[str, Any]) -> float:
        """Calculate relevance score for Google interviews (0.0-1.0)"""
        score = 0.0
        tags = problem.get("unified_tags", [])
        title = problem.get("title", "").lower()
        
        # Tag-based scoring
        for tag in tags:
            if tag in self.GOOGLE_RELEVANCE_KEYWORDS["high_priority"]:
                score += 0.3
            elif tag in self.GOOGLE_RELEVANCE_KEYWORDS["medium_priority"]:
                score += 0.2
            elif tag in self.GOOGLE_RELEVANCE_KEYWORDS["google_specific"]:
                score += 0.4
        
        # Title-based scoring
        for keyword in self.GOOGLE_RELEVANCE_KEYWORDS["high_priority"]:
            if keyword.replace("_", " ") in title:
                score += 0.1
        
        # Difficulty bonus (Google likes medium-hard problems)
        difficulty = problem.get("difficulty", {})
        if difficulty.get("level") == "medium":
            score += 0.1
        elif difficulty.get("level") == "hard":
            score += 0.05
            
        return min(score, 1.0)

    def _create_unified_problem(self, problem: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Create unified problem format"""
        
        # Generate consistent ID
        problem_id = self._generate_problem_id(problem, source)
        
        # Extract title
        title = problem.get("name") or problem.get("title", "Untitled Problem")
        
        # Create unified structure
        unified = {
            "id": problem_id,
            "source": source,
            "original_id": f"{problem.get('contestId', '')}_{problem.get('index', '')}" if source == "codeforces" 
                          else problem.get("id", problem_id),
            "title": title,
            "description": problem.get("description", ""),
            "difficulty": self._normalize_difficulty(problem, source),
            "unified_tags": self._extract_unified_tags(problem, source),
            "company_tags": problem.get("company_tags", []),
            "constraints": problem.get("constraints", {}),
            "test_cases": problem.get("test_cases", []),
            "editorial": problem.get("editorial"),
            "metadata": {
                "created_date": datetime.now().isoformat(),
                "source_url": problem.get("metadata", {}).get("source_url", ""),
                "acquisition_method": problem.get("metadata", {}).get("acquisition_method", "api"),
                "original_metadata": problem.get("metadata", {})
            }
        }
        
        # Calculate quality scores
        unified["quality_scores"] = self._calculate_quality_scores(unified)
        
        # Calculate Google relevance
        unified["google_relevance"] = self._calculate_google_relevance(unified)
        
        return unified

    def _generate_problem_id(self, problem: Dict[str, Any], source: str) -> str:
        """Generate consistent problem ID"""
        if source == "codeforces":
            contest_id = str(problem.get("contestId", ""))
            index = str(problem.get("index", ""))
            return f"cf_{contest_id}_{index}"
        elif source == "hackerrank":
            hr_id = problem.get("id", "")
            return f"hr_{hr_id}" if hr_id else f"hr_{hash(str(problem))}"
        elif source == "leetcode":
            lc_id = problem.get("id", "")
            return f"lc_{lc_id}" if lc_id else f"lc_{hash(str(problem))}"
        else:
            # Generate hash-based ID for other sources
            content = str(problem.get("title", "")) + str(problem.get("tags", []))
            hash_id = hashlib.md5(content.encode()).hexdigest()[:8]
            return f"{source}_{hash_id}"

    def _calculate_quality_scores(self, unified_problem: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality scores for the problem"""
        scores = {
            "completeness": 0.0,
            "difficulty_confidence": 0.0,
            "tag_quality": 0.0,
            "overall": 0.0
        }
        
        # Completeness score
        completeness_factors = [
            1.0 if unified_problem.get("title") else 0.0,
            1.0 if unified_problem.get("description") else 0.0,
            1.0 if unified_problem.get("unified_tags") else 0.0,
            1.0 if unified_problem.get("test_cases") else 0.0,
            1.0 if unified_problem.get("constraints") else 0.0
        ]
        scores["completeness"] = sum(completeness_factors) / len(completeness_factors)
        
        # Difficulty confidence
        scores["difficulty_confidence"] = unified_problem.get("difficulty", {}).get("confidence", 0.0)
        
        # Tag quality (more tags = better, up to a point)
        tag_count = len(unified_problem.get("unified_tags", []))
        scores["tag_quality"] = min(tag_count / 5.0, 1.0)
        
        # Overall score
        scores["overall"] = (
            scores["completeness"] * 0.4 +
            scores["difficulty_confidence"] * 0.3 +
            scores["tag_quality"] * 0.3
        )
        
        return scores

    def process_codeforces_problems(self) -> List[Dict[str, Any]]:
        """Process Codeforces problems"""
        print("Processing Codeforces problems...")
        
        cf_file = self.raw_dir / "codeforces" / "problems" / "problems_simple.json"
        if not cf_file.exists():
            print(f"⚠️  Codeforces file not found: {cf_file}")
            return []
        
        with cf_file.open("r", encoding="utf-8") as f:
            cf_data = json.load(f)
        
        problems = cf_data.get("problems", [])
        unified_problems = []
        
        for i, problem in enumerate(problems):
            if i % 1000 == 0:
                print(f"Processing Codeforces problem {i}/{len(problems)}")
            
            try:
                unified = self._create_unified_problem(problem, "codeforces")
                unified_problems.append(unified)
            except Exception as e:
                print(f"Error processing Codeforces problem {i}: {e}")
                continue
        
        print(f"✅ Processed {len(unified_problems)} Codeforces problems")
        return unified_problems

    def process_hackerrank_problems(self) -> List[Dict[str, Any]]:
        """Process HackerRank problems"""
        print("Processing HackerRank problems...")
        
        hr_file = self.raw_dir / "hackerrank" / "interview_kit" / "interview_kit_problems.json"
        if not hr_file.exists():
            print(f"⚠️  HackerRank file not found: {hr_file}")
            return []
        
        with hr_file.open("r", encoding="utf-8") as f:
            hr_problems = json.load(f)
        
        unified_problems = []
        
        for i, problem in enumerate(hr_problems):
            try:
                unified = self._create_unified_problem(problem, "hackerrank")
                unified_problems.append(unified)
            except Exception as e:
                print(f"Error processing HackerRank problem {i}: {e}")
                continue
        
        print(f"✅ Processed {len(unified_problems)} HackerRank problems")
        return unified_problems

    def process_additional_sources(self) -> List[Dict[str, Any]]:
        """Process other sources (AtCoder, CodeChef, etc.)"""
        print("Processing additional sources...")
        
        unified_problems = []
        
        # Process AtCoder
        atcoder_file = self.raw_dir / "atcoder" / "atcoder_problems.json"
        if atcoder_file.exists():
            try:
                with atcoder_file.open("r", encoding="utf-8") as f:
                    atcoder_data = json.load(f)
                    
                for problem in atcoder_data.get("problems", []):
                    unified = self._create_unified_problem(problem, "atcoder")
                    unified_problems.append(unified)
                    
                print(f"✅ Processed AtCoder problems")
            except Exception as e:
                print(f"❌ Error processing AtCoder: {e}")
        
        # Process CodeChef
        codechef_file = self.raw_dir / "codechef" / "codechef_problems.json"
        if codechef_file.exists():
            try:
                with codechef_file.open("r", encoding="utf-8") as f:
                    codechef_data = json.load(f)
                    
                for problem in codechef_data.get("problems", []):
                    unified = self._create_unified_problem(problem, "codechef")
                    unified_problems.append(unified)
                    
                print(f"✅ Processed CodeChef problems")
            except Exception as e:
                print(f"❌ Error processing CodeChef: {e}")
        
        print(f"✅ Processed {len(unified_problems)} additional problems")
        return unified_problems

    def calculate_cross_platform_statistics(self, unified_problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics across all platforms"""
        
        stats = {
            "total_problems": len(unified_problems),
            "by_source": {},
            "by_difficulty": {"easy": 0, "medium": 0, "hard": 0},
            "by_tags": {},
            "quality_metrics": {
                "high_quality": 0,
                "medium_quality": 0, 
                "low_quality": 0
            },
            "google_relevance": {
                "high_relevance": 0,
                "medium_relevance": 0,
                "low_relevance": 0
            }
        }
        
        for problem in unified_problems:
            # Source statistics
            source = problem.get("source", "unknown")
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
            
            # Difficulty statistics
            difficulty = problem.get("difficulty", {}).get("level", "medium")
            stats["by_difficulty"][difficulty] = stats["by_difficulty"].get(difficulty, 0) + 1
            
            # Tag statistics
            for tag in problem.get("unified_tags", []):
                stats["by_tags"][tag] = stats["by_tags"].get(tag, 0) + 1
            
            # Quality statistics
            quality_score = problem.get("quality_scores", {}).get("overall", 0.0)
            if quality_score >= 0.8:
                stats["quality_metrics"]["high_quality"] += 1
            elif quality_score >= 0.5:
                stats["quality_metrics"]["medium_quality"] += 1
            else:
                stats["quality_metrics"]["low_quality"] += 1
            
            # Google relevance statistics
            google_score = problem.get("google_relevance", 0.0)
            if google_score >= 0.7:
                stats["google_relevance"]["high_relevance"] += 1
            elif google_score >= 0.4:
                stats["google_relevance"]["medium_relevance"] += 1
            else:
                stats["google_relevance"]["low_relevance"] += 1
        
        # Sort tags by frequency
        stats["top_tags"] = sorted(
            stats["by_tags"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:20]
        
        return stats

    def run_unification_pipeline(self) -> Dict[str, Any]:
        """Run complete cross-platform unification pipeline"""
        print("=== Cross-Platform Data Unification Pipeline ===")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_status": "running",
            "unified_problems": []
        }
        
        try:
            # Process all sources
            all_problems = []
            
            # Codeforces (largest source)
            cf_problems = self.process_codeforces_problems()
            all_problems.extend(cf_problems)
            
            # HackerRank interview kit
            hr_problems = self.process_hackerrank_problems()
            all_problems.extend(hr_problems)
            
            # Additional sources
            additional_problems = self.process_additional_sources()
            all_problems.extend(additional_problems)
            
            # Calculate statistics
            print("\nCalculating cross-platform statistics...")
            stats = self.calculate_cross_platform_statistics(all_problems)
            
            # Save unified problems
            output_file = self.output_dir / "problems_unified_complete.json"
            unified_data = {
                "metadata": {
                    "creation_date": datetime.now().isoformat(),
                    "total_problems": len(all_problems),
                    "sources": list(stats["by_source"].keys()),
                    "pipeline_version": "1.0"
                },
                "statistics": stats,
                "problems": all_problems
            }
            
            with output_file.open("w", encoding="utf-8") as f:
                json.dump(unified_data, f, indent=2, ensure_ascii=False)
            
            # Create summary file
            summary_file = self.output_dir / "unification_summary.json"
            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_problems_unified": len(all_problems),
                "sources_processed": stats["by_source"],
                "quality_distribution": stats["quality_metrics"],
                "google_relevance_distribution": stats["google_relevance"],
                "output_files": {
                    "unified_problems": str(output_file),
                    "summary": str(summary_file)
                }
            }
            
            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            
            results["pipeline_status"] = "success"
            results["total_unified"] = len(all_problems)
            results["statistics"] = stats
            results["output_file"] = str(output_file)
            
            print(f"\n✅ Unification complete!")
            print(f"Total problems unified: {len(all_problems)}")
            print(f"Sources: {list(stats['by_source'].keys())}")
            print(f"High quality problems: {stats['quality_metrics']['high_quality']}")
            print(f"High Google relevance: {stats['google_relevance']['high_relevance']}")
            
            return results
            
        except Exception as e:
            results["pipeline_status"] = "failed"
            results["error"] = str(e)
            print(f"\n❌ Pipeline failed: {e}")
            return results


def main():
    """Main function for running cross-platform unification"""
    from pathlib import Path
    
    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    
    # Create processor
    processor = UnifiedDataProcessor(data_dir)
    
    # Run unification pipeline
    results = processor.run_unification_pipeline()
    
    if results["pipeline_status"] == "success":
        print("\n🎉 Cross-platform data unification completed successfully!")
    else:
        print(f"\n⚠️  Pipeline completed with status: {results['pipeline_status']}")
    
    return results


if __name__ == "__main__":
    main()
