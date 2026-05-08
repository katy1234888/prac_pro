import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Seashell Logistics | Festive Surge Report", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM THEMING & ASSETS ---
def apply_custom_design():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Story Card */
    .story-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 40px;
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        margin: 20px 0;
        line-height: 1.6;
    }

    h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: #00d4ff; text-transform: uppercase; letter-spacing: 2px; }
    
    .highlight { color: #00d4ff; font-weight: bold; }
    
    /* Navigation Bar */
    .stRadio > div { display: flex; justify-content: center; gap: 10px; }
    </style>
    """, unsafe_allow_html=True)

apply_custom_design()

# --- DATA ENGINE ---
@st.cache_data
def get_data(o, n, c, co, h, cp):
    try:
        # Loading all 6 files
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
        df_n['cat'] = df_n['score'].apply(lambda s: 'Detractor' if s <= 6 else ('Passive' if s <= 8 else 'Promoter'))
        return df_o, df_n, df_c, df_co, df_h, df_cp
    except: return None

# --- SIDEBAR UPLOAD ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830305.png", width=100)
    st.title("Command Center")
    u_o = st.file_uploader("Orders", type="csv")
    u_n = st.file_uploader("NPS", type="csv")
    u_c = st.file_uploader("Customers", type="csv")
    u_co = st.file_uploader("Complaints", type="csv")
    u_h = st.file_uploader("Hubs", type="csv")
    u_cp = st.file_uploader("Couriers", type="csv")

# --- STORY NAVIGATION (10 PAGES) ---
pages = [
    "01. The Mission", "02. The Surge", "03. The Fallout", 
    "04. Voice of Customer", "05. Segment Analysis", "06. Operational Gaps", 
    "07. Tier-2 Deep Dive", "08. Courier Performance", "09. Financial Impact", "10. The Roadmap"
]
current_page = st.select_slider("Select Chapter", options=pages)

# --- NARRATIVE CONTENT ---
if not (u_o and u_n and u_c and u_co and u_h and u_cp):
    st.markdown("""
    <div style='text-align: center; padding-top: 100px;'>
        <h1>Seashell Logistics Pvt Ltd</h1>
        <p style='font-size: 20px;'>Welcome to the Internal Diagnostic Portal.<br>
        Please upload the festive season datasets in the sidebar to initialize the <b>Story of the 2025 Peak Surge</b>.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    orders, nps, customers, complaints, hubs, couriers = get_data(u_o, u_n, u_c, u_co, u_h, u_cp)

    # --- PAGE 1: THE MISSION ---
    if current_page == "01. The Mission":
        st.markdown(f"""
        <div class='story-box'>
            <h1>01. THE MISSION</h1>
            <p>At <span class='highlight'>Seashell Logistics Pvt Ltd</span>, our goal for the 2025 festive season was simple: 
            <b>Scale and Deliver.</b> However, as the orders poured in from October to December, our systems reached a breaking point.</p>
            <p>This report serves as a post-mortem analysis of why our customer satisfaction plummeted while our volumes hit record highs.</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1566576721346-d4a3b4eaad5b?auto=format&fit=crop&q=80&w=1200", caption="The Seashell Hub at Midnight")

    # --- PAGE 2: THE SURGE ---
    elif current_page == "02. The Surge":
        st.markdown("<div class='story-box'><h1>02. THE FESTIVE SURGE</h1><p>October saw a massive influx of orders. Our infrastructure was tested like never before.</p></div>", unsafe_allow_html=True)
        vol_data = orders.groupby(orders['order_date'].dt.date).size().reset_index(name='Volume')
        fig = px.area(vol_data, x='order_date', y='Volume', title="Daily Order Influx", color_discrete_sequence=['#00d4ff'])
        st.plotly_chart(fig, use_container_width=True)

    # --- PAGE 3: THE FALLOUT ---
    elif current_page == "03. The Fallout":
        st.markdown("<div class='story-box'><h1>03. THE SYSTEM CRACKS</h1><p>With volume came <b>Delays</b>. The Promised Date vs. Actual Delivery Date gap began to widen.</p></div>", unsafe_allow_html=True)
        late_rate = orders['is_late'].mean() * 100
        st.metric("Overall SLA Breach Rate", f"{late_rate:.2f}%", delta="CRITICAL", delta_color="inverse")
        fig_late = px.histogram(orders, x='delay', title="Distribution of Delivery Delays (Days)", nbins=20)
        st.plotly_chart(fig_late, use_container_width=True)

    # --- PAGE 4: VOICE OF CUSTOMER ---
    elif current_page == "04. Voice of Customer":
        st.markdown("<div class='story-box'><h1>04. THE UNFILTERED TRUTH</h1><p>Net Promoter Score (NPS) dropped significantly. Detractors now outweigh our Promoters.</p></div>", unsafe_allow_html=True)
        nps_score = (nps['cat'].value_counts(normalize=True).get('Promoter', 0) - nps['cat'].value_counts(normalize=True).get('Detractor', 0)) * 100
        st.metric("Current NPS Score", f"{nps_score:.1f}")
        st.plotly_chart(px.pie(nps, names='cat', hole=0.6, title="NPS Category Breakdown"))

    # --- PAGE 5: SEGMENT ANALYSIS ---
    elif current_page == "05. Segment Analysis":
        st.markdown("<div class='story-box'><h1>05. WHO IS LEAVING?</h1><p>Our <b>'High Value'</b> customers are the unhappiest. This puts our long-term revenue at extreme risk.</p></div>", unsafe_allow_html=True)
        seg_data = nps.merge(customers[['customer_id', 'segment']], on='customer_id')
        fig_seg = px.bar(seg_data.groupby(['segment', 'cat']).size().unstack(), barmode='group', title="Sentiment by Customer Segment")
        st.plotly_chart(fig_seg, use_container_width=True)

    # --- PAGE 6: OPERATIONAL GAPS ---
    elif current_page == "06. Operational Gaps":
        st.markdown("<div class='story-box'><h1>06. THE HUB ANALYSIS</h1><p>Efficiency varied across cities. Some hubs effectively became bottlenecks.</p></div>", unsafe_allow_html=True)
        st.write("### Failed Attempts vs RTO Count")
        st.table(hubs[['city', 'failed_attempts', 'rto_count']])

    # --- PAGE 7: TIER-2 DEEP dive ---
    elif current_page == "07. Tier-2 Deep Dive":
        st.markdown("<div class='story-box'><h1>07. THE TIER-2 STRUGGLE</h1><p><b>Nagpur and Indore</b> showed 2x the average complaint rate. The infrastructure in these cities failed to handle the surge.</p></div>", unsafe_allow_html=True)
        t2_cities = ['Indore', 'Nagpur']
        t2_comps = complaints[complaints['order_id'].isin(orders[orders['city'].isin(t2_cities)]['order_id'])]
        st.plotly_chart(px.pie(t2_comps, names='issue_type', title="Top Complaint Drivers (Tier-2)"))

    # --- PAGE 8: COURIER PERFORMANCE ---
    elif current_page == "08. Courier Performance":
        st.markdown("<div class='story-box'><h1>08. PARTNER ACCOUNTABILITY</h1><p>Not all partners are equal. <b>QuickShip</b> breached SLAs 32% of the time.</p></div>", unsafe_allow_html=True)
        st.plotly_chart(px.bar(couriers, x='courier_partner', y='sla_breach_rate', color='sla_breach_rate', title="Partner Breach Rates"))

    # --- PAGE 9: FINANCIAL IMPACT ---
    elif current_page == "09. The Cost of Failure":
        st.markdown("<div class='story-box'><h1>09. THE COST OF FAILURE</h1><p>RTO (Return to Origin) isn't just a logistics metric; it's a direct loss of profit and packaging costs.</p></div>", unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1553413077-190dd305871c?auto=format&fit=crop&q=80&w=1200", caption="The Cost of Logistics Returns")
        st.metric("Total RTO Count Across Hubs", hubs['rto_count'].sum())

    # --- PAGE 10: THE ROADMAP ---
    elif current_page == "10. The Roadmap":
        st.markdown(f"""
        <div class='story-box'>
            <h1>10. THE RECOVERY ROADMAP</h1>
            <p>Based on our findings at <span class='highlight'>Seashell Logistics Pvt Ltd</span>, we propose:</p>
            <ul>
                <li><b>Phase 1:</b> Replace QuickShip in Tier-2 regions with local boutique couriers.</li>
                <li><b>Phase 2:</b> Implement "Automated Customer Interventions" for delays over 24 hours.</li>
                <li><b>Phase 3:</b> Loyalty points for Detractors to prevent churn.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
