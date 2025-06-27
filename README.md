
# Supply Chain Orchestration System

A comprehensive multi-agent supply chain management system built with LangGraph that monitors demand fluctuations, manages inventory, optimizes logistics, and coordinates multiple AI agents to identify bottlenecks and optimize operations.

## 🏗️ Architecture

### Multi-Agent System
- **Demand Monitoring Agent**: Tracks demand fluctuations and generates forecasts
- **Inventory Agent**: Monitors stock levels and identifies shortages/overstock
- **Logistics Agent**: Handles routing optimization and shipping coordination
- **Orchestrator Agent**: Coordinates between agents and makes final decisions

### Core Components
- **Data Loader**: CSV data ingestion with validation and preprocessing
- **Bottleneck Detector**: Identifies various supply chain bottlenecks
- **LangGraph Workflow**: Manages agent coordination and state
- **Dashboard**: Real-time monitoring and visualization

## 📊 Features

### Bottleneck Detection
- Inventory shortages and overstock situations
- Delayed shipments and at-risk deliveries
- Warehouse capacity constraints
- Demand spikes and unusual patterns
- Supplier reliability issues

### Agent Capabilities
- **Demand Analysis**: Pattern recognition, forecasting, spike detection
- **Inventory Management**: Reorder recommendations, distribution optimization
- **Logistics Optimization**: Route optimization, carrier selection
- **Orchestration**: Decision making, priority management, coordination

### Data Processing
- CSV data ingestion for POC (extensible to databases)
- Real-time data validation and preprocessing
- Historical trend analysis
- Performance metrics calculation

## 🚀 Quick Start

### Installation

1. **Clone and setup the project:**
```bash
git clone https://github.com/jahangeer10/supply-chain-orchestration.git
cd supply-chain-orchestration
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Run the analysis:**
```bash
python src/main.py --mode analysis
```

3. **Start the dashboard:**
```bash
streamlit run src/dashboard.py
```

### Command Line Options

```bash
# Full supply chain analysis
python src/main.py --mode analysis

# Real-time monitoring
python src/main.py --mode monitor

# Test data loading
python src/main.py --mode test-data

# Test bottleneck detection
python src/main.py --mode test-bottlenecks
```

## 📁 Project Structure

```
supply_chain_orchestration/
├── data/                          # CSV data files
│   ├── inventory.csv             # Product inventory data
│   ├── orders.csv                # Customer orders
│   ├── shipments.csv             # Shipping information
│   ├── suppliers.csv             # Supplier details
│   ├── demand_history.csv        # Historical demand data
│   └── warehouses.csv            # Warehouse information
├── src/                          # Source code
│   ├── main.py                   # Main entry point
│   ├── orchestrator.py           # Main orchestrator with LangGraph
│   ├── agents.py                 # Multi-agent implementations
│   ├── data_loader.py            # Data loading and validation
│   ├── bottleneck_detector.py    # Bottleneck detection algorithms
│   └── dashboard.py              # Streamlit dashboard
├── logs/                         # Log files and reports
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🔧 Configuration

### Data Sources
The system currently uses CSV files for data input. Each CSV file represents a different aspect of the supply chain:

- **inventory.csv**: Current stock levels, thresholds, and warehouse assignments
- **orders.csv**: Customer orders with priorities and delivery dates
- **shipments.csv**: Shipping status, carriers, and tracking information
- **suppliers.csv**: Supplier information, lead times, and reliability scores
- **demand_history.csv**: Historical demand patterns for forecasting
- **warehouses.csv**: Warehouse capacity and utilization data

### Agent Configuration
Agents can be configured by modifying their respective classes in `src/agents.py`. Key parameters include:

- Threshold values for bottleneck detection
- Forecasting algorithms and confidence levels
- Optimization criteria and weights
- Alert severity levels

## 📈 Dashboard Features

### Overview Page
- Key performance indicators (KPIs)
- Bottleneck analysis with charts
- Recent recommendations and alerts
- System status summary

