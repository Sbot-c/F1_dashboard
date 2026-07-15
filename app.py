import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. PAGE SETUP (Must be the very first Streamlit command)
st.set_page_config(
    page_title="F1 Performance & Economics Hub", 
    page_icon="🏎️", 
    layout="wide"
)

# 2. HIGH-CONTRAST F1 DESIGN STYLING (Injected via CSS)
st.markdown("""
    <style>
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
    # Load all 5 source dataframes
    rr = pd.read_csv('race_results.csv')
    ce = pd.read_csv('circuit_economics.csv')
    cf = pd.read_csv('constructor_finances.csv')
    ds = pd.read_csv('driver_standings.csv')
    fb = pd.read_csv('f1_business.csv')
    
    # Clean discrepancies: replace pre-cost-cap null values with 0
    cf['cost_cap_limit_usd_m'] = cf['cost_cap_limit_usd_m'].fillna(0)
    
    # Merge race-level tables safely using a left join
    races_full = pd.merge(rr, ce, on=['season', 'grand_prix'], how='left', suffixes=('', '_econ'))
    
    return races_full, cf, ds, fb

races_df, constructor_df, driver_df, business_df = load_and_clean_data()


# 4. DASHBOARD HEADER & F1 HERO IMAGE
# Clean, official transparent F1 track/car outline styling
st.image(
    "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?q=80&w=2070&auto=format&fit=crop", 
    caption="Formula 1 Strategic Data Hub", 
    use_container_width=True
)

st.title("🏎️ FORMULA 1 PERFORMANCE & ECONOMICS CENTRALE")
st.markdown("An elite, high-octane environment linking track performance directly to economic metrics.")
st.markdown("---")


# 5. GLOBAL SIDEBAR CONTROLS
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/f/f2/Formula_One_Official_Logo.svg", width=150)
st.sidebar.markdown("### 🛠️ DASHBOARD CONTROLS")

seasons_list = sorted(races_df['season'].unique(), reverse=True)
selected_season = st.sidebar.selectbox("🎯 CHOOSE RACING SEASON", seasons_list)

# Global filtered subsets based on selected season
s_races = races_df[races_df['season'] == selected_season]
s_constructors = constructor_df[constructor_df['season'] == selected_season]
s_drivers = driver_df[driver_df['season'] == selected_season]
s_business = business_df[business_df['season'] == selected_season]


# 6. ROW 1: SEASON HIGHLIGHT METRICS (KPIs)
st.subheader(f"🏁 {selected_season} Season Vitals")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Races Scheduled", value=len(s_races))

with kpi2:
    champ_row = s_drivers[s_drivers['is_world_champion'] == 1]
    champ_name = champ_row['driver_name'].values[0] if not champ_row.empty else "Undecided"
    st.metric(label="Drivers' Champion", value=champ_name)

with kpi3:
    const_row = s_constructors[s_constructors['is_constructors_champion'] == 1]
    const_name = const_row['team_name'].values[0] if not const_row.empty else "Undecided"
    st.metric(label="Constructors' Champion", value=const_name)

with kpi4:
    if not s_business.empty and s_business['global_avg_race_viewers_m'].values[0] > 0:
        viewers = f"{s_business['global_avg_race_viewers_m'].values[0]}M"
    else:
        viewers = "Data N/A"
    st.metric(label="Avg Global Viewers", value=viewers)

st.markdown("   ")


# 7. TABBED INTERACTIVE ANALYTICS
tab1, tab2, tab3 = st.tabs(["📊 FINANCIALS & TREEMAPS", "🏆 TRACK RACE ANALYTICS", "📈 MACRO ECONOMIC TRENDS"])

# ==================== TAB 1: FINANCIALS & TREEMAPS ====================
with tab1:
    st.markdown("### 💰 Team Financial Breakdown & Revenue Distribution")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.write("**Visualizing Corporate Footprints: Team Revenue vs Budgets**")
        if not s_constructors.empty:
            # Interactive Treemap showing Team Sizes by Budget and Country Origin
            fig_tree = px.treemap(
                s_constructors,
                path=['country_iso3', 'team_name'],
                values='operating_budget_usd_m',
                color='total_revenue_usd_m',
                color_continuous_scale='Reds',
                labels={'operating_budget_usd_m': 'Budget ($M)', 'total_revenue_usd_m': 'Total Revenue ($M)'},
                title=f"Treemap: Team Operating Budgets Grouped by Country ({selected_season})"
            )
            fig_tree.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.info("No constructor financial data available for this specific season.")
            
    with col2:
        st.write("**Revenue Breakdown for Top Constructors**")
        if not s_constructors.empty:
            # Dynamic filter inside the tab for looking at specific teams
            selected_team = st.selectbox("Select Team for Share Breakdown", s_constructors['team_name'].unique())
            team_data = s_constructors[s_constructors['team_name'] == selected_team].iloc[0]
            
            # Interactive Pie chart for financial streams
            revenue_streams = ['Sponsorship Revenue', 'Prize Money']
            revenue_values = [team_data['sponsorship_revenue_usd_m'], team_data['prize_money_usd_m']]
            
            fig_pie = px.pie(
                names=revenue_streams,
                values=revenue_values,
                hole=0.4,
                color_discrete_sequence=['#FF1801', '#FFFFFF'],
                title=f"{selected_team} Core Revenue Streams ($M)"
            )
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No team breakdown data loaded.")

# ==================== TAB 2: TRACK RACE ANALYTICS ====================
with tab2:
    st.markdown("### 🏁 Grand Prix Dominance & Circuit Hosting Economics")
    
    col_race1, col_race2 = st.columns(2)
    
    with col_race1:
        st.write("**Race Winners Distribution**")
        if not s_races.empty:
            # Pie Chart of Winners to spot seasonal dominance instantly
            winner_counts = s_races['winner'].value_counts().reset_index()
            winner_counts.columns = ['Driver', 'Wins']
            
            fig_win_pie = px.pie(
                winner_counts,
                names='Driver',
                values='Wins',
                color_discrete_sequence=px.colors.sequential.Reds_r,
                title=f"Proportion of Wins by Driver in {selected_season}"
            )
            fig_win_pie.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_win_pie, use_container_width=True)
        else:
            st.info("No race result records found.")
            
    with col_race2:
        st.write("**Circuit Hosting Fee vs Attendance Density**")
        # Ensure we have rows with attendance metrics before charting
        valid_ce = s_races[s_races['weekend_attendance_k'] > 0]
        if not valid_ce.empty:
            fig_scatter = px.scatter(
                valid_ce,
                x="hosting_fee_usd_m_est",
                y="weekend_attendance_k",
                size="weekend_attendance_k",
                color="is_street_circuit",
                hover_name="grand_prix",
                labels={"hosting_fee_usd_m_est": "Hosting Fee ($M USD)", "weekend_attendance_k": "Weekend Fan Attendance (Thousands)"},
                color_discrete_sequence=['#FF1801', '#00E5FF'],
                title="Economic Yield per Track"
            )
            fig_scatter.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Hosting fees and weekend attendance fields are missing or zero for this season's circuits.")

# ==================== TAB 3: MACRO ECONOMIC TRENDS ====================
with tab3:
    st.markdown("### 📈 Macro-Commercial Evolution Over Time (All Seasons)")
    st.markdown("This historical analysis evaluates how F1's top-tier revenue grew alongside the Netflix era.")
    
    # Historical multi-line analysis across all eras
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
    fig_historical.add_trace(go.Scatter(
        x=business_df['season'], y=business_df['drive_to_survive_viewers_m_est'],
        mode='bar', name='Drive to Survive Viewers (Millions)',
        yaxis='y2', opacity=0.3, marker_color='#A0A5B5'
    ))

    # Dual-axis layout configurations for elegant parsing
    fig_historical.update_layout(
        title="F1 Commercial Revenue Acceleration vs Drive To Survive Viewership",
        xaxis=dict(title="Season Year"),
        yaxis=dict(title="Revenue ($M USD)", color="#FF1801"),
        yaxis2=dict(title="Netflix Viewership (M)", color="#A0A5B5", overlaying='y', side='right'),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig_historical, use_container_width=True)


# 8. DATA EXPLORER ACCORDION (For deep dives)
with st.expander("🔍 INSPECT RAW SELECTION RECORD MANIFESTS"):
    st.write(f"Showing raw loaded slices for the {selected_season} Season:")
    inspect_col1, inspect_col2 = st.columns(2)
    with inspect_col1:
        st.dataframe(s_drivers[['championship_position', 'driver_name', 'total_points', 'wins']].sort_values(by='championship_position'))
    with inspect_col2:
        st.dataframe(s_races[['round_number', 'grand_prix', 'circuit', 'winner', 'safety_car_periods']])
