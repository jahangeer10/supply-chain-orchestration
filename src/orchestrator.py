
from typing import Dict, List, Any
import pandas as pd
import logging
from datetime import datetime
import json

from data_loader import DataLoader
from bottleneck_detector import BottleneckDetector
from agents import (
    SupplyChainState, 
    DemandMonitoringAgent, 
    InventoryAgent, 
    LogisticsAgent, 
    OrchestratorAgent
)

class SupplyChainOrchestrator:
    """Main orchestrator for the supply chain management system."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_loader = DataLoader(data_dir)
        self.bottleneck_detector = BottleneckDetector()
        self.setup_logging()
        self.setup_workflow()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/orchestrator.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_workflow(self):
        """Setup the workflow for agent coordination."""
        # Simple sequential workflow without LangGraph for now
        self.workflow_steps = [
            self.load_data_node,
            self.detect_bottlenecks_node,
            self.demand_monitoring_node,
            self.inventory_management_node,
            self.logistics_optimization_node,
            self.orchestration_node,
            self.generate_report_node
        ]
        
        self.logger.info("Workflow setup completed")
    
    def load_data_node(self, state: SupplyChainState) -> SupplyChainState:
        """Load all supply chain data."""
        try:
            data = self.data_loader.load_all_data()
            state.data = data
            state.status = "DATA_LOADED"
            self.logger.info("Data loading completed successfully")
        except Exception as e:
            state.status = "FAILED"
            state.error = str(e)
            self.logger.error(f"Data loading failed: {e}")
        
        return state
    
    def detect_bottlenecks_node(self, state: SupplyChainState) -> SupplyChainState:
        """Detect bottlenecks in the supply chain."""
        if state.status == "FAILED":
            return state
        
        try:
            bottlenecks = self.bottleneck_detector.run_full_analysis(state.data)
            state.bottlenecks = bottlenecks
            state.status = "BOTTLENECKS_DETECTED"
            self.logger.info(f"Detected {len(bottlenecks)} bottlenecks")
        except Exception as e:
            state.status = "FAILED"
            state.error = str(e)
            self.logger.error(f"Bottleneck detection failed: {e}")
        
        return state
    
    def demand_monitoring_node(self, state: SupplyChainState) -> SupplyChainState:
        """Run demand monitoring agent."""
        if state.status == "FAILED":
            return state
        
        try:
            agent = DemandMonitoringAgent()
            recommendations = agent.analyze_demand(state.data, state.bottlenecks)
            state.recommendations.extend(recommendations)
            state.status = "DEMAND_ANALYZED"
            self.logger.info(f"Demand monitoring completed with {len(recommendations)} recommendations")
        except Exception as e:
            state.status = "FAILED"
            state.error = str(e)
            self.logger.error(f"Demand monitoring failed: {e}")
        
        return state
    
    def inventory_management_node(self, state: SupplyChainState) -> SupplyChainState:
        """Run inventory management agent."""
        if state.status == "FAILED":
            return state
        
        try:
            agent = InventoryAgent()
            recommendations = agent.optimize_inventory(state.data, state.bottlenecks)
            state.recommendations.extend(recommendations)
            state.status = "INVENTORY_OPTIMIZED"
            self.logger.info(f"Inventory optimization completed with {len(recommendations)} recommendations")
        except Exception as e:
            state.status = "FAILED"
            state.error = str(e)
            self.logger.error(f"Inventory optimization failed: {e}")
        
        return state
    
    def logistics_optimization_node(self, state: SupplyChainState) -> SupplyChainState:
        """Run logistics optimization agent."""
        if state.status == "FAILED":
            return state
        
        try:
            agent = LogisticsAgent()
            recommendations = agent.optimize_logistics(state.data, state.bottlenecks)
            state.recommendations.extend(recommendations)
            state.status = "LOGISTICS_OPTIMIZED"
            self.logger.info(f"Logistics optimization completed with {len(recommendations)} recommendations")
        except Exception as e:
            state.status = "FAILED"
            state.error = str(e)
            self.logger.error(f"Logistics optimization failed: {e}")
        
        return state
    
    def orchestration_node(self, state: SupplyChainState) -> SupplyChainState:
        """Run orchestrator agent for final decisions."""
        if state.status == "FAILED":
            return state
        
        try:
            agent = OrchestratorAgent()
            final_decisions = agent.make_decisions(state.data, state.bottlenecks, state.recommendations)
            state.final_decisions = final_decisions
            state.status = "DECISIONS_MADE"
            self.logger.info(f"Orchestration completed with {len(final_decisions)} final decisions")
        except Exception as e:
            state.status = "FAILED"
            state.error = str(e)
            self.logger.error(f"Orchestration failed: {e}")
        
        return state
    
    def generate_report_node(self, state: SupplyChainState) -> SupplyChainState:
        """Generate final analysis report."""
        if state.status == "FAILED":
            return state
        
        try:
            report = self.create_comprehensive_report(state)
            state.final_report = report
            state.status = "COMPLETED"
            
            # Save report to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/supply_chain_report_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            state.report_filename = filename
            self.logger.info(f"Report generated and saved to {filename}")
        except Exception as e:
            state.status = "FAILED"
            state.error = str(e)
            self.logger.error(f"Report generation failed: {e}")
        
        return state
    
    def create_comprehensive_report(self, state: SupplyChainState) -> Dict[str, Any]:
        """Create a comprehensive analysis report."""
        # Calculate summary statistics
        total_bottlenecks = len(state.bottlenecks)
        critical_bottlenecks = len([b for b in state.bottlenecks if b['severity'] == 'HIGH'])
        total_recommendations = len(state.recommendations)
        high_priority_recs = len([r for r in state.recommendations if r.get('priority') == 'HIGH'])
        
        # Determine overall status
        if critical_bottlenecks > 5:
            overall_status = "CRITICAL"
        elif critical_bottlenecks > 2:
            overall_status = "WARNING"
        else:
            overall_status = "NORMAL"
        
        # Create alerts
        alerts = []
        for bottleneck in state.bottlenecks:
            if bottleneck['severity'] == 'HIGH':
                alerts.append({
                    'type': 'CRITICAL_BOTTLENECK',
                    'message': bottleneck['message'],
                    'action_required': bottleneck['recommended_action'],
                    'severity': 'HIGH'
                })
        
        for rec in state.recommendations:
            if rec.get('priority') == 'HIGH':
                alerts.append({
                    'type': 'HIGH_PRIORITY_RECOMMENDATION',
                    'message': rec.get('message', rec['type']),
                    'action_required': rec.get('action', 'REVIEW'),
                    'severity': 'MEDIUM'
                })
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'status': overall_status,
            'summary': {
                'total_bottlenecks': total_bottlenecks,
                'critical_bottlenecks': critical_bottlenecks,
                'total_recommendations': total_recommendations,
                'high_priority_items': high_priority_recs,
                'total_alerts': len(alerts)
            },
            'bottlenecks': {
                'summary': self.bottleneck_detector.get_bottleneck_summary(),
                'details': state.bottlenecks
            },
            'recommendations': state.recommendations,
            'final_decisions': state.final_decisions,
            'alerts': alerts,
            'data_summary': self.data_loader.get_data_summary()
        }
        
        return report
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run the complete supply chain analysis workflow."""
        self.logger.info("Starting supply chain analysis workflow")
        
        # Initialize state
        state = SupplyChainState()
        
        # Execute workflow steps
        for step in self.workflow_steps:
            state = step(state)
            if state.status == "FAILED":
                self.logger.error(f"Workflow failed at step {step.__name__}: {state.error}")
                return {
                    'status': 'FAILED',
                    'error': state.error,
                    'failed_step': step.__name__
                }
        
        self.logger.info("Supply chain analysis workflow completed successfully")
        
        return {
            'status': 'SUCCESS',
            'final_report': state.final_report,
            'report_filename': state.report_filename
        }
    
    def get_real_time_status(self) -> Dict[str, Any]:
        """Get real-time status of the supply chain."""
        try:
            # Load current data
            data = self.data_loader.load_all_data()
            
            # Quick bottleneck check
            bottlenecks = self.bottleneck_detector.run_full_analysis(data)
            critical_issues = [b for b in bottlenecks if b['severity'] == 'HIGH']
            
            # Determine system health
            system_health = {
                'data_loading': 'GOOD',
                'inventory_levels': 'WARNING' if len([b for b in bottlenecks if 'INVENTORY' in b['type']]) > 0 else 'GOOD',
                'shipment_status': 'WARNING' if len([b for b in bottlenecks if 'SHIPMENT' in b['type']]) > 0 else 'GOOD',
                'supplier_reliability': 'WARNING' if len([b for b in bottlenecks if 'SUPPLIER' in b['type']]) > 0 else 'GOOD'
            }
            
            overall_status = "CRITICAL" if len(critical_issues) > 3 else "WARNING" if len(critical_issues) > 0 else "NORMAL"
            
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'overall_status': overall_status,
                'total_bottlenecks': len(bottlenecks),
                'critical_issues_count': len(critical_issues),
                'critical_issues': critical_issues[:5],  # Top 5 critical issues
                'system_health': system_health
            }
            
        except Exception as e:
            self.logger.error(f"Real-time status check failed: {e}")
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'overall_status': 'ERROR',
                'error': str(e)
            }
