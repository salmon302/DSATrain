"""
Google-Style Code Editor Demo
Showcase the enhanced features without needing full backend setup
"""

from src.analysis.google_analyzer import GoogleStyleCodeAnalyzer

def demo_interview_simulation():
    """Demonstrate Google interview simulation features"""
    
    print("🎯 Google Interview Simulation Demo")
    print("=" * 50)
    
    analyzer = GoogleStyleCodeAnalyzer()
    
    # Simulate a candidate solving Two Sum problem
    print("\n📝 Problem: Two Sum")
    print("Given an array of integers nums and an integer target,")
    print("return indices of the two numbers such that they add up to target.")
    
    # Phase 1: Brute Force Approach (typical first attempt)
    print("\n🔄 Phase 1: Initial Brute Force Approach")
    brute_force_code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
    """
    
    # Simulate thinking out loud
    communication_notes_1 = [
        "I'll start with a brute force approach",
        "Check every pair of numbers",
        "This will work but might not be optimal"
    ]
    
    analysis_1 = perform_analysis(analyzer, brute_force_code, "python", 
                                300, True, communication_notes_1, "Brute Force")
    
    # Phase 2: Optimized Hash Map Approach
    print("\n⚡ Phase 2: Optimized Hash Map Approach")
    optimized_code = """
def two_sum(nums, target):
    \"\"\"
    Find two numbers that add up to target using hash map.
    Time: O(n), Space: O(n)
    \"\"\"
    num_to_index = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_to_index:
            return [num_to_index[complement], i]
        num_to_index[num] = i
    
    return []  # No solution found

# Test cases
test_cases = [
    ([2, 7, 11, 15], 9),    # Expected: [0, 1]
    ([3, 2, 4], 6),         # Expected: [1, 2]
    ([3, 3], 6)             # Expected: [0, 1]
]

