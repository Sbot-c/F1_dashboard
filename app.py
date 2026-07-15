import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. PAGE SETUP
st.set_page_config(
    page_title="F1 Performance & Economics Hub", 
    page_icon="🏎️", 
    layout="wide"
)

# 2. HIGH-CONTRAST F1 DESIGN STYLING (Injected via CSS)
st.markdown("""
    <style>
    /* HIDE THE DEFAULT TOP WHITE BAR AND MINIMIZE PADDING GAP */
    [data-testid="stHeader"] {
        visibility: hidden;
        height: 0% !important;
    }
    div.block-container {
        padding-top: 1rem !important;
    }
    
    /* Main Background & Fonts */
    .stApp {
        background-color: #0B0C10;
        color: #FFFFFF;
    }
    
    /* Custom Red Accent Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #11141A !important;
        border: 1px solid #222630 !important;
        border-left: 6px solid #FF1801 !important;
        padding: 15px 20px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Highlight Title text inside metrics */
    div[data-testid="metric-container"] label {
        color: #A0A5B5 !important;
        font-family: 'Helvetica Neue', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85rem !important;
    }
    
    /* Highlight Values inside metrics */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }
    
    /* Tab formatting */
    button[data-baseweb="tab"] {
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FF1801 !important;
        border-bottom-color: #FF1801 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# 3. CACHED DATA LOADING & CLEANING
@st.cache_data
def load_and_clean_data():
    rr = pd.read_csv('race_results.csv')
    ce = pd.read_csv('circuit_economics.csv')
    cf = pd.read_csv('constructor_finances.csv')
    ds = pd.read_csv('driver_standings.csv')
    fb = pd.read_csv('f1_business.csv')
    
    cf['cost_cap_limit_usd_m'] = cf['cost_cap_limit_usd_m'].fillna(0)
    races_full = pd.merge(rr, ce, on=['season', 'grand_prix'], how='left', suffixes=('', '_econ'))
    
    return races_full, cf, ds, fb

races_df, constructor_df, driver_df, business_df = load_and_clean_data()


# 4. DASHBOARD HEADER
st.title("🏎️ FORMULA 1 PERFORMANCE & ECONOMICS CENTRALE")
st.markdown("An elite analytics environment mapping on-track Grand Prix parameters directly to macroeconomic variables.")
st.markdown("---")


# 5. TABBED INTERACTIVE ANALYTICS (Using local selectors for every chart area)
tab1, tab2, tab3 = st.tabs(["📊 FINANCIALS & TREEMAPS", "🏆 TRACK RACE ANALYTICS", "📈 MACRO ECONOMIC TRENDS"])

# ==================== TAB 1: FINANCIALS & TREEMAPS ====================
with tab1:
    st.markdown("### 💰 Team Financial Breakdown & Revenue Distribution")
    
    all_seasons = sorted(constructor_df['season'].unique(), reverse=True)
    fin_season = st.selectbox("📅 Filter Financials by Season:", all_seasons, key="fin_season_select")
    s_constructors = constructor_df[constructor_df['season'] == fin_season]
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.write("**Visualizing Corporate Footprints: Multi-Level Financial Treemap**")
        if not s_constructors.empty:
            fig_tree = px.treemap(
                s_constructors,
                path=['in_cost_cap_era', 'country_iso3', 'team_name'],
                values='operating_budget_usd_m',
                color='total_revenue_usd_m',
                color_continuous_scale='Reds',
                labels={
                    'in_cost_cap_era': 'Cost Cap Era',
                    'country_iso3': 'HQ Country',
                    'team_name': 'Team Name',
                    'operating_budget_usd_m': 'Operating Budget ($M)',
                    'total_revenue_usd_m': 'Total Revenue ($M)'
                },
                title=f"Hierarchical Allocation of Team Budgets & Revenue Profiles ({fin_season})"
            )
            fig_tree.update_layout(
                template="plotly_dark", 
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FFFFFF")
            )
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.info("No constructor financial data available for this specific season.")
            
    with col2:
        st.write("**Revenue Stream Proportions**")
        if not s_constructors.empty:
            selected_team = st.selectbox("Select Team for Share Breakdown:", s_constructors['team_name'].unique(), key="team_pie_select")
            team_data = s_constructors[s_constructors['team_name'] == selected_team].iloc[0]
            
            revenue_streams = ['Sponsorship Revenue', 'Prize Money']
            revenue_values = [team_data['sponsorship_revenue_usd_m'], team_data['prize_money_usd_m']]
            
            fig_pie = px.pie(
                names=revenue_streams,
                values=revenue_values,
                hole=0.4,
                color_discrete_sequence=['#FF1801', '#FFFFFF'],
                title=f"{selected_team} Core Income Split ($M)"
            )
            fig_pie.update_layout(
                template="plotly_dark", 
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FFFFFF"),
                legend=dict(font=dict(color="#FFFFFF"))
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No team breakdown data loaded.")

# ==================== TAB 2: TRACK RACE ANALYTICS ====================
with tab2:
    st.markdown("### 🏁 Grand Prix Dominance & Circuit Hosting Economics")
    
    race_seasons = sorted(races_df['season'].unique(), reverse=True)
    race_season = st.selectbox("📅 Filter Race Data by Season:", race_seasons, key="race_season_select")
    s_races = races_df[races_df['season'] == race_season]
    
    col_race1, col_race2 = st.columns(2)
    
    with col_race1:
        st.write("**Race Winners Distribution**")
        if not s_races.empty:
            winner_counts = s_races['winner'].value_counts().reset_index()
            winner_counts.columns = ['Driver', 'Wins']
            
            fig_win_pie = px.pie(
                winner_counts,
                names='Driver',
                values='Wins',
                hole=0.3,
                color_discrete_sequence=px.colors.sequential.Reds_r,
                title=f"Proportion of Wins by Driver ({race_season})"
            )
            fig_win_pie.update_layout(
                template="plotly_dark", 
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FFFFFF"),
                legend=dict(font=dict(color="#FFFFFF"))
            )
            st.plotly_chart(fig_win_pie, use_container_width=True)
        else:
            st.info("No race result records found.")
            
    with col_race2:
        st.write("**Circuit Hosting Fee vs Attendance Density**")
        valid_ce = s_races[s_races['weekend_attendance_k'] > 0]
        if not valid_ce.empty:
            fig_scatter = px.scatter(
                valid_ce,
                x="hosting_fee_usd_m_est",
                y="weekend_attendance_k",
                size="weekend_attendance_k",
                color="is_street_circuit",
                hover_name="grand_prix",
                labels={"hosting_fee_usd_m_est": "Hosting Fee ($M USD)", "weekend_attendance_k": "Weekend Attendance (k)"},
                color_discrete_sequence=['#FF1801', '#00E5FF'],
                title="Economic Yield per Track Asset"
            )
            fig_scatter.update_layout(
                template="plotly_dark", 
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FFFFFF"),
                legend=dict(font=dict(color="#FFFFFF"))
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Hosting metrics or attendance fields are zero or missing for this specific season's circuits.")

# ==================== TAB 3: MACRO ECONOMIC TRENDS ====================
with tab3:
    st.markdown("### 📈 Macro-Commercial Evolution Over Time (All Seasons)")
    st.markdown("This historical analysis evaluates how F1's top-tier revenue grew alongside the Netflix era.")
    
    fig_historical = go.Figure()
    
    fig_historical.add_trace(go.Scatter(
        x=business_df['season'], y=business_df['total_revenue_usd_m'],
        mode='lines+markers', name='Total F1 Corporate Revenue ($M)',
        line=dict(color='#FF1801', width=3)
    ))
    
    fig_historical.add_trace(go.Scatter(
        x=business_df['season'], y=business_df['broadcast_media_usd_m'],
        mode='lines', name='TV Broadcast Media Revenue ($M)',
        line=dict(color='#FFFFFF', dash='dash')
    ))
    
    fig_historical.add_trace(go.Bar(
        x=business_df['season'], y=business_df['drive_to_survive_viewers_m_est'],
        name='Drive to Survive Viewers (Millions)',
        yaxis='y2', opacity=0.25, marker_color='#FFFFFF'
    ))

    # Cleaned, multi-method layout approach to ensure total platform cross-compatibility
    fig_historical.update_layout(
        title="F1 Commercial Revenue Acceleration vs Drive To Survive Viewership Over Time",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF"),
        legend=dict(x=0.01, y=0.99, font=dict(color="#FFFFFF")),
        barmode='overlay'
    )
    
    # Update axes explicitly to guarantee font color overrides apply properly
    fig_historical.update_xaxes(title_text="Season Year", title_font=dict(color="#FFFFFF"), tickfont=dict(color="#FFFFFF"))
    fig_historical.update_yaxes(title_text="Revenue ($M USD)", title_font=dict(color="#FF1801"), tickfont=dict(color="#FFFFFF"))
    fig_historical.update_yaxes(title_text="Netflix Viewership (M)", title_font=dict(color="#A0A5B5"), tickfont=dict(color="#FFFFFF"), overlaying='y', side='right', showgrid=False)
    
    st.plotly_chart(fig_historical, use_container_width=True)
