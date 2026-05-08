import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Seashell Logistics | Festive Surge 2025", layout="wide")

# --- ADVANCED CUSTOM STYLING (The "Attractive" Layer) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&family=Roboto:wght@300;400&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f1f5f9;
        font-family: 'Roboto', sans-serif;
    }

    /* Vibrant Gradient Title */
    .company-title {
        background: -webkit-linear-gradient(#00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        font-size: 45px;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 18px;
        margin-bottom: 40px;
        text-transform: uppercase;
        letter-spacing: 3px;
    }

    /* Colorful Story Cards */
    .content-card {
        background: rgba(255, 255, 255, 0.05);
        border-left: 5px solid #00d2ff;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .impact-text {
        color: #38bdf8;
        font-weight: 700;
        font-size: 20px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #334155;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        color: #0ea5e9;
        font-family: 'Montserrat', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA HUB ---
@st.cache_data
def load_and_enhance(o_f, n_f, cu_f, co_f, h_f, cp_f):
    try:
        # Load
        o, n, cu, co, h, cp = [pd.read_csv(f) for f in [o_f, n_f, cu_f, co_f, h_f, cp_f]]
        
        # Calculations
        o['order_date'] = pd.to_datetime(o['order_date'])
        o['delivery_date'] = pd.to_datetime(o['delivery_date'])
        o['promised_date'] = pd.to_datetime(o['promised_date'])
        o['delay'] = (o['delivery_date'] - o['promised_date']).dt.days
        o['is_late'] = o['delay'] > 0
        o['month'] = o['order_date'].dt.strftime('%B')
        
        # NPS Scoring
        n = n.dropna(subset=['score'])
        n['type'] = n['score'].apply(lambda s: 'Detractor' if s <= 6 else ('Passive' if s <= 8 else 'Promoter'))
        
        return o, n, cu, co, h, cp
    except: return None

# --- SIDEBAR NAV ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/609/609361.png", width=100)
    st.markdown("### Executive Navigation")
    chapter = st.radio("SELECT CHAPTER", [
        "01. Mission Briefing", "02. The Growth Surge", "03. The Performance Gap",
        "04. Customer Sentiment", "05. High-Value Risk", "06. Infrastructure Gaps",
        "07. Tier-2 Deep-Dive", "08. Partner Scorecard", "09. Financial Leakage", "10. Strategic Pivot"
    ])
    st.divider()
    st.markdown("### Core Data Upload")
    files = {
        "orders": st.file_uploader("Upload Orders.csv"),
        "nps": st.file_uploader("Upload NPS.csv"),
        "customers": st.file_uploader("Upload Customers.csv"),
        "complaints": st.file_uploader("Upload Complaints.csv"),
        "hubs": st.file_uploader("Upload Hubs.csv"),
        "couriers": st.file_uploader("Upload Couriers.csv")
    }

# --- PAGE RENDERING ---
if not all(files.values()):
    st.markdown("<div class='company-title'>SEASHELL LOGISTICS PVT LTD</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Diagnostic Report: Festive Surge Delivery Crisis</div>", unsafe_allow_html=True)
    st.info("👋 Welcome, Executive. Please upload all 6 datasets in the sidebar to visualize the 2025 Festive Season story.")
    st.image("https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
else:
    o, n, cu, co, h, cp = load_and_enhance(*files.values())

    st.markdown("<div class='company-title'>SEASHELL LOGISTICS PVT LTD</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Chapter {chapter}</div>", unsafe_allow_html=True)

    # PAGE 1: MISSION
    if "01" in chapter:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                <div class='content-card'>
                    <p class='impact-text'>The Situation</p>
                    <p>Between October and December 2025, Seashell Logistics scaled rapidly to meet festive demand. 
                    However, operational friction led to a decline in delivery quality.</p>
                    <p><b>Goal:</b> Identify why NPS fell and how to recover customer trust.</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.image("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&q=80&w=800")

    # PAGE 2: GROWTH
    elif "02" in chapter:
        st.markdown("<div class='content-card'><p class='impact-text'>The Growth Surge</p><p>Daily order volume hit record highs, stressing our hub capacities.</p></div>", unsafe_allow_html=True)
        daily_vol = o.groupby(o['order_date'].dt.date).size().reset_index(name='Orders')
        fig = px.area(daily_vol, x='order_date', y='Orders', title="Festive Order Trajectory", color_discrete_sequence=['#0ea5e9'])
        st.plotly_chart(fig, use_container_width=True)

    # PAGE 3: PERFORMANCE GAP
    elif "03" in chapter:
        st.markdown("<div class='content-card'><p class='impact-text'>The SLA Crisis</p><p>Delivery delays began to spiral as the season progressed.</p></div>", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Average Delay", f"{o['delay'].mean():.1f} Days")
        m2.metric("SLA Breach Rate", f"{(o['is_late'].mean()*100):.1f}%")
        fig = px.bar(o.groupby('month')['is_late'].mean().reset_index(), x='month', y='is_late', color='is_late', color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)

    # PAGE 4: SENTIMENT
    elif "04" in chapter:
        st.markdown("<div class='content-card'><p class='impact-text'>NPS Breakdown</p><p>Detractors reached a critical high of 35%+ in December.</p></div>", unsafe_allow_html=True)
        fig = px.pie(n, names='type', hole=0.5, color='type', 
                    color_discrete_map={'Detractor':'#ef4444', 'Passive':'#f59e0b', 'Promoter':'#10b981'})
        st.plotly_chart(fig, use_container_width=True)

    # PAGE 7: TIER-2
    elif "07" in chapter:
        st.markdown("<div class='content-card'><p class='impact-text'>Tier-2 Infrastructure Gap</p><p>Nagpur and Indore hubs show a failure attempt rate 2.5x higher than Mumbai.</p></div>", unsafe_allow_html=True)
        t2 = co[co['order_id'].isin(o[o['city'].isin(['Indore', 'Nagpur'])]['order_id'])]
        st.plotly_chart(px.pie(t2, names='issue_type', title="Top Complaints in Tier-2"))

    # PAGE 10: ROADMAP
    elif "10" in chapter:
        st.markdown("""
            <div class='content-card' style='border-left: 5px solid #10b981;'>
                <p class='impact-text'>The 2026 Strategy</p>
                <ul>
                    <li><b>Automation:</b> Real-time SMS delay notifications to manage expectations.</li>
                    <li><b>Infrastructure:</b> Expand Nagpur hub capacity by 40% before next peak.</li>
                    <li><b>Partnerships:</b> Re-negotiate SLAs with QuickShip or re-route volumes.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        st.balloons()