for nums, target in test_cases:
    result = two_sum(nums, target)
    print(f"Input: {nums}, Target: {target}, Output: {result}")
    """
    
    # Enhanced communication notes
    communication_notes_2 = [
        "Let me optimize this with a hash map",
        "I can solve this in one pass",
        "Trade space for time complexity",
        "Hash map gives O(1) lookups",
        "Added comprehensive documentation",
        "Included test cases for verification"
    ]
    
    analysis_2 = perform_analysis(analyzer, optimized_code, "python", 
                                600, True, communication_notes_2, "Optimized Hash Map")
    
    # Compare the two approaches
    print("\n📊 Interview Performance Comparison")
    print("=" * 50)
    
    comparison_data = [
        ("Approach", "Brute Force", "Hash Map"),
        ("Time Complexity", analysis_1.complexity.time_complexity, analysis_2.complexity.time_complexity),
        ("Space Complexity", analysis_1.complexity.space_complexity, analysis_2.complexity.space_complexity),
        ("Code Quality", f"{analysis_1.quality.overall_score}/100", f"{analysis_2.quality.overall_score}/100"),
        ("GCA Score", f"{analysis_1.google_criteria.gca_score}/100", f"{analysis_2.google_criteria.gca_score}/100"),
        ("RRK Score", f"{analysis_1.google_criteria.rrk_score}/100", f"{analysis_2.google_criteria.rrk_score}/100"),
        ("Communication", f"{analysis_1.google_criteria.communication_score}/100", f"{analysis_2.google_criteria.communication_score}/100"),
        ("Googleyness", f"{analysis_1.google_criteria.googleyness_score}/100", f"{analysis_2.google_criteria.googleyness_score}/100"),
        ("Overall Score", f"{analysis_1.google_criteria.overall_score}/100", f"{analysis_2.google_criteria.overall_score}/100"),
    ]
    
    for metric, score1, score2 in comparison_data:
        improvement = "📈" if score2 > score1 else "📊" if score2 == score1 else "📉"
        print(f"{metric:15} | {score1:12} | {score2:12} | {improvement}")
    
    print("\n💡 Key Interview Insights:")
    print("• Started with working solution, then optimized (excellent approach)")
    print("• Demonstrated strong algorithmic thinking progression")
    print("• Excellent communication throughout the process")
    print("• Added documentation and test cases (shows engineering mindset)")
    print("• Final solution meets Google's efficiency standards")

def perform_analysis(analyzer, code, language, time_spent, thinking_out_loud, 
                    communication_notes, approach_name):
    """Perform comprehensive analysis and display results"""
    
    print(f"\n🔍 Analyzing {approach_name}...")
    
    # Core analyses
    complexity = analyzer.analyze_complexity(code, language)
    quality = analyzer.analyze_code_quality(code, language)
    google_criteria = analyzer.evaluate_google_criteria(
        code=code,
        language=language,
        time_spent=time_spent,
        thinking_out_loud=thinking_out_loud,
        communication_notes=communication_notes,
        complexity=complexity,
        quality=quality
    )
    
    # Create result object for easier access
    class AnalysisResult:
        def __init__(self):
            self.complexity = complexity
            self.quality = quality
            self.google_criteria = google_criteria
    
    result = AnalysisResult()
    
    # Display key metrics
    print(f"⏱️  Complexity: {complexity.time_complexity} time, {complexity.space_complexity} space")
    print(f"📊 Code Quality: {quality.overall_score}/100")
    print(f"🎓 Google Score: {google_criteria.overall_score}/100")
    print(f"💬 Communication: {len(communication_notes)} explanations provided")
    
    return result

def demo_google_doc_simulation():
    """Demonstrate the Google Doc coding environment simulation"""
    
    print("\n📝 Google Doc Environment Simulation")
    print("=" * 50)
    
    print("🎯 Features of Google Interview Environment:")
    print("• Plain text editor (no syntax highlighting)")
    print("• No auto-completion or IntelliSense")
    print("• No debugging tools")
    print("• Must write test cases manually")
    print("• Time pressure (45 minutes typical)")
    print("• Thinking out loud required")
    print("• Collaborative problem-solving")
    
    print("\n⚙️  Editor Configuration for Google Doc Mode:")
    config = {
        "lineNumbers": "off",
        "minimap": False,
        "quickSuggestions": False,
        "parameterHints": False,
        "wordBasedSuggestions": False,
        "theme": "google-doc-plain",
        "fontSize": 14,
        "glyphMargin": False,
        "folding": False
    }
    
    for feature, setting in config.items():
        print(f"  • {feature}: {setting}")
    
    print("\n🎤 Communication Tracking:")
    sample_notes = [
        "00:02 - Reading and understanding the problem",
        "00:05 - Explaining my initial approach",
        "00:08 - Discussing time complexity concerns",
        "00:15 - Implementing the brute force solution",
        "00:20 - Testing with example cases",
        "00:25 - Optimizing with hash map approach",
        "00:35 - Final solution with documentation",
        "00:40 - Discussing edge cases and trade-offs"
    ]
    
    for note in sample_notes:
        print(f"  📝 {note}")

def demo_improvement_suggestions():
    """Demonstrate improvement suggestions based on analysis"""
    
    print("\n💡 Improvement Suggestions Demo")
    print("=" * 50)
    
    analyzer = GoogleStyleCodeAnalyzer()
    
    # Example of poorly written code
    poor_code = """
def f(a,t):
    for i in range(len(a)):
        for j in range(len(a)):
            if a[i]+a[j]==t:
                return [i,j]
    """
    
    complexity = analyzer.analyze_complexity(poor_code, "python")
    quality = analyzer.analyze_code_quality(poor_code, "python")
    google_criteria = analyzer.evaluate_google_criteria(
        code=poor_code,
        language="python",
        time_spent=1800,  # 30 minutes
        thinking_out_loud=False,
        communication_notes=[],
        complexity=complexity,
        quality=quality
    )
    
    print("📉 Analysis of Poor Code Example:")
    print(f"Code Quality: {quality.overall_score}/100")
    print(f"Google Score: {google_criteria.overall_score}/100")
    
    print("\n🎯 Improvement Suggestions:")
    suggestions = [
        "Use descriptive variable names (nums, target instead of a, t)",
        "Add docstring explaining the function purpose",
        "Fix bug: j should start from i+1 to avoid duplicate pairs",
        "Optimize time complexity from O(n²) to O(n) using hash map",
        "Add type hints for better code documentation",
        "Include test cases to verify correctness",
        "Add comments explaining the algorithm approach",
        "Consider edge cases (empty array, no solution)",
        "Practice explaining your thought process out loud",
        "Follow PEP 8 style guidelines for Python"
    ]
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i:2}. {suggestion}")
    
    print("\n🏆 After Implementing Suggestions:")
    improved_code = """
