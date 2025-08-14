#!/usr/bin/env python3
"""
DSATrain Redesign Cleanup Preparation Script

This script prepares the archive structure and identifies all files
that need to be moved for the single-user redesign cleanup.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime

class RedesignCleanupPrep:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.archive_root = self.project_root / "archive"
        
        # Files to archive (based on redesign plan)
        self.files_to_archive = {
            "legacy_servers": [
                "flask_skill_tree_server.py",
                "robust_flask_server.py", 
                "simple_skill_tree_server.py",
                "dev_skill_tree_server.py",
                "minimal_flask_test.py",
                "production_flask_test.py",
                "http_server_test.py",
                "production_skill_tree_server.py"
            ],
            "agentic_prototypes": [
                "agentic_client.py",
                "agentic_platform_controller.py",
                "agentic_skill_tree_client.py", 
                "agentic_skill_tree_server.py",
                "agentic_workflow_demo.py"
            ],
            "integration_legacy": [
                "integration_demo.py",
                "integration_summary.py",
                "test_platform_integration.py",
                "platform_integration_report.json",
                "skill_tree_test_data.json",
                "enhance_database.py",
                "migrate_databases.py"
            ],
            "test_files": [
                # All test_*.py files in root
                "test_http_server.py",
                "test_production_server.py", 
                "test_minimal_server.py",
                "test_backend_direct.py",
                "test_flask_api.py",
                "test_production_api.py",
                "test_skill_tree_api.py",
                "test_skill_tree_simple.py",
                "test_api_goals.py",
                "test_goal_selection.py",
                "test_fixed_engine.py",
                "test_goal_impact.py",
                "test_new_query.py",
                "test_all_weeks.py",
                "test_frontend_integration.py",
                "test_enriched_api.py",
                "test_api_endpoint.py",
                "test_direct_generation.py",
                "test_fastapi_app.py",
                "test_imports.py",
                "test_learning_path_api.py",
                "test_structure.py",
                "simple_api_test.py",
                "simple_test.py"
            ],
            "debug_utilities": [
                "debug_easy_problems.py",
                "debug_skill_tree.py",
                "demo_skill_tree.py",
                "init_templates.py"
            ],
            "status_reports": [
                "CODE_EDITOR_INTEGRATION_ANALYSIS.md",
                "NAVIGATION_FIX_SUMMARY.md", 
                "PRODUCTION_READY_SUMMARY.md",
                "SKILL_TREE_IMPLEMENTATION_SUMMARY.md",
                "SKILL_TREE_STATUS.md",
                "SKILL_TREE_PERFORMANCE_OPTIMIZATION_REPORT.md",
                "SYSTEM_REQUIREMENTS_ANALYSIS.md",
                "improvement_recommendations.md"
            ],
            "legacy_databases": [
                "dsatrain_skilltree.db",
                "dsatrain_skilltree_backup_20250731_220201.db",
                "dsatrain_phase4_backup_20250731_220201.db", 
                "dsatrain_phase4_backup.db"
            ],
            "frontend_duplicates": [
                "frontend/src/components/SkillTreeVisualization.jsx",
                "frontend/src/components/OptimizedSkillTreeVisualization.jsx"
            ]
        }
        
        # Batch scripts and configs to keep but organize
        self.config_files = [
            "launch_dsatrain_dev.bat",
            "launch_dsatrain.bat",
            "start_skill_tree_server.bat",
            "stop_dsatrain.bat"
        ]

    def create_archive_structure(self):
        """Create the archive directory structure"""
        print("🏗️  Creating archive structure...")
        
        archive_dirs = [
            "legacy_servers",
            "agentic_prototypes", 
            "integration_legacy",
            "test_files",
            "debug_utilities",
            "status_reports",
            "legacy_databases",
            "frontend_duplicates",
            "batch_scripts"
        ]
        
        for dir_name in archive_dirs:
            archive_dir = self.archive_root / dir_name
            archive_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {archive_dir}")
            
            # Create README for each archive directory
            readme_path = archive_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"# Archived {dir_name.replace('_', ' ').title()}\n\n")
                f.write(f"**Archived on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Reason:** DSATrain single-user redesign cleanup\n\n")
                f.write("These files were moved from the root directory as part of the ")
                f.write("consolidation to a single FastAPI backend architecture.\n\n")
                f.write("Files in this directory are preserved for reference but are ")
                f.write("not part of the active codebase.\n")

    def analyze_current_files(self) -> Dict:
        """Analyze current file distribution"""
        print("🔍 Analyzing current file distribution...")
        
        analysis = {
            "root_files": [],
            "found_for_archive": {category: [] for category in self.files_to_archive.keys()},
            "missing_files": {category: [] for category in self.files_to_archive.keys()},
            "total_root_files": 0,
            "total_to_archive": 0
        }
        
        # Get all files in root directory
        for item in self.project_root.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                analysis["root_files"].append(item.name)
        
        analysis["total_root_files"] = len(analysis["root_files"])
        
        # Check which files exist for archiving
        for category, file_list in self.files_to_archive.items():
            for filename in file_list:
                if filename.startswith("frontend/"):
                    # Handle frontend files specially
                    file_path = self.project_root / filename
                else:
                    file_path = self.project_root / filename
                    
                if file_path.exists():
                    analysis["found_for_archive"][category].append(filename)
                    if not filename.startswith("frontend/"):
                        analysis["total_to_archive"] += 1
                else:
                    analysis["missing_files"][category].append(filename)
        
        return analysis

    def generate_cleanup_report(self, analysis: Dict):
        """Generate a detailed cleanup report"""
        print("📊 Generating cleanup report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_root_files": analysis["total_root_files"],
                "files_to_archive": analysis["total_to_archive"],
                "files_remaining": analysis["total_root_files"] - analysis["total_to_archive"],
                "cleanup_percentage": round((analysis["total_to_archive"] / analysis["total_root_files"]) * 100, 1) if analysis["total_root_files"] > 0 else 0
            },
            "archive_plan": analysis["found_for_archive"],
            "missing_files": analysis["missing_files"],
            "target_structure": {
                "essential_root_files": [
                    "README.md",
                    "PROJECT_STRUCTURE.md", 
                    "alembic.ini",
                    "dsatrain_phase4.db",
                    ".gitignore",
                    ".gitattributes"
                ],
                "essential_directories": [
                    "src/",
                    "frontend/", 
                    "tests/",
                    "docs/",
                    "data/",
                    "archive/",
                    "alembic/",
                    "logs/"
                ]
            }
        }
        
        # Save report
        docs_dir = self.project_root / "docs"
        docs_dir.mkdir(exist_ok=True)
        report_path = docs_dir / "CLEANUP_ANALYSIS_REPORT.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"  ✅ Report saved: {report_path}")
        return report

    def print_summary(self, analysis: Dict):
        """Print a summary of the cleanup plan"""
        print("\n" + "="*60)
        print("🎯 REDESIGN CLEANUP SUMMARY")
        print("="*60)
        
        print(f"📁 Current root directory files: {analysis['total_root_files']}")
        print(f"📦 Files to archive: {analysis['total_to_archive']}")
        print(f"📌 Files remaining in root: {analysis['total_root_files'] - analysis['total_to_archive']}")
        
        cleanup_percentage = round((analysis['total_to_archive'] / analysis['total_root_files']) * 100, 1) if analysis['total_root_files'] > 0 else 0
        print(f"🧹 Cleanup percentage: {cleanup_percentage}%")
        
        print("\n📊 ARCHIVE BREAKDOWN:")
        for category, files in analysis["found_for_archive"].items():
            if files:
                print(f"  • {category.replace('_', ' ').title()}: {len(files)} files")
        
        print("\n⚠️  MISSING FILES (mentioned in plan but not found):")
        total_missing = 0
        for category, files in analysis["missing_files"].items():
            if files:
                print(f"  • {category.replace('_', ' ').title()}: {len(files)} files")
                for missing_file in files:
                    print(f"    - {missing_file}")
                total_missing += len(files)
        
        if total_missing == 0:
            print("  ✅ All expected files found!")
        
        print("\n🎯 TARGET: ≤15 files in root directory")
        target_achieved = (analysis['total_root_files'] - analysis['total_to_archive']) <= 15
        status = "✅ ACHIEVABLE" if target_achieved else "⚠️  NEEDS MORE CLEANUP"
        print(f"   Status: {status}")

    def create_file_move_script(self, analysis: Dict):
        """Create a script to actually move the files"""
        
        # Add the actual move operations
        moves_dict = {}
        for category, files in analysis["found_for_archive"].items():
            if files:
                moves_dict[category] = files
        
        script_content = f'''#!/usr/bin/env python3
"""
Auto-generated file moving script for DSATrain redesign cleanup
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import os
import shutil
from pathlib import Path

