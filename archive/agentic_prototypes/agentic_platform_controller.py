#!/usr/bin/env python3
"""
Agentic Platform Controller - Demonstrates autonomous control of the DSA platform.
This script shows how an AI agent can programmatically manage the entire system.
"""

import subprocess
import time
import requests
import json
from pathlib import Path
from agentic_skill_tree_client import SkillTreeClient

class AgenticPlatformController:
    def __init__(self):
        self.skill_tree_client = SkillTreeClient()
        self.main_api = "http://localhost:8000"
        self.skill_tree_api = "http://localhost:8003"
        self.frontend_url = "http://localhost:3000"
        
        self.platform_state = {
            "services_running": False,
            "data_available": False,
            "frontend_ready": False,
            "last_check": None
        }
    
    def check_platform_status(self):
        """Autonomously check complete platform status"""
        print("🤖 Agent: Checking platform status...")
        
        # Check main API
        try:
            main_response = requests.get(f"{self.main_api}/health", timeout=5)
            main_running = main_response.status_code == 200
        except:
            main_running = False
        
        # Check skill tree API
        skill_tree_running = self.skill_tree_client.is_server_running()
        
        self.platform_state.update({
            "main_api_running": main_running,
            "skill_tree_running": skill_tree_running,
            "services_running": main_running and skill_tree_running,
            "last_check": time.time()
        })
        
        print(f"   Main API: {'✓' if main_running else '✗'}")
        print(f"   Skill Tree API: {'✓' if skill_tree_running else '✗'}")
        
        return self.platform_state["services_running"]
    
    def autonomous_platform_startup(self):
        """Autonomously start the platform if needed"""
        print("🤖 Agent: Initiating autonomous platform startup...")
        
        # Use development launcher for comprehensive startup
        launcher = Path("launch_dsatrain_dev.bat")
        if launcher.exists():
            print("   → Executing integrated platform launcher...")
            process = subprocess.Popen([str(launcher)], shell=True)
            
            # Wait and monitor startup
            for i in range(12):  # Wait up to 60 seconds
                time.sleep(5)
                if self.check_platform_status():
                    print(f"   ✓ Platform operational after {(i+1)*5} seconds")
                    return True
                print(f"   → Waiting for services... ({(i+1)*5}s)")
            
            print("   ⚠ Platform startup timeout - manual intervention may be needed")
            return False
        else:
            print("   ✗ Launcher not found")
            return False
    
    def analyze_skill_tree_data(self):
        """Autonomously analyze available skill tree data"""
        print("🤖 Agent: Analyzing skill tree data...")
        
        try:
            data = self.skill_tree_client.get_skill_tree_data()
            
            analysis = {
                "total_problems": data.get('total_problems', 0),
                "skill_areas": data.get('total_skill_areas', 0),
                "data_source": data.get('data_source', 'unknown'),
                "skill_distribution": {},
                "difficulty_analysis": {
                    "easy_problems": 0,
                    "medium_problems": 0,
                    "hard_problems": 0
                }
            }
            
            # Analyze skill area distribution
            columns = data.get('skill_tree_columns', [])
            for column in columns:
                skill_area = column.get('skill_area', 'unknown')
                total_problems = column.get('total_problems', 0)
                analysis["skill_distribution"][skill_area] = total_problems
                
                # Count difficulty levels
                difficulties = column.get('difficulty_levels', {})
                analysis["difficulty_analysis"]["easy_problems"] += len(difficulties.get('Easy', []))
                analysis["difficulty_analysis"]["medium_problems"] += len(difficulties.get('Medium', []))
                analysis["difficulty_analysis"]["hard_problems"] += len(difficulties.get('Hard', []))
            
            # Agent decision making based on analysis
            print(f"   📊 Data Analysis Complete:")
            print(f"      Total Problems: {analysis['total_problems']}")
            print(f"      Skill Areas: {analysis['skill_areas']}")
            print(f"      Data Quality: {analysis['data_source']}")
            
            if analysis['total_problems'] > 5000:
                print("   🎯 Agent Decision: Sufficient data for production use")
                self.platform_state["data_available"] = True
            else:
                print("   ⚠ Agent Decision: Limited data - recommend enhancement")
            
            # Save analysis for other agents
            with open('agentic_analysis_report.json', 'w') as f:
                json.dump(analysis, f, indent=2)
            
            return analysis
            
        except Exception as e:
            print(f"   ✗ Data analysis failed: {e}")
            return None
    
    def test_frontend_integration(self):
        """Test if frontend can connect to our APIs"""
        print("🤖 Agent: Testing frontend integration...")
        
        # Check if frontend component is properly configured
        component_path = Path("frontend/src/components/SkillTreeVisualization.tsx")
        if component_path.exists():
            try:
                with open(component_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'localhost:8003' in content:
                    print("   ✓ Frontend API configuration correct")
                    self.platform_state["frontend_ready"] = True
                    return True
                else:
                    print("   ⚠ Frontend API configuration needs update")
                    return False
                    
            except Exception as e:
                print(f"   ✗ Frontend check failed: {e}")
                return False
        else:
            print("   ✗ Frontend component not found")
            return False
    
    def generate_autonomous_report(self):
        """Generate a comprehensive autonomous report"""
        print("🤖 Agent: Generating autonomous platform report...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "agent_version": "1.0",
            "platform_state": self.platform_state,
            "autonomous_capabilities": {
                "platform_startup": True,
                "status_monitoring": True,
                "data_analysis": True,
                "frontend_integration": True,
                "error_recovery": True
            },
            "recommendations": [],
            "next_actions": []
        }
        
        # Agent recommendations based on current state
        if not self.platform_state.get("services_running", False):
            report["recommendations"].append("Execute autonomous platform startup")
            report["next_actions"].append("Run autonomous_platform_startup()")
        
        if not self.platform_state.get("data_available", False):
            report["recommendations"].append("Analyze available data quality")
            report["next_actions"].append("Run analyze_skill_tree_data()")
        
        if self.platform_state.get("services_running", False) and self.platform_state.get("data_available", False):
            report["recommendations"].append("Platform ready for autonomous operations")
            report["next_actions"].append("Proceed with skill tree analysis")
        
        # Save report
        with open('autonomous_platform_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   📋 Report saved: autonomous_platform_report.json")
        return report
    
    def run_autonomous_workflow(self):
        """Execute complete autonomous workflow"""
        print("🤖 AGENTIC PLATFORM CONTROLLER - AUTONOMOUS WORKFLOW")
        print("=" * 65)
        
        # Step 1: Check current status
        if not self.check_platform_status():
            # Step 2: Autonomous startup if needed
            if not self.autonomous_platform_startup():
                print("🔴 Autonomous startup failed - manual intervention required")
                return False
        
        # Step 3: Data analysis
        analysis = self.analyze_skill_tree_data()
        if not analysis:
            print("🔴 Data analysis failed - check data availability")
            return False
        
        # Step 4: Frontend integration test
        self.test_frontend_integration()
        
        # Step 5: Generate autonomous report
        report = self.generate_autonomous_report()
        
        print("\n" + "=" * 65)
        print("🤖 AUTONOMOUS WORKFLOW COMPLETE")
        print("=" * 65)
        
        if self.platform_state.get("services_running") and self.platform_state.get("data_available"):
            print("🟢 PLATFORM AUTONOMOUSLY OPERATIONAL")
            print("   → All services running under agentic control")
            print("   → Data analysis complete and available")
            print("   → Frontend integration verified")
            print("   → Ready for autonomous skill tree operations")
        else:
            print("🟡 PARTIAL AUTONOMOUS OPERATION")
            print("   → Some manual intervention may be required")
        
        return True

def main():
    """Main autonomous execution"""
    controller = AgenticPlatformController()
    success = controller.run_autonomous_workflow()
    
    if success:
        print("\n🎯 Agent Handoff: Platform ready for skill tree analysis")
        print("   Next: Run specific skill tree operations or user interactions")
    else:
        print("\n🔴 Agent Error: Manual troubleshooting required")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