def two_sum(nums: List[int], target: int) -> List[int]:
    \"\"\"
    Find indices of two numbers that add up to target.
    
    Args:
        nums: List of integers
        target: Target sum value
        
    Returns:
        List containing indices of the two numbers, or empty list if no solution
        
    Time Complexity: O(n)
    Space Complexity: O(n)
    \"\"\"
    # Use hash map for O(1) lookup time
    num_to_index = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        
        # Check if complement exists in hash map
        if complement in num_to_index:
            return [num_to_index[complement], i]
        
        # Store current number and its index
        num_to_index[num] = i
    
    # No solution found
    return []

# Test cases to verify correctness
test_cases = [
    ([2, 7, 11, 15], 9, [0, 1]),  # Standard case
    ([3, 2, 4], 6, [1, 2]),       # Different order
    ([3, 3], 6, [0, 1]),          # Duplicate numbers
    ([1, 2, 3], 7, [])            # No solution
]

for nums, target, expected in test_cases:
    result = two_sum(nums, target)
    status = "✅" if result == expected else "❌"
    print(f"{status} Input: {nums}, Target: {target}, Got: {result}, Expected: {expected}")
    """
    
    improved_complexity = analyzer.analyze_complexity(improved_code, "python")
    improved_quality = analyzer.analyze_code_quality(improved_code, "python")
    improved_google = analyzer.evaluate_google_criteria(
        code=improved_code,
        language="python",
        time_spent=1200,  # 20 minutes
        thinking_out_loud=True,
        communication_notes=["Explained approach", "Discussed complexity", "Added test cases"],
        complexity=improved_complexity,
        quality=improved_quality
    )
    
    print(f"\n📈 Improved Code Quality: {improved_quality.overall_score}/100 (+{improved_quality.overall_score - quality.overall_score})")
    print(f"🎓 Improved Google Score: {improved_google.overall_score}/100 (+{improved_google.overall_score - google_criteria.overall_score})")
    
    print("\n✨ Key Improvements Achieved:")
    improvements = [
        f"Time Complexity: {complexity.time_complexity} → {improved_complexity.time_complexity}",
        f"Documentation: {quality.documentation}/100 → {improved_quality.documentation}/100",
        f"Naming: {quality.naming_conventions}/100 → {improved_quality.naming_conventions}/100",
        f"Best Practices: {quality.best_practices}/100 → {improved_quality.best_practices}/100",
        f"Communication: {google_criteria.communication_score}/100 → {improved_google.communication_score}/100"
    ]
    
    for improvement in improvements:
        print(f"  • {improvement}")

if __name__ == "__main__":
    print("🚀 DSATrain Google Enhancement Showcase")
    print("🎯 Demonstrating Google Interview Methodologies")
    print("\n" + "=" * 60)
    
    try:
        # Main demo sections
        demo_interview_simulation()
        demo_google_doc_simulation()
        demo_improvement_suggestions()
        
        print("\n" + "=" * 60)
        print("✅ Google Enhancement Demo Complete!")
        print("\n🎓 What You've Seen:")
        print("• Real-time code analysis using Google's criteria")
        print("• Interview simulation with thinking out loud")
        print("• Complexity analysis and optimization guidance") 
        print("• Code quality assessment based on Google standards")
        print("• Improvement suggestions for interview success")
        
        print("\n🚀 Ready for Google Interviews:")
        print("• Practice with realistic interview constraints")
        print("• Get feedback on all four Google criteria")
        print("• Learn to communicate effectively while coding")
        print("• Develop Google-level engineering practices")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
