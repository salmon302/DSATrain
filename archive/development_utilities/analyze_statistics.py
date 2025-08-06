"""
Advanced Data Statistics Analysis for DSATrain
Focus on Difficulty and Google Relevance Calibration
"""

import json
from src.models.database import DatabaseConfig, Problem
from sqlalchemy import func, case, and_, or_
from collections import Counter, defaultdict
import statistics

def analyze_current_statistics():
    """Analyze current difficulty and Google relevance statistics"""
    
    db_config = DatabaseConfig()
    session = db_config.get_session()
    
    analysis_results = []
    analysis_results.append("🔍 DSATrain Data Statistics Analysis")
    analysis_results.append("=" * 60)
    analysis_results.append("")
    
    try:
        # 1. Current Difficulty Analysis
        analysis_results.append("📊 CURRENT DIFFICULTY DISTRIBUTION ANALYSIS")
        analysis_results.append("-" * 50)
        
        difficulty_stats = session.query(
            Problem.difficulty,
            func.count(Problem.id).label('count'),
            func.avg(Problem.quality_score).label('avg_quality'),
            func.avg(Problem.google_interview_relevance).label('avg_relevance'),
            func.min(Problem.google_interview_relevance).label('min_relevance'),
            func.max(Problem.google_interview_relevance).label('max_relevance'),
            func.avg(Problem.difficulty_rating).label('avg_rating')
        ).group_by(Problem.difficulty).all()
        
        total_problems = session.query(Problem).count()
        
        for diff_stat in difficulty_stats:
            difficulty = diff_stat.difficulty
            count = diff_stat.count
            percentage = (count / total_problems * 100)
            avg_quality = diff_stat.avg_quality or 0
            avg_relevance = diff_stat.avg_relevance or 0
            min_relevance = diff_stat.min_relevance or 0
            max_relevance = diff_stat.max_relevance or 0
            avg_rating = diff_stat.avg_rating or 0
            
            analysis_results.append(f"• {difficulty} ({count:,} problems, {percentage:.1f}%)")
            analysis_results.append(f"  └─ Quality: {avg_quality:.2f} | Google Relevance: {avg_relevance:.2f} (range: {min_relevance:.1f}-{max_relevance:.1f})")
            analysis_results.append(f"  └─ Difficulty Rating: {avg_rating:.0f}")
            analysis_results.append("")
        
        # 2. Google Relevance Deep Analysis
        analysis_results.append("🎯 GOOGLE RELEVANCE DEEP ANALYSIS")
        analysis_results.append("-" * 50)
        
        # Relevance distribution by ranges
        relevance_ranges = [
            ("Excellent (9-10)", 9.0, 10.0),
            ("Very High (8-9)", 8.0, 8.9),
            ("High (7-8)", 7.0, 7.9),
            ("Good (6-7)", 6.0, 6.9),
            ("Moderate (5-6)", 5.0, 5.9),
            ("Low (3-5)", 3.0, 4.9),
            ("Very Low (1-3)", 1.0, 2.9),
            ("Minimal (0-1)", 0.0, 0.9)
        ]
        
        for range_name, min_val, max_val in relevance_ranges:
            count = session.query(Problem).filter(
                and_(
                    Problem.google_interview_relevance >= min_val,
                    Problem.google_interview_relevance <= max_val
                )
            ).count()
            percentage = (count / total_problems * 100) if total_problems > 0 else 0
            analysis_results.append(f"• {range_name:<20}: {count:>5,} problems ({percentage:5.1f}%)")
        
        analysis_results.append("")
        
        # 3. Platform-specific Analysis
        analysis_results.append("🌐 PLATFORM-SPECIFIC RELEVANCE ANALYSIS")
        analysis_results.append("-" * 50)
        
        platform_relevance = session.query(
            Problem.platform,
            func.count(Problem.id).label('count'),
            func.avg(Problem.google_interview_relevance).label('avg_relevance'),
            func.count(case([(Problem.google_interview_relevance >= 8.0, 1)])).label('high_relevance'),
            func.count(case([(Problem.google_interview_relevance >= 6.0, 1)])).label('good_relevance')
        ).group_by(Problem.platform).all()
        
        for platform_stat in platform_relevance:
            platform = platform_stat.platform
            count = platform_stat.count
            avg_relevance = platform_stat.avg_relevance or 0
            high_count = platform_stat.high_relevance or 0
            good_count = platform_stat.good_relevance or 0
            
            high_percentage = (high_count / count * 100) if count > 0 else 0
            good_percentage = (good_count / count * 100) if count > 0 else 0
            
            analysis_results.append(f"• {platform.upper()}:")
            analysis_results.append(f"  └─ Average Relevance: {avg_relevance:.2f}")
            analysis_results.append(f"  └─ High Relevance (8+): {high_count:,} ({high_percentage:.1f}%)")
            analysis_results.append(f"  └─ Good Relevance (6+): {good_count:,} ({good_percentage:.1f}%)")
            analysis_results.append("")
        
        # 4. Algorithm Tag vs Relevance Analysis
        analysis_results.append("🧮 ALGORITHM TAG vs GOOGLE RELEVANCE")
        analysis_results.append("-" * 50)
        
        # Get all problems with their tags and relevance
        problems_with_tags = session.query(
            Problem.algorithm_tags,
            Problem.google_interview_relevance,
            Problem.difficulty
        ).all()
        
        tag_relevance_map = defaultdict(list)
        for problem in problems_with_tags:
            if problem.algorithm_tags and problem.google_interview_relevance is not None:
                for tag in problem.algorithm_tags:
                    tag_relevance_map[tag].append(problem.google_interview_relevance)
        
        # Calculate statistics for each tag
        tag_stats = []
        for tag, relevances in tag_relevance_map.items():
            if len(relevances) >= 10:  # Only tags with sufficient data
                avg_relevance = statistics.mean(relevances)
                high_relevance_count = sum(1 for r in relevances if r >= 8.0)
                high_percentage = (high_relevance_count / len(relevances) * 100)
                
                tag_stats.append({
                    'tag': tag,
                    'count': len(relevances),
                    'avg_relevance': avg_relevance,
                    'high_percentage': high_percentage
                })
        
        # Sort by average relevance (descending)
        tag_stats.sort(key=lambda x: x['avg_relevance'], reverse=True)
        
        analysis_results.append("Top 15 Algorithm Tags by Google Interview Relevance:")
        analysis_results.append("")
        for i, tag_stat in enumerate(tag_stats[:15], 1):
            tag = tag_stat['tag']
            count = tag_stat['count']
            avg_rel = tag_stat['avg_relevance']
            high_pct = tag_stat['high_percentage']
            
            analysis_results.append(f"{i:2d}. {tag:<25} | {count:>4} problems | Avg: {avg_rel:5.2f} | High: {high_pct:5.1f}%")
        
        analysis_results.append("")
        analysis_results.append("Bottom 10 Algorithm Tags by Google Interview Relevance:")
        analysis_results.append("")
        for i, tag_stat in enumerate(tag_stats[-10:], 1):
            tag = tag_stat['tag']
            count = tag_stat['count']
            avg_rel = tag_stat['avg_relevance']
            high_pct = tag_stat['high_percentage']
            
            analysis_results.append(f"{i:2d}. {tag:<25} | {count:>4} problems | Avg: {avg_rel:5.2f} | High: {high_pct:5.1f}%")
        
        analysis_results.append("")
        
        # 5. Issues and Recommendations
        analysis_results.append("⚠️  IDENTIFIED ISSUES & IMPROVEMENT OPPORTUNITIES")
        analysis_results.append("-" * 50)
        
        # Calculate some key metrics for analysis
        total_high_relevance = session.query(Problem).filter(Problem.google_interview_relevance >= 8.0).count()
        total_low_relevance = session.query(Problem).filter(Problem.google_interview_relevance <= 3.0).count()
        
        high_percentage = (total_high_relevance / total_problems * 100)
        low_percentage = (total_low_relevance / total_problems * 100)
        
        analysis_results.append("🔍 Current Issues:")
        analysis_results.append(f"• Only {high_percentage:.1f}% of problems are highly Google-relevant (8+)")
        analysis_results.append(f"• {low_percentage:.1f}% of problems have low Google relevance (≤3)")
        analysis_results.append("• Codeforces problems have much lower relevance than LeetCode")
        analysis_results.append("• Some algorithm tags show consistently low interview relevance")
        analysis_results.append("")
        
        analysis_results.append("💡 Recommended Improvements:")
        analysis_results.append("• Implement intelligent relevance scoring based on algorithm tags")
        analysis_results.append("• Create company-specific relevance scores (Google, Amazon, Microsoft)")
        analysis_results.append("• Add difficulty calibration based on solve rates and user feedback")
        analysis_results.append("• Implement dynamic relevance updates based on user interactions")
        analysis_results.append("• Create interview question pattern matching")
        analysis_results.append("")
        
        # 6. Calibration Targets
        analysis_results.append("🎯 CALIBRATION TARGETS")
        analysis_results.append("-" * 50)
        analysis_results.append("Ideal Distribution Goals:")
        analysis_results.append("• High Google Relevance (8+): 15-20% of problems")
        analysis_results.append("• Good Google Relevance (6+): 40-50% of problems")
        analysis_results.append("• Interview-relevant algorithms: Prioritize based on actual usage")
        analysis_results.append("• Difficulty balance: 30% Easy, 40% Medium, 30% Hard")
        analysis_results.append("• Platform balance: Maintain quality while expanding coverage")
        analysis_results.append("")
        
    except Exception as e:
        analysis_results.append(f"❌ Error during analysis: {e}")
    finally:
        session.close()
    
    # Write results to file
    with open("statistics_analysis.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(analysis_results))
    
    print("📊 Statistics analysis complete!")
    print("📄 Detailed analysis saved to: statistics_analysis.txt")
    print("🎯 Ready to implement improvements!")

if __name__ == "__main__":
    analyze_current_statistics()
