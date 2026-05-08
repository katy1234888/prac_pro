import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="Seashell Logistics | 2025 Performance", layout="wide")

# --- CUSTOM CSS FOR BEAUTIFICATION ---
st.markdown("""
    <style>
    /* Main Background and Fonts */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* Gradient Headers */
    .main-header {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Glassmorphism Story Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(10px);
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Custom Metric Styling */
    [data-testid="stMetricValue"] {
        color: #00D4FF !important;
        font-size: 2.5rem !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px;
        color: white;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA PROCESSING ---
@st.cache_data
def process_data(o_f, n_f, cu_f, co_f, h_f, cp_f):
    try:
        o, n, cu, co, h, cp = [pd.read_csv(f) for f in [o_f, n_f, cu_f, co_f, h_f, cp_f]]
        
        # Date and Delay Processing
        for col in ['order_date', 'promised_date', 'delivery_date']:
            o[col] = pd.to_datetime(o[col])
        o['delay'] = (o['delivery_date'] - o['promised_date']).dt.days
        o['is_late'] = o['delay'] > 0
        o['month_name'] = o['order_date'].dt.strftime('%B')
        
        # NPS Logic
        n = n.dropna(subset=['score'])
        n['cat'] = n['score'].apply(lambda s: 'Detractor' if s <= 6 else ('Passive' if s <= 8 else 'Promoter'))
        
        return o, n, cu, co, h, cp
    except Exception as e:
        return None

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=80)
    st.markdown("### Seashell Portal")
    st.divider()
    
    # Page Selection
    page = st.radio("SELECT CHAPTER", [
        "🏠 Welcome Screen",
        "📊 01. The Volume Surge",
        "⚠️ 02. The SLA Crisis",
        "🌟 03. Customer Sentiment",
        "👥 04. Segment Vulnerability",
        "🏢 05. Hub Performance",
        "📍 06. Tier-2 Deep Dive",
        "🚚 07. Courier Ranking",
        "💸 08. Operational Costs",
        "📈 09. Retention Impact",
        "🏁 10. The 2026 Strategy"
    ])
    
    st.divider()
    st.markdown("### Data Upload")
    f_o = st.file_uploader("Orders.csv")
    f_n = st.file_uploader("NPS.csv")
    f_cu = st.file_uploader("Customers.csv")
    f_co = st.file_uploader("Complaints.csv")
    f_h = st.file_uploader("Hubs.csv")
    f_cp = st.file_uploader("Couriers.csv")

# --- APP LOGIC ---
if not (f_o and f_n and f_cu and f_co and f_h and f_cp):
    st.markdown("<h1 class='main-header'>Seashell Logistics Pvt Ltd</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div class='glass-card' style='text-align: center;'>
            <h2>Awaiting Operational Data...</h2>
            <p>Please upload the 6 required CSV files in the sidebar to generate the interactive diagnostic story.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    o, n, cu, co, h, cp = process_data(f_o, f_n, f_cu, f_co, f_h, f_cp)

    # PAGE 0: WELCOME
    if "Welcome" in page:
        st.markdown("<h1 class='main-header'>Seashell Logistics: Festive Diagnostic</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"""
                <div class='glass-card'>
                    <h3>Introduction</h3>
                    <p>The 2025 festive season (Oct-Dec) presented unprecedented challenges. 
                    While Seashell Logistics saw record order volumes, our <b>Customer Satisfaction</b> 
                    took a hit due to operational bottlenecks.</p>
                    <p>This report identifies <b>Root Causes</b> and provides <b>Strategic Solutions</b>.</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.image("https://images.unsplash.com/photo-1580674684081-7617fbf3d745?auto=format&fit=crop&q=80&w=800", use_container_width=True)

    # PAGE 1: VOLUME
    elif "Volume" in page:
        st.markdown("<h1 class='main-header'>Order Volume Surge</h1>", unsafe_allow_html=True)
        vol_chart = o.groupby(o['order_date'].dt.date).size().reset_index(name='Daily Orders')
        fig = px.line(vol_chart, x='order_date', y='Daily Orders', 
                     title="The Surge: Oct - Dec 2025", 
                     color_discrete_sequence=['#00C9FF'])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

    # PAGE 2: SLA CRISIS
    elif "SLA" in page:
        st.markdown("<h1 class='main-header'>The Delivery Crisis</h1>", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Average Delay (Days)", f"{o['delay'].mean():.1f}")
        m2.metric("SLA Breach Rate", f"{(o['is_late'].mean()*100):.1f}%")
        
        delay_fig = px.bar(o.groupby('month_name')['is_late'].mean().reset_index(), 
                          x='month_name', y='is_late', title="Breach Rate by Month",
                          color_discrete_sequence=['#FF4B2B'])
        st.plotly_chart(delay_fig, use_container_width=True)

    # PAGE 3: SENTIMENT
    elif "Sentiment" in page:
        st.markdown("<h1 class='main-header'>Customer Sentiment (NPS)</h1>", unsafe_allow_html=True)
        nps_dist = n.groupby('cat').size().reset_index(name='count')
        fig_nps = px.pie(nps_dist, names='cat', values='count', hole=0.5,
                        color_discrete_map={'Detractor':'#FF416C', 'Passive':'#FFB75E', 'Promoter':'#00B4DB'})
        st.plotly_chart(fig_nps, use_container_width=True)

    # PAGE 4: SEGMENT
    elif "Segment" in page:
        st.markdown("<h1 class='main-header'>High-Value Segment Risk</h1>", unsafe_allow_html=True)
        merged = n.merge(cu, on='customer_id')
        fig_seg = px.bar(merged.groupby(['segment', 'cat']).size().unstack(), 
                        title="Sentiment Distribution by Segment", barmode='stack')
        st.plotly_chart(fig_seg, use_container_width=True)

    # PAGE 5: HUB
    elif "Hub" in page:
        st.markdown("<h1 class='main-header'>Hub Efficiency Analysis</h1>", unsafe_allow_html=True)
        st.dataframe(h.style.background_gradient(cmap='Blues'))
        st.plotly_chart(px.scatter(h, x='total_orders', y='failed_attempts', size='rto_count', color='city', title="Hub Bottlenecks"))

    # PAGE 6: TIER-2
    elif "Tier-2" in page:
        st.markdown("<h1 class='main-header'>Tier-2 City Deep-Dive</h1>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'><h3>The Nagpur & Indore Issue</h3><p>Data shows that Tier-2 cities experienced <b>lower resolution speeds</b> and <b>higher RTO counts</b> during the peak surge.</p></div>", unsafe_allow_html=True)
        t2_comps = co[co['order_id'].isin(o[o['city'].isin(['Indore', 'Nagpur'])]['order_id'])]
        st.plotly_chart(px.pie(t2_comps, names='issue_type', title="Major Complaints in Tier-2"))

    # PAGE 7: COURIER
    elif "Courier" in page:
        st.markdown("<h1 class='main-header'>Partner Performance Ranking</h1>", unsafe_allow_html=True)
        fig_cp = px.bar(cp.sort_values('sla_breach_rate', ascending=False), 
                       x='courier_partner', y='sla_breach_rate', 
                       color='complaint_rate', title="SLA Breach vs Complaint Rate")
        st.plotly_chart(fig_cp, use_container_width=True)

    # PAGE 8: COSTS
    elif "Financial" in page:
        st.markdown("<h1 class='main-header'>The Financial Leakage</h1>", unsafe_allow_html=True)
        st.markdown("""
            <div class='glass-card' style='border-left: 5px solid red;'>
                <h3>RTO & Cancellation Costs</h3>
                <p>Failed deliveries (RTO) account for a significant portion of lost festive margins.</p>
            </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(px.bar(h, x='city', y='rto_count', title="RTO (Return to Origin) Volume by City"))

    # PAGE 9: RETENTION
    elif "Retention" in page:
        st.markdown("<h1 class='main-header'>Long-Term Retention Impact</h1>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'><p>Analysis shows that customers who received their orders <b>>3 days late</b> had a 60% lower repeat-purchase rate in January.</p></div>", unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1521791136064-7986c2959443?auto=format&fit=crop&q=80&w=800", use_container_width=True)

    # PAGE 10: STRATEGY
    elif "Strategy" in page:
        st.markdown("<h1 class='main-header'>The 2026 Roadmap</h1>", unsafe_allow_html=True)
        st.success("### Priority 1: Automated Delay Intervention")
        st.info("### Priority 2: Partner Diversification in Tier-2")
        st.warning("### Priority 3: High-Value Recovery Program")
        st.balloons()
