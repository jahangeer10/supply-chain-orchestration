import pandas as pd
import os
from typing import Dict, Any
import logging

class DataLoader:
    """Handles loading and preprocessing of supply chain data from CSV files."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.data_cache = {}
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/data_loader.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_inventory_data(self) -> pd.DataFrame:
        """Load inventory data with validation."""
        try:
            df = pd.read_csv(os.path.join(self.data_dir, 'inventory.csv'))
            df['last_updated'] = pd.to_datetime(df['last_updated'])
            
            # Validate critical columns
            required_cols = ['product_id', 'current_stock', 'min_threshold', 'warehouse_id']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            self.logger.info(f"Loaded {len(df)} inventory records")
            return df
        except Exception as e:
            self.logger.error(f"Error loading inventory data: {e}")
            raise
    
    def load_orders_data(self) -> pd.DataFrame:
        """Load orders data with validation."""
        try:
            df = pd.read_csv(os.path.join(self.data_dir, 'orders.csv'))
            df['order_date'] = pd.to_datetime(df['order_date'])
            df['expected_delivery'] = pd.to_datetime(df['expected_delivery'])
            
            self.logger.info(f"Loaded {len(df)} order records")
            return df
        except Exception as e:
            self.logger.error(f"Error loading orders data: {e}")
            raise
    
    def load_shipments_data(self) -> pd.DataFrame:
        """Load shipments data with validation."""
        try:
            df = pd.read_csv(os.path.join(self.data_dir, 'shipments.csv'))
            df['ship_date'] = pd.to_datetime(df['ship_date'])
            df['estimated_arrival'] = pd.to_datetime(df['estimated_arrival'])
            
            # Handle actual_arrival which might have NaN values
            df['actual_arrival'] = pd.to_datetime(df['actual_arrival'], errors='coerce')
            
            self.logger.info(f"Loaded {len(df)} shipment records")
            return df
        except Exception as e:
            self.logger.error(f"Error loading shipments data: {e}")
            raise
    
    def load_suppliers_data(self) -> pd.DataFrame:
        """Load suppliers data."""
        try:
            df = pd.read_csv(os.path.join(self.data_dir, 'suppliers.csv'))
            self.logger.info(f"Loaded {len(df)} supplier records")
            return df
        except Exception as e:
            self.logger.error(f"Error loading suppliers data: {e}")
            raise
    
    def load_demand_history(self) -> pd.DataFrame:
        """Load demand history data."""
        try:
            df = pd.read_csv(os.path.join(self.data_dir, 'demand_history.csv'))
            df['date'] = pd.to_datetime(df['date'])
            self.logger.info(f"Loaded {len(df)} demand history records")
            return df
        except Exception as e:
            self.logger.error(f"Error loading demand history data: {e}")
            raise
    
    def load_warehouses_data(self) -> pd.DataFrame:
        """Load warehouses data."""
        try:
            df = pd.read_csv(os.path.join(self.data_dir, 'warehouses.csv'))
            self.logger.info(f"Loaded {len(df)} warehouse records")
            return df
        except Exception as e:
            self.logger.error(f"Error loading warehouses data: {e}")
            raise
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all supply chain data."""
        data = {
            'inventory': self.load_inventory_data(),
            'orders': self.load_orders_data(),
            'shipments': self.load_shipments_data(),
            'suppliers': self.load_suppliers_data(),
            'demand_history': self.load_demand_history(),
            'warehouses': self.load_warehouses_data()
        }
        
        self.data_cache = data
        self.logger.info("All data loaded successfully")
        return data
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary statistics of loaded data."""
        if not self.data_cache:
            self.load_all_data()
        
        summary = {}
        for name, df in self.data_cache.items():
            summary[name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum()
            }
        
        return summary
