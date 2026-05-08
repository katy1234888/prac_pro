import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Logistics Analytics: Festive Surge", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9f9fb; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e1e4e8; }
    h1, h2, h3 { color: #003366; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION & UPLOAD ---
st.sidebar.title("📈 Navigation")
page = st.sidebar.radio("Analysis Chapters", [
    "Introduction: The Problem",
    "Chapter 1: The NPS Story",
    "Chapter 2: Operational Deep-Dive",
    "Chapter 3: Tier-2 Investigation",
    "Chapter 4: Recommendations"
])

st.sidebar.divider()
st.sidebar.header("📁 Required Datasets")
st.sidebar.info("Upload the CSVs to unlock the analysis.")

def upload_and_check(label, key):
    return st.sidebar.file_uploader(label, type=['csv'], key=key)

orders_f = upload_and_check("1. Orders Data", "orders_key")
nps_f = upload_and_check("2. NPS Responses", "nps_key")
cust_f = upload_and_check("3. Customer Data", "cust_key")
comp_f = upload_and_check("4. Complaints Data", "comp_key")

# --- DATA PROCESSING ENGINE ---
@st.cache_data
def process_logistics_data(o_file, n_file, c_file, co_file):
    try:
        # Load
        df_o = pd.read_csv(o_file)
        df_n = pd.read_csv(n_file).dropna(subset=['score'])
        df_c = pd.read_csv(c_file).dropna(subset=['customer_id'])
        df_co = pd.read_csv(co_file).dropna(subset=['order_id'])

        # 1. Orders Calculations [cite: 25, 26, 27]
        df_o['order_date'] = pd.to_datetime(df_o['order_date'])
        df_o['promised_date'] = pd.to_datetime(df_o['promised_date'])
        df_o['delivery_date'] = pd.to_datetime(df_o['delivery_date'])
        df_o['delivery_delay'] = (df_o['delivery_date'] - df_o['promised_date']).dt.days
        df_o['sla_breach'] = df_o['delivery_delay'] > 0
        df_o['month_year'] = df_o['order_date'].dt.strftime('%b %Y')

        # 2. NPS Categorization [cite: 32, 33, 34, 35, 36]
        def categorize(s):
            if s <= 6: return 'Detractor'
            return 'Passive' if s <= 8 else 'Promoter'
        df_n['category'] = df_n['score'].apply(categorize)
        df_n['month_year'] = pd.to_datetime(df_n['response_date']).dt.strftime('%b %Y')

        return df_o, df_n, df_c, df_co
    except Exception as e:
        st.error(f"Error processing files: {e}")
        return None

# --- PAGE LOGIC ---
if not (orders_f and nps_f and cust_f and comp_f):
    st.title("🚚 ITM Logistics Analyst Workspace")
    st.warning("Awaiting Data Upload...")
    st.markdown("""
    ### Welcome to the Festive Surge Diagnosis
    Please upload the following files in the sidebar to begin:
    * **Orders Data**: For SLA and delay tracking[cite: 23].
    * **NPS Responses**: To measure customer sentiment[cite: 30].
    * **Customer Data**: To see impact by segments[cite: 28].
    * **Complaints**: To identify root causes of frustration[cite: 37].
    """)
else:
    # Get processed data
    orders, nps, customers, complaints = process_logistics_data(orders_f, nps_f, cust_f, comp_f)

    if page == "Introduction: The Problem":
        st.title("🍂 The Festive Crisis: October - December")
        st.write("Our order volume peaked, but so did our problems. Here is the high-level impact.")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Festive Orders", len(orders))
        c2.metric("SLA Breach Rate", f"{(orders['sla_breach'].mean()*100):.1f}%")
        c3.metric("Complaints Filed", len(complaints))

        vol_trend = orders.groupby('month_year').size().reset_index(name='Orders')
        st.plotly_chart(px.line(vol_trend, x='month_year', y='Orders', title="Festive Order Surge Volume"), use_container_width=True)

    elif page == "Chapter 1: The NPS Story":
        st.title("🗣️ Chapter 1: The Voice of the Customer")
        
        # NPS Calculation [cite: 100]
        n_vals = nps['category'].value_counts(normalize=True) * 100
        total_nps = n_vals.get('Promoter', 0) - n_vals.get('Detractor', 0)
        
        st.subheader(f"Overall Net Promoter Score: {total_nps:.1f}")
        
        # Retention Impact [cite: 19, 78]
        merged_nps = nps.merge(customers[['customer_id', 'segment']], on='customer_id')
        fig = px.bar(merged_nps, x='segment', color='category', title="NPS Category by Customer Segment",
                    color_discrete_map={'Detractor': '#EF553B', 'Passive': '#FECB52', 'Promoter': '#636EFA'})
        st.plotly_chart(fig, use_container_width=True)
        st.write("**Finding:** High-value customers are increasingly becoming detractors due to delivery issues.")

    elif page == "Chapter 2: Operational Deep-Dive":
        st.title("⚙️ Chapter 2: Operational Efficiency")
        
        tab1, tab2 = st.tabs(["Courier Partners", "City Performance"])
        with tab1:
            # Courier Breach Rate [cite: 58]
            c_perf = orders.groupby('courier_partner')['sla_breach'].mean().sort_values() * 100
            st.plotly_chart(px.bar(c_perf, title="SLA Breach % by Courier"), use_container_width=True)
        
        with tab2:
            # Hub Delays [cite: 56]
            city_delays = orders.groupby('city')['delivery_delay'].mean().sort_values()
            st.plotly_chart(px.bar(city_delays, title="Avg Delay Days per City"), use_container_width=True)

    elif page == "Chapter 3: Tier-2 Investigation":
        st.title("🔍 Chapter 3: The Tier-2 Investigation")
        st.info("Investigating why Tier-2 cities show higher complaint rates[cite: 68].")
        
        t2_data = orders[orders['city'].isin(['Indore', 'Nagpur'])]
        t2_comps = complaints[complaints['order_id'].isin(t2_data['order_id'])]
        
        issue_chart = px.pie(t2_comps, names='issue_type', title="Top Complaint Drivers in Tier-2 Cities")
        st.plotly_chart(issue_chart, use_container_width=True)
        st.markdown("""
        **Root Causes Identified:**
        1. **Failed Attempts:** Hub data shows 2x higher failed delivery attempts in Nagpur/Indore[cite: 71].
        2. **SLA Breach:** Partners are struggling with Tier-2 geography during peak surge[cite: 69].
        """)

    elif page == "Chapter 4: Recommendations":
        st.title("🚀 Chapter 4: The Recovery Roadmap")
        
        st.subheader("Final Strategic Proposals [cite: 80]")
        st.success("**Quick Wins (Short Term)**: Implement real-time SMS alerts for delayed orders and re-assign poor-performing Tier-2 hubs[cite: 82].")
        st.info("**Strategic Fixes (Long Term)**: Expand hub capacities in Tier-2 cities and renegotiate SLAs with 'QuickShip'[cite: 83].")
        
        st.divider()
        st.write("### Target KPIs for Next Season [cite: 84]")
        st.write("✅ **Target NPS**: +40 | ✅ **Target SLA Breach**: < 10% | ✅ **Repeat Rate**: > 25%")
