"""
Phase 3B Integration Script - Solution Analysis Completion
Combines all solution collections and creates comprehensive analytics for Phase 3B

This script integrates:
- LeetCode Solutions: 3 problems, 5 solutions (Interview focus)
- Codeforces Solutions: 5 problems, 6 solutions (Competitive programming)

Creates unified solution analytics, learning paths, and educational content.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple


def load_all_solution_collections() -> Dict[str, List[Dict[str, Any]]]:
    """Load all solution collections from Phase 3B"""
    print("📂 Loading all solution collections...")
    
    collections_by_platform = {}
    
    # Load LeetCode solutions
    leetcode_dir = Path("data/solutions/leetcode")
    if leetcode_dir.exists():
        leetcode_collections = []
        for file_path in leetcode_dir.glob("*_solutions.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                collection = json.load(f)
                leetcode_collections.append(collection)
        collections_by_platform["leetcode"] = leetcode_collections
        print(f"✅ Loaded {len(leetcode_collections)} LeetCode solution collections")
    
    # Load Codeforces solutions
    codeforces_dir = Path("data/solutions/codeforces")
    if codeforces_dir.exists():
        codeforces_collections = []
        for file_path in codeforces_dir.glob("*_solutions.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                collection = json.load(f)
                codeforces_collections.append(collection)
        collections_by_platform["codeforces"] = codeforces_collections
        print(f"✅ Loaded {len(codeforces_collections)} Codeforces solution collections")
    
    return collections_by_platform


def extract_all_solutions(collections_by_platform: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Extract all individual solutions from collections"""
    all_solutions = []
    
    for platform, collections in collections_by_platform.items():
        for collection in collections:
            for solution in collection["solutions"]:
                # Add platform metadata
                solution["platform"] = platform
                all_solutions.append(solution)
    
    print(f"📊 Extracted {len(all_solutions)} total solutions")
    return all_solutions