### Inventory Status
- Stock level monitoring
- Critical inventory alerts
- Inventory distribution analysis
- Reorder recommendations

### Shipment Tracking
- Shipment status distribution
- Carrier performance analysis
- Delivery tracking and delays
- Cost optimization insights

### Real-time Analysis
- Current system health status
- Live bottleneck detection
- Critical issue alerts
- Performance metrics

## 🤖 Agent Workflows

### LangGraph Workflow
The system uses LangGraph to orchestrate the multi-agent workflow:

1. **Data Loading**: Load and validate all supply chain data
2. **Bottleneck Detection**: Identify potential issues across all areas
3. **Demand Monitoring**: Analyze demand patterns and generate forecasts
4. **Inventory Management**: Monitor stock levels and optimize distribution
5. **Logistics Optimization**: Optimize routes and shipping decisions
6. **Orchestration**: Coordinate agents and make final decisions
7. **Report Generation**: Create comprehensive analysis reports

### Agent Communication
Agents communicate through a shared state object that contains:
- Supply chain data
- Detected bottlenecks
- Recommendations from each agent
- Alerts and notifications
- Decision history

## 📊 Sample Data

The system includes realistic mock data for testing:

- **10 products** across 3 warehouses
- **10 customer orders** with various priorities
- **5 active shipments** with different carriers
- **4 suppliers** with varying reliability scores
- **Historical demand data** for trend analysis
- **3 warehouses** with different capacities

## 🔍 Bottleneck Types

The system detects various types of bottlenecks:

1. **Inventory Shortages**: Stock below minimum thresholds
2. **Insufficient Stock**: Not enough inventory for pending orders
3. **Delayed Shipments**: Overdue or at-risk deliveries
4. **Capacity Constraints**: Warehouse utilization issues
5. **Demand Spikes**: Unusual increases in product demand
6. **Supplier Issues**: Reliability or lead time problems

## 📝 Logging and Monitoring

### Log Files
- `logs/data_loader.log`: Data loading operations
- `logs/orchestrator.log`: Main orchestration activities
- `logs/supply_chain_report_*.json`: Analysis reports with timestamps

### Monitoring Features
- Real-time status updates
- Performance metrics tracking
- Alert notifications
- Decision audit trail

## 🔮 Future Enhancements

### Planned Features
- Database integration (PostgreSQL, MongoDB)
- Machine learning-based forecasting
- Advanced optimization algorithms
- Integration with external APIs (weather, traffic, etc.)
- Mobile dashboard application
- Automated decision execution
- Multi-tenant support

### Scalability Considerations
- Microservices architecture
- Container deployment (Docker/Kubernetes)
- Message queue integration (Redis, RabbitMQ)
- Distributed processing capabilities
- Cloud deployment options

## 🛠️ Development

### Adding New Agents
1. Create a new agent class inheriting from `BaseAgent`
2. Implement required methods for analysis and recommendations
3. Add the agent to the workflow in `orchestrator.py`
4. Update the dashboard to display agent-specific metrics

### Extending Data Sources
1. Add new CSV files to the `data/` directory
2. Update `DataLoader` class to handle new data types
3. Modify agents to utilize new data sources
4. Update bottleneck detection algorithms as needed

### Custom Bottleneck Detection
1. Add new detection methods to `BottleneckDetector` class
2. Define severity levels and recommended actions
3. Update the orchestrator to handle new bottleneck types
4. Add visualization to the dashboard

## 📞 Support

For questions, issues, or contributions:

1. Check the logs in the `logs/` directory for error details
2. Verify data file formats match the expected schema
3. Ensure all dependencies are installed correctly
4. Review agent configurations for threshold adjustments

## 📄 License

This project is designed as a proof-of-concept for supply chain orchestration using multi-agent systems and LangGraph. It demonstrates the capabilities of AI-driven supply chain management and can be extended for production use cases.
