from __future__ import annotations

import argparse
from pathlib import Path

from src.monitoring.trend_monitor import InterviewTrendMonitor


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor Google interview and hiring practice trends")
    parser.add_argument("--data-dir", default=None, help="Override default data directory")
    parser.add_argument("--google-only", action="store_true", help="Monitor only Google official sources")
    parser.add_argument("--discussions-only", action="store_true", help="Monitor only public discussions")
    parser.add_argument("--platforms-only", action="store_true", help="Monitor only competitive platforms")
    args = parser.parse_args()

    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = Path(__file__).resolve().parents[2] / "data"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("Monitoring Google interview and hiring practice trends...")
    print("This tracks changes in official documentation, public discussions, and platform patterns.")
    
    monitor = InterviewTrendMonitor(data_dir)
    
    if args.google_only:
        print("\n=== Google Official Sources Only ===")
        result = monitor.monitor_google_engineering_updates()
        print(f"Monitored {result['sources_checked']} Google sources")
        
    elif args.discussions_only:
        print("\n=== Public Discussions Only ===")
        result = monitor.monitor_interview_discussions()
        print(f"Monitored {result['sources_checked']} discussion sources")
        
    elif args.platforms_only:
        print("\n=== Competitive Platforms Only ===")
        result = monitor.monitor_competitive_platforms()
        print(f"Monitored {result['platforms_checked']} platforms")
        
    else:
        print("\n=== Comprehensive Monitoring Cycle ===")
        result = monitor.run_monitoring_cycle()
        print(f"✅ Monitoring complete!")
        print(f"   📊 Sources monitored: {result['sources_monitored']}")
        print(f"   🚨 Alerts generated: {result['alerts_generated']}")
        print(f"   📄 Report saved to: monitoring/ directory")
        
        if result['alerts_generated'] > 0:
            print(f"\n⚠️  {result['alerts_generated']} alerts require attention - check the trend report")


if __name__ == "__main__":
    main()
