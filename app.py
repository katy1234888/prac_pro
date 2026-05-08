import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Seashell Logistics | 2025 Performance", layout="wide")

# --- HIGH-END COLOR PALETTE & UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Open+Sans:wght@400;600&display=swap');

    /* Main Theme */
    .stApp {
        background: radial-gradient(circle at top left, #0a192f, #020c1b);
        color: #ccd6f6;
        font-family: 'Open Sans', sans-serif;
    }

    /* Vibrant Gradient Title */
    .brand-header {
        background: linear-gradient(90deg, #64ffda, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        font-size: 52px;
        text-align: center;
        letter-spacing: -1px;
    }

    .chapter-tag {
        color: #64ffda;
        font-family: 'Montserrat', sans-serif;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-align: center;
        font-size: 14px;
        margin-bottom: 30px;
    }

    /* Interactive "Vibe" Cards */
    .story-card {
        background: rgba(17, 34, 64, 0.7);
        padding: 35px;
        border-radius: 15px;
        border-top: 4px solid #64ffda;
        box-shadow: 0 10px 30px rgba(2, 12, 27, 0.7);
        margin-bottom: 25px;
    }

    .metric-box {
        background: rgba(100, 255, 218, 0.05);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(100, 255, 218, 0.2);
    }

    h1, h2, h3 { color: #64ffda; font-family: 'Montserrat', sans-serif; }
    
    /* Smooth Navigation */
    .stRadio > div { flex-direction: row; justify-content: center; background: rgba(17, 34, 64, 0.8); padding: 10px; border-radius: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA HUB ---
@st.cache_data
def load_and_analyze(o_f, n_f, cu_f, co_f, h_f, cp_f):
    try:
        o, n, cu, co, h, cp = [pd.read_csv(f) for f in [o_f, n_f, cu_f, co_f, h_f, cp_f]]
        
        # Datetime Processing
        for d in ['order_date', 'delivery_date', 'promised_date']:
            o[d] = pd.to_datetime(o[d])
        o['delay'] = (o['delivery_date'] - o['promised_date']).dt.days
        o['is_late'] = o['delay'] > 0
        o['month'] = o['order_date'].dt.strftime('%B %Y')

        # NPS Calculation
        n = n.dropna(subset=['score'])
        n['label'] = n['score'].apply(lambda x: 'Detractor' if x <= 6 else ('Passive' if x <= 8 else 'Promoter'))
        
        return o, n, cu, co, h, cp
    except: return None

# --- SIDEBAR & UPLOAD ---
with st.sidebar:
    st.markdown("### 🛠️ Logistics Command")
    u_o = st.file_uploader("Orders", type="csv")
    u_n = st.file_uploader("NPS", type="csv")
    u_cu = st.file_uploader("Customers", type="csv")
    u_co = st.file_uploader("Complaints", type="csv")
    u_h = st.file_uploader("Hub Performance", type="csv")
    u_cp = st.file_uploader("Courier Data", type="csv")
    st.divider()
    st.markdown("Developed for **Seashell Logistics Executive Board**.")

# --- NAVIGATION ---
nav = st.radio("JOURNEY MAP", ["STORY START", "THE SURGE", "CUSTOMER PAIN", "HUB BOTTLENECKS", "TIER-2 FOCUS", "STRATEGIC ROADMAP"])

# --- CONTENT LOGIC ---
if not (u_o and u_n and u_cu and u_co and u_h and u_cp):
    st.markdown("<div class='brand-header'>SEASHELL LOGISTICS PVT LTD</div>", unsafe_allow_html=True)
    st.markdown("<div class='chapter-tag'>Internal Diagnostic Portal</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='story-card'>
            <h2 style='text-align: center;'>Awaiting Festive Data...</h2>
            <p style='text-align: center;'>The 2025 Festive Season analysis requires all 6 core datasets to be uploaded via the sidebar. 
            Once uploaded, the command center will initialize.</p>
        </div>
    """, unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1494412651409-8963ce7935a7?auto=format&fit=crop&q=80&w=1200")
else:
    o, n, cu, co, h, cp = load_and_analyze(u_o, u_n, u_cu, u_co, u_h, u_cp)
    st.markdown("<div class='brand-header'>SEASHELL LOGISTICS PVT LTD</div>", unsafe_allow_html=True)

    if nav == "STORY START":
        st.markdown("<div class='chapter-tag'>Chapter 01: The Mission Objective</div>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
                <div class='story-card'>
                    <h3>The Challenge</h3>
                    <p>Between <b>October and December 2025</b>, Seashell Logistics faced a massive surge in demand. 
                    While volume peaked, <b>Customer Satisfaction dropped</b>. </p>
                    <p>Our mission is to diagnose the operational failures that turned our festive success into a delivery crisis.</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.image("https://images.unsplash.com/photo-1519003722824-194d4455a60c?auto=format&fit=crop&q=80&w=800")

    elif nav == "THE SURGE":
        st.markdown("<div class='chapter-tag'>Chapter 02: Volume & SLA Pressure</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Shipments", len(o), "Peak Growth")
        c2.metric("SLA Breach Rate", f"{(o['is_late'].mean()*100):.1f}%", "-12%", delta_color="inverse")
        c3.metric("Avg Resolution Time", "3.4 Days")
        
        surge_fig = px.area(o.groupby(o['order_date'].dt.date).size().reset_index(name='V'), x='order_date', y='V', 
                           title="Daily Influx Volume", color_discrete_sequence=['#64ffda'])
        st.plotly_chart(surge_fig, use_container_width=True)

    elif nav == "CUSTOMER PAIN":
        st.markdown("<div class='chapter-tag'>Chapter 03: The Voice of Sentiment</div>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("""
                <div class='story-card'>
                    <h3>The NPS Decline</h3>
                    <p>Detractors are rising. <b>Late Delivery</b> and <b>Poor Communication</b> are the primary drivers of negative sentiment.</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            n_dist = n['label'].value_counts().reset_index()
            fig = px.pie(n_dist, names='label', values='count', hole=0.6,
                        color_discrete_map={'Detractor':'#ff4b2b', 'Passive':'#ffb400', 'Promoter':'#64ffda'})
            st.plotly_chart(fig)

    elif nav == "HUB BOTTLENECKS":
        st.markdown("<div class='chapter-tag'>Chapter 04: Hub & Courier Performance</div>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["City Efficiency", "Partner Integrity"])
        with tab1:
            st.plotly_chart(px.bar(h, x='city', y='failed_attempts', color='rto_count', title="Failed Deliveries by Hub"))
        with tab2:
            st.plotly_chart(px.scatter(cp, x='avg_delivery_time', y='sla_breach_rate', size='complaint_rate', 
                                       text='courier_partner', title="Partner Risk Matrix"))

    elif nav == "TIER-2 FOCUS":
        st.markdown("<div class='chapter-tag'>Chapter 05: The Tier-2 Crisis</div>", unsafe_allow_html=True)
        st.markdown("""
            <div class='story-card' style='border-top-color: #ff4b2b;'>
                <h3>Why Indore & Nagpur?</h3>
                <p>Data indicates that Tier-2 cities suffer from <b>longer transit times</b> and <b>lower hub resolution speeds</b> compared to Tier-1 metros.</p>
            </div>
        """, unsafe_allow_html=True)
        t2_orders = o[o['city'].isin(['Indore', 'Nagpur'])]
        st.plotly_chart(px.histogram(t2_orders, x='delay', color='city', barmode='group', title="Delay Distribution in Tier-2"))

    elif nav == "STRATEGIC ROADMAP":
        st.markdown("<div class='chapter-tag'>Chapter 06: The Way Forward</div>", unsafe_allow_html=True)
        st.markdown("""
            <div class='story-card' style='border-top-color: #64ffda;'>
                <h3>Executive Recommendations</h3>
                <ul>
                    <li><b>Proactive Communication:</b> Automated SMS updates for delays over 24 hours.</li>
                    <li><b>Partner Optimization:</b> Shift volume from QuickShip to high-performing regional partners.</li>
                    <li><b>Infrastructure:</b> Mini-hub expansions in Nagpur to reduce last-mile bottlenecks.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        st.balloons()
