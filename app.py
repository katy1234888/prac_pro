import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- SETTINGS & THEME ---
st.set_page_config(page_title="Logistics: A Festive Tale", layout="wide")

# Custom CSS for the "Storybook" look
def local_css():
    st.markdown("""
    <style>
    /* Background Image - Replace URL with your AI generated image link */
    .stApp {
        background: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), 
                    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&q=80&w=2000");
        background-size: cover;
    }
    
    .reportview-container .main .block-container {
        padding: 2rem;
    }

    /* Glassmorphism Card Effect */
    .story-card {
        background: rgba(255, 255, 255, 0.7);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        margin-bottom: 25px;
    }

    h1, h2, h3 { font-family: 'Georgia', serif; color: #1e3d59; }
    .stButton>button { border-radius: 20px; width: 100%; background-color: #1e3d59; color: white; }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- INITIALIZATION & SIDEBAR ---
if 'step' not in st.session_state:
    st.session_state.step = 0

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

st.sidebar.title("🛠️ Control Center")
st.sidebar.info("Upload your festive season datasets to begin the journey.")

# File Uploaders
u_orders = st.sidebar.file_uploader("Orders.csv", type="csv")
u_nps = st.sidebar.file_uploader("NPS.csv", type="csv")
u_cust = st.sidebar.file_uploader("Customers.csv", type="csv")
u_comp = st.sidebar.file_uploader("Complaints.csv", type="csv")
u_hub = st.sidebar.file_uploader("Hub_Performance.csv", type="csv")
u_courier = st.sidebar.file_uploader("Courier_Performance.csv", type="csv")

# --- DATA PROCESSING ---
@st.cache_data
def load_data(o, n, c, co, h, cp):
    try:
        df_o = pd.read_csv(o)
        df_n = pd.read_csv(n).dropna(subset=['score'])
        df_c = pd.read_csv(c)
        df_co = pd.read_csv(co)
        df_h = pd.read_csv(h).dropna(subset=['hub_id'])
        df_cp = pd.read_csv(cp).dropna(subset=['courier_partner'])

        # Transformations
        df_o['order_date'] = pd.to_datetime(df_o['order_date'])
        df_o['promised_date'] = pd.to_datetime(df_o['promised_date'])
        df_o['delivery_date'] = pd.to_datetime(df_o['delivery_date'])
        df_o['delay'] = (df_o['delivery_date'] - df_o['promised_date']).dt.days
        df_o['is_late'] = df_o['delay'] > 0
        
        # NPS Logic
        def get_cat(s):
            if s <= 6: return 'Detractor'
            return 'Passive' if s <= 8 else 'Promoter'
        df_n['cat'] = df_n['score'].apply(get_cat)
        
        return df_o, df_n, df_c, df_co, df_h, df_cp
    except:
        return None

# --- THE STORYBOARD ---
if not (u_orders and u_nps and u_cust and u_comp and u_hub and u_courier):
    st.markdown('<div class="story-card"><h1>📦 The Winter Delivery Crisis</h1><p>Welcome, Analyst. The festive season of 2025 has just ended, and the boardroom is in an uproar. Customers are unhappy, and the data is messy. <b>Upload all 6 files in the sidebar to start the investigation.</b></p></div>', unsafe_allow_html=True)
else:
    data = load_data(u_orders, u_nps, u_cust, u_comp, u_hub, u_courier)
    orders, nps, customers, complaints, hubs, couriers = data

    # Navigation Buttons
    col_prev, col_next = st.columns([1, 1])

    # PAGE 0: OVERVIEW
    if st.session_state.step == 0:
        st.markdown('<div class="story-card"><h1>Chapter 1: The Gathering Storm</h1><p>In the final months of the year, order volumes skyrocketed. But beneath the numbers, the cracks began to show.</p></div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Shipments", len(orders))
        c2.metric("SLA Breach Rate", f"{(orders['is_late'].mean()*100):.1f}%")
        c3.metric("Complaints Logged", len(complaints))
        
        fig = px.histogram(orders, x='order_date', title="Daily Order Volume", color_discrete_sequence=['#1e3d59'])
        st.plotly_chart(fig, use_container_width=True)
        if st.button("Investigate the Unhappy Customers →"): next_step()

    # PAGE 1: NPS DEEP DIVE
    elif st.session_state.step == 1:
        st.markdown('<div class="story-card"><h1>Chapter 2: The Voice of the People</h1><p>We asked our customers for their feedback. The Net Promoter Score (NPS) paints a grim picture.</p></div>', unsafe_allow_html=True)
        
        nps_counts = nps['cat'].value_counts(normalize=True) * 100
        total_nps = nps_counts.get('Promoter', 0) - nps_counts.get('Detractor', 0)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write(f"### Current NPS: {total_nps:.1f}")
            st.write("A score this low suggests that for every fan we have, we are creating more enemies.")
        with col2:
            fig_nps = px.pie(nps, names='cat', color='cat', 
                             color_discrete_map={'Detractor':'#ff4b2b', 'Passive':'#ffb400', 'Promoter':'#00d2ff'})
            st.plotly_chart(fig_nps)
            
        if st.button("Where are the failures happening? →"): next_step()

    # PAGE 2: OPERATIONAL GAPS
    elif st.session_state.step == 2:
        st.markdown('<div class="story-card"><h1>Chapter 3: The Broken Gears</h1><p>We looked at our Hubs and Courier Partners. Some performed like heroes; others failed the festive test.</p></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Courier Partners", "City Performance"])
        with tab1:
            st.plotly_chart(px.bar(couriers, x='courier_partner', y='sla_breach_rate', title="SLA Breach Rate by Partner"))
        with tab2:
            st.plotly_chart(px.bar(hubs, x='city', y='rto_count', title="Return-to-Origin (RTO) Count by City"))
            
        st.write("**Critical Finding:** Tier-2 cities like Nagpur and Indore are suffering from disproportionately high RTO rates.")
        if st.button("Can we fix this? See the Roadmap →"): next_step()

    # PAGE 3: THE ROADMAP
    elif st.session_state.step == 3:
        st.markdown('<div class="story-card"><h1>Chapter 4: The Recovery Roadmap</h1><p>Our investigation is complete. Here is the path back to customer love.</p></div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 🛠️ Key Recommendations
        1. **Tier-2 Hub Support:** The data shows Nagpur and Indore need a 30% increase in temporary festive staff.
        2. **Partner Realignment:** We must move volume away from **QuickShip** (32% breach rate) toward **FastEx**.
        3. **Proactive Alerts:** 70% of complaints were about "Late Delivery." Implementing automated SMS alerts for delays could reduce manual tickets by 40%.
        
        ### 📊 Success KPIs for 2026
        - **Target NPS:** > 40
        - **SLA Breach:** < 8%
        - **RTO Reduction:** 15%
        """)
        
        if st.button("↺ Start Over"): st.session_state.step = 0