def move_files():
    project_root = Path(".")
    archive_root = project_root / "archive"
    
    # Files to move (only existing files included)
    moves = {repr(moves_dict)}
    
    print("🚀 Starting file archival process...")
    
    for destination, files in moves.items():
        dest_dir = archive_root / destination
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in files:
            if file_path.startswith("frontend/"):
                source = project_root / file_path
                target = dest_dir / Path(file_path).name
            else:
                source = project_root / file_path
                target = dest_dir / Path(file_path).name
            
            if source.exists():
                print(f"  📦 Moving: {{file_path}} → {{destination}}/")
                try:
                    shutil.move(str(source), str(target))
                except Exception as e:
                    print(f"  ⚠️  Error moving {{file_path}}: {{e}}")
            else:
                print(f"  ⚠️  Skipping missing file: {{file_path}}")
    
    print("\\n✅ File archival complete!")
    print("\\n📋 Next steps:")
    print("  1. Test that FastAPI server still runs")
    print("  2. Test frontend builds successfully")
    print("  3. Update .gitignore if needed") 
    print("  4. Commit changes")

if __name__ == "__main__":
    move_files()
'''
        
        script_path = self.project_root / "scripts" / "execute_redesign_cleanup.py"
        script_path.parent.mkdir(exist_ok=True)
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"📝 Created move script: {script_path}")
        return script_path

    def validate_prerequisites(self) -> bool:
        """Validate that it's safe to proceed with cleanup"""
        print("🔍 Validating prerequisites...")
        
        issues = []
        
        # Check if main database exists
        main_db = self.project_root / "dsatrain_phase4.db"
        if not main_db.exists():
            issues.append("Main database (dsatrain_phase4.db) not found")
        
        # Check if FastAPI main.py exists
        main_api = self.project_root / "src" / "api" / "main.py" 
        if not main_api.exists():
            issues.append("Main FastAPI file (src/api/main.py) not found")
        
        # Check if frontend exists
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            issues.append("Frontend directory not found")
        
        # Check for git repository
        git_dir = self.project_root / ".git"
        if not git_dir.exists():
            issues.append("Not a git repository - changes cannot be tracked")
        
        if issues:
            print("❌ Prerequisites check failed:")
            for issue in issues:
                print(f"  • {issue}")
            return False
        
        print("✅ All prerequisites satisfied")
        return True

    def run(self):
        """Run the complete preparation process"""
        print("🎯 DSATrain Redesign Cleanup Preparation")
        print("=" * 50)
        
        # Validate prerequisites
        if not self.validate_prerequisites():
            print("\n❌ Cannot proceed - fix issues above first")
            return False
        
        # Create archive structure
        self.create_archive_structure()
        
        # Analyze current files
        analysis = self.analyze_current_files()
        
        # Generate report
        report = self.generate_cleanup_report(analysis)
        
        # Print summary
        self.print_summary(analysis)
        
        # Create move script
        move_script = self.create_file_move_script(analysis)
        
        print(f"\n🎉 Preparation complete!")
        print(f"📄 Detailed report: docs/CLEANUP_ANALYSIS_REPORT.json")
        print(f"🚀 Execute cleanup: python {move_script}")
        print(f"\n⚠️  IMPORTANT: Create a backup before running the cleanup script!")
        
        return True

if __name__ == "__main__":
    prep = RedesignCleanupPrep()
    prep.run() 