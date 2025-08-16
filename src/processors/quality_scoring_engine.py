"""
Quality Scoring Engine
Implements cross-platform quality scoring with Google interview relevance metrics
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import Counter
import math


@dataclass
class QualityScoringEngine:
    """Implements comprehensive quality scoring for problems and solutions"""
    
    data_dir: Path
    output_dir: Optional[Path] = None
    
    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = self.data_dir / "processed" / "quality_scoring"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.processed_dir = self.data_dir / "processed"

    def load_quality_criteria(self) -> Dict[str, Any]:
        """Load academic quality criteria and rules"""
        print("Loading quality criteria from academic datasets...")
        
        # Load academic quality rules
        quality_rules_file = self.processed_dir / "academic_datasets" / "ml4code_quality_rules.json"
        quality_engine_file = self.processed_dir / "academic_datasets" / "code_quality_engine.json"
        
        criteria = {
            "academic_rules": {},
            "evaluation_framework": {},
            "google_standards": []
        }
        
        if quality_rules_file.exists():
            with quality_rules_file.open("r") as f:
                data = json.load(f)
                criteria["academic_rules"] = data
        
        if quality_engine_file.exists():
            with quality_engine_file.open("r") as f:
                data = json.load(f)
                criteria["evaluation_framework"] = data.get("evaluation_framework", {})
        
        print(f"✅ Loaded quality criteria")
        return criteria

    def calculate_content_quality_score(self, problem: Dict[str, Any]) -> Dict[str, float]:
        """Calculate content quality score for a problem"""
        scores = {
            "completeness": 0.0,
            "clarity": 0.0,
            "specificity": 0.0,
            "educational_value": 0.0,
            "overall": 0.0
        }
        
        title = problem.get("title", "")
        description = problem.get("description", "")
        tags = problem.get("unified_tags", [])
        
        # Completeness score (0-1)
        completeness_factors = []
        completeness_factors.append(1.0 if title else 0.0)
        completeness_factors.append(1.0 if description else 0.0)
        completeness_factors.append(1.0 if tags else 0.0)
        completeness_factors.append(1.0 if problem.get("constraints") else 0.0)
        completeness_factors.append(1.0 if problem.get("test_cases") else 0.0)
        
        scores["completeness"] = sum(completeness_factors) / len(completeness_factors)
        
        # Clarity score based on text quality
        if title and description:
            # Check for clear, descriptive title
            title_words = len(title.split())
            title_clarity = min(1.0, title_words / 5.0)  # 5 words is optimal
            
            # Check for adequate description length
            desc_words = len(description.split())
            desc_clarity = min(1.0, desc_words / 50.0)  # 50 words minimum
            
            scores["clarity"] = (title_clarity + desc_clarity) / 2
        
        # Specificity score based on tag quality and detail
        if tags:
            # More specific tags = better
            specific_tags = ["dynamic_programming", "binary_search", "graphs", "trees"]
            general_tags = ["implementation", "math", "greedy"]
            
            specific_count = sum(1 for tag in tags if tag in specific_tags)
            general_count = sum(1 for tag in tags if tag in general_tags)
            
            scores["specificity"] = min(1.0, (specific_count * 0.8 + general_count * 0.3) / 3)
        
        # Educational value (based on common interview topics)
        educational_tags = [
            "arrays", "strings", "dynamic_programming", "graphs", "trees",
            "binary_search", "sorting", "hash_tables", "two_pointers"
        ]
        
        educational_score = sum(1 for tag in tags if tag in educational_tags)
        scores["educational_value"] = min(1.0, educational_score / 5.0)
        
        # Overall score (weighted average)
        weights = {
            "completeness": 0.3,
            "clarity": 0.25,
            "specificity": 0.25,
            "educational_value": 0.2
        }
        
        scores["overall"] = sum(scores[key] * weight for key, weight in weights.items())
        
        return scores

    def calculate_google_interview_relevance(self, problem: Dict[str, Any]) -> Dict[str, float]:
        """Calculate Google interview relevance score"""
        scores = {
            "topic_relevance": 0.0,
            "difficulty_appropriateness": 0.0,
            "frequency_score": 0.0,
            "company_alignment": 0.0,
            "overall_relevance": 0.0
        }
        
        tags = problem.get("unified_tags", [])
        title = problem.get("title", "").lower()
        difficulty = problem.get("difficulty", {})
        
        # Topic relevance (based on known Google interview topics)
        google_topics = {
            "high_priority": ["dynamic_programming", "graphs", "trees", "arrays", "strings"],
            "medium_priority": ["binary_search", "sorting", "hash_tables", "two_pointers"],
            "system_topics": ["system_design", "scalability", "distributed_systems"]
        }
        
        high_count = sum(1 for tag in tags if tag in google_topics["high_priority"])
        medium_count = sum(1 for tag in tags if tag in google_topics["medium_priority"])
        system_count = sum(1 for tag in tags if tag in google_topics["system_topics"])
        
        scores["topic_relevance"] = min(1.0, (high_count * 0.8 + medium_count * 0.5 + system_count * 0.9) / 3)
        
        # Difficulty appropriateness (Google prefers medium to hard)
        diff_level = difficulty.get("level", "medium")
        if diff_level == "medium":
            scores["difficulty_appropriateness"] = 1.0
        elif diff_level == "hard":
            scores["difficulty_appropriateness"] = 0.8
        else:
            scores["difficulty_appropriateness"] = 0.4
        
        # Frequency score (common interview patterns)
        common_patterns = [
            "two sum", "merge", "binary search", "dfs", "bfs", 
            "dynamic", "substring", "palindrome", "tree traversal"
        ]
        
        pattern_matches = sum(1 for pattern in common_patterns if pattern in title)
        scores["frequency_score"] = min(1.0, pattern_matches / 2.0)
        
        # Company alignment (Google-specific indicators)
        google_indicators = ["optimization", "efficiency", "scale", "distributed", "large"]
        company_matches = sum(1 for indicator in google_indicators if indicator in title)
        scores["company_alignment"] = min(1.0, company_matches / 2.0)
        
        # Overall relevance
        weights = {
            "topic_relevance": 0.4,
            "difficulty_appropriateness": 0.3,
            "frequency_score": 0.2,
            "company_alignment": 0.1
        }
        
        scores["overall_relevance"] = sum(scores[key] * weight for key, weight in weights.items())
        
        return scores

    def calculate_learning_path_position(self, problem: Dict[str, Any], all_problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate where this problem fits in learning progression"""
        
        tags = problem.get("unified_tags", [])
        difficulty = problem.get("difficulty", {})
        
        # Define prerequisite relationships
        prerequisite_map = {
            "dynamic_programming": ["arrays", "recursion"],
            "graphs": ["arrays", "data_structures"],
            "trees": ["recursion", "data_structures"], 
            "binary_search": ["arrays", "sorting"],
            "advanced_dp": ["dynamic_programming"],
            "graph_algorithms": ["graphs", "dynamic_programming"]
        }
        
        position_info = {
            "prerequisites": [],
            "difficulty_tier": 1,
            "learning_order": 0,
            "next_topics": [],
            "mastery_level": "beginner"
        }
        
        # Identify prerequisites
        for tag in tags:
            if tag in prerequisite_map:
                position_info["prerequisites"].extend(prerequisite_map[tag])
        
        position_info["prerequisites"] = list(set(position_info["prerequisites"]))
        
        # Assign difficulty tier
        diff_level = difficulty.get("level", "medium")
        rating = difficulty.get("rating", 1500)
        
        if diff_level == "easy" or rating < 1200:
            position_info["difficulty_tier"] = 1
            position_info["mastery_level"] = "beginner"
        elif diff_level == "medium" or rating < 1600:
            position_info["difficulty_tier"] = 2
            position_info["mastery_level"] = "intermediate"
        else:
            position_info["difficulty_tier"] = 3
            position_info["mastery_level"] = "advanced"
        
        # Calculate learning order (problems with fewer prerequisites come first)
        position_info["learning_order"] = len(position_info["prerequisites"])
        
        # Identify next topics
        for topic, prereqs in prerequisite_map.items():
            if all(prereq in tags for prereq in prereqs) and topic not in tags:
                position_info["next_topics"].append(topic)
        
        return position_info

    def score_all_problems(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Score all problems with comprehensive quality metrics"""
        print("=== Scoring All Problems ===")
        
        scoring_results = {
            "metadata": {
                "total_problems": len(problems),
                "scoring_date": datetime.now().isoformat(),
                "version": "1.0"
            },
            "scores": {},
            "statistics": {
                "high_quality_count": 0,
                "medium_quality_count": 0,
                "low_quality_count": 0,
                "high_relevance_count": 0,
                "medium_relevance_count": 0,
                "low_relevance_count": 0
            }
        }
        
        for i, problem in enumerate(problems):
            if i % 50 == 0:
                print(f"Scoring problem {i}/{len(problems)}")
            
            problem_id = problem.get("id", f"unknown_{i}")
            
            # Calculate all scores
            content_scores = self.calculate_content_quality_score(problem)
            relevance_scores = self.calculate_google_interview_relevance(problem)
            position_info = self.calculate_learning_path_position(problem, problems)
            
            # Combine into final score
            final_score = {
                "content_quality": content_scores,
                "google_relevance": relevance_scores,
                "learning_position": position_info,
                "overall_score": (content_scores["overall"] * 0.6 + relevance_scores["overall_relevance"] * 0.4),
                "recommendation": self._generate_recommendation(content_scores, relevance_scores)
            }
            
            scoring_results["scores"][problem_id] = final_score
            
            # Update statistics
            overall = final_score["overall_score"]
            if overall >= 0.8:
                scoring_results["statistics"]["high_quality_count"] += 1
            elif overall >= 0.5:
                scoring_results["statistics"]["medium_quality_count"] += 1
            else:
                scoring_results["statistics"]["low_quality_count"] += 1
            
            relevance = relevance_scores["overall_relevance"]
            if relevance >= 0.7:
                scoring_results["statistics"]["high_relevance_count"] += 1
            elif relevance >= 0.4:
                scoring_results["statistics"]["medium_relevance_count"] += 1
            else:
                scoring_results["statistics"]["low_relevance_count"] += 1
        
        print(f"✅ Scored {len(problems)} problems")
        return scoring_results

    def _generate_recommendation(self, content_scores: Dict[str, float], relevance_scores: Dict[str, float]) -> str:
        """Generate recommendation based on scores"""
        content_overall = content_scores["overall"]
        relevance_overall = relevance_scores["overall_relevance"]
        
        if content_overall >= 0.8 and relevance_overall >= 0.7:
            return "highly_recommended"
        elif content_overall >= 0.6 and relevance_overall >= 0.5:
            return "recommended"
        elif content_overall >= 0.4 or relevance_overall >= 0.4:
            return "conditionally_recommended"
        else:
            return "not_recommended"

    def generate_quality_report(self, scoring_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive quality assessment report"""
        print("=== Generating Quality Report ===")
        
        scores = scoring_results["scores"]
        stats = scoring_results["statistics"]
        
        report = {
            "executive_summary": {
                "total_problems_analyzed": len(scores),
                "high_quality_percentage": (stats["high_quality_count"] / len(scores)) * 100,
                "google_relevance_percentage": (stats["high_relevance_count"] / len(scores)) * 100,
                "overall_recommendation": self._get_overall_recommendation(stats, len(scores))
            },
            "quality_distribution": {
                "high_quality": stats["high_quality_count"],
                "medium_quality": stats["medium_quality_count"], 
                "low_quality": stats["low_quality_count"]
            },
            "relevance_distribution": {
                "high_relevance": stats["high_relevance_count"],
                "medium_relevance": stats["medium_relevance_count"],
                "low_relevance": stats["low_relevance_count"]
            },
            "top_problems": self._get_top_problems(scores, 10),
            "improvement_recommendations": self._get_improvement_recommendations(scores)
        }
        
        print("✅ Generated quality report")
        return report

    def _get_overall_recommendation(self, stats: Dict[str, int], total: int) -> str:
        """Get overall dataset recommendation"""
        high_quality_pct = (stats["high_quality_count"] / total) * 100
        high_relevance_pct = (stats["high_relevance_count"] / total) * 100
        
        if high_quality_pct >= 30 and high_relevance_pct >= 20:
            return "excellent_dataset"
        elif high_quality_pct >= 20 and high_relevance_pct >= 15:
            return "good_dataset"
        elif high_quality_pct >= 10 or high_relevance_pct >= 10:
            return "fair_dataset_needs_curation"
        else:
            return "poor_dataset_requires_major_improvement"

    def _get_top_problems(self, scores: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Get top-rated problems"""
        scored_problems = [
            {
                "problem_id": problem_id,
                "overall_score": data["overall_score"],
                "content_quality": data["content_quality"]["overall"],
                "google_relevance": data["google_relevance"]["overall_relevance"],
                "recommendation": data["recommendation"]
            }
            for problem_id, data in scores.items()
        ]
        
        # Sort by overall score
        scored_problems.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return scored_problems[:limit]

    def _get_improvement_recommendations(self, scores: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Analyze common issues
        low_content_count = sum(1 for data in scores.values() 
                               if data["content_quality"]["overall"] < 0.5)
        low_relevance_count = sum(1 for data in scores.values() 
                                 if data["google_relevance"]["overall_relevance"] < 0.4)
        
        total = len(scores)
        
        if (low_content_count / total) > 0.3:
            recommendations.append("Improve problem descriptions and add more detailed constraints")
        
        if (low_relevance_count / total) > 0.4:
            recommendations.append("Focus on more Google-relevant algorithmic topics")
        
        recommendations.append("Add more test cases and examples to problems")
        recommendations.append("Standardize difficulty ratings across platforms")
        
        return recommendations

    def run_quality_scoring_pipeline(self) -> Dict[str, Any]:
        """Run complete quality scoring pipeline"""
        print("=== Quality Scoring Pipeline ===")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_status": "running"
        }
        
        try:
            # Load unified problems
            problems_file = self.processed_dir / "problems_unified_complete.json"
            if not problems_file.exists():
                raise FileNotFoundError(f"Unified problems file not found: {problems_file}")
            
            print("Loading unified problems...")
            with problems_file.open("r", encoding="utf-8") as f:
                problems_data = json.load(f)
            
            problems = problems_data.get("problems", [])
            print(f"Loaded {len(problems)} unified problems")
            
            # Load quality criteria
            criteria = self.load_quality_criteria()
            
            # Score all problems
            scoring_results = self.score_all_problems(problems)
            
            # Generate quality report
            quality_report = self.generate_quality_report(scoring_results)
            
            # Save results
            scores_file = self.output_dir / "quality_scores.json"
            with scores_file.open("w", encoding="utf-8") as f:
                json.dump(scoring_results, f, indent=2)
            
            report_file = self.output_dir / "quality_report.json"
            with report_file.open("w", encoding="utf-8") as f:
                json.dump(quality_report, f, indent=2)
            
            results["pipeline_status"] = "success"
            results["problems_scored"] = len(problems)
            results["scores_file"] = str(scores_file)
            results["report_file"] = str(report_file)
            results["executive_summary"] = quality_report["executive_summary"]
            
            print(f"\n✅ Quality scoring complete!")
            print(f"Problems scored: {len(problems)}")
            print(f"High quality: {quality_report['quality_distribution']['high_quality']}")
            print(f"High relevance: {quality_report['relevance_distribution']['high_relevance']}")
            
            return results
            
        except Exception as e:
            results["pipeline_status"] = "failed"
            results["error"] = str(e)
            print(f"\n❌ Pipeline failed: {e}")
            return results


def main():
    """Main function for running quality scoring"""
    from pathlib import Path
    
    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    
    # Create scoring engine
    engine = QualityScoringEngine(data_dir)
    
    # Run scoring pipeline
    results = engine.run_quality_scoring_pipeline()
    
    if results["pipeline_status"] == "success":
        print("\n🎉 Quality scoring completed successfully!")
    else:
        print(f"\n⚠️  Pipeline completed with status: {results['pipeline_status']}")
    
    return results


if __name__ == "__main__":
    main()
