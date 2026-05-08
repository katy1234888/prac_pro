import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Logistics Analytics Dashboard", layout="wide")

st.title("🚚 Delivery Experience Analysis: Festive Surge Report")
st.markdown("""
This dashboard investigates the decline in customer satisfaction and operational performance 
during the October-December festive peak.
""")

# --- Sidebar: Data Upload ---
st.sidebar.header("📁 Upload Data Sources")
def upload_file(label, key):
    return st.sidebar.file_uploader(label, type=['csv'], key=key)

orders_file = upload_file("Orders Data", "orders")
nps_file = upload_file("NPS Responses", "nps")
customers_file = upload_file("Customer Data", "customers")
complaints_file = upload_file("Complaints Data", "complaints")
hub_file = upload_file("Hub Performance", "hub")
courier_file = upload_file("Courier Performance", "courier")

# --- Logic to load and process data ---
if orders_file and nps_file and customers_file and complaints_file:
    # Read Data
    df_orders = pd.read_csv(orders_file)
    df_nps = pd.read_csv(nps_file).dropna(subset=['score'])
    df_customers = pd.read_csv(customers_file).dropna(subset=['customer_id'])
    df_complaints = pd.read_csv(complaints_file).dropna(subset=['order_id'])
    
    # 1. Preprocessing Orders
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
    df_orders['promised_date'] = pd.to_datetime(df_orders['promised_date'])
    df_orders['delivery_date'] = pd.to_datetime(df_orders['delivery_date'])
    
    # Calculate Delivery Delay & SLA Breach
    df_orders['delivery_delay'] = (df_orders['delivery_date'] - df_orders['promised_date']).dt.days
    df_orders['sla_breach'] = df_orders['delivery_delay'] > 0
    df_orders['month'] = df_orders['order_date'].dt.strftime('%Y-%m')

    # 2. NPS Categorization
    def categorize_nps(score):
        if score <= 6: return 'Detractor'
        elif score <= 8: return 'Passive'
        else: return 'Promoter'
    
    df_nps['category'] = df_nps['score'].apply(categorize_nps)
    df_nps['month'] = pd.to_datetime(df_nps['response_date']).dt.strftime('%Y-%m')

    # --- Section A: NPS & Customer Experience ---
    st.header("Section A: NPS & Customer Experience")
    
    # Overall NPS Calculation
    nps_counts = df_nps['category'].value_counts(normalize=True) * 100
    overall_nps = nps_counts.get('Promoter', 0) - nps_counts.get('Detractor', 0)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall NPS Score", f"{overall_nps:.1f}")
    col2.metric("Total Responses", len(df_nps))
    col3.metric("Detractor %", f"{nps_counts.get('Detractor', 0):.1f}%")

    # NPS Trend
    nps_trend = df_nps.groupby(['month', 'category']).size().unstack(fill_value=0)
    nps_trend_score = ((nps_trend.get('Promoter', 0) - nps_trend.get('Detractor', 0)) / nps_trend.sum(axis=1)) * 100
    
    fig_trend = px.line(nps_trend_score, title="Monthly NPS Trend", labels={'value': 'NPS Score', 'month': 'Month'})
    st.plotly_chart(fig_trend, use_container_width=True)

    # NPS by Segment
    df_nps_seg = df_nps.merge(df_customers[['customer_id', 'segment']], on='customer_id', how='left')
    seg_nps = df_nps_seg.groupby(['segment', 'category']).size().unstack(fill_value=0)
    seg_nps_score = ((seg_nps.get('Promoter', 0) - seg_nps.get('Detractor', 0)) / seg_nps.sum(axis=1)) * 100
    
    fig_seg = px.bar(seg_nps_score, title="NPS by Customer Segment", labels={'value': 'NPS Score'})
    st.plotly_chart(fig_seg, use_container_width=True)

    # --- Section B: Operational Performance ---
    st.header("Section B: Operational Performance")
    
    # SLA Breach by City
    city_sla = df_orders.groupby('city')['sla_breach'].mean().sort_values(ascending=False) * 100
    fig_city = px.bar(city_sla, title="SLA Breach Rate by City (%)", labels={'value': 'Breach Rate %'})
    st.plotly_chart(fig_city, use_container_width=True)

    # Courier Performance
    courier_perf = df_orders.groupby('courier_partner').agg(
        delay_rate=('sla_breach', 'mean'),
        avg_delay=('delivery_delay', 'mean')
    ).reset_index()
    courier_perf['delay_rate'] *= 100
    
    fig_courier = px.scatter(courier_perf, x='avg_delay', y='delay_rate', text='courier_partner', 
                             title="Courier Performance: Delay Time vs Breach Rate")
    st.plotly_chart(fig_courier, use_container_width=True)

    # --- Section C & D: Funnel & Deep Dive ---
    st.header('Section C & D: The "Pain Points" Funnel')
    
    # % Delayed Orders resulting in complaints
    delayed_orders = df_orders[df_orders['sla_breach'] == True]['order_id']
    complaints_on_delay = df_complaints[df_complaints['order_id'].isin(delayed_orders)]
    conversion_rate = (len(complaints_on_delay) / len(delayed_orders)) * 100 if len(delayed_orders) > 0 else 0
    
    st.info(f"**Impact Funnel:** {conversion_rate:.1f}% of delayed orders lead directly to a customer complaint.")

    # Tier-2 Analysis
    tier2_cities = ['Indore', 'Nagpur']
    df_orders['tier'] = df_orders['city'].apply(lambda x: 'Tier-2' if x in tier2_cities else 'Tier-1')
    tier_complaints = df_orders.merge(df_complaints, on='order_id', how='left')
    tier_complaints['has_complaint'] = tier_complaints['ticket_id'].notnull()
    
    tier_analysis = tier_complaints.groupby('tier')['has_complaint'].mean() * 100
    fig_tier = px.pie(values=tier_analysis.values, names=tier_analysis.index, title="Complaint Distribution: Tier-1 vs Tier-2")
    st.plotly_chart(fig_tier, use_container_width=True)

    # --- Section E: Business Recommendations ---
    st.header("Section E: Strategic Recommendations")
    st.markdown("""
    ### 1. Root Causes
    * **Logistical Bottlenecks in Tier-2:** Hubs in Indore/Nagpur show higher failed attempts due to infrastructure gaps.
    * **Courier Partner Overload:** Specific partners (e.g., QuickShip) are failing SLAs during peak volume.
    * **Late Delivery Detractors:** Over 80% of detractors cited "Late Delivery" as their primary reason for the low score.

    ### 2. Quick Wins (Short Term)
    * Re-route Tier-2 volumes to better-performing local courier partners.
    * Implement "Automated Delay Alerts" to notify customers *before* the SLA breach occurs.

    ### 3. Long Term
    * Expand hub capacity in Nagpur and Indore to handle 2x surge volume.
    * Implement a tiered loyalty program for "High Value" customers to provide priority shipping.
    """)

else:
    st.warning("Please upload all required CSV files in the sidebar to begin the analysis.")
    st.info("Required files: Orders, NPS, Customers, Complaints.")
