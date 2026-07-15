import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Formula 1 Analytics", layout="wide")
st.title("🏎️ Formula 1 Insights Dashboard")
st.markdown("Explore F1 race data, constructor budgets, and macro-economics.")

# 2. Load Data Helper (Cached for speed)
@st.cache_data
def load_data():
    rr = pd.read_csv('race_results.csv')
    ce = pd.read_csv('circuit_economics.csv')
    cf = pd.read_csv('constructor_finances.csv')
    ds = pd.read_csv('driver_standings.csv')
    fb = pd.read_csv('f1_business.csv')
    
    # Merge race results and circuit economics for a richer race table
    races_full = pd.merge(rr, ce, on=['season', 'grand_prix'], how='left')
    return races_full, cf, ds, fb

races_df, constructor_df, driver_df, business_df = load_data()

# 3. Sidebar Filter: Season Selection
seasons = sorted(races_df['season'].unique(), reverse=True)
selected_season = st.sidebar.selectbox("Select Season", seasons)

# Filter DataFrames based on the selected season
season_races = races_df[races_df['season'] == selected_season]
season_constructors = constructor_df[constructor_df['season'] == selected_season]
season_drivers = driver_df[driver_df['season'] == selected_season]
season_business = business_df[business_df['season'] == selected_season]

# 4. KPI Metrics at the Top
st.header(f"🏆 {selected_season} Season Highlights")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    total_races = len(season_races)
    st.metric("Total Races", total_races)
with kpi2:
    champs = season_drivers[season_drivers['is_world_champion'] == 1]
    champ_name = champs['driver_name'].values[0] if not champs.empty else "N/A"
    st.metric("World Champion", champ_name)
with kpi3:
    if not season_business.empty:
        global_viewers = season_business['global_avg_race_viewers_m'].values[0]
        st.metric("Global Avg Viewers", f"{global_viewers}M")
    else:
        st.metric("Global Avg Viewers", "N/A")
with kpi4:
    total_attendance = season_races['weekend_attendance_k'].sum()
    st.metric("Total Attendance (est)", f"{total_attendance:,.0f}k" if total_attendance > 0 else "N/A")

st.markdown("---")

# 5. Dashboard Layout Split
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Constructor Finances vs Championship Status")
    if not season_constructors.empty:
        fig_finance = px.bar(
            season_constructors,
            x="team_name",
            y="operating_budget_usd_m",
            color="is_constructors_champion",
            labels={"operating_budget_usd_m": "Budget ($M USD)", "team_name": "Team"},
            title="Team Operating Budgets",
            color_discrete_map={0: "lightblue", 1: "gold"}
        )
        st.plotly_chart(fig_finance, use_container_width=True)
    else:
        st.write("No constructor data available for this season.")

with col2:
    st.subheader("🏁 Season Driver Standings")
    if not season_drivers.empty:
        fig_drivers = px.bar(
            season_drivers.sort_values(by="total_points", ascending=True),
            x="total_points",
            y="driver_name",
            orientation='h',
            title="Points Standings",
            labels={"total_points": "Points", "driver_name": "Driver"},
            color="total_points",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_drivers, use_container_width=True)
    else:
        st.write("No driver standings available for this season.")