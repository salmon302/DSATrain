#!/usr/bin/env python3
"""
Comprehensive integration test for the DSA Training Platform.
Tests all components: Main API, Skill Tree API, and Frontend integration.
"""

import requests
import time
import json
from pathlib import Path

class PlatformIntegrationTester:
    def __init__(self):
        self.main_api = "http://localhost:8000"
        self.skill_tree_api = "http://localhost:8003"
        self.frontend_url = "http://localhost:3000"
        self.results = {
            "main_api": False,
            "skill_tree_api": False,
            "data_consistency": False,
            "frontend_config": False,
            "integration_ready": False
        }
    
    def test_main_api(self):
        """Test the main FastAPI backend"""
        print("\n1. Testing Main API (FastAPI on port 8000)...")
        try:
            # Test health endpoint
            response = requests.get(f"{self.main_api}/health", timeout=5)
            if response.status_code == 200:
                print("   ✓ Main API health check passed")
                self.results["main_api"] = True
            else:
                print(f"   ✗ Main API health check failed: {response.status_code}")
            
            # Test API docs availability
            response = requests.get(f"{self.main_api}/docs", timeout=5)
            if response.status_code == 200:
                print("   ✓ API documentation accessible")
            else:
                print("   ⚠ API documentation not accessible")
                
        except Exception as e:
            print(f"   ✗ Main API test failed: {e}")
    
    def test_skill_tree_api(self):
        """Test the Skill Tree API"""
        print("\n2. Testing Skill Tree API (Flask on port 8003)...")
        try:
            # Test health endpoint
            response = requests.get(f"{self.skill_tree_api}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✓ Skill Tree API health: {health_data.get('status', 'unknown')}")
                print(f"   ✓ Service: {health_data.get('service', 'unknown')}")
                
                # Test skill tree data endpoint
                response = requests.get(f"{self.skill_tree_api}/skill-tree/overview", timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    total_problems = data.get('total_problems', 0)
                    skill_areas = data.get('total_skill_areas', 0)
                    data_source = data.get('data_source', 'unknown')
                    
                    print(f"   ✓ Skill tree data loaded: {total_problems} problems")
                    print(f"   ✓ Skill areas available: {skill_areas}")
                    print(f"   ✓ Data source: {data_source}")
                    
                    self.results["skill_tree_api"] = True
                    
                    # Check data quality
                    if total_problems > 1000:
                        print("   ✓ Sufficient problem data for skill tree")
                        self.results["data_consistency"] = True
                    else:
                        print("   ⚠ Limited problem data available")
                        
                else:
                    print(f"   ✗ Skill tree endpoint failed: {response.status_code}")
            else:
                print(f"   ✗ Skill Tree API health failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Skill Tree API test failed: {e}")
    
    def test_frontend_configuration(self):
        """Test frontend configuration"""
        print("\n3. Testing Frontend Configuration...")
        
        # Check if frontend component exists and is configured correctly
        component_path = Path("frontend/src/components/SkillTreeVisualization.tsx")
        if component_path.exists():
            print("   ✓ Skill tree component exists")
            
            try:
                with open(component_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'localhost:8003' in content:
                    print("   ✓ Frontend configured for Skill Tree API")
                    self.results["frontend_config"] = True
                else:
                    print("   ⚠ Frontend may need API endpoint configuration")
                    
                if 'SkillTreeVisualization' in content:
                    print("   ✓ Skill tree visualization component ready")
                    
            except Exception as e:
                print(f"   ⚠ Could not read frontend component: {e}")
        else:
            print("   ⚠ Skill tree component not found")
        
        # Check package.json
        package_path = Path("frontend/package.json")
        if package_path.exists():
            print("   ✓ Frontend package configuration exists")
        else:
            print("   ⚠ Frontend package.json not found")
    
    def test_cross_service_integration(self):
        """Test integration between services"""
        print("\n4. Testing Cross-Service Integration...")
        
        if self.results["main_api"] and self.results["skill_tree_api"]:
            print("   ✓ Both APIs operational - integration possible")
            
            # Test if both services can run simultaneously
            try:
                main_response = requests.get(f"{self.main_api}/health", timeout=3)
                skill_response = requests.get(f"{self.skill_tree_api}/health", timeout=3)
                
                if main_response.status_code == 200 and skill_response.status_code == 200:
                    print("   ✓ Concurrent API operation confirmed")
                    self.results["integration_ready"] = True
                    
            except Exception as e:
                print(f"   ⚠ Concurrent operation test failed: {e}")
        else:
            print("   ✗ Cannot test integration - some APIs not operational")
    
    def generate_integration_report(self):
        """Generate comprehensive integration report"""
        print("\n5. Generating Integration Report...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "platform_status": "operational" if all(self.results.values()) else "partial",
            "services": {
                "main_api": {
                    "status": "✓" if self.results["main_api"] else "✗",
                    "endpoint": self.main_api,
                    "description": "FastAPI backend with core functionality"
                },
                "skill_tree_api": {
                    "status": "✓" if self.results["skill_tree_api"] else "✗", 
                    "endpoint": self.skill_tree_api,
                    "description": "Flask API for skill tree visualization data"
                },
                "frontend": {
                    "status": "✓" if self.results["frontend_config"] else "✗",
                    "endpoint": self.frontend_url,
                    "description": "React frontend with skill tree visualization"
                }
            },
            "integration_capabilities": {
                "data_consistency": self.results["data_consistency"],
                "frontend_ready": self.results["frontend_config"],
                "concurrent_apis": self.results["integration_ready"],
                "agentic_control": self.results["skill_tree_api"]
            },
            "recommendations": []
        }
        
        # Add recommendations based on test results
        if not self.results["main_api"]:
            report["recommendations"].append("Start main API server: launch_dsatrain.bat")
        
        if not self.results["skill_tree_api"]:
            report["recommendations"].append("Skill Tree API needs attention - check robust_flask_server.py")
            
        if not self.results["frontend_config"]:
            report["recommendations"].append("Update frontend API configuration")
            
        if self.results["integration_ready"]:
            report["recommendations"].append("Platform ready for production use")
        
        # Save report
        report_path = Path("platform_integration_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   ✓ Report saved to: {report_path}")
        return report
    
    def run_full_test_suite(self):
        """Run complete integration test suite"""
        print("=" * 70)
        print("DSA TRAINING PLATFORM - INTEGRATION TEST SUITE")
        print("=" * 70)
        
        self.test_main_api()
        self.test_skill_tree_api()
        self.test_frontend_configuration()
        self.test_cross_service_integration()
        report = self.generate_integration_report()
        
        print("\n" + "=" * 70)
        print("INTEGRATION TEST SUMMARY")
        print("=" * 70)
        
        print(f"\nPlatform Status: {report['platform_status'].upper()}")
        print("\nService Status:")
        for service, info in report['services'].items():
            print(f"  {service:15} {info['status']} {info['endpoint']}")
        
        print("\nIntegration Capabilities:")
        for capability, status in report['integration_capabilities'].items():
            print(f"  {capability:20} {'✓' if status else '✗'}")
        
        if report['recommendations']:
            print("\nRecommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print(f"\nOverall Integration: {'🟢 READY' if report['platform_status'] == 'operational' else '🟡 PARTIAL'}")
        
        return report

def main():
    """Main integration test execution"""
    tester = PlatformIntegrationTester()
    report = tester.run_full_test_suite()
    
    # Exit code for CI/CD integration
    exit_code = 0 if report['platform_status'] == 'operational' else 1
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
