#!/usr/bin/env python3
"""
Main entry point for the Supply Chain Orchestration System.
"""

import os
import sys
import argparse
import json
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from orchestrator import SupplyChainOrchestrator
from data_loader import DataLoader
from bottleneck_detector import BottleneckDetector

def setup_directories():
    """Ensure all necessary directories exist."""
    directories = ['logs', 'data', 'reports']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def run_full_analysis():
    """Run the complete supply chain analysis."""
    print("=" * 60)
    print("SUPPLY CHAIN ORCHESTRATION SYSTEM")
    print("=" * 60)
    print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize orchestrator
    orchestrator = SupplyChainOrchestrator(data_dir="data")
    
    # Run analysis
    result = orchestrator.run_analysis()
    
    if result.get('status') == 'FAILED':
        print(f"❌ Analysis failed: {result.get('error')}")
        return False
    
    # Display results
    if 'final_report' in result:
        report = result['final_report']
        print("📊 ANALYSIS RESULTS")
        print("-" * 40)
        print(f"Status: {report['status']}")
        print(f"Total Bottlenecks: {report['summary']['total_bottlenecks']}")
        print(f"Total Recommendations: {report['summary']['total_recommendations']}")
        print(f"Total Alerts: {report['summary']['total_alerts']}")
        print(f"High Priority Items: {report['summary']['high_priority_items']}")
        print()
        
        # Show critical bottlenecks
        critical_bottlenecks = [b for b in report['bottlenecks']['details'] if b['severity'] == 'HIGH']
        if critical_bottlenecks:
            print("🚨 CRITICAL BOTTLENECKS")
            print("-" * 40)
            for i, bottleneck in enumerate(critical_bottlenecks[:5], 1):
                print(f"{i}. {bottleneck['type']}: {bottleneck['message']}")
                print(f"   Action: {bottleneck['recommended_action']}")
            print()
        
        # Show top recommendations
        high_priority_recs = [r for r in report['recommendations'] if r.get('priority') == 'HIGH']
        if high_priority_recs:
            print("💡 HIGH PRIORITY RECOMMENDATIONS")
            print("-" * 40)
            for i, rec in enumerate(high_priority_recs[:5], 1):
                print(f"{i}. {rec['type']}")
                if 'product_id' in rec:
                    print(f"   Product: {rec['product_id']}")
                if 'message' in rec:
                    print(f"   Details: {rec['message']}")
                print(f"   Agent: {rec['agent']}")
            print()
        
        print(f"📄 Full report saved to: {result.get('report_filename')}")
        
    print("=" * 60)
    print(f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return True

def run_real_time_monitoring():
    """Run real-time monitoring mode."""
    print("🔄 REAL-TIME MONITORING MODE")
    print("-" * 40)
    
    orchestrator = SupplyChainOrchestrator(data_dir="data")
    
    try:
        while True:
            status = orchestrator.get_real_time_status()
            
            print(f"\n⏰ {status['timestamp']}")
            print(f"Overall Status: {status['overall_status']}")
            print(f"Critical Issues: {status['critical_issues_count']}")
            print(f"Total Bottlenecks: {status['total_bottlenecks']}")
            
            if status['critical_issues']:
                print("\n🚨 Top Critical Issues:")
                for i, issue in enumerate(status['critical_issues'], 1):
                    print(f"  {i}. {issue['type']}: {issue['message']}")
            
            print(f"\n📊 System Health:")
            for component, health in status['system_health'].items():
                emoji = "✅" if health == "GOOD" else "⚠️"
                print(f"  {emoji} {component.replace('_', ' ').title()}: {health}")
            
            print("\n" + "-" * 40)
            
            # Wait for 30 seconds before next check
            import time
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")

def test_data_loading():
    """Test data loading functionality."""
    print("🧪 TESTING DATA LOADING")
    print("-" * 40)
    
    try:
        data_loader = DataLoader(data_dir="data")
        data = data_loader.load_all_data()
        
        print("✅ Data loading successful!")
        print("\nData Summary:")
        for name, df in data.items():
            print(f"  {name}: {len(df)} rows, {len(df.columns)} columns")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def test_bottleneck_detection():
    """Test bottleneck detection functionality."""
    print("🧪 TESTING BOTTLENECK DETECTION")
    print("-" * 40)
    
    try:
        data_loader = DataLoader(data_dir="data")
        data = data_loader.load_all_data()
        
        detector = BottleneckDetector()
        bottlenecks = detector.run_full_analysis(data)
        
        print("✅ Bottleneck detection successful!")
        print(f"\nDetected {len(bottlenecks)} bottlenecks:")
        
        summary = detector.get_bottleneck_summary()
        for b_type, count in summary['by_type'].items():
            print(f"  {b_type}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Bottleneck detection failed: {e}")
        return False

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Supply Chain Orchestration System")
    parser.add_argument('--mode', choices=['analysis', 'monitor', 'test-data', 'test-bottlenecks'], 
                       default='analysis', help='Operation mode')
    
    args = parser.parse_args()
    
    # Setup directories
    setup_directories()
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)
    
    if args.mode == 'analysis':
        success = run_full_analysis()
        sys.exit(0 if success else 1)
    elif args.mode == 'monitor':
        run_real_time_monitoring()
    elif args.mode == 'test-data':
        success = test_data_loading()
        sys.exit(0 if success else 1)
    elif args.mode == 'test-bottlenecks':
        success = test_bottleneck_detection()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
