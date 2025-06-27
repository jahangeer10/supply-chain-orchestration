
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime, timedelta

class BottleneckDetector:
    """Detects various types of bottlenecks in the supply chain."""
    
    def __init__(self):
        self.setup_logging()
        self.bottlenecks = []
    
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def detect_inventory_shortages(self, inventory_df: pd.DataFrame, orders_df: pd.DataFrame) -> List[Dict]:
        """Detect products with inventory below minimum threshold or insufficient for pending orders."""
        shortages = []
        
        # Check against minimum thresholds
        low_stock = inventory_df[inventory_df['current_stock'] <= inventory_df['min_threshold']]
        
        for _, item in low_stock.iterrows():
            shortages.append({
                'type': 'INVENTORY_SHORTAGE',
                'severity': 'HIGH' if item['current_stock'] < item['min_threshold'] * 0.5 else 'MEDIUM',
                'product_id': item['product_id'],
                'product_name': item['product_name'],
                'current_stock': item['current_stock'],
                'min_threshold': item['min_threshold'],
                'warehouse_id': item['warehouse_id'],
                'message': f"Product {item['product_name']} is below minimum threshold",
                'recommended_action': 'REORDER_IMMEDIATELY'
            })
        
        # Check against pending orders
        pending_orders = orders_df[orders_df['status'].isin(['PENDING', 'PROCESSING'])]
        order_demand = pending_orders.groupby('product_id')['quantity'].sum().reset_index()
        
        inventory_check = inventory_df.merge(order_demand, on='product_id', how='left')
        inventory_check['quantity'] = inventory_check['quantity'].fillna(0)
        
        insufficient_stock = inventory_check[inventory_check['current_stock'] < inventory_check['quantity']]
        
        for _, item in insufficient_stock.iterrows():
            shortages.append({
                'type': 'INSUFFICIENT_STOCK_FOR_ORDERS',
                'severity': 'HIGH',
                'product_id': item['product_id'],
                'product_name': item['product_name'],
                'current_stock': item['current_stock'],
                'required_quantity': item['quantity'],
                'shortage': item['quantity'] - item['current_stock'],
                'warehouse_id': item['warehouse_id'],
                'message': f"Insufficient stock for pending orders of {item['product_name']}",
                'recommended_action': 'EXPEDITE_REORDER'
            })
        
        self.logger.info(f"Detected {len(shortages)} inventory-related bottlenecks")
        return shortages
    
    def detect_delayed_shipments(self, shipments_df: pd.DataFrame) -> List[Dict]:
        """Detect shipments that are delayed or at risk of delay."""
        delays = []
        current_date = datetime.now()
        
        # Check for overdue shipments
        overdue = shipments_df[
            (shipments_df['estimated_arrival'] < current_date) & 
            (shipments_df['status'] != 'DELIVERED')
        ]
        
        for _, shipment in overdue.iterrows():
            days_overdue = (current_date - shipment['estimated_arrival']).days
            delays.append({
                'type': 'DELAYED_SHIPMENT',
                'severity': 'HIGH' if days_overdue > 3 else 'MEDIUM',
                'shipment_id': shipment['shipment_id'],
                'order_id': shipment['order_id'],
                'carrier': shipment['carrier'],
                'days_overdue': days_overdue,
                'estimated_arrival': shipment['estimated_arrival'],
                'status': shipment['status'],
                'message': f"Shipment {shipment['shipment_id']} is {days_overdue} days overdue",
                'recommended_action': 'CONTACT_CARRIER'
            })
        
        # Check for at-risk shipments (arriving within 1 day but still in transit)
        at_risk = shipments_df[
            (shipments_df['estimated_arrival'] <= current_date + timedelta(days=1)) &
            (shipments_df['estimated_arrival'] >= current_date) &
            (shipments_df['status'] == 'IN_TRANSIT')
        ]
        
        for _, shipment in at_risk.iterrows():
            delays.append({
                'type': 'AT_RISK_SHIPMENT',
                'severity': 'MEDIUM',
                'shipment_id': shipment['shipment_id'],
                'order_id': shipment['order_id'],
                'carrier': shipment['carrier'],
                'estimated_arrival': shipment['estimated_arrival'],
                'status': shipment['status'],
                'message': f"Shipment {shipment['shipment_id']} may be at risk of delay",
                'recommended_action': 'MONITOR_CLOSELY'
            })
        
        self.logger.info(f"Detected {len(delays)} shipping-related bottlenecks")
        return delays
    
    def detect_capacity_constraints(self, warehouses_df: pd.DataFrame, inventory_df: pd.DataFrame) -> List[Dict]:
        """Detect warehouse capacity constraints."""
        constraints = []
        
        # Calculate utilization by warehouse
        warehouse_utilization = inventory_df.groupby('warehouse_id').agg({
            'current_stock': 'sum'
        }).reset_index()
        
        warehouse_data = warehouses_df.merge(warehouse_utilization, on='warehouse_id', how='left')
        warehouse_data['current_stock'] = warehouse_data['current_stock'].fillna(0)
        warehouse_data['utilization_rate'] = warehouse_data['current_stock'] / warehouse_data['capacity']
        
        # Check for high utilization
        high_utilization = warehouse_data[warehouse_data['utilization_rate'] > 0.9]
        
        for _, warehouse in high_utilization.iterrows():
            constraints.append({
                'type': 'WAREHOUSE_CAPACITY_CONSTRAINT',
                'severity': 'HIGH' if warehouse['utilization_rate'] > 0.95 else 'MEDIUM',
                'warehouse_id': warehouse['warehouse_id'],
                'warehouse_name': warehouse['warehouse_name'],
                'utilization_rate': warehouse['utilization_rate'],
                'capacity': warehouse['capacity'],
                'current_utilization': warehouse['current_utilization'],
                'message': f"Warehouse {warehouse['warehouse_name']} is at {warehouse['utilization_rate']:.1%} capacity",
                'recommended_action': 'REDISTRIBUTE_INVENTORY'
            })
        
        self.logger.info(f"Detected {len(constraints)} capacity-related bottlenecks")
        return constraints
    
    def detect_demand_spikes(self, demand_history_df: pd.DataFrame) -> List[Dict]:
        """Detect unusual demand spikes."""
        spikes = []
        
        # Calculate demand trends by product
        for product_id in demand_history_df['product_id'].unique():
            product_data = demand_history_df[demand_history_df['product_id'] == product_id].copy()
            product_data = product_data.sort_values('date')
            
            if len(product_data) < 3:
                continue
            
            # Calculate moving average and detect spikes
            product_data['moving_avg'] = product_data['demand_quantity'].rolling(window=3, min_periods=1).mean()
            product_data['spike_threshold'] = product_data['moving_avg'] * 1.5
            
            recent_demand = product_data.iloc[-1]
            if recent_demand['demand_quantity'] > recent_demand['spike_threshold']:
                spikes.append({
                    'type': 'DEMAND_SPIKE',
                    'severity': 'MEDIUM',
                    'product_id': product_id,
                    'current_demand': recent_demand['demand_quantity'],
                    'average_demand': recent_demand['moving_avg'],
                    'spike_ratio': recent_demand['demand_quantity'] / recent_demand['moving_avg'],
                    'date': recent_demand['date'],
                    'message': f"Demand spike detected for product {product_id}",
                    'recommended_action': 'INCREASE_INVENTORY'
                })
        
        self.logger.info(f"Detected {len(spikes)} demand-related bottlenecks")
        return spikes
    
    def detect_supplier_issues(self, suppliers_df: pd.DataFrame, inventory_df: pd.DataFrame) -> List[Dict]:
        """Detect supplier reliability issues."""
        issues = []
        
        # Check for low reliability suppliers
        unreliable_suppliers = suppliers_df[suppliers_df['reliability_score'] < 0.9]
        
        for _, supplier in unreliable_suppliers.iterrows():
            # Find products from this supplier
            supplier_products = inventory_df[inventory_df['supplier_id'] == supplier['supplier_id']]
            
            issues.append({
                'type': 'SUPPLIER_RELIABILITY_ISSUE',
                'severity': 'HIGH' if supplier['reliability_score'] < 0.85 else 'MEDIUM',
                'supplier_id': supplier['supplier_id'],
                'supplier_name': supplier['supplier_name'],
                'reliability_score': supplier['reliability_score'],
                'lead_time_days': supplier['lead_time_days'],
                'affected_products': len(supplier_products),
                'message': f"Supplier {supplier['supplier_name']} has low reliability score",
                'recommended_action': 'FIND_ALTERNATIVE_SUPPLIER'
            })
        
        self.logger.info(f"Detected {len(issues)} supplier-related bottlenecks")
        return issues
    
    def run_full_analysis(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Run complete bottleneck analysis on all data."""
        all_bottlenecks = []
        
        # Run all detection methods
        all_bottlenecks.extend(self.detect_inventory_shortages(data['inventory'], data['orders']))
        all_bottlenecks.extend(self.detect_delayed_shipments(data['shipments']))
        all_bottlenecks.extend(self.detect_capacity_constraints(data['warehouses'], data['inventory']))
        all_bottlenecks.extend(self.detect_demand_spikes(data['demand_history']))
        all_bottlenecks.extend(self.detect_supplier_issues(data['suppliers'], data['inventory']))
        
        # Add timestamps and IDs
        for i, bottleneck in enumerate(all_bottlenecks):
            bottleneck['id'] = f"BN_{i+1:03d}"
            bottleneck['detected_at'] = datetime.now().isoformat()
        
        self.bottlenecks = all_bottlenecks
        self.logger.info(f"Total bottlenecks detected: {len(all_bottlenecks)}")
        
        return all_bottlenecks
    
    def get_bottleneck_summary(self) -> Dict[str, Any]:
        """Get summary of detected bottlenecks."""
        if not self.bottlenecks:
            return {'total': 0, 'by_type': {}, 'by_severity': {}}
        
        summary = {
            'total': len(self.bottlenecks),
            'by_type': {},
            'by_severity': {}
        }
        
        for bottleneck in self.bottlenecks:
            b_type = bottleneck['type']
            severity = bottleneck['severity']
            
            summary['by_type'][b_type] = summary['by_type'].get(b_type, 0) + 1
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
        
        return summary
    
    def get_critical_bottlenecks(self) -> List[Dict]:
        """Get only high-severity bottlenecks."""
        return [b for b in self.bottlenecks if b['severity'] == 'HIGH']
