#!/usr/bin/env python3
"""
DSATrain Enhanced Google Code Editor Demo
Demonstrates the advanced interview simulation features
"""

import time
import json
import requests
from typing import Dict, Any

class DSATrainDemo:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        
    def test_backend_connection(self) -> bool:
        """Test if the backend API is accessible"""
        try:
            response = requests.get(f"{self.base_url}/")
            return response.status_code == 200
        except:
            return False
    
    def test_google_analysis_api(self) -> Dict[str, Any]:
        """Test the Google code analysis API"""
        sample_code = """
def two_sum(nums, target):
    # Hash map approach for O(n) solution
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""
        
        submission = {
            "code": sample_code,
            "language": "python",
            "problem_id": "two-sum",
            "time_spent_seconds": 300,
            "thinking_out_loud": True,
            "communication_notes": [
                "Explained my approach using hash map",
                "Discussed time complexity - O(n)",
                "Mentioned space complexity - O(n)"
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/google/analyze",
                json=submission
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API returned {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_google_standards(self) -> Dict[str, Any]:
        """Get Google's coding standards"""
        try:
            response = requests.get(f"{self.base_url}/google/google-standards")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API returned {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def demonstrate_features(self):
        """Demonstrate all enhanced features"""
        print("=" * 80)
        print("🚀 DSATrain Enhanced Google Code Editor Demo")
        print("=" * 80)
        
        # 1. Test backend connection
        print("\n📡 Testing Backend Connection...")
        if self.test_backend_connection():
            print("✅ Backend API is running successfully!")
        else:
            print("❌ Backend API is not accessible. Please start the server.")
            return
        
        # 2. Test Google Analysis API
        print("\n🔍 Testing Google Code Analysis API...")
        analysis_result = self.test_google_analysis_api()
        
        if "error" not in analysis_result:
            print("✅ Google Code Analysis API is working!")
            print("\n📊 Sample Analysis Results:")
            
            # Display complexity analysis
            complexity = analysis_result.get("complexity", {})
            print(f"   Time Complexity: {complexity.get('time_complexity', 'N/A')}")
            print(f"   Space Complexity: {complexity.get('space_complexity', 'N/A')}")
            print(f"   Confidence: {complexity.get('confidence', 0) * 100:.1f}%")
            
            # Display Google criteria scores
            criteria = analysis_result.get("google_criteria", {})
            print(f"\n🎯 Google Evaluation Scores:")
            print(f"   GCA (General Cognitive Ability): {criteria.get('gca_score', 0)}/100")
            print(f"   RRK (Role-Related Knowledge): {criteria.get('rrk_score', 0)}/100")
            print(f"   Communication: {criteria.get('communication_score', 0)}/100")
            print(f"   Googleyness: {criteria.get('googleyness_score', 0)}/100")
            print(f"   Overall Score: {criteria.get('overall_score', 0)}/100")
            
            # Display suggestions
            suggestions = analysis_result.get("suggestions", [])
            if suggestions:
                print(f"\n💡 Improvement Suggestions:")
                for i, suggestion in enumerate(suggestions[:3], 1):
                    print(f"   {i}. {suggestion}")
        else:
            print(f"❌ Google Code Analysis API error: {analysis_result['error']}")
        
        # 3. Get Google Standards
        print("\n📋 Fetching Google Coding Standards...")
        standards = self.get_google_standards()
        
        if "error" not in standards:
            print("✅ Google Standards retrieved successfully!")
            criteria = standards.get("evaluation_criteria", {})
            print("\n🎯 Google's Four Core Evaluation Criteria:")
            for key, criterion in criteria.items():
                print(f"   • {criterion['name']}: {criterion['description']}")
        else:
            print(f"❌ Error fetching standards: {standards['error']}")
        
        # 4. Feature Overview
        print("\n" + "=" * 80)
        print("🎨 Enhanced Code Editor Features Overview")
        print("=" * 80)
        
        features = [
            "✅ Google Doc Simulation Mode (minimal syntax highlighting)",
            "✅ Real-time Interview Timer with time pressure alerts",
            "✅ Typing Speed Tracking (WPM calculation)",
            "✅ Communication Notes with timestamps",
            "✅ Interview Pressure Simulation (5 levels)",
            "✅ Code Templates for common patterns",
            "✅ Google Criteria Evaluation (GCA, RRK, Communication, Googleyness)",
            "✅ Complexity Analysis with confidence scoring",
            "✅ Improvement suggestions based on Google standards",
            "✅ Interview interruption simulation",
            "✅ Focus time tracking",
            "✅ Keystroke analysis",
            "✅ Template insertion for common algorithms"
        ]
        
        for feature in features:
            print(f"  {feature}")
        
        print("\n" + "=" * 80)
        print("🎯 Usage Instructions")
        print("=" * 80)
        
        instructions = [
            "1. Open the frontend at: http://localhost:3000",
            "2. Navigate to Code Practice page",
            "3. Toggle 'Google Interview Mode' switch",
            "4. Enable 'Thinking Out Loud' for communication tracking",
            "5. Adjust pressure level (1-5) for interview simulation",
            "6. Start the timer and begin coding",
            "7. Use the Analysis tab for real-time feedback",
            "8. Check Google Criteria tab for interview-style evaluation",
            "9. Use Templates tab for common algorithm patterns",
            "10. Monitor Pressure tab for interview simulation events"
        ]
        
        for instruction in instructions:
            print(f"  {instruction}")
        
        print("\n" + "=" * 80)
        print("🏆 Google Interview Best Practices")
        print("=" * 80)
        
        practices = [
            "• Always think out loud during coding",
            "• Explain your approach before writing code",
            "• Discuss time and space complexity",
            "• Consider edge cases and test with examples",
            "• Write clean, readable code with meaningful variable names",
            "• Ask clarifying questions when needed",
            "• Optimize iteratively (brute force → optimal)",
            "• Handle interviewer interruptions gracefully"
        ]
        
        for practice in practices:
            print(f"  {practice}")
        
        print("\n✨ Demo completed successfully!")
        print(f"🌐 Frontend: {self.frontend_url}")
        print(f"🔧 Backend API: {self.base_url}")
        print(f"📚 API Docs: {self.base_url}/docs")

if __name__ == "__main__":
    demo = DSATrainDemo()
    demo.demonstrate_features()
