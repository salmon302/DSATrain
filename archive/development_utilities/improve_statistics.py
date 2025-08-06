"""
Enhanced Data Statistics and Calibration System for DSATrain
"""

import json
from src.models.database import DatabaseConfig, Problem
from sqlalchemy import func, and_, or_, text
from collections import Counter, defaultdict
import statistics
import numpy as np

class DataStatisticsImprover:
    """Enhanced statistics and calibration system"""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.session = self.db_config.get_session()
        
    def analyze_current_state(self):
        """Comprehensive analysis of current data state"""
        print("🔍 Analyzing current data statistics...")
        
        # Basic counts
        total_problems = self.session.query(Problem).count()
        print(f"📊 Total problems: {total_problems:,}")
        
        # Google relevance analysis
        high_relevance = self.session.query(Problem).filter(Problem.google_interview_relevance >= 8.0).count()
        medium_relevance = self.session.query(Problem).filter(
            and_(Problem.google_interview_relevance >= 5.0, Problem.google_interview_relevance < 8.0)
        ).count()
        low_relevance = self.session.query(Problem).filter(Problem.google_interview_relevance < 5.0).count()
        
        print(f"🎯 Google Relevance Distribution:")
        print(f"   High (8+): {high_relevance:,} ({high_relevance/total_problems*100:.1f}%)")
        print(f"   Medium (5-8): {medium_relevance:,} ({medium_relevance/total_problems*100:.1f}%)")
        print(f"   Low (<5): {low_relevance:,} ({low_relevance/total_problems*100:.1f}%)")
        
        return {
            'total_problems': total_problems,
            'high_relevance': high_relevance,
            'medium_relevance': medium_relevance,
            'low_relevance': low_relevance
        }
    
    def calculate_algorithm_relevance_scores(self):
        """Calculate interview relevance scores for algorithm tags"""
        print("🧮 Calculating algorithm tag relevance scores...")
        
        # Define interview-relevant algorithm tags based on common patterns
        algorithm_relevance_map = {
            # High relevance (8-10) - Core interview topics
            'dynamic_programming': 9.5,
            'dp': 9.5,
            'binary_search': 9.0,
            'two_pointers': 9.0,
            'sliding_window': 9.0,
            'hash_map': 9.0,
            'trees': 8.5,
            'graphs': 8.5,
            'dfs_and_similar': 8.5,
            'bfs': 8.5,
            'linked_lists': 8.5,
            'arrays': 8.5,
            'strings': 8.0,
            'sorting': 8.0,
            'sortings': 8.0,
            'greedy': 8.0,
            'backtracking': 8.0,
            
            # Medium relevance (5-7) - Important but less common
            'data_structures': 7.0,
            'stack': 7.0,
            'queue': 7.0,
            'heap': 7.0,
            'trie': 7.0,
            'graph_traversal': 7.0,
            'divide_and_conquer': 6.5,
            'recursion': 6.5,
            'bit_manipulation': 6.5,
            'bitmasks': 6.5,
            'math': 6.0,
            'number_theory': 5.5,
            'combinatorics': 5.5,
            'implementation': 5.0,
            
            # Lower relevance (2-4) - Specialized topics
            'geometry': 3.0,
            'string_matching': 4.0,
            'flows': 3.0,
            'network_flows': 3.0,
            '2-sat': 2.0,
            'fft': 2.0,
            'chinese_remainder_theorem': 2.0,
            'matrix': 4.0,
            'linear_algebra': 3.0,
            'game_theory': 3.0,
            'probabilistic': 3.0,
            
            # Very specialized (1-2) - Competitive programming specific
            'meet-in-the-middle': 2.0,
            'ternary_search': 2.0,
            'heavy-light_decomposition': 1.0,
            'centroid_decomposition': 1.0,
            'suffix_array': 2.0,
            'persistent_data_structures': 1.5,
            '*special': 1.0
        }
        
        return algorithm_relevance_map
    
    def improve_google_relevance_scores(self):
        """Improve Google relevance scores based on algorithm tags and other factors"""
        print("🎯 Improving Google relevance scores...")
        
        algorithm_relevance = self.calculate_algorithm_relevance_scores()
        
        # Get all problems
        problems = self.session.query(Problem).all()
        updated_count = 0
        
        for problem in problems:
            # Calculate new relevance score
            new_relevance = self.calculate_enhanced_relevance(problem, algorithm_relevance)
            
            # Only update if there's a significant change
            if abs(new_relevance - (problem.google_interview_relevance or 0)) > 0.1:
                problem.google_interview_relevance = new_relevance
                updated_count += 1
                
                if updated_count % 1000 == 0:
                    print(f"   Updated {updated_count} problems...")
        
        # Commit changes
        self.session.commit()
        print(f"✅ Updated {updated_count} problem relevance scores")
        
        return updated_count
    
    def calculate_enhanced_relevance(self, problem, algorithm_relevance_map):
        """Calculate enhanced relevance score for a problem"""
        base_score = 0.0
        
        # 1. Algorithm tag based scoring (main factor)
        if problem.algorithm_tags:
            tag_scores = []
            for tag in problem.algorithm_tags:
                # Check exact match first
                if tag in algorithm_relevance_map:
                    tag_scores.append(algorithm_relevance_map[tag])
                else:
                    # Check partial matches
                    partial_score = 0
                    for known_tag, score in algorithm_relevance_map.items():
                        if known_tag in tag or tag in known_tag:
                            partial_score = max(partial_score, score * 0.8)  # Reduced score for partial match
                    if partial_score > 0:
                        tag_scores.append(partial_score)
                    else:
                        # Default score for unknown tags
                        tag_scores.append(3.0)
            
            if tag_scores:
                # Use weighted average, giving more weight to higher scores
                tag_scores.sort(reverse=True)
                if len(tag_scores) == 1:
                    base_score = tag_scores[0]
                else:
                    # Weight: 60% highest score, 30% second highest, 10% others
                    if len(tag_scores) == 2:
                        weights = [0.6, 0.4]
                    else:
                        remaining_weight = 0.1 / max(1, len(tag_scores) - 2)
                        weights = [0.6, 0.3] + [remaining_weight] * (len(tag_scores) - 2)
                    base_score = sum(score * weight for score, weight in zip(tag_scores, weights))
        else:
            base_score = 3.0  # Default for problems without tags
        
        # 2. Platform adjustments
        platform_multipliers = {
            'leetcode': 1.2,  # LeetCode problems are generally more interview-focused
            'codeforces': 0.8,  # Codeforces can be more competitive programming focused
            'hackerrank': 1.0,
            'atcoder': 0.9,
            'codechef': 0.9
        }
        
        platform_multiplier = platform_multipliers.get(problem.platform.lower(), 1.0)
        base_score *= platform_multiplier
        
        # 3. Difficulty adjustments
        difficulty_adjustments = {
            'Easy': 0.1,    # Slight boost for easy problems (good for interviews)
            'Medium': 0.2,  # Boost for medium problems (most common in interviews)
            'Hard': -0.1    # Slight penalty for hard problems (less common in interviews)
        }
        
        difficulty_adj = difficulty_adjustments.get(problem.difficulty, 0)
        base_score += difficulty_adj
        
        # 4. Quality factor (high quality problems are more likely to be asked)
        if problem.quality_score and problem.quality_score >= 95:
            base_score += 0.3
        elif problem.quality_score and problem.quality_score >= 90:
            base_score += 0.1
        
        # 5. Ensure score is within bounds
        base_score = max(0.0, min(10.0, base_score))
        
        # 6. Round to 1 decimal place
        return round(base_score, 1)
    
    def improve_difficulty_ratings(self):
        """Improve difficulty ratings based on multiple factors"""
        print("⭐ Improving difficulty ratings...")
        
        problems = self.session.query(Problem).all()
        updated_count = 0
        
        for problem in problems:
            new_rating = self.calculate_enhanced_difficulty_rating(problem)
            
            if abs(new_rating - (problem.difficulty_rating or 0)) > 10:
                problem.difficulty_rating = new_rating
                updated_count += 1
                
                if updated_count % 1000 == 0:
                    print(f"   Updated {updated_count} problems...")
        
        self.session.commit()
        print(f"✅ Updated {updated_count} problem difficulty ratings")
        
        return updated_count
    
    def calculate_enhanced_difficulty_rating(self, problem):
        """Calculate enhanced difficulty rating"""
        
        # Base ratings by difficulty level
        base_ratings = {
            'Easy': 1200,
            'Medium': 1600,
            'Hard': 2100
        }
        
        base_rating = base_ratings.get(problem.difficulty, 1500)
        
        # Adjust based on algorithm complexity
        complexity_adjustments = {
            'dp': 200,
            'dynamic_programming': 200,
            'graphs': 150,
            'trees': 100,
            'dfs_and_similar': 100,
            'binary_search': 50,
            'two_pointers': -50,
            'greedy': 0,
            'implementation': -100,
            'brute_force': -150,
            'math': 100,
            'geometry': 200,
            'flows': 300,
            'fft': 400,
            'string_matching': 150
        }
        
        if problem.algorithm_tags:
            max_adjustment = 0
            for tag in problem.algorithm_tags:
                for complex_tag, adjustment in complexity_adjustments.items():
                    if complex_tag in tag.lower() or tag.lower() in complex_tag:
                        max_adjustment = max(max_adjustment, adjustment)
            
            base_rating += max_adjustment
        
        # Platform adjustments
        platform_adjustments = {
            'leetcode': 0,      # LeetCode ratings are fairly accurate
            'codeforces': -100,  # Codeforces can be slightly harder
            'hackerrank': -50,
            'atcoder': 0,
            'codechef': -50
        }
        
        platform_adj = platform_adjustments.get(problem.platform.lower(), 0)
        base_rating += platform_adj
        
        # Ensure rating is within reasonable bounds
        base_rating = max(800, min(3500, base_rating))
        
        return base_rating
    
    def generate_improved_statistics(self):
        """Generate comprehensive statistics after improvements"""
        print("📊 Generating improved statistics...")
        
        stats = {}
        
        # Total counts
        stats['total_problems'] = self.session.query(Problem).count()
        
        # Google relevance distribution
        relevance_ranges = [
            ('excellent', 9.0, 10.0),
            ('very_high', 8.0, 9.0),
            ('high', 7.0, 8.0),
            ('good', 6.0, 7.0),
            ('moderate', 5.0, 6.0),
            ('low', 3.0, 5.0),
            ('very_low', 0.0, 3.0)
        ]
        
        stats['relevance_distribution'] = {}
        for range_name, min_val, max_val in relevance_ranges:
            count = self.session.query(Problem).filter(
                and_(
                    Problem.google_interview_relevance >= min_val,
                    Problem.google_interview_relevance < max_val
                )
            ).count()
            stats['relevance_distribution'][range_name] = {
                'count': count,
                'percentage': count / stats['total_problems'] * 100
            }
        
        # Difficulty distribution
        difficulty_stats = self.session.query(
            Problem.difficulty,
            func.count(Problem.id).label('count'),
            func.avg(Problem.google_interview_relevance).label('avg_relevance'),
            func.avg(Problem.difficulty_rating).label('avg_rating')
        ).group_by(Problem.difficulty).all()
        
        stats['difficulty_distribution'] = {}
        for diff_stat in difficulty_stats:
            stats['difficulty_distribution'][diff_stat.difficulty] = {
                'count': diff_stat.count,
                'percentage': diff_stat.count / stats['total_problems'] * 100,
                'avg_relevance': diff_stat.avg_relevance,
                'avg_rating': diff_stat.avg_rating
            }
        
        # Platform statistics
        platform_stats = self.session.query(
            Problem.platform,
            func.count(Problem.id).label('count'),
            func.avg(Problem.google_interview_relevance).label('avg_relevance')
        ).group_by(Problem.platform).all()
        
        stats['platform_distribution'] = {}
        for platform_stat in platform_stats:
            stats['platform_distribution'][platform_stat.platform] = {
                'count': platform_stat.count,
                'percentage': platform_stat.count / stats['total_problems'] * 100,
                'avg_relevance': platform_stat.avg_relevance
            }
        
        return stats
    
    def save_statistics_report(self, stats):
        """Save comprehensive statistics report"""
        report = []
        report.append("🚀 Enhanced DSATrain Statistics Report")
        report.append("=" * 60)
        report.append(f"Generated on: {str(self.session.query(func.now()).scalar())}")
        report.append("")
        
        # Overview
        report.append("📊 OVERVIEW")
        report.append("-" * 30)
        report.append(f"Total Problems: {stats['total_problems']:,}")
        report.append("")
        
        # Google Relevance Distribution
        report.append("🎯 GOOGLE INTERVIEW RELEVANCE DISTRIBUTION")
        report.append("-" * 50)
        for range_name, data in stats['relevance_distribution'].items():
            count = data['count']
            percentage = data['percentage']
            report.append(f"• {range_name.replace('_', ' ').title():<15}: {count:>6,} problems ({percentage:5.1f}%)")
        report.append("")
        
        # Difficulty Distribution
        report.append("⭐ DIFFICULTY DISTRIBUTION")
        report.append("-" * 30)
        for difficulty, data in stats['difficulty_distribution'].items():
            count = data['count']
            percentage = data['percentage']
            avg_relevance = data['avg_relevance'] or 0
            avg_rating = data['avg_rating'] or 0
            report.append(f"• {difficulty}:")
            report.append(f"  └─ Count: {count:,} ({percentage:.1f}%)")
            report.append(f"  └─ Avg Relevance: {avg_relevance:.2f}")
            report.append(f"  └─ Avg Rating: {avg_rating:.0f}")
            report.append("")
        
        # Platform Distribution
        report.append("🌐 PLATFORM DISTRIBUTION")
        report.append("-" * 30)
        for platform, data in stats['platform_distribution'].items():
            count = data['count']
            percentage = data['percentage']
            avg_relevance = data['avg_relevance'] or 0
            report.append(f"• {platform.upper()}:")
            report.append(f"  └─ Count: {count:,} ({percentage:.1f}%)")
            report.append(f"  └─ Avg Relevance: {avg_relevance:.2f}")
            report.append("")
        
        # Improvements summary
        high_relevance_count = stats['relevance_distribution']['very_high']['count'] + stats['relevance_distribution']['excellent']['count']
        high_relevance_pct = high_relevance_count / stats['total_problems'] * 100
        
        report.append("✅ IMPROVEMENTS ACHIEVED")
        report.append("-" * 30)
        report.append(f"• High Google Relevance (8+): {high_relevance_count:,} problems ({high_relevance_pct:.1f}%)")
        report.append("• Enhanced algorithm-based relevance scoring")
        report.append("• Improved difficulty rating calibration")
        report.append("• Platform-specific adjustments applied")
        report.append("• Quality-based relevance bonuses added")
        report.append("")
        
        with open("enhanced_statistics_report.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        
        print("📄 Enhanced statistics report saved to: enhanced_statistics_report.txt")
    
    def close(self):
        """Close database session"""
        self.session.close()

def main():
    """Main function to run statistics improvements"""
    print("🚀 Starting DSATrain Statistics Enhancement")
    print("=" * 50)
    
    improver = DataStatisticsImprover()
    
    try:
        # 1. Analyze current state
        current_stats = improver.analyze_current_state()
        print()
        
        # 2. Improve Google relevance scores
        relevance_updates = improver.improve_google_relevance_scores()
        print()
        
        # 3. Improve difficulty ratings
        difficulty_updates = improver.improve_difficulty_ratings()
        print()
        
        # 4. Generate improved statistics
        improved_stats = improver.generate_improved_statistics()
        
        # 5. Save comprehensive report
        improver.save_statistics_report(improved_stats)
        
        print()
        print("🎉 Statistics Enhancement Complete!")
        print(f"✅ Updated {relevance_updates} relevance scores")
        print(f"✅ Updated {difficulty_updates} difficulty ratings")
        print("📊 Enhanced statistics system ready!")
        
    except Exception as e:
        print(f"❌ Error during enhancement: {e}")
    finally:
        improver.close()

if __name__ == "__main__":
    main()
