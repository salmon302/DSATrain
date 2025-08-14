#!/usr/bin/env python3
"""
Auto-generated file moving script for DSATrain redesign cleanup
Generated on: 2025-08-14 00:15:28
"""

import os
import shutil
from pathlib import Path

def move_files():
    project_root = Path(".")
    archive_root = project_root / "archive"
    
    # Files to move (only existing files included)
    moves = {'legacy_servers': ['flask_skill_tree_server.py', 'robust_flask_server.py', 'simple_skill_tree_server.py', 'dev_skill_tree_server.py', 'minimal_flask_test.py', 'production_flask_test.py', 'http_server_test.py', 'production_skill_tree_server.py'], 'agentic_prototypes': ['agentic_client.py', 'agentic_platform_controller.py', 'agentic_skill_tree_client.py', 'agentic_skill_tree_server.py', 'agentic_workflow_demo.py'], 'integration_legacy': ['integration_demo.py', 'integration_summary.py', 'test_platform_integration.py', 'platform_integration_report.json', 'skill_tree_test_data.json', 'enhance_database.py', 'migrate_databases.py'], 'test_files': ['test_http_server.py', 'test_production_server.py', 'test_minimal_server.py', 'test_backend_direct.py', 'test_flask_api.py', 'test_production_api.py', 'test_skill_tree_api.py', 'test_skill_tree_simple.py', 'test_api_goals.py', 'test_goal_selection.py', 'test_fixed_engine.py', 'test_goal_impact.py', 'test_new_query.py', 'test_all_weeks.py', 'test_frontend_integration.py', 'test_enriched_api.py', 'test_api_endpoint.py', 'test_direct_generation.py', 'test_fastapi_app.py', 'test_imports.py', 'test_learning_path_api.py', 'test_structure.py', 'simple_api_test.py', 'simple_test.py'], 'debug_utilities': ['debug_easy_problems.py', 'debug_skill_tree.py', 'demo_skill_tree.py', 'init_templates.py'], 'status_reports': ['CODE_EDITOR_INTEGRATION_ANALYSIS.md', 'NAVIGATION_FIX_SUMMARY.md', 'PRODUCTION_READY_SUMMARY.md', 'SKILL_TREE_IMPLEMENTATION_SUMMARY.md', 'SKILL_TREE_STATUS.md', 'SKILL_TREE_PERFORMANCE_OPTIMIZATION_REPORT.md', 'SYSTEM_REQUIREMENTS_ANALYSIS.md', 'improvement_recommendations.md'], 'legacy_databases': ['dsatrain_skilltree.db', 'dsatrain_skilltree_backup_20250731_220201.db', 'dsatrain_phase4_backup_20250731_220201.db', 'dsatrain_phase4_backup.db'], 'frontend_duplicates': ['frontend/src/components/SkillTreeVisualization.jsx', 'frontend/src/components/OptimizedSkillTreeVisualization.jsx']}
    
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
                print(f"  📦 Moving: {file_path} → {destination}/")
                try:
                    shutil.move(str(source), str(target))
                except Exception as e:
                    print(f"  ⚠️  Error moving {file_path}: {e}")
            else:
                print(f"  ⚠️  Skipping missing file: {file_path}")
    
    print("\n✅ File archival complete!")
    print("\n📋 Next steps:")
    print("  1. Test that FastAPI server still runs")
    print("  2. Test frontend builds successfully")
    print("  3. Update .gitignore if needed") 
    print("  4. Commit changes")

if __name__ == "__main__":
    move_files()
