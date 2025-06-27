
from typing import Dict, List, Any, Optional
import pandas as pd
import logging
from datetime import datetime, timedelta
import json

# Define the state structure for the multi-agent system
class SupplyChainState:
    def __init__(self):
        self.data: Dict[str, pd.DataFrame] = {}
        self.bottlenecks: List[Dict] = []
        self.recommendations: List[Dict] = []
        self.alerts: List[Dict] = []
        self.agent_messages: List[Dict] = []
        self.current_agent: str = ""
        self.iteration: int = 0
        self.status: str = "INITIALIZING"
        self.final_decisions: List[Dict] = []
        self.final_report: Dict = {}
        self.report_filename: str = ""
        self.error: str = ""

class BaseAgent:
    """Base class for all supply chain agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"Agent.{self.name}")
    
    def log_action(self, action: str, details: Dict = None):
        """Log agent actions for monitoring."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.name,
            'action': action,
            'details': details or {}
        }
        self.logger.info(f"[{self.name}] {action}: {details}")
        return log_entry

class DemandMonitoringAgent(BaseAgent):
    """Agent responsible for monitoring demand fluctuations and forecasting."""
    
    def __init__(self):
        super().__init__("DemandMonitor")
    
    def analyze_demand(self, data: Dict[str, pd.DataFrame], bottlenecks: List[Dict]) -> List[Dict]:
        """Analyze demand patterns and generate recommendations."""
        self.log_action("ANALYZING_DEMAND_PATTERNS")
        
        recommendations = []
        demand_df = data.get('demand_history')
        orders_df = data.get('orders')
        
        if demand_df is None or orders_df is None:
            self.logger.warning("Missing demand or orders data")
            return recommendations
        
        # Analyze recent vs historical demand
        recent_orders = orders_df[orders_df['order_date'] >= datetime.now() - timedelta(days=7)]
        recent_demand = recent_orders.groupby('product_id')['quantity'].sum().reset_index()
        historical_avg = demand_df.groupby('product_id')['demand_quantity'].mean().reset_index()
        
        # Merge and calculate variance
        demand_analysis = recent_demand.merge(historical_avg, on='product_id', how='outer', suffixes=('_recent', '_avg'))
        demand_analysis = demand_analysis.fillna(0)
        demand_analysis['variance_ratio'] = demand_analysis['quantity'] / (demand_analysis['demand_quantity'] + 1)
        
        # Generate recommendations based on demand patterns
        for _, row in demand_analysis.iterrows():
            if row['variance_ratio'] > 1.5:  # 50% increase
                recommendations.append({
                    'type': 'INCREASE_INVENTORY_FOR_DEMAND_SPIKE',
                    'product_id': row['product_id'],
                    'current_demand': row['quantity'],
                    'historical_avg': row['demand_quantity'],
                    'recommended_increase': row['quantity'] * 0.3,
                    'agent': self.name,
                    'priority': 'HIGH',
                    'message': f"Demand spike detected for product {row['product_id']}"
                })
            elif row['variance_ratio'] < 0.5:  # 50% decrease
                recommendations.append({
                    'type': 'REDUCE_INVENTORY_FOR_LOW_DEMAND',
                    'product_id': row['product_id'],
                    'current_demand': row['quantity'],
                    'historical_avg': row['demand_quantity'],
                    'agent': self.name,
                    'priority': 'MEDIUM',
                    'message': f"Low demand detected for product {row['product_id']}"
                })
        
        # Analyze demand-related bottlenecks
        demand_bottlenecks = [b for b in bottlenecks if 'DEMAND' in b['type']]
        for bottleneck in demand_bottlenecks:
            recommendations.append({
                'type': 'ADDRESS_DEMAND_BOTTLENECK',
                'bottleneck_id': bottleneck.get('id'),
                'product_id': bottleneck.get('product_id'),
                'agent': self.name,
                'priority': 'HIGH',
                'action': 'FORECAST_ADJUSTMENT',
                'message': f"Address demand bottleneck: {bottleneck['message']}"
            })
        
        self.log_action("DEMAND_ANALYSIS_COMPLETED", {'recommendations': len(recommendations)})
        return recommendations

