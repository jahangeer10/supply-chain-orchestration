
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(__file__))

from orchestrator import SupplyChainOrchestrator
from data_loader import DataLoader

# Page configuration
st.set_page_config(
    page_title="Supply Chain Orchestration Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = SupplyChainOrchestrator(data_dir="data")

def load_latest_report():
    """Load the latest analysis report."""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        return None
    
    report_files = [f for f in os.listdir(logs_dir) if f.startswith("supply_chain_report_") and f.endswith(".json")]
    if not report_files:
        return None
    
    latest_report = max(report_files)
    
    try:
        with open(os.path.join(logs_dir, latest_report), 'r') as f:
            return json.load(f)
    except:
        return None

def display_kpi_metrics(report):
    """Display key performance indicators."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Bottlenecks",
            value=report['summary']['total_bottlenecks'],
            delta=f"{report['summary']['critical_bottlenecks']} Critical"
        )
    
    with col2:
        st.metric(
            label="Recommendations",
            value=report['summary']['total_recommendations'],
            delta=f"{report['summary']['high_priority_items']} High Priority"
        )
    
    with col3:
        st.metric(
            label="Active Alerts",
            value=report['summary']['total_alerts'],
            delta="Real-time"
        )
    
    with col4:
        status_color = {
            'NORMAL': '🟢',
            'WARNING': '🟡', 
            'CRITICAL': '🔴'
        }
        st.metric(
            label="System Status",
            value=f"{status_color.get(report['status'], '⚪')} {report['status']}"
        )

def display_bottleneck_analysis(report):
    """Display bottleneck analysis charts."""
    st.subheader("🔍 Bottleneck Analysis")
    
    if not report['bottlenecks']['details']:
        st.info("No bottlenecks detected in the current analysis.")
        return
    
    # Bottleneck distribution by type
    bottleneck_summary = report['bottlenecks']['summary']
    
    col1, col2 = st.columns(2)
    
    with col1:
        if bottleneck_summary['by_type']:
            fig_type = px.pie(
                values=list(bottleneck_summary['by_type'].values()),
                names=list(bottleneck_summary['by_type'].keys()),
                title="Bottlenecks by Type"
            )
            st.plotly_chart(fig_type, use_container_width=True)
    
    with col2:
        if bottleneck_summary['by_severity']:
            fig_severity = px.bar(
                x=list(bottleneck_summary['by_severity'].keys()),
                y=list(bottleneck_summary['by_severity'].values()),
                title="Bottlenecks by Severity",
                color=list(bottleneck_summary['by_severity'].keys()),
                color_discrete_map={'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'yellow'}
            )
            st.plotly_chart(fig_severity, use_container_width=True)

def display_recommendations(report):
    """Display recommendations table."""
    st.subheader("💡 Recent Recommendations")
    
    if not report['recommendations']:
        st.info("No recommendations available.")
        return
    
    # Convert recommendations to DataFrame
    recs_df = pd.DataFrame(report['recommendations'])
    
    # Display top recommendations
    top_recs = recs_df.head(10)
    
    for i, rec in top_recs.iterrows():
        priority_color = {
            'HIGH': '🔴',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }
        
        with st.expander(f"{priority_color.get(rec.get('priority', 'LOW'), '⚪')} {rec['type']} - {rec['agent']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Product ID:** {rec.get('product_id', 'N/A')}")
                st.write(f"**Priority:** {rec.get('priority', 'N/A')}")
                st.write(f"**Agent:** {rec['agent']}")
            with col2:
                st.write(f"**Message:** {rec.get('message', 'No message')}")
                if 'action' in rec:
                    st.write(f"**Action:** {rec['action']}")

def display_alerts(report):
    """Display active alerts."""
    st.subheader("🚨 Active Alerts")
    
    if not report['alerts']:
        st.success("No active alerts.")
        return
    
    for alert in report['alerts'][:10]:  # Show top 10 alerts
        severity_color = {
            'HIGH': 'error',
            'MEDIUM': 'warning',
            'LOW': 'info'
        }
        
        alert_type = severity_color.get(alert.get('severity', 'LOW'), 'info')
        
        if alert_type == 'error':
            st.error(f"**{alert['type']}**: {alert['message']}")
        elif alert_type == 'warning':
            st.warning(f"**{alert['type']}**: {alert['message']}")
        else:
            st.info(f"**{alert['type']}**: {alert['message']}")

def display_inventory_status():
    """Display current inventory status."""
    st.subheader("📦 Inventory Status")
    
    try:
        data_loader = DataLoader(data_dir="data")
        inventory_df = data_loader.load_inventory_data()
        
        # Calculate inventory status
        inventory_df['status'] = inventory_df.apply(
            lambda row: 'Critical' if row['current_stock'] < row['min_threshold'] * 0.5
            else 'Low' if row['current_stock'] < row['min_threshold']
            else 'Normal', axis=1
        )
        
        # Status distribution
        status_counts = inventory_df['status'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Inventory Status Distribution",
                color_discrete_map={'Critical': 'red', 'Low': 'orange', 'Normal': 'green'}
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Critical inventory items
            critical_items = inventory_df[inventory_df['status'] == 'Critical']
            if not critical_items.empty:
                st.write("**Critical Inventory Items:**")
                for _, item in critical_items.iterrows():
                    st.error(f"{item['product_name']}: {item['current_stock']} units (Min: {item['min_threshold']})")
            else:
                st.success("No critical inventory items!")
        
        # Inventory levels chart
        fig_levels = px.bar(
            inventory_df,
            x='product_name',
            y=['current_stock', 'min_threshold'],
            title="Current Stock vs Minimum Threshold",
            barmode='group'
        )
        st.plotly_chart(fig_levels, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading inventory data: {e}")

def display_shipment_tracking():
    """Display shipment tracking information."""
    st.subheader("🚚 Shipment Tracking")
    
    try:
        data_loader = DataLoader(data_dir="data")
        shipments_df = data_loader.load_shipments_data()
        
        # Shipment status distribution
        status_counts = shipments_df['status'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_shipments = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Shipment Status Distribution"
            )
            st.plotly_chart(fig_shipments, use_container_width=True)
        
        with col2:
            # Carrier performance
            carrier_stats = shipments_df.groupby('carrier').agg({
                'cost': 'mean',
                'shipment_id': 'count'
            }).round(2)
            carrier_stats.columns = ['Avg Cost', 'Shipment Count']
            st.write("**Carrier Performance:**")
            st.dataframe(carrier_stats)
        
        # Recent shipments
        st.write("**Recent Shipments:**")
        recent_shipments = shipments_df.sort_values('ship_date', ascending=False).head(5)
        st.dataframe(recent_shipments[['shipment_id', 'carrier', 'status', 'estimated_arrival', 'cost']])
        
    except Exception as e:
        st.error(f"Error loading shipment data: {e}")

def display_real_time_analysis():
    """Display real-time analysis."""
    st.subheader("⚡ Real-time Analysis")
    
    if st.button("🔄 Run Real-time Analysis", type="primary"):
        with st.spinner("Running real-time analysis..."):
            try:
                status = st.session_state.orchestrator.get_real_time_status()
                
                # Display system health
                st.write("### System Health Status")
                health_cols = st.columns(len(status['system_health']))
                
                for i, (component, health) in enumerate(status['system_health'].items()):
                    with health_cols[i]:
                        health_emoji = "✅" if health == "GOOD" else "⚠️"
                        st.metric(
                            label=component.replace('_', ' ').title(),
                            value=f"{health_emoji} {health}"
                        )
                
                # Display critical issues
                if status['critical_issues']:
                    st.write("### Critical Issues")
                    for issue in status['critical_issues']:
                        st.error(f"**{issue['type']}**: {issue['message']}")
                else:
                    st.success("No critical issues detected!")
                
                # Overall status
                st.write(f"### Overall Status: {status['overall_status']}")
                st.write(f"**Last Updated:** {status['timestamp']}")
                
            except Exception as e:
                st.error(f"Error running real-time analysis: {e}")

# Main dashboard
def main():
    st.title("📦 Supply Chain Orchestration Dashboard")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Overview", "Inventory Status", "Shipment Tracking", "Real-time Analysis"]
    )
    
    # Load latest report
    report = load_latest_report()
    
    if page == "Overview":
        if report:
            st.write(f"**Last Analysis:** {report['timestamp']}")
            display_kpi_metrics(report)
            st.markdown("---")
            display_bottleneck_analysis(report)
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                display_recommendations(report)
            with col2:
                display_alerts(report)
        else:
            st.warning("No analysis report found. Please run the analysis first.")
            if st.button("Run Analysis"):
                with st.spinner("Running supply chain analysis..."):
                    try:
                        result = st.session_state.orchestrator.run_analysis()
                        if result['status'] == 'SUCCESS':
                            st.success("Analysis completed successfully!")
                            st.rerun()
                        else:
                            st.error(f"Analysis failed: {result.get('error')}")
                    except Exception as e:
                        st.error(f"Error running analysis: {e}")
    
    elif page == "Inventory Status":
        display_inventory_status()
    
    elif page == "Shipment Tracking":
        display_shipment_tracking()
    
    elif page == "Real-time Analysis":
        display_real_time_analysis()

if __name__ == "__main__":
    main()