def analyze_solution_patterns(all_solutions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze patterns across all solutions"""
    print("🔍 Analyzing solution patterns...")
    
    # Algorithm pattern analysis
    algorithm_patterns = defaultdict(list)
    for solution in all_solutions:
        for tag in solution["algorithm_tags"]:
            algorithm_patterns[tag].append({
                "solution_id": solution["id"],
                "problem_id": solution["problem_id"],
                "platform": solution["platform"],
                "approach": solution["approach_type"],
                "quality": solution["code_quality"]["overall_score"],
                "complexity": solution["complexity"]["time_complexity"]
            })
    
    # Data structure usage analysis
    data_structure_usage = defaultdict(list)
    for solution in all_solutions:
        for ds in solution["data_structures_used"]:
            data_structure_usage[ds].append(solution["id"])
    
    # Complexity distribution
    time_complexities = [sol["complexity"]["time_complexity"] for sol in all_solutions]
    space_complexities = [sol["complexity"]["space_complexity"] for sol in all_solutions]
    
    # Quality score distribution
    quality_scores = [sol["code_quality"]["overall_score"] for sol in all_solutions]
    
    # Platform comparison
    platform_stats = {}
    for platform in ["leetcode", "codeforces"]:
        platform_solutions = [s for s in all_solutions if s["platform"] == platform]
        if platform_solutions:
            platform_stats[platform] = {
                "total_solutions": len(platform_solutions),
                "avg_quality": sum(s["code_quality"]["overall_score"] for s in platform_solutions) / len(platform_solutions),
                "avg_google_relevance": sum(s["google_interview_relevance"] for s in platform_solutions) / len(platform_solutions),
                "most_common_algorithms": Counter(
                    tag for s in platform_solutions for tag in s["algorithm_tags"]
                ).most_common(5),
                "difficulty_range": {
                    "min_implementation": min(s["implementation_difficulty"] for s in platform_solutions),
                    "max_implementation": max(s["implementation_difficulty"] for s in platform_solutions),
                    "avg_conceptual": sum(s["conceptual_difficulty"] for s in platform_solutions) / len(platform_solutions)
                }
            }
    
    return {
        "algorithm_patterns": dict(algorithm_patterns),
        "data_structure_usage": dict(data_structure_usage),
        "complexity_analysis": {
            "time_complexity_distribution": Counter(time_complexities),
            "space_complexity_distribution": Counter(space_complexities),
            "most_common_time_complexity": Counter(time_complexities).most_common(1)[0] if time_complexities else None,
            "optimization_opportunities": len([tc for tc in time_complexities if "n²" in tc or "n^2" in tc])
        },
        "quality_analysis": {
            "average_quality": sum(quality_scores) / len(quality_scores),
            "quality_distribution": {
                "excellent": len([q for q in quality_scores if q >= 90]),
                "good": len([q for q in quality_scores if 80 <= q < 90]),
                "acceptable": len([q for q in quality_scores if 70 <= q < 80]),
                "needs_improvement": len([q for q in quality_scores if q < 70])
            },
            "highest_quality_solution": max(all_solutions, key=lambda s: s["code_quality"]["overall_score"])["id"],
            "most_educational_solution": max(all_solutions, key=lambda s: s["google_interview_relevance"])["id"]
        },
        "platform_comparison": platform_stats
    }


def create_learning_paths(all_solutions: List[Dict[str, Any]], patterns: Dict[str, Any]) -> Dict[str, Any]:
    """Create structured learning paths based on solution analysis"""
    print("🎓 Creating educational learning paths...")
    
    # Group solutions by difficulty progression
    beginner_solutions = [s for s in all_solutions if s["implementation_difficulty"] <= 3]
    intermediate_solutions = [s for s in all_solutions if 4 <= s["implementation_difficulty"] <= 6]
    advanced_solutions = [s for s in all_solutions if s["implementation_difficulty"] >= 7]
    
    # Create algorithm-specific learning paths
    algorithm_paths = {}
    for algorithm, solutions_info in patterns["algorithm_patterns"].items():
        if len(solutions_info) >= 2:  # Only create paths for algorithms with multiple examples
            sorted_solutions = sorted(solutions_info, key=lambda x: x["quality"], reverse=True)
            algorithm_paths[algorithm] = {
                "total_solutions": len(sorted_solutions),
                "recommended_order": [s["solution_id"] for s in sorted_solutions],
                "skill_progression": {
                    "beginner": [s for s in sorted_solutions if s["solution_id"] in [sol["id"] for sol in beginner_solutions]],
                    "intermediate": [s for s in sorted_solutions if s["solution_id"] in [sol["id"] for sol in intermediate_solutions]],
                    "advanced": [s for s in sorted_solutions if s["solution_id"] in [sol["id"] for sol in advanced_solutions]]
                },
                "complexity_progression": list(set(s["complexity"] for s in sorted_solutions)),
                "platforms_covered": list(set(s["platform"] for s in sorted_solutions))
            }
    
    # Create interview preparation path
    interview_solutions = sorted(
        [s for s in all_solutions if s["google_interview_relevance"] >= 75],
        key=lambda x: x["google_interview_relevance"],
        reverse=True
    )
    
    interview_path = {
        "total_solutions": len(interview_solutions),
        "progression_levels": {
            "foundation": [s["id"] for s in interview_solutions if s["implementation_difficulty"] <= 4],
            "core_skills": [s["id"] for s in interview_solutions if 5 <= s["implementation_difficulty"] <= 7],
            "advanced_topics": [s["id"] for s in interview_solutions if s["implementation_difficulty"] >= 8]
        },
        "algorithm_coverage": Counter(tag for s in interview_solutions for tag in s["algorithm_tags"]),
        "platform_distribution": Counter(s["platform"] for s in interview_solutions),
        "estimated_study_time": {
            "foundation": len([s for s in interview_solutions if s["implementation_difficulty"] <= 4]) * 30,  # 30 min per problem
            "core_skills": len([s for s in interview_solutions if 5 <= s["implementation_difficulty"] <= 7]) * 45,  # 45 min per problem
            "advanced_topics": len([s for s in interview_solutions if s["implementation_difficulty"] >= 8]) * 60  # 60 min per problem
        }
    }
    
    # Create competitive programming path
    competitive_solutions = [s for s in all_solutions if s["platform"] == "codeforces"]
    
    competitive_path = {
        "total_solutions": len(competitive_solutions),
        "contest_progression": {
            "div2_a": [s["id"] for s in competitive_solutions if s.get("contest_type", "").startswith("Div2-A")],
            "div2_bc": [s["id"] for s in competitive_solutions if "Div2-B" in s.get("contest_type", "") or "Div2-C" in s.get("contest_type", "")],
            "div1": [s["id"] for s in competitive_solutions if "Div1" in s.get("contest_type", "")]
        },
        "skill_development": {
            "implementation": [s["id"] for s in competitive_solutions if s["implementation_difficulty"] >= 7],
            "algorithm_design": [s["id"] for s in competitive_solutions if s["conceptual_difficulty"] >= 8],
            "optimization": [s["id"] for s in competitive_solutions if "optimization" in s["algorithm_tags"]]
        },
        "time_investment": len(competitive_solutions) * 25  # 25 min average per competitive problem
    }
    
    return {
        "difficulty_progression": {
            "beginner": {
                "solutions": [s["id"] for s in beginner_solutions],
                "focus": "Basic programming concepts and simple algorithms",
                "estimated_time": len(beginner_solutions) * 20
            },
            "intermediate": {
                "solutions": [s["id"] for s in intermediate_solutions],
                "focus": "Data structures and algorithmic thinking",
                "estimated_time": len(intermediate_solutions) * 40
            },
            "advanced": {
                "solutions": [s["id"] for s in advanced_solutions],
                "focus": "Complex algorithms and optimization techniques",
                "estimated_time": len(advanced_solutions) * 60
            }
        },
        "algorithm_specific_paths": algorithm_paths,
        "interview_preparation_path": interview_path,
        "competitive_programming_path": competitive_path,
        "cross_platform_learning": {
            "leetcode_to_codeforces": "Start with LeetCode for interview prep, then Codeforces for competitive skills",
            "codeforces_to_leetcode": "Build algorithmic foundation with Codeforces, then focus on interview-style problems",
            "parallel_study": "Alternate between platforms to build both interview and competitive programming skills"
        }
    }


def create_solution_recommendations(all_solutions: List[Dict[str, Any]], patterns: Dict[str, Any]) -> Dict[str, Any]:
    """Create solution recommendations for different use cases"""
    print("💡 Creating solution recommendations...")
    
    # Best solutions by category
    recommendations = {
        "for_interviews": {
            "must_know": [],
            "good_to_know": [],
            "advanced_topics": []
        },
        "for_competitive_programming": {
            "contest_essentials": [],
            "optimization_techniques": [],
            "advanced_algorithms": []
        },
        "for_learning": {
            "beginner_friendly": [],
            "concept_builders": [],
            "pattern_examples": []
        },
        "by_algorithm": {},
        "by_data_structure": {}
    }
    
    # Interview recommendations
    interview_solutions = sorted(all_solutions, key=lambda x: x["google_interview_relevance"], reverse=True)
    
    recommendations["for_interviews"]["must_know"] = [
        {
            "solution_id": s["id"],
            "problem_title": s.get("title", ""),
            "reason": f"High interview relevance ({s['google_interview_relevance']:.0f}%), {s['approach_type']} approach",
            "key_concepts": s["algorithm_tags"][:3],
            "difficulty": s["implementation_difficulty"]
        }
        for s in interview_solutions[:3]  # Top 3
    ]
    
    recommendations["for_interviews"]["good_to_know"] = [
        {
            "solution_id": s["id"],
            "problem_title": s.get("title", ""),
            "reason": f"Good interview practice, {s['complexity']['time_complexity']} complexity",
            "key_concepts": s["algorithm_tags"][:2]
        }
        for s in interview_solutions[3:6]  # Next 3
    ]
    
    # Competitive programming recommendations
    competitive_solutions = [s for s in all_solutions if s["platform"] == "codeforces"]
    competitive_solutions.sort(key=lambda x: x["code_quality"]["overall_score"], reverse=True)
    
    recommendations["for_competitive_programming"]["contest_essentials"] = [
        {
            "solution_id": s["id"],
            "problem_title": s.get("title", ""),
            "reason": f"Essential for {s.get('contest_type', 'contests')}, high code quality",
            "algorithms": s["algorithm_tags"],
            "contest_type": s.get("contest_type", "")
        }
        for s in competitive_solutions[:3]
    ]
    
    # Learning recommendations
    learning_solutions = sorted(all_solutions, key=lambda x: (
        len(x["step_by_step"]) + len(x["key_insights"]) * 2
    ), reverse=True)
    
    recommendations["for_learning"]["concept_builders"] = [
        {
            "solution_id": s["id"],
            "problem_title": s.get("title", ""),
            "reason": f"Excellent educational content with {len(s['step_by_step'])} steps and {len(s['key_insights'])} insights",
            "learning_value": len(s["step_by_step"]) + len(s["key_insights"]),
            "concepts": s["algorithm_tags"]
        }
        for s in learning_solutions[:4]
    ]
    
    # Algorithm-specific recommendations
    for algorithm, solutions_info in patterns["algorithm_patterns"].items():
        if len(solutions_info) >= 1:
            best_solution = max(solutions_info, key=lambda x: x["quality"])
            recommendations["by_algorithm"][algorithm] = {
                "best_example": best_solution["solution_id"],
                "quality_score": best_solution["quality"],
                "complexity": best_solution["complexity"],
                "platform": best_solution["platform"],
                "all_examples": [s["solution_id"] for s in solutions_info]
            }
    
    # Data structure recommendations
    for ds, solution_ids in patterns["data_structure_usage"].items():
        if len(solution_ids) >= 1:
            ds_solutions = [s for s in all_solutions if s["id"] in solution_ids]
            best_ds_solution = max(ds_solutions, key=lambda x: x["code_quality"]["overall_score"])
            recommendations["by_data_structure"][ds] = {
                "best_example": best_ds_solution["id"],
                "quality_score": best_ds_solution["code_quality"]["overall_score"],
                "usage_examples": len(solution_ids),
                "platforms": list(set(s["platform"] for s in ds_solutions))
            }
    
    return recommendations


def create_phase3b_comprehensive_analytics(
    collections_by_platform: Dict[str, List[Dict[str, Any]]],
    all_solutions: List[Dict[str, Any]],
    patterns: Dict[str, Any],
    learning_paths: Dict[str, Any],
    recommendations: Dict[str, Any]
) -> Dict[str, Any]:
    """Create comprehensive analytics for Phase 3B"""
    print("📊 Creating comprehensive Phase 3B analytics...")
    
    # Basic statistics
    total_problems = sum(len(collections) for collections in collections_by_platform.values())
    total_solutions = len(all_solutions)
    
    # Platform analysis
    platform_analysis = {}
    for platform, collections in collections_by_platform.items():
        platform_solutions = [s for s in all_solutions if s["platform"] == platform]
        platform_analysis[platform] = {
            "problems": len(collections),
            "solutions": len(platform_solutions),
            "avg_solutions_per_problem": len(platform_solutions) / len(collections) if collections else 0,
            "quality_metrics": {
                "avg_quality": sum(s["code_quality"]["overall_score"] for s in platform_solutions) / len(platform_solutions),
                "avg_google_relevance": sum(s["google_interview_relevance"] for s in platform_solutions) / len(platform_solutions),
                "high_quality_count": len([s for s in platform_solutions if s["code_quality"]["overall_score"] >= 85])
            },
            "algorithm_coverage": len(set(tag for s in platform_solutions for tag in s["algorithm_tags"])),
            "unique_approaches": len(set(s["approach_type"] for s in platform_solutions))
        }
    
    # Educational value assessment
    educational_analysis = {
        "solutions_with_explanations": len([s for s in all_solutions if len(s["explanation"]) > 50]),
        "solutions_with_step_by_step": len([s for s in all_solutions if len(s["step_by_step"]) > 0]),
        "solutions_with_insights": len([s for s in all_solutions if len(s["key_insights"]) > 0]),
        "high_educational_value": len([s for s in all_solutions if 
                                     len(s["explanation"]) > 50 and 
                                     len(s["step_by_step"]) > 2 and 
                                     len(s["key_insights"]) > 1]),
        "interview_ready_solutions": len([s for s in all_solutions if s["google_interview_relevance"] >= 80]),
        "learning_path_coverage": {
            "beginner_problems": len(learning_paths["difficulty_progression"]["beginner"]["solutions"]),
            "intermediate_problems": len(learning_paths["difficulty_progression"]["intermediate"]["solutions"]),
            "advanced_problems": len(learning_paths["difficulty_progression"]["advanced"]["solutions"])
        }
    }
    
    # Code quality insights
    quality_insights = {
        "overall_quality_score": sum(s["code_quality"]["overall_score"] for s in all_solutions) / len(all_solutions),
        "quality_by_platform": {
            platform: platform_analysis[platform]["quality_metrics"]["avg_quality"]
            for platform in platform_analysis
        },
        "quality_by_approach": {
            approach: sum(s["code_quality"]["overall_score"] for s in all_solutions if s["approach_type"] == approach) / 
                     len([s for s in all_solutions if s["approach_type"] == approach])
            for approach in set(s["approach_type"] for s in all_solutions)
        },
        "documentation_quality": {
            "well_documented": len([s for s in all_solutions if s["code_quality"]["documentation_score"] >= 80]),
            "needs_documentation": len([s for s in all_solutions if s["code_quality"]["documentation_score"] < 60])
        }
    }
    
    # Performance analysis
    performance_analysis = {
        "runtime_distribution": {
            "fast": len([s for s in all_solutions if s["performance"]["runtime_ms"] <= 50]),
            "medium": len([s for s in all_solutions if 50 < s["performance"]["runtime_ms"] <= 100]),
            "slow": len([s for s in all_solutions if s["performance"]["runtime_ms"] > 100])
        },
        "complexity_efficiency": {
            "optimal_time": len([s for s in all_solutions if "O(n)" in s["complexity"]["time_complexity"] or "O(1)" in s["complexity"]["time_complexity"]]),
            "suboptimal_time": len([s for s in all_solutions if "O(n²)" in s["complexity"]["time_complexity"] or "O(n^2)" in s["complexity"]["time_complexity"]]),
            "space_efficient": len([s for s in all_solutions if "O(1)" in s["complexity"]["space_complexity"]])
        }
    }
    
    # Collection completeness
    completeness_metrics = {
        "problems_with_multiple_solutions": len([
            collections for collections in collections_by_platform.values()
            for collection in collections if collection["total_solutions"] > 1
        ]),
        "problems_with_optimal_solutions": len([
            collections for collections in collections_by_platform.values()
            for collection in collections if collection.get("optimal_solution_id")
        ]),
        "algorithm_pattern_coverage": len(patterns["algorithm_patterns"]),
        "data_structure_coverage": len(patterns["data_structure_usage"]),
        "cross_platform_algorithms": len([
            alg for alg, solutions in patterns["algorithm_patterns"].items()
            if len(set(s["platform"] for s in solutions)) > 1
        ])
    }
    
    return {
        "phase_3b_summary": {
            "completion_date": datetime.now().isoformat(),
            "total_problems": total_problems,
            "total_solutions": total_solutions,
            "platforms_covered": len(collections_by_platform),
            "solution_collection_status": "completed",
            "phase_3b_achievements": [
                f"Collected {total_solutions} high-quality solutions",
                f"Covered {len(patterns['algorithm_patterns'])} algorithm patterns",
                f"Created learning paths for {len(learning_paths['algorithm_specific_paths'])} algorithms",
                f"Generated {len(recommendations['by_algorithm'])} algorithm-specific recommendations"
            ]
        },
        "platform_analysis": platform_analysis,
        "solution_patterns": patterns,
        "learning_paths_summary": {
            "total_algorithm_paths": len(learning_paths["algorithm_specific_paths"]),
            "interview_prep_solutions": learning_paths["interview_preparation_path"]["total_solutions"],
            "competitive_prog_solutions": learning_paths["competitive_programming_path"]["total_solutions"],
            "estimated_study_time": {
                "beginner": learning_paths["difficulty_progression"]["beginner"]["estimated_time"],
                "intermediate": learning_paths["difficulty_progression"]["intermediate"]["estimated_time"],
                "advanced": learning_paths["difficulty_progression"]["advanced"]["estimated_time"]
            }
        },
        "recommendations_summary": {
            "interview_must_know": len(recommendations["for_interviews"]["must_know"]),
            "competitive_essentials": len(recommendations["for_competitive_programming"]["contest_essentials"]),
            "learning_concept_builders": len(recommendations["for_learning"]["concept_builders"]),
            "algorithm_examples": len(recommendations["by_algorithm"]),
            "data_structure_examples": len(recommendations["by_data_structure"])
        },
        "educational_value": educational_analysis,
        "code_quality_insights": quality_insights,
        "performance_analysis": performance_analysis,
        "collection_completeness": completeness_metrics,
        "next_phase_recommendations": {
            "expand_to_more_problems": f"Current coverage: {total_problems} problems, target: 100+ problems",
            "add_more_platforms": "Consider adding HackerRank, AtCoder solution collections",
            "automated_code_analysis": "Implement automated code review and quality assessment",
            "solution_clustering": "Group similar solutions for pattern recognition",
            "ml_model_training": "Use solution data for training recommendation models"
        }
    }


def save_phase3b_comprehensive_data(
    analytics: Dict[str, Any],
    learning_paths: Dict[str, Any],
    recommendations: Dict[str, Any],
    patterns: Dict[str, Any]
):
    """Save all Phase 3B comprehensive data"""
    print("💾 Saving Phase 3B comprehensive data...")
    
    # Create output directories
    phase3b_dir = Path("data/phase3b_solutions")
    final_exports_dir = Path("data/exports/phase3b_final")
    
    for directory in [phase3b_dir, final_exports_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save comprehensive analytics
    analytics_file = phase3b_dir / "phase3b_comprehensive_analytics.json"
    with open(analytics_file, 'w', encoding='utf-8') as f:
        json.dump(analytics, f, indent=2, ensure_ascii=False)
    saved_files['analytics'] = str(analytics_file)
    print(f"📊 Saved comprehensive analytics: {analytics_file}")
    
    # Save learning paths
    learning_paths_file = final_exports_dir / "learning_paths.json"
    with open(learning_paths_file, 'w', encoding='utf-8') as f:
        json.dump(learning_paths, f, indent=2, ensure_ascii=False)
    saved_files['learning_paths'] = str(learning_paths_file)
    print(f"🎓 Saved learning paths: {learning_paths_file}")
    
    # Save recommendations
    recommendations_file = final_exports_dir / "solution_recommendations.json"
    with open(recommendations_file, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False)
    saved_files['recommendations'] = str(recommendations_file)
    print(f"💡 Saved recommendations: {recommendations_file}")
    
    # Save solution patterns
    patterns_file = final_exports_dir / "solution_patterns.json"
    with open(patterns_file, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)
    saved_files['patterns'] = str(patterns_file)
    print(f"🔍 Saved solution patterns: {patterns_file}")
    
    # Save quick reference guides
    quick_guides = {
        "interview_preparation": {
            "must_know_solutions": [r["solution_id"] for r in recommendations["for_interviews"]["must_know"]],
            "study_order": learning_paths["interview_preparation_path"]["progression_levels"],
            "estimated_time": learning_paths["interview_preparation_path"]["estimated_study_time"],
            "key_algorithms": list(learning_paths["interview_preparation_path"]["algorithm_coverage"].keys())[:10]
        },
        "competitive_programming": {
            "contest_essentials": [r["solution_id"] for r in recommendations["for_competitive_programming"]["contest_essentials"]],
            "progression": learning_paths["competitive_programming_path"]["contest_progression"],
            "skill_development": learning_paths["competitive_programming_path"]["skill_development"]
        },
        "algorithm_quick_reference": {
            alg: {
                "best_example": rec["best_example"],
                "complexity": rec["complexity"],
                "platform": rec["platform"]
            }
            for alg, rec in recommendations["by_algorithm"].items()
        }
    }
    
    quick_guide_file = final_exports_dir / "quick_reference_guide.json"
    with open(quick_guide_file, 'w', encoding='utf-8') as f:
        json.dump(quick_guides, f, indent=2, ensure_ascii=False)
    saved_files['quick_guide'] = str(quick_guide_file)
    print(f"⚡ Saved quick reference guide: {quick_guide_file}")
    
    return saved_files


def print_phase3b_completion_summary(analytics: Dict[str, Any], saved_files: Dict[str, str]):
    """Print comprehensive Phase 3B completion summary"""
    print("\n" + "="*80)
    print("🎊 PHASE 3B: SOLUTION ANALYSIS COMPLETED!")
    print("="*80)
    
    summary = analytics['phase_3b_summary']
    platform_analysis = analytics['platform_analysis']
    educational = analytics['educational_value']
    quality = analytics['code_quality_insights']
    
    print(f"📊 COLLECTION SUMMARY:")
    print(f"   Total Problems: {summary['total_problems']}")
    print(f"   Total Solutions: {summary['total_solutions']}")
    print(f"   Platforms Covered: {summary['platforms_covered']}")
    
    print(f"\n🌐 PLATFORM BREAKDOWN:")
    for platform, stats in platform_analysis.items():
        print(f"   {platform.title()}:")
        print(f"     Problems: {stats['problems']} | Solutions: {stats['solutions']}")
        print(f"     Avg Quality: {stats['quality_metrics']['avg_quality']:.1f}")
        print(f"     Google Relevance: {stats['quality_metrics']['avg_google_relevance']:.1f}")
    
    print(f"\n🎯 CODE QUALITY METRICS:")
    print(f"   Overall Quality Score: {quality['overall_quality_score']:.1f}")
    print(f"   Well Documented Solutions: {quality['documentation_quality']['well_documented']}")
    print(f"   Quality by Platform:")
    for platform, score in quality['quality_by_platform'].items():
        print(f"     {platform.title()}: {score:.1f}")
    
    print(f"\n🎓 EDUCATIONAL VALUE:")
    print(f"   Interview-Ready Solutions: {educational['interview_ready_solutions']}")
    print(f"   High Educational Value: {educational['high_educational_value']}")
    print(f"   Learning Path Coverage:")
    for level, count in educational['learning_path_coverage'].items():
        print(f"     {level.title()}: {count} problems")
    
    print(f"\n🧠 ALGORITHM & PATTERN COVERAGE:")
    patterns = analytics['solution_patterns']
    print(f"   Algorithm Patterns: {len(patterns['algorithm_patterns'])}")
    print(f"   Data Structures: {len(patterns['data_structure_usage'])}")
    print(f"   Most Common Algorithms:")
    for alg in list(patterns['algorithm_patterns'].keys())[:5]:
        count = len(patterns['algorithm_patterns'][alg])
        print(f"     {alg}: {count} examples")
    
    print(f"\n📈 PERFORMANCE INSIGHTS:")
    performance = analytics['performance_analysis']
    print(f"   Fast Solutions (<50ms): {performance['runtime_distribution']['fast']}")
    print(f"   Optimal Time Complexity: {performance['complexity_efficiency']['optimal_time']}")
    print(f"   Space Efficient (O(1)): {performance['complexity_efficiency']['space_efficient']}")
    
    print(f"\n🎯 LEARNING PATHS CREATED:")
    learning_summary = analytics['learning_paths_summary']
    print(f"   Algorithm-Specific Paths: {learning_summary['total_algorithm_paths']}")
    print(f"   Interview Prep Solutions: {learning_summary['interview_prep_solutions']}")
    print(f"   Competitive Programming: {learning_summary['competitive_prog_solutions']}")
    print(f"   Total Study Time Estimate: {sum(learning_summary['estimated_study_time'].values())} minutes")
    
    print(f"\n💡 RECOMMENDATIONS GENERATED:")
    rec_summary = analytics['recommendations_summary']
    print(f"   Interview Must-Know: {rec_summary['interview_must_know']}")
    print(f"   Competitive Essentials: {rec_summary['competitive_essentials']}")
    print(f"   Learning Concept Builders: {rec_summary['learning_concept_builders']}")
    print(f"   Algorithm Examples: {rec_summary['algorithm_examples']}")
    print(f"   Data Structure Examples: {rec_summary['data_structure_examples']}")
    
    print(f"\n📁 KEY FILES CREATED:")
    for file_type, file_path in saved_files.items():
        print(f"   {file_type.replace('_', ' ').title()}: {file_path}")
    
    print(f"\n✅ PHASE 3B ACHIEVEMENTS:")
    for achievement in summary['phase_3b_achievements']:
        print(f"   ✓ {achievement}")
    
    print(f"\n🚀 READY FOR PHASE 4:")
    next_steps = analytics['next_phase_recommendations']
    for step, description in next_steps.items():
        print(f"   • {step.replace('_', ' ').title()}: {description}")
    
    print("="*80)
    print("🎉 PHASE 3B SOLUTION ANALYSIS SUCCESSFULLY COMPLETED! 🎉")
    print("="*80)


def main():
    """Main Phase 3B integration function"""
    print("Phase 3B Integration: Solution Analysis Completion")
    print("="*70)
    
    # Load all solution collections
    collections_by_platform = load_all_solution_collections()
    
    if not any(collections_by_platform.values()):
        print("❌ No solution collections found. Please run solution collectors first.")
        return
    
    # Extract all solutions
    all_solutions = extract_all_solutions(collections_by_platform)
    
    # Analyze solution patterns
    patterns = analyze_solution_patterns(all_solutions)
    
    # Create learning paths
    learning_paths = create_learning_paths(all_solutions, patterns)
    
    # Create recommendations
    recommendations = create_solution_recommendations(all_solutions, patterns)
    
    # Create comprehensive analytics
    analytics = create_phase3b_comprehensive_analytics(
        collections_by_platform, all_solutions, patterns, learning_paths, recommendations
    )
    
    # Save all data
    saved_files = save_phase3b_comprehensive_data(analytics, learning_paths, recommendations, patterns)
    
    # Print completion summary
    print_phase3b_completion_summary(analytics, saved_files)


if __name__ == "__main__":
    main()
