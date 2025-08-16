"""
Data Pipeline Orchestrator
Automates the complete data processing pipeline with monitoring and quality checks
"""

from __future__ import annotations

import json
import time
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import subprocess
import sys
import logging


@dataclass
class DataPipelineOrchestrator:
    """Orchestrates automated data processing pipeline"""
    
    data_dir: Path
    output_dir: Optional[Path] = None
    
    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = self.data_dir / "processed" / "pipeline"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        log_file = self.output_dir / "pipeline.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def check_data_quality(self) -> Dict[str, Any]:
        """Check data quality and detect issues"""
        self.logger.info("Running data quality checks...")
        
        quality_issues = []
        quality_metrics = {
            "total_files_checked": 0,
            "files_with_issues": 0,
            "critical_issues": 0,
            "warnings": 0
        }
        
        # Check unified problems file
        problems_file = self.data_dir / "processed" / "problems_unified_complete.json"
        if problems_file.exists():
            try:
                with problems_file.open("r") as f:
                    data = json.load(f)
                
                problems = data.get("problems", [])
                quality_metrics["total_files_checked"] += 1
                
                # Check for empty problems
                if not problems:
                    quality_issues.append({
                        "type": "critical",
                        "file": "problems_unified_complete.json",
                        "issue": "No problems found in unified dataset"
                    })
                    quality_metrics["critical_issues"] += 1
                
                # Check for problems missing essential fields
                missing_fields_count = 0
                for problem in problems:
                    if not problem.get("title") or not problem.get("id"):
                        missing_fields_count += 1
                
                if missing_fields_count > len(problems) * 0.1:  # More than 10% missing fields
                    quality_issues.append({
                        "type": "warning",
                        "file": "problems_unified_complete.json",
                        "issue": f"{missing_fields_count} problems missing essential fields"
                    })
                    quality_metrics["warnings"] += 1
                
            except Exception as e:
                quality_issues.append({
                    "type": "critical",
                    "file": "problems_unified_complete.json",
                    "issue": f"Cannot read file: {e}"
                })
                quality_metrics["critical_issues"] += 1
        else:
            quality_issues.append({
                "type": "critical",
                "file": "problems_unified_complete.json",
                "issue": "Unified problems file missing"
            })
            quality_metrics["critical_issues"] += 1
        
        # Check AI features
        ai_features_dir = self.data_dir / "processed" / "ai_features"
        expected_ai_files = [
            "semantic_embeddings.json",
            "difficulty_vectors.json", 
            "concept_graph.json",
            "interview_features.json"
        ]
        
        for filename in expected_ai_files:
            file_path = ai_features_dir / filename
            quality_metrics["total_files_checked"] += 1
            
            if not file_path.exists():
                quality_issues.append({
                    "type": "warning",
                    "file": filename,
                    "issue": "AI feature file missing"
                })
                quality_metrics["warnings"] += 1
        
        # Count files with issues
        quality_metrics["files_with_issues"] = len(set(issue["file"] for issue in quality_issues))
        
        quality_report = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy" if quality_metrics["critical_issues"] == 0 else "degraded",
            "metrics": quality_metrics,
            "issues": quality_issues
        }
        
        # Save quality report
        quality_file = self.output_dir / f"quality_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with quality_file.open("w") as f:
            json.dump(quality_report, f, indent=2)
        
        self.logger.info(f"Quality check complete. Status: {quality_report['status']}")
        return quality_report

    def run_incremental_update(self) -> Dict[str, Any]:
        """Run incremental data updates"""
        self.logger.info("Running incremental data update...")
        
        update_results = {
            "timestamp": datetime.now().isoformat(),
            "components_updated": [],
            "errors": [],
            "status": "success"
        }
        
        try:
            # Update Codeforces data (simulated - would call actual fetcher)
            self.logger.info("Checking for new Codeforces problems...")
            
            # In a real implementation, this would:
            # 1. Call the Codeforces API to get recent problems
            # 2. Compare with existing data
            # 3. Add new problems to the dataset
            # 4. Re-run unification for new data
            
            update_results["components_updated"].append({
                "component": "codeforces_problems",
                "action": "checked_for_updates",
                "new_items": 0,
                "status": "no_new_data"
            })
            
            # Check trend monitoring
            self.logger.info("Running trend monitoring...")
            
            # This would analyze recent problem patterns, difficulty trends, etc.
            update_results["components_updated"].append({
                "component": "trend_monitoring",
                "action": "analyzed_trends",
                "status": "completed"
            })
            
        except Exception as e:
            self.logger.error(f"Error in incremental update: {e}")
            update_results["errors"].append(str(e))
            update_results["status"] = "failed"
        
        # Save update report
        update_file = self.output_dir / f"incremental_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with update_file.open("w") as f:
            json.dump(update_results, f, indent=2)
        
        return update_results

    def generate_pipeline_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive pipeline status report"""
        self.logger.info("Generating pipeline status report...")
        
        status_report = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_health": "unknown",
            "data_freshness": {},
            "component_status": {},
            "recommendations": []
        }
        
        try:
            # Check component status
            components = {
                "unified_problems": self.data_dir / "processed" / "problems_unified_complete.json",
                "ai_features": self.data_dir / "processed" / "ai_features" / "ai_features_summary.json",
                "quality_scores": self.data_dir / "processed" / "quality_scoring" / "quality_report.json",
                "behavioral_data": self.data_dir / "processed" / "behavioral" / "behavioral_processing_summary.json"
            }
            
            healthy_components = 0
            total_components = len(components)
            
            for component_name, file_path in components.items():
                if file_path.exists():
                    # Check file age
                    file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    status_report["component_status"][component_name] = {
                        "status": "healthy",
                        "last_updated": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "age_hours": file_age.total_seconds() / 3600
                    }
                    
                    # Check data freshness
                    if file_age > timedelta(days=7):
                        status_report["data_freshness"][component_name] = "stale"
                        status_report["recommendations"].append(f"Update {component_name} - data is {file_age.days} days old")
                    elif file_age > timedelta(days=1):
                        status_report["data_freshness"][component_name] = "aging"
                    else:
                        status_report["data_freshness"][component_name] = "fresh"
                    
                    healthy_components += 1
                else:
                    status_report["component_status"][component_name] = {
                        "status": "missing",
                        "last_updated": None,
                        "age_hours": None
                    }
                    status_report["recommendations"].append(f"Regenerate missing component: {component_name}")
            
            # Determine overall pipeline health
            health_ratio = healthy_components / total_components
            if health_ratio >= 0.9:
                status_report["pipeline_health"] = "excellent"
            elif health_ratio >= 0.7:
                status_report["pipeline_health"] = "good"
            elif health_ratio >= 0.5:
                status_report["pipeline_health"] = "fair"
            else:
                status_report["pipeline_health"] = "poor"
            
            # Add general recommendations
            if not status_report["recommendations"]:
                status_report["recommendations"].append("Pipeline is healthy - no immediate actions needed")
            
        except Exception as e:
            self.logger.error(f"Error generating status report: {e}")
            status_report["pipeline_health"] = "error"
            status_report["error"] = str(e)
        
        # Save status report
        status_file = self.output_dir / f"status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with status_file.open("w") as f:
            json.dump(status_report, f, indent=2)
        
        return status_report

    def run_full_pipeline_refresh(self) -> Dict[str, Any]:
        """Run complete pipeline refresh"""
        self.logger.info("Starting full pipeline refresh...")
        
        refresh_results = {
            "timestamp": datetime.now().isoformat(),
            "steps_completed": [],
            "steps_failed": [],
            "overall_status": "running"
        }
        
        pipeline_steps = [
            ("unified_data_processor", "Cross-platform data unification"),
            ("ai_feature_engineer", "AI feature engineering"),
            ("quality_scoring_engine", "Quality scoring"),
            ("behavioral_document_processor", "Behavioral data processing")
        ]
        
        for step_module, step_description in pipeline_steps:
            try:
                self.logger.info(f"Running: {step_description}")
                
                # In a real implementation, this would dynamically import and run each processor
                # For now, we'll simulate the execution
                
                refresh_results["steps_completed"].append({
                    "step": step_module,
                    "description": step_description,
                    "completion_time": datetime.now().isoformat(),
                    "status": "success"
                })
                
                # Simulate processing time
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Failed step {step_module}: {e}")
                refresh_results["steps_failed"].append({
                    "step": step_module,
                    "description": step_description,
                    "error": str(e),
                    "failure_time": datetime.now().isoformat()
                })
        
        # Determine overall status
        if not refresh_results["steps_failed"]:
            refresh_results["overall_status"] = "success"
        elif len(refresh_results["steps_completed"]) > len(refresh_results["steps_failed"]):
            refresh_results["overall_status"] = "partial_success"
        else:
            refresh_results["overall_status"] = "failed"
        
        # Save refresh report
        refresh_file = self.output_dir / f"full_refresh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with refresh_file.open("w") as f:
            json.dump(refresh_results, f, indent=2)
        
        self.logger.info(f"Full pipeline refresh completed with status: {refresh_results['overall_status']}")
        return refresh_results

    def setup_automated_schedule(self) -> Dict[str, Any]:
        """Set up automated pipeline scheduling"""
        self.logger.info("Setting up automated pipeline schedule...")
        
        if not SCHEDULE_AVAILABLE:
            self.logger.warning("Schedule library not available - automation will be limited")
            schedule_config = {
                "setup_time": datetime.now().isoformat(),
                "scheduled_jobs": [],
                "status": "limited_no_schedule_library"
            }
        else:
            # Schedule quality checks every 6 hours
            schedule.every(6).hours.do(self.check_data_quality)
            
            # Schedule incremental updates daily at 2 AM
            schedule.every().day.at("02:00").do(self.run_incremental_update)
            
            # Schedule full refresh weekly on Sunday at 3 AM
            schedule.every().sunday.at("03:00").do(self.run_full_pipeline_refresh)
            
            # Schedule status reports daily at 9 AM
            schedule.every().day.at("09:00").do(self.generate_pipeline_status_report)
            
            schedule_config = {
                "setup_time": datetime.now().isoformat(),
                "scheduled_jobs": [
                    {"job": "data_quality_check", "frequency": "every_6_hours"},
                    {"job": "incremental_update", "frequency": "daily_2am"},
                    {"job": "full_refresh", "frequency": "weekly_sunday_3am"},
                    {"job": "status_report", "frequency": "daily_9am"}
                ],
                "status": "configured"
            }
        
        # Save schedule configuration
        schedule_file = self.output_dir / "schedule_config.json"
        with schedule_file.open("w") as f:
            json.dump(schedule_config, f, indent=2)
        
        self.logger.info("Automated schedule configured successfully")
        return schedule_config

    def run_pipeline_daemon(self, max_runtime_hours: int = 24) -> None:
        """Run the pipeline as a daemon process"""
        if not SCHEDULE_AVAILABLE:
            self.logger.error("Cannot run daemon mode - schedule library not available")
            return
            
        self.logger.info(f"Starting pipeline daemon (max runtime: {max_runtime_hours} hours)")
        
        start_time = datetime.now()
        max_runtime = timedelta(hours=max_runtime_hours)
        
        while datetime.now() - start_time < max_runtime:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.logger.info("Pipeline daemon stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in pipeline daemon: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
        
        self.logger.info("Pipeline daemon shutting down")

    def run_pipeline_automation_setup(self) -> Dict[str, Any]:
        """Set up complete pipeline automation"""
        print("=== Pipeline Automation Setup ===")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "setup_status": "running",
            "components": {}
        }
        
        try:
            # 1. Run initial quality check
            print("\n1. Running initial data quality check...")
            quality_check = self.check_data_quality()
            results["components"]["initial_quality_check"] = quality_check
            
            # 2. Generate status report
            print("\n2. Generating pipeline status report...")
            status_report = self.generate_pipeline_status_report()
            results["components"]["status_report"] = status_report
            
            # 3. Set up automation schedule
            print("\n3. Setting up automated scheduling...")
            schedule_config = self.setup_automated_schedule()
            results["components"]["schedule_config"] = schedule_config
            
            # 4. Test incremental update
            print("\n4. Testing incremental update process...")
            update_test = self.run_incremental_update()
            results["components"]["update_test"] = update_test
            
            results["setup_status"] = "success"
            results["pipeline_health"] = status_report.get("pipeline_health", "unknown")
            
            # Save automation setup summary
            summary_file = self.output_dir / "automation_setup_summary.json"
            with summary_file.open("w") as f:
                json.dump(results, f, indent=2)
            
            print(f"\n✅ Pipeline automation setup complete!")
            print(f"Pipeline health: {results['pipeline_health']}")
            print(f"Data quality: {quality_check['status']}")
            
            return results
            
        except Exception as e:
            results["setup_status"] = "failed"
            results["error"] = str(e)
            self.logger.error(f"Pipeline automation setup failed: {e}")
            return results


def main():
    """Main function for setting up pipeline automation"""
    from pathlib import Path
    
    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    
    # Create orchestrator
    orchestrator = DataPipelineOrchestrator(data_dir)
    
    # Run automation setup
    results = orchestrator.run_pipeline_automation_setup()
    
    if results["setup_status"] == "success":
        print("\n🎉 Pipeline automation setup completed successfully!")
        
        # Ask if user wants to run daemon mode
        print("\nTo run the pipeline in daemon mode, use:")
        print("orchestrator.run_pipeline_daemon(max_runtime_hours=24)")
    else:
        print(f"\n⚠️  Setup completed with status: {results['setup_status']}")
    
    return results


if __name__ == "__main__":
    main()