class InventoryAgent(BaseAgent):
    """Agent responsible for inventory management and optimization."""
    
    def __init__(self):
        super().__init__("InventoryManager")
    
    def optimize_inventory(self, data: Dict[str, pd.DataFrame], bottlenecks: List[Dict]) -> List[Dict]:
        """Optimize inventory levels and generate recommendations."""
        self.log_action("OPTIMIZING_INVENTORY")
        
        recommendations = []
        inventory_df = data.get('inventory')
        orders_df = data.get('orders')
        
        if inventory_df is None:
            self.logger.warning("Missing inventory data")
            return recommendations
        
        # Analyze inventory levels
        for _, item in inventory_df.iterrows():
            stock_ratio = item['current_stock'] / item['min_threshold']
            
            if stock_ratio < 0.5:  # Critical low stock
                recommendations.append({
                    'type': 'EMERGENCY_REORDER',
                    'product_id': item['product_id'],
                    'product_name': item['product_name'],
                    'current_stock': item['current_stock'],
                    'min_threshold': item['min_threshold'],
                    'recommended_quantity': item['min_threshold'] * 2,
                    'warehouse_id': item['warehouse_id'],
                    'supplier_id': item['supplier_id'],
                    'agent': self.name,
                    'priority': 'HIGH',
                    'message': f"Emergency reorder needed for {item['product_name']}"
                })
            elif stock_ratio < 1.0:  # Below minimum
                recommendations.append({
                    'type': 'STANDARD_REORDER',
                    'product_id': item['product_id'],
                    'product_name': item['product_name'],
                    'current_stock': item['current_stock'],
                    'min_threshold': item['min_threshold'],
                    'recommended_quantity': item['min_threshold'] * 1.5,
                    'warehouse_id': item['warehouse_id'],
                    'supplier_id': item['supplier_id'],
                    'agent': self.name,
                    'priority': 'MEDIUM',
                    'message': f"Standard reorder recommended for {item['product_name']}"
                })
        
        # Address inventory-related bottlenecks
        inventory_bottlenecks = [b for b in bottlenecks if 'INVENTORY' in b['type']]
        for bottleneck in inventory_bottlenecks:
            recommendations.append({
                'type': 'RESOLVE_INVENTORY_BOTTLENECK',
                'bottleneck_id': bottleneck.get('id'),
                'product_id': bottleneck.get('product_id'),
                'warehouse_id': bottleneck.get('warehouse_id'),
                'agent': self.name,
                'priority': 'HIGH',
                'action': bottleneck.get('recommended_action', 'REORDER'),
                'message': f"Resolve inventory bottleneck: {bottleneck['message']}"
            })
        
        self.log_action("INVENTORY_OPTIMIZATION_COMPLETED", {'recommendations': len(recommendations)})
        return recommendations

class LogisticsAgent(BaseAgent):
    """Agent responsible for logistics optimization and shipping coordination."""
    
    def __init__(self):
        super().__init__("LogisticsOptimizer")
    
    def optimize_logistics(self, data: Dict[str, pd.DataFrame], bottlenecks: List[Dict]) -> List[Dict]:
        """Optimize logistics and shipping operations."""
        self.log_action("OPTIMIZING_LOGISTICS")
        
        recommendations = []
        shipments_df = data.get('shipments')
        orders_df = data.get('orders')
        
        if shipments_df is None:
            self.logger.warning("Missing shipments data")
            return recommendations
        
        # Analyze shipment performance
        current_date = datetime.now()
        
        # Check for delayed shipments
        delayed_shipments = shipments_df[
            (shipments_df['estimated_arrival'] < current_date) & 
            (shipments_df['status'] != 'DELIVERED')
        ]
        
        for _, shipment in delayed_shipments.iterrows():
            recommendations.append({
                'type': 'EXPEDITE_DELAYED_SHIPMENT',
                'shipment_id': shipment['shipment_id'],
                'order_id': shipment['order_id'],
                'carrier': shipment['carrier'],
                'estimated_arrival': shipment['estimated_arrival'],
                'agent': self.name,
                'priority': 'HIGH',
                'action': 'CONTACT_CARRIER',
                'message': f"Expedite delayed shipment {shipment['shipment_id']}"
            })
        
        # Analyze carrier performance
        carrier_performance = shipments_df.groupby('carrier').agg({
            'cost': 'mean',
            'shipment_id': 'count'
        }).reset_index()
        carrier_performance.columns = ['carrier', 'avg_cost', 'shipment_count']
        
        # Recommend cost optimization
        if len(carrier_performance) > 1:
            cheapest_carrier = carrier_performance.loc[carrier_performance['avg_cost'].idxmin()]
            recommendations.append({
                'type': 'OPTIMIZE_CARRIER_SELECTION',
                'recommended_carrier': cheapest_carrier['carrier'],
                'avg_cost': cheapest_carrier['avg_cost'],
                'agent': self.name,
                'priority': 'MEDIUM',
                'message': f"Consider using {cheapest_carrier['carrier']} for cost optimization"
            })
        
        # Address logistics-related bottlenecks
        logistics_bottlenecks = [b for b in bottlenecks if 'SHIPMENT' in b['type'] or 'DELAYED' in b['type']]
        for bottleneck in logistics_bottlenecks:
            recommendations.append({
                'type': 'RESOLVE_LOGISTICS_BOTTLENECK',
                'bottleneck_id': bottleneck.get('id'),
                'shipment_id': bottleneck.get('shipment_id'),
                'carrier': bottleneck.get('carrier'),
                'agent': self.name,
                'priority': 'HIGH',
                'action': bottleneck.get('recommended_action', 'INVESTIGATE'),
                'message': f"Resolve logistics bottleneck: {bottleneck['message']}"
            })
        
        self.log_action("LOGISTICS_OPTIMIZATION_COMPLETED", {'recommendations': len(recommendations)})
        return recommendations

