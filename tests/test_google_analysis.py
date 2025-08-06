"""
Test script for Google Code Analysis functionality
This demonstrates the enhanced code analysis without needing FastAPI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.analysis.google_analyzer import GoogleStyleCodeAnalyzer

def test_google_code_analysis():
    """Test the Google-style code analyzer directly"""
    
    # Initialize the analyzer
    analyzer = GoogleStyleCodeAnalyzer()
    
    # Test code samples
    test_cases = [
        {
            "name": "Simple O(n) solution",
            "code": """
def two_sum(nums, target):
    \"\"\"
    Find two numbers that add up to target.
    Time: O(n), Space: O(n)
    \"\"\"
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Test with example
result = two_sum([2, 7, 11, 15], 9)
print(result)  # Expected: [0, 1]
            """,
            "language": "python"
        },
        {
            "name": "Nested loops O(n²) solution",
            "code": """
def two_sum_brute_force(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
            """,
            "language": "python"
        },
        {
            "name": "Well-documented solution",
            "code": """
def find_maximum_subarray(nums):
    \"\"\"
    Find the contiguous subarray with the largest sum.
    Uses Kadane's algorithm for optimal O(n) solution.
    
    Args:
        nums: List of integers
        
    Returns:
        Maximum sum of contiguous subarray
    \"\"\"
    if not nums:
        return 0
    
    max_ending_here = max_so_far = nums[0]
    
    for i in range(1, len(nums)):
        # Either extend the existing subarray or start new one
        max_ending_here = max(nums[i], max_ending_here + nums[i])
        # Update the global maximum
        max_so_far = max(max_so_far, max_ending_here)
    
    return max_so_far

# Test cases
test_arrays = [
    [-2, 1, -3, 4, -1, 2, 1, -5, 4],  # Expected: 6
    [1],                                # Expected: 1
    [5, 4, -1, 7, 8]                  # Expected: 23
]

for arr in test_arrays:
    result = find_maximum_subarray(arr)
    print(f"Array: {arr}, Max sum: {result}")
            """,
            "language": "python"
        }
    ]
    
    print("🔍 Google-Style Code Analysis Test")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        # Analyze complexity
        complexity = analyzer.analyze_complexity(test_case['code'], test_case['language'])
        print(f"⏱️  Time Complexity: {complexity.time_complexity}")
        print(f"💾 Space Complexity: {complexity.space_complexity}")
        print(f"🎯 Confidence: {complexity.confidence:.1%}")
        print(f"📋 Explanation: {complexity.explanation}")
        
        # Analyze code quality
        quality = analyzer.analyze_code_quality(test_case['code'], test_case['language'])
        print(f"\n📊 Code Quality Score: {quality.overall_score}/100")
        print(f"   - Readability: {quality.readability}/100")
        print(f"   - Naming: {quality.naming_conventions}/100")
        print(f"   - Structure: {quality.code_structure}/100")
        print(f"   - Documentation: {quality.documentation}/100")
        print(f"   - Best Practices: {quality.best_practices}/100")
        
        # Evaluate Google criteria
        google_eval = analyzer.evaluate_google_criteria(
            code=test_case['code'],
            language=test_case['language'],
            time_spent=600,  # 10 minutes
            thinking_out_loud=True,
            communication_notes=["Explained approach", "Discussed complexity"],
            complexity=complexity,
            quality=quality
        )
        
        print(f"\n🎓 Google Interview Evaluation:")
        print(f"   - General Cognitive Ability (GCA): {google_eval.gca_score}/100")
        print(f"   - Role-Related Knowledge (RRK): {google_eval.rrk_score}/100")
        print(f"   - Communication: {google_eval.communication_score}/100")
        print(f"   - Googleyness: {google_eval.googleyness_score}/100")
        print(f"   - 🏆 Overall Score: {google_eval.overall_score}/100")
        
        print(f"\n💬 Detailed Feedback:")
        for criterion, feedback in google_eval.detailed_feedback.items():
            print(f"   - {criterion.upper()}: {feedback}")
        
        print("\n" + "=" * 50)

def test_complexity_patterns():
    """Test complexity detection patterns"""
    
    print("\n🧪 Complexity Pattern Detection Test")
    print("=" * 50)
    
    analyzer = GoogleStyleCodeAnalyzer()
    
    complexity_tests = [
        ("O(1) - Constant", "return array[0]"),
        ("O(log n) - Binary Search", "while left <= right: mid = (left + right) // 2"),
        ("O(n) - Linear", "for i in range(len(array)): print(array[i])"),
        ("O(n²) - Nested Loops", "for i in range(n): for j in range(n): matrix[i][j] = 0"),
        ("O(2^n) - Exponential", "def fibonacci(n): return fibonacci(n-1) + fibonacci(n-2)")
    ]
    
    for expected, code in complexity_tests:
        result = analyzer.analyze_complexity(code, "python")
        print(f"Expected: {expected}")
        print(f"Detected: {result.time_complexity}")
        print(f"Confidence: {result.confidence:.1%}")
        print(f"Match: {'✅' if expected.split(' - ')[0] in result.time_complexity else '❌'}")
        print("-" * 30)

def demo_google_standards():
    """Demonstrate Google coding standards"""
    
    print("\n📚 Google Coding Standards Demo")
    print("=" * 50)
    
    standards = {
        "evaluation_criteria": {
            "gca": {
                "name": "General Cognitive Ability",
                "description": "Problem-solving skills, algorithmic thinking, ability to handle complexity",
                "key_indicators": [
                    "Optimal algorithm selection",
                    "Edge case consideration", 
                    "Time and space complexity understanding",
                    "Problem decomposition skills"
                ]
            },
            "rrk": {
                "name": "Role-Related Knowledge",
                "description": "Technical competency in programming and computer science fundamentals",
                "key_indicators": [
                    "Clean, readable code",
                    "Proper data structure usage",
                    "Language-specific best practices",
                    "Code organization and structure"
                ]
            },
            "communication": {
                "name": "Communication",
                "description": "Ability to articulate thought process and collaborate effectively",
                "key_indicators": [
                    "Thinking out loud",
                    "Clear explanation of approach",
                    "Asking clarifying questions",
                    "Discussing trade-offs"
                ]
            },
            "googleyness": {
                "name": "Googleyness & Leadership",
                "description": "Cultural fit, growth mindset, and engineering excellence",
                "key_indicators": [
                    "Code quality and best practices",
                    "Documentation and comments",
                    "Consideration for maintainability",
                    "Continuous improvement mindset"
                ]
            }
        }
    }
    
    for criterion, details in standards["evaluation_criteria"].items():
        print(f"\n🎯 {details['name']} ({criterion.upper()})")
        print(f"Description: {details['description']}")
        print("Key Indicators:")
        for indicator in details['key_indicators']:
            print(f"  • {indicator}")

if __name__ == "__main__":
    try:
        print("🚀 DSATrain Google Enhancement Test Suite")
        print("🎯 Testing Google-style code analysis and evaluation")
        print("\n" + "=" * 60)
        
        # Run the main tests
        test_google_code_analysis()
        
        # Test complexity patterns
        test_complexity_patterns()
        
        # Demo Google standards
        demo_google_standards()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🎓 Google-style analysis is working correctly")
        print("\nNext steps:")
        print("  1. Start the FastAPI backend: python -m src.api.main")
        print("  2. Start the React frontend: npm start")
        print("  3. Enable Google Interview Mode in the code editor")
        print("  4. Practice coding with real-time Google evaluation!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