class OrchestratorAgent(BaseAgent):
    """Agent responsible for coordinating decisions across all other agents."""
    
    def __init__(self):
        super().__init__("Orchestrator")
    
    def make_decisions(self, data: Dict[str, pd.DataFrame], bottlenecks: List[Dict], recommendations: List[Dict]) -> List[Dict]:
        """Make final coordinated decisions based on all agent inputs."""
        self.log_action("MAKING_FINAL_DECISIONS")
        
        final_decisions = []
        
        # Prioritize recommendations
        high_priority_recs = [r for r in recommendations if r.get('priority') == 'HIGH']
        medium_priority_recs = [r for r in recommendations if r.get('priority') == 'MEDIUM']
        
        # Group by type for coordination
        decision_groups = {}
        for rec in high_priority_recs + medium_priority_recs:
            rec_type = rec['type']
            if rec_type not in decision_groups:
                decision_groups[rec_type] = []
            decision_groups[rec_type].append(rec)
        
        # Make coordinated decisions
        for decision_type, recs in decision_groups.items():
            if 'REORDER' in decision_type or 'INVENTORY' in decision_type:
                # Consolidate inventory decisions
                products = {}
                for rec in recs:
                    product_id = rec.get('product_id')
                    if product_id:
                        if product_id not in products:
                            products[product_id] = rec
                        else:
                            # Merge recommendations for same product
                            existing = products[product_id]
                            if rec.get('priority') == 'HIGH' and existing.get('priority') != 'HIGH':
                                products[product_id] = rec
                
                for product_id, decision in products.items():
                    final_decisions.append({
                        'decision_id': f"DEC_{len(final_decisions)+1:03d}",
                        'type': 'INVENTORY_ACTION',
                        'action': decision['type'],
                        'product_id': product_id,
                        'priority': decision['priority'],
                        'details': decision,
                        'coordinating_agent': self.name,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'APPROVED'
                    })
            
            elif 'LOGISTICS' in decision_type or 'SHIPMENT' in decision_type:
                # Consolidate logistics decisions
                for rec in recs:
                    final_decisions.append({
                        'decision_id': f"DEC_{len(final_decisions)+1:03d}",
                        'type': 'LOGISTICS_ACTION',
                        'action': rec['type'],
                        'shipment_id': rec.get('shipment_id'),
                        'carrier': rec.get('carrier'),
                        'priority': rec['priority'],
                        'details': rec,
                        'coordinating_agent': self.name,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'APPROVED'
                    })
            
            else:
                # Other decisions
                for rec in recs:
                    final_decisions.append({
                        'decision_id': f"DEC_{len(final_decisions)+1:03d}",
                        'type': 'GENERAL_ACTION',
                        'action': rec['type'],
                        'priority': rec['priority'],
                        'details': rec,
                        'coordinating_agent': self.name,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'APPROVED'
                    })
        
        # Add decisions for critical bottlenecks
        critical_bottlenecks = [b for b in bottlenecks if b['severity'] == 'HIGH']
        for bottleneck in critical_bottlenecks:
            final_decisions.append({
                'decision_id': f"DEC_{len(final_decisions)+1:03d}",
                'type': 'CRITICAL_BOTTLENECK_RESOLUTION',
                'action': bottleneck.get('recommended_action', 'INVESTIGATE'),
                'bottleneck_id': bottleneck.get('id'),
                'priority': 'CRITICAL',
                'details': bottleneck,
                'coordinating_agent': self.name,
                'timestamp': datetime.now().isoformat(),
                'status': 'URGENT'
            })
        
        self.log_action("FINAL_DECISIONS_COMPLETED", {
            'total_decisions': len(final_decisions),
            'critical_decisions': len([d for d in final_decisions if d['priority'] == 'CRITICAL'])
        })
        
        return final_decisions
