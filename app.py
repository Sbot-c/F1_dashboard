"""Formula 1 · Performance & Economics — Streamlit dashboard. Run: streamlit run app.py"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="F1 · Performance & Economics", page_icon="🏁",
                   layout="wide", initial_sidebar_state="collapsed")

# Palette drawn from the sport's own colour language: tyre compounds and the
# timing screen (purple = fastest sector, green = personal best).
ASPHALT = "#0B0E14"
SURFACE = "#121824"
LINE = "#212B3B"
AMBER = "#F2B705"      # money
TYRE_RED = "#E10600"   # soft / on-track
PURPLE = "#B45AF2"     # fastest sector
GREEN = "#43B02A"      # intermediate
BLUE = "#1E7FD6"       # wet
WHITE = "#E8EDF5"
MUTED = "#7C8AA0"

COLORWAY = [AMBER, TYRE_RED, PURPLE, BLUE, GREEN, WHITE, "#FF8A3D"]
HEAT = [[0.0, "#101725"], [0.35, "#7A1810"], [0.7, TYRE_RED], [1.0, AMBER]]
DIVERGING = [[0.0, BLUE], [0.5, "#141B28"], [1.0, AMBER]]

# ─────────────────────────────────────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=Barlow:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');

.stApp {{
    background:
      repeating-linear-gradient(45deg, rgba(255,255,255,.014) 0 2px, rgba(0,0,0,0) 2px 5px),
      repeating-linear-gradient(-45deg, rgba(255,255,255,.014) 0 2px, rgba(0,0,0,0) 2px 5px),
      radial-gradient(1200px 560px at 8% -12%, #1B2436 0%, rgba(11,14,20,0) 62%),
      radial-gradient(900px 460px at 98% 0%, #2A1418 0%, rgba(11,14,20,0) 58%),
      {ASPHALT};
    color: {WHITE};
    font-family: 'Barlow', system-ui, sans-serif;
}}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.6rem; padding-bottom: 4rem; max-width: 1540px; }}
#MainMenu, footer {{ visibility: hidden; }}
h1, h2, h3, h4 {{ color: {WHITE}; font-family: 'Chakra Petch', sans-serif; }}
p, li, label {{ color: {WHITE}; }}

/* ── Masthead ─────────────────────────────────────────── */
.masthead {{ padding: .4rem 0 1.1rem; }}
.eyebrow {{
    display: inline-block; transform: skewX(-12deg);
    background: {TYRE_RED}; color: #fff; padding: .18rem .85rem;
    font-family: 'JetBrains Mono', monospace; font-size: .66rem;
    letter-spacing: .2em; text-transform: uppercase; margin-bottom: .85rem;
}}
.eyebrow span {{ display: inline-block; transform: skewX(12deg); }}
.masthead h1 {{
    font-family: 'Chakra Petch', sans-serif; font-weight: 700;
    font-size: clamp(2rem, 4.6vw, 3.4rem); line-height: 1; margin: 0;
    letter-spacing: -.015em; text-transform: uppercase;
}}
.masthead h1 em {{ font-style: normal; color: {AMBER}; }}
.masthead .dek {{ color: {MUTED}; font-size: .95rem; margin-top: .75rem; max-width: 70ch; }}

/* ── Era rule: signature strip under the masthead ─────── */
.era {{ display: flex; gap: 3px; margin: 1.15rem 0 .5rem; height: 9px; }}
.era span {{ display: block; border-radius: 1px; }}
.eralabels {{
    display: flex; flex-wrap: wrap; gap: 1.4rem;
    font-family: 'JetBrains Mono', monospace; font-size: .66rem;
    letter-spacing: .12em; text-transform: uppercase; color: {MUTED};
}}
.eralabels b {{ color: {WHITE}; font-weight: 500; }}

/* ── Timing-tower KPI plates ──────────────────────────── */
.plate {{
    position: relative; background: linear-gradient(180deg, {SURFACE} 0%, #0E1420 100%);
    border: 1px solid {LINE}; border-left: 3px solid var(--accent, {AMBER});
    padding: .85rem 1rem .8rem 1.05rem; height: 100%;
    transition: transform .16s ease, border-color .16s ease;
}}
.plate:hover {{ transform: translateY(-2px); border-color: var(--accent, {AMBER}); }}
.plate .k {{
    font-family: 'JetBrains Mono', monospace; font-size: .62rem; letter-spacing: .16em;
    text-transform: uppercase; color: {MUTED};
}}
.plate .v {{
    font-family: 'Chakra Petch', sans-serif; font-weight: 700; font-size: 1.75rem;
    line-height: 1.1; margin: .3rem 0 .15rem; color: {WHITE};
    font-variant-numeric: tabular-nums;
}}
.plate .s {{ font-size: .74rem; color: var(--accent, {AMBER}); font-family: 'JetBrains Mono', monospace; }}

/* ── Sections and notes ───────────────────────────────── */
.sect {{ margin: 1.8rem 0 .35rem; }}
.sect .t {{
    font-family: 'Chakra Petch', sans-serif; font-weight: 600; font-size: 1.3rem;
    text-transform: uppercase; letter-spacing: .01em;
}}
.sect .d {{ color: {MUTED}; font-size: .85rem; margin-top: .1rem; }}
.rule {{ border: 0; border-top: 1px solid {LINE}; margin: 1.5rem 0 0; }}
.note {{
    border-left: 2px solid {AMBER}; background: rgba(242,183,5,.06);
    padding: .58rem .85rem; font-size: .86rem; margin-top: .4rem; color: {WHITE};
}}
.note b {{ color: {AMBER}; }}
.flag {{
    border-left: 2px solid {TYRE_RED}; background: rgba(225,6,0,.07);
    padding: .58rem .85rem; font-size: .86rem; margin-top: .4rem; color: {WHITE};
}}
.flag b {{ color: {TYRE_RED}; }}

/* ── Tabs as timing-screen buttons ────────────────────── */
.stTabs [data-baseweb="tab-list"] {{ gap: .3rem; border-bottom: 1px solid {LINE}; }}
.stTabs [data-baseweb="tab"] {{
    background: transparent; color: {MUTED}; padding: .5rem .95rem;
    font-family: 'JetBrains Mono', monospace; font-size: .74rem;
    letter-spacing: .12em; text-transform: uppercase; border-radius: 2px 2px 0 0;
}}
.stTabs [aria-selected="true"] {{
    background: rgba(242,183,5,.10); color: {AMBER} !important;
    border-bottom: 2px solid {AMBER};
}}

/* ── Widgets ──────────────────────────────────────────── */
div[data-baseweb="select"] > div {{ background-color: {SURFACE}; border-color: {LINE}; }}
.stMultiSelect [data-baseweb="tag"] {{ background-color: rgba(225,6,0,.55); }}
[data-testid="stWidgetLabel"] p {{
    font-family: 'JetBrains Mono', monospace; font-size: .66rem !important;
    letter-spacing: .14em; text-transform: uppercase; color: {MUTED};
}}
[data-testid="stExpander"] {{ border: 1px solid {LINE}; background: {SURFACE}; }}
[data-testid="stDataFrame"] {{ border: 1px solid {LINE}; }}
.stSlider [data-baseweb="slider"] div[role="slider"] {{ background-color: {AMBER}; }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>
""",
    unsafe_allow_html=True,
)

paddock = go.layout.Template()
paddock.layout = go.Layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Barlow, sans-serif", color=WHITE, size=13),
    title=dict(font=dict(family="Chakra Petch, sans-serif", size=17, color=WHITE), x=0, xanchor="left"),
    colorway=COLORWAY,
    xaxis=dict(gridcolor="rgba(232,237,245,.06)", zerolinecolor="rgba(232,237,245,.14)",
               linecolor=LINE, tickfont=dict(color=MUTED, size=11), title_font=dict(color=MUTED, size=12)),
    yaxis=dict(gridcolor="rgba(232,237,245,.06)", zerolinecolor="rgba(232,237,245,.14)",
               linecolor=LINE, tickfont=dict(color=MUTED, size=11), title_font=dict(color=MUTED, size=12)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=11), title_font=dict(color=MUTED)),
    hoverlabel=dict(bgcolor=SURFACE, bordercolor=AMBER, font=dict(color=WHITE, family="Barlow")),
    margin=dict(l=12, r=12, t=52, b=12),
    colorscale=dict(sequential=HEAT, diverging=DIVERGING),
)
pio.templates["paddock"] = paddock
pio.templates.default = "paddock"

# Every raw column name gets a readable label with its unit. px.defaults.labels applies
# these to axis titles, legend titles and hover rows across every chart in the app.
LABELS = {
    "season": "Season",
    "team_name": "Team",
    "country_iso3": "HQ country",
    "operating_budget_usd_m": "Operating budget ($M)",
    "total_revenue_usd_m": "Total revenue ($M)",
    "sponsorship_revenue_usd_m": "Sponsorship revenue ($M)",
    "prize_money_usd_m": "Prize money ($M)",
    "cost_cap_limit_usd_m": "Cost cap limit ($M)",
    "Surplus": "Surplus: revenue − budget ($M)",
    "Margin": "Operating margin",
    "Sponsorship share": "Sponsorship share of income",
    "Cap era": "Era",
    "Budget rank": "Budget rank that season (1 = biggest spender)",
    "Titles": "Constructors' titles won",
    "hosting_fee_usd_m_est": "Hosting fee ($M est.)",
    "weekend_attendance_k": "Weekend attendance (thousands)",
    "Fee per fan": "Hosting fee per attendee ($)",
    "Venue age": "Seasons since venue debut",
    "Era": "Venue era",
    "Circuit type": "Circuit type",
    "grand_prix": "Grand Prix",
    "circuit": "Circuit",
    "region": "Region",
    "Share": "Share of rounds",
    "winner": "Race winner",
    "Wins": "Race wins",
    "driver_name": "Driver",
    "total_points": "Championship points",
    "wins": "Race wins",
    "poles": "Pole positions",
    "podiums_est": "Podiums (est.)",
    "Conversion": "Races won from pole",
    "Champion": "Result",
    "Growth": "Change on previous season",
    "Coverage": "Races with fee & attendance data",
    "Value": "Revenue ($M)",
    "Stream": "Revenue stream",
}
px.defaults.labels = LABELS


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def chart(fig, key=None, height=None):
    """Version-safe plotly_chart (Streamlit renamed use_container_width -> width)."""
    if height:
        fig.update_layout(height=height)
    try:
        st.plotly_chart(fig, width="stretch", key=key)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, key=key)


def table(df, height=None, key=None):
    try:
        st.dataframe(df, width="stretch", height=height, key=key)
    except TypeError:
        st.dataframe(df, use_container_width=True, height=height, key=key)


def section(title, desc=""):
    st.markdown(f"<div class='sect'><div class='t'>{title}</div><div class='d'>{desc}</div></div>",
                unsafe_allow_html=True)


def plate(col, label, value, sub="", accent=AMBER):
    col.markdown(
        f"<div class='plate' style='--accent:{accent}'><div class='k'>{label}</div>"
        f"<div class='v'>{value}</div><div class='s'>{sub}</div></div>",
        unsafe_allow_html=True)


def note(text):
    st.markdown(f"<div class='note'>{text}</div>", unsafe_allow_html=True)


def flag(text):
    st.markdown(f"<div class='flag'>{text}</div>", unsafe_allow_html=True)


def multi(label, options, key, default=None):
    """Local filter that never leaves a chart with an empty frame."""
    opts = list(options)
    picked = st.multiselect(label, opts, default=opts if default is None else default, key=key)
    return picked or opts


def money(v, unit="M"):
    return f"${v:,.0f}{unit}"


# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
FILES = ["race_results.csv", "circuit_economics.csv", "constructor_finances.csv",
         "driver_standings.csv", "f1_business.csv"]


def _locate(name):
    for base in [Path("."), Path(__file__).parent, Path("data"),
                 Path("/mnt/user-data/uploads")]:
        p = base / name
        if p.exists():
            return p
    return None


@st.cache_data(show_spinner="Loading the season files…")
def load_data(paths):
    rr = pd.read_csv(paths["race_results.csv"])
    ce = pd.read_csv(paths["circuit_economics.csv"])
    cf = pd.read_csv(paths["constructor_finances.csv"])
    ds = pd.read_csv(paths["driver_standings.csv"])
    fb = pd.read_csv(paths["f1_business.csv"])
    audit = {}

    # ── races ────────────────────────────────────────────────────────────────
    rr["race_date"] = pd.to_datetime(rr["race_date"], errors="coerce")
    rr["Sprint weekend"] = np.where(rr["is_sprint_weekend"] == 1, "Sprint", "Standard")
    rr["Pole converted"] = rr["pole_position"] == rr["winner"]
    rr["All-podium"] = rr[["winner", "podium_p2", "podium_p3"]].agg(", ".join, axis=1)

    # ── circuits ─────────────────────────────────────────────────────────────
    ce["Circuit type"] = ce["is_street_circuit"].map({0: "Permanent", 1: "Street"})
    ce["Venue age"] = ce["season"] - ce["debut_year"]
    ce["Era"] = np.where(ce["is_new_circuit_post_2020"] == 1, "New (post-2020)", "Established")
    # Fee per attending fan. 2020 ran behind closed doors, so the ratio is meaningless there.
    ce["Fee per fan"] = np.where(ce["weekend_attendance_k"] >= 20,
                                 ce["hosting_fee_usd_m_est"] * 1000 / ce["weekend_attendance_k"],
                                 np.nan)

    # ── constructors ─────────────────────────────────────────────────────────
    # Keep cost_cap_limit as NaN before 2021 — there was no cap, and filling it with 0
    # makes every pre-cap team look infinitely over budget.
    audit["cap_missing"] = int(cf["cost_cap_limit_usd_m"].isna().sum())
    cf["Cap era"] = np.where(cf["in_cost_cap_era"] == 1, "Cost cap era", "Pre-cap era")
    cf["Surplus"] = cf["total_revenue_usd_m"] - cf["operating_budget_usd_m"]
    cf["Margin"] = cf["Surplus"] / cf["total_revenue_usd_m"]
    cf["Sponsorship share"] = cf["sponsorship_revenue_usd_m"] / cf["total_revenue_usd_m"]
    cf["Budget vs cap"] = cf["operating_budget_usd_m"] - cf["cost_cap_limit_usd_m"]
    cf["Champion"] = np.where(cf["is_constructors_champion"] == 1, "Champion", "Field")

    # ── standings ────────────────────────────────────────────────────────────
    ds["Champion"] = np.where(ds["is_world_champion"] == 1, "Champion", "Contender")
    ds["Points per win"] = (ds["total_points"] / ds["wins"].replace(0, np.nan)).round(1)

    # ── business ─────────────────────────────────────────────────────────────
    REV_PARTS = ["race_promotion_fees_usd_m", "broadcast_media_usd_m",
                 "sponsorship_usd_m", "other_revenue_usd_m"]
    fb["Parts total"] = fb[REV_PARTS].sum(axis=1)
    fb["Reporting gap"] = fb["Parts total"] - fb["total_revenue_usd_m"]
    fb["Era"] = np.where(fb["is_liberty_media_era"] == 1, "Liberty Media", "CVC / Ecclestone")
    races_per_season = rr.groupby("season").size().rename("races")
    fb = fb.merge(races_per_season, left_on="season", right_index=True, how="left")
    fb["Revenue per race"] = fb["total_revenue_usd_m"] / fb["races"]
    fb["Growth"] = fb["total_revenue_usd_m"].pct_change()

    # ── joined race + circuit view (coverage is partial — measure it) ────────
    races = rr.merge(ce.drop(columns=["circuit", "country_iso3", "region"], errors="ignore"),
                     on=["season", "grand_prix"], how="left")
    audit["races"] = len(rr)
    audit["races_with_econ"] = int(races["hosting_fee_usd_m_est"].notna().sum())
    audit["econ_coverage"] = audit["races_with_econ"] / audit["races"]

    coverage = (races.assign(has=races["hosting_fee_usd_m_est"].notna())
                .groupby("season").agg(Races=("race_id", "count"), With_economics=("has", "sum")))
    coverage["Coverage"] = coverage["With_economics"] / coverage["Races"]

    audit["seasons"] = (int(rr["season"].min()), int(rr["season"].max()))
    counts = rr.groupby("season").size()
    audit["last_full"] = int(counts[counts >= 15].index.max())
    audit["partial"] = [int(y) for y in counts[counts < 15].index]
    # The four revenue streams turn out to be fixed percentages of the headline total in
    # every season — worth knowing before anyone reads a "mix shift" into them.
    shares = fb[REV_PARTS].div(fb["total_revenue_usd_m"], axis=0)
    audit["mix_fixed"] = bool((shares.std() < 0.01).all())
    audit["mix_shares"] = (shares.median() * 100).round(0).to_dict()
    audit["rev_gap_seasons"] = fb.loc[fb["Reporting gap"].abs() > 5, ["season", "Reporting gap"]]
    audit["over_cap"] = int(((cf["Budget vs cap"] > 0) & cf["cost_cap_limit_usd_m"].notna()).sum())
    audit["cap_rows"] = int(cf["cost_cap_limit_usd_m"].notna().sum())

    return rr, ce, cf, ds, fb, races, coverage, audit


paths, missing = {}, []
for f in FILES:
    p = _locate(f)
    (paths.setdefault(f, p) if p else missing.append(f))

if missing:
    # Tucked into an expander so the loader does not sit on top of the dashboard once
    # the files are in. It only appears at all when a CSV is not next to app.py.
    with st.expander("Data files", expanded=True):
        st.write("Put these next to `app.py`, or upload them here:")
        st.code("\n".join(missing))
        ups = st.file_uploader("CSV files", type="csv", accept_multiple_files=True,
                               label_visibility="collapsed")
    for u in ups or []:
        if u.name in missing:
            paths[u.name] = u
            missing = [m for m in missing if m != u.name]
    if missing:
        st.stop()

races_df, circuits_df, teams_df, drivers_df, business_df, race_econ, coverage_df, audit = load_data(paths)

LATEST = int(business_df["season"].max())
FIRST = int(business_df["season"].min())

# ─────────────────────────────────────────────────────────────────────────────
# MASTHEAD
# ─────────────────────────────────────────────────────────────────────────────
era_rev = business_df.groupby("Era", sort=False)["total_revenue_usd_m"].sum()
era_bar, era_labels = "", ""
for i, (era, val) in enumerate(era_rev.items()):
    share = val / era_rev.sum() * 100
    era_bar += f"<span style='flex:{share};background:{[TYRE_RED, AMBER][i % 2]}'></span>"
    era_labels += f"<div><b>{era}</b> {share:.0f}% of cumulative revenue</div>"

st.markdown(
    f"""
<div class='masthead'>
  <div class='eyebrow'><span>{audit['seasons'][0]}–{audit['seasons'][1]} · {audit['races']} races · {teams_df['team_name'].nunique()} teams</span></div>
  <h1>Formula 1 · <em>Performance &amp; Economics</em></h1>
  <div class='dek'>Five files, one sport: what the calendar earns, what the teams spend,
  what the circuits pay to host, and who actually wins. The money and the results are read
  side by side rather than in separate reports.</div>
  <div class='era'>{era_bar}</div>
  <div class='eralabels'>{era_labels}</div>
</div>
""",
    unsafe_allow_html=True,
)

latest_row = business_df[business_df["season"] == LATEST].iloc[0]
first_row = business_df[business_df["season"] == FIRST].iloc[0]
cagr = (latest_row["total_revenue_usd_m"] / first_row["total_revenue_usd_m"]) ** (1 / (LATEST - FIRST)) - 1
cap_now = teams_df.loc[teams_df["season"] == LATEST, "cost_cap_limit_usd_m"].max()

k = st.columns(6)
plate(k[0], f"{LATEST} revenue", money(latest_row["total_revenue_usd_m"]),
      f"+{latest_row['Growth']*100:.1f}% on {LATEST-1}", AMBER)
plate(k[1], "Revenue CAGR", f"{cagr*100:.1f}%", f"{FIRST}→{LATEST}", AMBER)
plate(k[2], "Races run", f"{audit['races']}",
      f"{races_df.groupby('season').size().iloc[-1]} in {LATEST}"
      + (" (in progress)" if LATEST in audit["partial"] else ""), TYRE_RED)
plate(k[3], "Race winners", f"{races_df['winner'].nunique()}",
      f"{races_df['winner'].value_counts().index[0]} leads", TYRE_RED)
plate(k[4], "Avg hosting fee", money(circuits_df.loc[circuits_df['season'] == LATEST, 'hosting_fee_usd_m_est'].mean()),
      f"{LATEST} calendar", PURPLE)
plate(k[5], "Cost cap", money(cap_now) if pd.notna(cap_now) else "—",
      f"{audit['over_cap']} team-seasons above it", BLUE)

st.markdown("<hr class='rule'>", unsafe_allow_html=True)

tabs = st.tabs(["Sport P&L", "Teams", "Circuits", "On track", "Cross-analysis", "Data & integrity"])

# ═════════════════════════════════════════════════════════════════════════════
# 1 · SPORT P&L
# ═════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    section("Where the sport's money comes from",
            "Four revenue lines, seventeen seasons, two ownership eras.")
    REV_PARTS = {"race_promotion_fees_usd_m": "Race promotion fees",
                 "broadcast_media_usd_m": "Broadcast & media",
                 "sponsorship_usd_m": "Sponsorship",
                 "other_revenue_usd_m": "Other"}
    c1, c2 = st.columns([3, 2])

    with c1:
        view = st.radio("Show as", ["Dollars", "Share of revenue"], horizontal=True, key="pl_view")
        m = business_df.melt(id_vars="season", value_vars=list(REV_PARTS),
                             var_name="Stream", value_name="Value")
        m["Stream"] = m["Stream"].map(REV_PARTS)
        if view == "Share of revenue":
            m["Value"] = m["Value"] / m.groupby("season")["Value"].transform("sum")
        fig = px.area(m, x="season", y="Value", color="Stream",
                      color_discrete_sequence=[AMBER, TYRE_RED, PURPLE, BLUE],
                      title="Revenue by stream")
        fig.update_layout(
            yaxis_tickformat=".0%" if view == "Share of revenue" else "$,.0f",
            xaxis_title="Season",
            yaxis_title="Share of total revenue" if view == "Share of revenue" else "Revenue ($M)",
            legend=dict(orientation="h", y=1.14, title_text="Revenue stream"))
        fig.update_traces(hovertemplate="Season %{x}<br>%{fullData.name}: " +
                          ("%{y:.1%} of revenue" if view == "Share of revenue" else "$%{y:,.0f}M") +
                          "<extra></extra>")
        chart(fig, key="fig_pl_area", height=420)
        sh = audit["mix_shares"]
        if audit["mix_fixed"]:
            note("Switch to the share view and the answer is a flat block: the four streams sit at a "
                 f"fixed <b>{sh['race_promotion_fees_usd_m']:.0f} / {sh['broadcast_media_usd_m']:.0f} / "
                 f"{sh['sponsorship_usd_m']:.0f} / {sh['other_revenue_usd_m']:.0f}</b> split in every "
                 "season. They are proportions of the headline number rather than independently "
                 "measured lines, so read scale from this chart, never mix shift.")
        else:
            note("Race promotion fees are the largest single line in every season — the calendar "
                 "is the sport's main product.")

    with c2:
        fig = go.Figure()
        for era, colr in [("CVC / Ecclestone", TYRE_RED), ("Liberty Media", AMBER)]:
            e = business_df[business_df["Era"] == era]
            fig.add_trace(go.Scatter(x=e["season"], y=e["Revenue per race"], mode="lines+markers",
                                     name=era, line=dict(color=colr, width=3), marker=dict(size=8)))
        fig.update_layout(title="Revenue earned per race",
                          yaxis_title="Sport revenue ÷ rounds run ($M per race)",
                          xaxis_title="Season", legend=dict(title_text="Ownership era"))
        fig.update_traces(hovertemplate="Season %{x}<br>$%{y:,.0f}M per race<extra>%{fullData.name}</extra>")
        chart(fig, key="fig_pl_perrace", height=420)
        rpr = business_df.groupby("Era")["Revenue per race"].mean()
        note(f"Per race, the sport earns <b>{money(rpr['Liberty Media'])}</b> under Liberty Media "
             f"against {money(rpr['CVC / Ecclestone'])} before it — roughly "
             f"{rpr['Liberty Media']/rpr['CVC / Ecclestone']:.1f}× more from each round, on a longer "
             "calendar.")

    section("Audience and the streaming effect",
            "Viewership against the Drive to Survive audience the file estimates.")
    c3, c4 = st.columns(2)
    with c3:
        metric = st.selectbox("Audience measure", ["us_avg_race_viewers_m", "global_avg_race_viewers_m"],
                              format_func=lambda s: "US average race viewers (M)" if s.startswith("us")
                              else "Global average race viewers (M)", key="pl_aud")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=business_df["season"], y=business_df["drive_to_survive_viewers_m_est"],
                             name="Drive to Survive viewers (M)", marker_color="rgba(180,90,242,.45)"))
        fig.add_trace(go.Scatter(x=business_df["season"], y=business_df[metric], yaxis="y2",
                                 name="Race viewers (M)", line=dict(color=AMBER, width=3),
                                 mode="lines+markers"))
        fig.update_layout(title="Streaming audience vs race audience",
                          yaxis=dict(title="DTS viewers (M)"),
                          yaxis2=dict(title="Race viewers (M)", overlaying="y", side="right", showgrid=False),
                          legend=dict(orientation="h", y=1.16), xaxis_title="Season")
        chart(fig, key="fig_pl_aud", height=400)
        dts = business_df[business_df["drive_to_survive_viewers_m_est"] > 0]
        note(f"Across the seasons with a Drive to Survive audience, its correlation with "
             f"{'US' if metric.startswith('us') else 'global'} race viewers is "
             f"<b>{dts['drive_to_survive_viewers_m_est'].corr(dts[metric]):.2f}</b>. "
             "Note the series peaks and then falls back while race viewing keeps climbing — "
             "the show looks like an accelerant, not the engine.")

    with c4:
        fig = px.bar(business_df, x="season", y="Growth", color="Growth",
                     color_continuous_scale=DIVERGING, range_color=[-.6, .6],
                     title="Year-on-year revenue growth", text_auto=".0%")
        fig.add_hline(y=0, line_color=MUTED, line_width=1)
        fig.update_layout(yaxis_tickformat=".0%", coloraxis_showscale=False,
                          xaxis_title="Season", yaxis_title="Change in total revenue vs prior season")
        fig.update_traces(textposition="outside",
                          hovertemplate="Season %{x}<br>%{y:+.1%} vs prior season<extra></extra>")
        chart(fig, key="fig_pl_growth", height=400)
        worst = business_df.loc[business_df["Growth"].idxmin()]
        note(f"The one break in the curve is <b>{int(worst['season'])}</b> at "
             f"{worst['Growth']*100:.0f}%. Everything else is growth, in both ownership eras.")

# ═════════════════════════════════════════════════════════════════════════════
# 2 · TEAMS
# ═════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    section("The paddock as ten businesses",
            "Operating budget against revenue. Above the line, a team funds itself.")
    c1, c2 = st.columns([3, 2])

    with c1:
        f_era = multi("Era", list(teams_df["Cap era"].unique()), "tm_era")
        d = teams_df[teams_df["Cap era"].isin(f_era)]
        fig = px.scatter(d, x="operating_budget_usd_m", y="total_revenue_usd_m",
                         color="team_name", size="total_revenue_usd_m", size_max=22,
                         symbol="Cap era", hover_name="team_name",
                         hover_data={"season": True, "Surplus": ":.1f", "Margin": ":.1%"},
                         color_discrete_sequence=COLORWAY + px.colors.qualitative.Set3,
                         title="Budget vs revenue, every team-season")
        lim = [0, max(d["operating_budget_usd_m"].max(), d["total_revenue_usd_m"].max()) * 1.05]
        fig.add_trace(go.Scatter(x=lim, y=lim, mode="lines", name="Break-even",
                                 line=dict(color=MUTED, dash="dot", width=1)))
        fig.update_layout(xaxis_title="Operating budget ($M) — what the team spends",
                          yaxis_title="Total revenue ($M) — what the team earns",
                          legend=dict(title_text="Team / era"))
        fig.add_annotation(x=lim[1] * .78, y=lim[1] * .92, text="funds itself", showarrow=False,
                           font=dict(color=MUTED, size=11))
        fig.add_annotation(x=lim[1] * .92, y=lim[1] * .70, text="spends more than it earns",
                           showarrow=False, font=dict(color=MUTED, size=11))
        chart(fig, key="fig_tm_scatter", height=470)

    with c2:
        yearly = teams_df.groupby(["season", "Cap era"], as_index=False)["Surplus"].mean()
        fig = px.bar(yearly, x="season", y="Surplus", color="Cap era",
                     color_discrete_map={"Pre-cap era": TYRE_RED, "Cost cap era": AMBER},
                     title="Average surplus per team")
        fig.add_hline(y=0, line_color=MUTED, line_width=1)
        fig.update_layout(yaxis_title="Average surplus per team: revenue − budget ($M)",
                          xaxis_title="Season",
                          legend=dict(orientation="h", y=1.14, title_text="Era"))
        fig.update_traces(hovertemplate="Season %{x}<br>Avg surplus $%{y:,.0f}M<extra>%{fullData.name}</extra>")
        chart(fig, key="fig_tm_surplus", height=470)
        pre = teams_df[teams_df["in_cost_cap_era"] == 0]["Surplus"].mean()
        post = teams_df[teams_df["in_cost_cap_era"] == 1]["Surplus"].mean()
        note(f"Average team-season surplus: <b>{money(pre)}</b> before the cap, "
             f"<b>{money(post)}</b> after. The cap is the single clearest financial event in "
             "the file — it turned a spending race into a set of profitable businesses.")

    section("Did the cap close the gap?",
            "Spread of operating budgets across the grid, season by season, against the cap itself.")
    c3, c4 = st.columns([3, 2])
    with c3:
        f_teams = multi("Teams", sorted(teams_df["team_name"].unique()), "tm_box")
        d = teams_df[teams_df["team_name"].isin(f_teams)]
        fig = px.box(d, x="season", y="operating_budget_usd_m", points="all",
                     color="Cap era", color_discrete_map={"Pre-cap era": TYRE_RED, "Cost cap era": AMBER},
                     hover_name="team_name", title="Operating budget spread")
        cap_line = teams_df.dropna(subset=["cost_cap_limit_usd_m"]).groupby("season")["cost_cap_limit_usd_m"].max()
        fig.add_trace(go.Scatter(x=cap_line.index, y=cap_line.values, mode="lines+markers",
                                 name="Cost cap limit", line=dict(color=BLUE, width=2.5, dash="dash")))
        fig.update_layout(xaxis_title="Season", yaxis_title="Operating budget ($M)",
                          legend=dict(orientation="h", y=1.12, title_text=""))
        chart(fig, key="fig_tm_box", height=460)
    with c4:
        spread = teams_df.groupby("season")["operating_budget_usd_m"].agg(
            Spread=lambda s: s.max() - s.min(), Ratio=lambda s: s.max() / s.min())
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=spread.index, y=spread["Spread"], name="Top−bottom gap ($M)",
                                 line=dict(color=AMBER, width=3), fill="tozeroy",
                                 fillcolor="rgba(242,183,5,.10)"))
        fig.add_trace(go.Scatter(x=spread.index, y=spread["Ratio"], name="Top ÷ bottom (×)",
                                 yaxis="y2", line=dict(color=PURPLE, width=2, dash="dot")))
        fig.update_layout(title="Grid inequality",
                          yaxis_title="Budget gap, biggest − smallest ($M)",
                          yaxis2=dict(title="Biggest ÷ smallest budget (×)", overlaying="y",
                                      side="right", showgrid=False),
                          xaxis_title="Season", legend=dict(orientation="h", y=1.16))
        chart(fig, key="fig_tm_spread", height=460)
        note(f"The gap between the biggest and smallest budget peaked at "
             f"<b>{money(spread['Spread'].max())}</b> in {int(spread['Spread'].idxmax())} and sits at "
             f"{money(spread['Spread'].iloc[-1])} in {LATEST}. Narrowing — but the grid is still not flat.")

    section("Team ledger", "Pick a season and read the paddock as a set of accounts.")
    c5, c6 = st.columns([2, 3])
    with c5:
        season_pick = st.selectbox("Season", sorted(teams_df["season"].unique(), reverse=True),
                                   key="tm_season")
        s = teams_df[teams_df["season"] == season_pick].sort_values("total_revenue_usd_m", ascending=False)
        fig = px.treemap(s, path=[px.Constant(f"{season_pick} grid"), "country_iso3", "team_name"],
                         values="total_revenue_usd_m", color="Margin",
                         color_continuous_scale=HEAT, custom_data=["operating_budget_usd_m"],
                         title=f"Revenue by team, shaded by margin ({season_pick})")
        fig.update_traces(marker_line_color=ASPHALT, marker_line_width=2,
                          texttemplate="<b>%{label}</b><br>Revenue $%{value:,.0f}M",
                          hovertemplate="<b>%{label}</b><br>Revenue $%{value:,.0f}M"
                                        "<br>Operating margin %{color:.0%}<extra></extra>")
        fig.update_layout(coloraxis_colorbar=dict(title="Operating<br>margin", tickformat=".0%"))
        chart(fig, key="fig_tm_tree", height=430)
    with c6:
        stack = s.melt(id_vars="team_name",
                       value_vars=["sponsorship_revenue_usd_m", "prize_money_usd_m"],
                       var_name="Stream", value_name="Value")
        stack["Stream"] = stack["Stream"].map({"sponsorship_revenue_usd_m": "Sponsorship",
                                               "prize_money_usd_m": "Prize money"})
        fig = px.bar(stack, x="Value", y="team_name", color="Stream", orientation="h",
                     color_discrete_map={"Sponsorship": AMBER, "Prize money": TYRE_RED},
                     title=f"Income split by team ({season_pick})")
        fig.add_trace(go.Scatter(x=s["operating_budget_usd_m"], y=s["team_name"], mode="markers",
                                 name="Operating budget", marker=dict(color=WHITE, symbol="line-ns-open",
                                                                      size=16, line=dict(width=3))))
        fig.update_layout(barmode="stack", xaxis_title="Income ($M)", yaxis_title="Team",
                          yaxis={"categoryorder": "total ascending"},
                          legend=dict(orientation="h", y=1.1, title_text=""))
        chart(fig, key="fig_tm_split", height=430)
        top_dep = s.loc[s["Sponsorship share"].idxmax()]
        note(f"Sponsorship carries <b>{top_dep['Sponsorship share']*100:.0f}%</b> of "
             f"{top_dep['team_name']}'s income in {season_pick} — the most commercially exposed team "
             "on the grid that year. The white marks show where each team's budget sits against its income.")

# ═════════════════════════════════════════════════════════════════════════════
# 3 · CIRCUITS
# ═════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    section("What a race weekend costs a host",
            "Hosting fee against the crowd that turns up. The relationship is not what you would expect.")
    c1, c2 = st.columns([3, 2])

    with c1:
        f_reg = multi("Region", sorted(circuits_df["region"].unique()), "ci_region")
        yr = st.slider("Seasons", int(circuits_df["season"].min()), int(circuits_df["season"].max()),
                       (int(circuits_df["season"].min()), int(circuits_df["season"].max())), key="ci_years")
        d = circuits_df[circuits_df["region"].isin(f_reg) & circuits_df["season"].between(*yr)]
        fig = px.scatter(d, x="hosting_fee_usd_m_est", y="weekend_attendance_k",
                         color="Era", symbol="Circuit type", size="Venue age", size_max=18,
                         hover_name="grand_prix", hover_data={"season": True, "circuit": True,
                                                              "Fee per fan": ":$,.0f"},
                         color_discrete_map={"Established": AMBER, "New (post-2020)": PURPLE},
                         trendline="ols", trendline_scope="overall",
                         trendline_color_override=TYRE_RED,
                         title="Hosting fee vs weekend attendance")
        fig.update_layout(xaxis_title="Hosting fee paid to F1 ($M est.)",
                          yaxis_title="Weekend attendance (thousands)",
                          legend=dict(title_text="Venue era / circuit type"))
        fig.update_traces(selector=dict(mode="lines"), name="Overall trend", showlegend=True)
        chart(fig, key="fig_ci_scatter", height=480)
        corr = d["hosting_fee_usd_m_est"].corr(d["weekend_attendance_k"])
        note(f"Correlation between fee and attendance: <b>{corr:.2f}</b>. It runs the wrong way — "
             "the venues paying most are drawing smaller crowds. Fees are set by what a host "
             "government will pay for the exposure, not by ticket demand.")

    with c2:
        cmp_ = circuits_df.groupby("Era").agg(Fee=("hosting_fee_usd_m_est", "mean"),
                                              Attendance=("weekend_attendance_k", "mean"),
                                              Per_fan=("Fee per fan", "median")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=cmp_["Era"], y=cmp_["Fee"], name="Average hosting fee ($M)",
                             marker_color=AMBER, texttemplate="$%{y:.1f}M", textposition="outside",
                             hovertemplate="%{x}<br>Average fee $%{y:.1f}M<extra></extra>"))
        fig.add_trace(go.Bar(x=cmp_["Era"], y=cmp_["Attendance"], name="Average attendance (thousands)",
                             marker_color=TYRE_RED, yaxis="y2", texttemplate="%{y:.0f}k",
                             textposition="outside",
                             hovertemplate="%{x}<br>Average attendance %{y:.0f}k<extra></extra>"))
        fig.update_layout(title="New venues vs established ones", barmode="group",
                          xaxis_title="Venue era",
                          yaxis=dict(title="Average hosting fee ($M)"),
                          yaxis2=dict(title="Average attendance (thousands)", overlaying="y",
                                      side="right", showgrid=False),
                          legend=dict(orientation="h", y=1.14))
        chart(fig, key="fig_ci_era", height=480)
        new = cmp_[cmp_["Era"] == "New (post-2020)"].iloc[0]
        old = cmp_[cmp_["Era"] == "Established"].iloc[0]
        note(f"Post-2020 venues pay <b>{new['Fee']/old['Fee']:.1f}×</b> the fee of established ones "
             f"({money(new['Fee'])} vs {money(old['Fee'])}) while drawing "
             f"{new['Attendance']/old['Attendance']*100:.0f}% of the crowd.")

    c3, c4 = st.columns(2)
    with c3:
        section("Cost per fan through the gate", "Hosting fee divided by attendance, 2020 excluded.")
        f_type = multi("Circuit type", sorted(circuits_df["Circuit type"].unique()), "ci_type")
        d = circuits_df[circuits_df["Circuit type"].isin(f_type)].dropna(subset=["Fee per fan"])
        rank = (d.groupby(["grand_prix", "Circuit type"], as_index=False)["Fee per fan"].median()
                .sort_values("Fee per fan", ascending=False))
        show = pd.concat([rank.head(8), rank.tail(8)])
        fig = px.bar(show, x="Fee per fan", y="grand_prix", orientation="h", color="Fee per fan",
                     color_continuous_scale=HEAT, title="Most and least expensive fans to reach")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, yaxis_title="Grand Prix",
                          xaxis_title="Hosting fee per attendee ($) — median across seasons",
                          coloraxis_showscale=False)
        fig.update_traces(texttemplate="$%{x:,.0f}", textposition="outside",
                          hovertemplate="%{y}<br>$%{x:,.0f} per attendee<extra></extra>")
        chart(fig, key="fig_ci_perfan", height=470)

    with c4:
        section("Where the calendar goes", "Share of rounds by region, season by season.")
        f_type2 = multi("Circuit type", sorted(circuits_df["Circuit type"].unique()), "ci_type2")
        d = circuits_df[circuits_df["Circuit type"].isin(f_type2)]
        reg = d.groupby(["season", "region"]).size().rename("Rounds").reset_index()
        reg["Share"] = reg["Rounds"] / reg.groupby("season")["Rounds"].transform("sum")
        fig = px.area(reg, x="season", y="Share", color="region",
                      color_discrete_sequence=COLORWAY, title="Regional mix of the calendar")
        fig.update_layout(yaxis_tickformat=".0%", xaxis_title="Season",
                          yaxis_title="Share of the season's rounds",
                          legend=dict(orientation="h", y=1.14, title_text="Region"))
        fig.update_traces(hovertemplate="Season %{x}<br>%{y:.0%} of rounds<extra>%{fullData.name}</extra>")
        chart(fig, key="fig_ci_region", height=470)
        eu = reg[reg["region"] == "Europe"].set_index("season")["Share"]
        last_full = audit["last_full"]
        if last_full in eu.index:
            note(f"Europe held {eu.iloc[0]*100:.0f}% of the rounds in {int(eu.index[0])} and "
                 f"{eu.loc[last_full]*100:.0f}% in {last_full}, the last complete season. The "
                 "calendar's centre of gravity has moved east and west of it.")

# ═════════════════════════════════════════════════════════════════════════════
# 4 · ON TRACK
# ═════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    section("Who wins, and how evenly", "Race wins by driver across the period.")
    c1, c2 = st.columns([3, 2])

    with c1:
        f_reg2 = multi("Region", sorted(races_df["region"].unique()), "ot_region")
        d = races_df[races_df["region"].isin(f_reg2)]
        top_n = st.slider("Drivers shown", 4, 12, 8, key="ot_topn")
        top_drivers = d["winner"].value_counts().head(top_n).index
        wins = (d[d["winner"].isin(top_drivers)].groupby(["season", "winner"]).size()
                .rename("Wins").reset_index())
        fig = px.area(wins, x="season", y="Wins", color="winner", line_group="winner",
                      color_discrete_sequence=COLORWAY + px.colors.qualitative.Set3,
                      title="Race wins per season")
        fig.update_layout(xaxis_title="Season", yaxis_title="Race wins that season",
                          legend=dict(orientation="h", y=1.14, title_text="Driver"))
        fig.update_traces(hovertemplate="Season %{x}<br>%{y} wins<extra>%{fullData.name}</extra>")
        chart(fig, key="fig_ot_wins", height=440)

    with c2:
        hhi = races_df.groupby("season")["winner"].apply(
            lambda s: (s.value_counts(normalize=True) ** 2).sum())
        margin = (drivers_df[drivers_df["championship_position"] <= 2]
                  .pivot_table(index="season", columns="championship_position", values="total_points"))
        margin["Margin"] = margin[1] - margin[2]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=margin.index, y=margin["Margin"], name="Title margin (pts)",
                             marker_color="rgba(30,127,214,.5)"))
        fig.add_trace(go.Scatter(x=hhi.index, y=hhi.values, name="Win concentration (HHI)",
                                 yaxis="y2", line=dict(color=AMBER, width=3), mode="lines+markers"))
        fig.update_layout(title="How one-sided was the season?",
                          yaxis=dict(title="Points between P1 and P2"),
                          yaxis2=dict(title="HHI", overlaying="y", side="right", showgrid=False),
                          xaxis_title="Season", legend=dict(orientation="h", y=1.16))
        chart(fig, key="fig_ot_hhi", height=440)
        note(f"Peak dominance is <b>{int(hhi.idxmax())}</b> (HHI {hhi.max():.2f}, title margin "
             f"{margin.loc[hhi.idxmax(),'Margin']:.0f} points). The closest fight on both measures "
             f"is {int(hhi.idxmin())}. HHI of 1.0 would mean one driver won everything.")

    c3, c4 = st.columns(2)
    with c3:
        section("Does pole still matter?", "Share of races won from pole position.")
        f_sprint = multi("Weekend format", sorted(races_df["Sprint weekend"].unique()), "ot_sprint")
        d = races_df[races_df["Sprint weekend"].isin(f_sprint)]
        conv = d.groupby("season").agg(Conversion=("Pole converted", "mean"),
                                       Races=("race_id", "count")).reset_index()
        fig = px.bar(conv, x="season", y="Conversion", color="Conversion",
                     color_continuous_scale=HEAT, text_auto=".0%",
                     title="Pole-to-win conversion")
        fig.add_hline(y=d["Pole converted"].mean(), line_dash="dot", line_color=WHITE,
                      annotation_text="period average", annotation_font_color=MUTED)
        fig.update_layout(yaxis_tickformat=".0%", coloraxis_showscale=False,
                          xaxis_title="Season", yaxis_title="Share of races won from pole")
        fig.update_traces(textposition="outside",
                          hovertemplate="Season %{x}<br>%{y:.0%} of races won from pole<extra></extra>")
        chart(fig, key="fig_ot_pole", height=430)
        note(f"Pole converts to a win <b>{d['Pole converted'].mean()*100:.0f}%</b> of the time across "
             "the period — Saturday buys track position, not the trophy.")

    with c4:
        section("Race disruption", "Safety car periods and the arrival of sprint weekends.")
        f_reg3 = multi("Region", sorted(races_df["region"].unique()), "ot_region3")
        d = races_df[races_df["region"].isin(f_reg3)]
        dis = d.groupby("season").agg(Safety_cars=("safety_car_periods", "mean"),
                                      Sprints=("is_sprint_weekend", "sum")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=dis["season"], y=dis["Sprints"], name="Sprint weekends",
                             marker_color="rgba(180,90,242,.55)"))
        fig.add_trace(go.Scatter(x=dis["season"], y=dis["Safety_cars"], name="Avg safety cars per race",
                                 yaxis="y2", line=dict(color=TYRE_RED, width=3), mode="lines+markers"))
        fig.update_layout(title="Sprints and safety cars", yaxis=dict(title="Sprint weekends"),
                          yaxis2=dict(title="Safety cars per race", overlaying="y", side="right",
                                      showgrid=False),
                          xaxis_title="Season", legend=dict(orientation="h", y=1.16))
        chart(fig, key="fig_ot_disrupt", height=430)

    section("Championship table", "The top of the standings for a chosen season.")
    season_d = st.selectbox("Season", sorted(drivers_df["season"].unique(), reverse=True), key="ot_season")
    sd = drivers_df[drivers_df["season"] == season_d].sort_values("championship_position")
    c5, c6 = st.columns([3, 2])
    with c5:
        fig = px.bar(sd, x="total_points", y="driver_name", orientation="h", color="Champion",
                     color_discrete_map={"Champion": AMBER, "Contender": "#2A3446"},
                     text="total_points", hover_data=["wins", "poles", "podiums_est"],
                     title=f"Points, {season_d}")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, yaxis_title="Driver",
                          xaxis_title="Championship points", showlegend=False)
        fig.update_traces(textposition="outside",
                          hovertemplate="%{y}<br>%{x} points<br>%{customdata[0]} wins · "
                                        "%{customdata[1]} poles · %{customdata[2]} podiums<extra></extra>")
        chart(fig, key="fig_ot_table", height=380)
    with c6:
        fig = px.scatter(sd, x="poles", y="wins", size="total_points", color="driver_name",
                         text="driver_name", size_max=30, custom_data=["total_points"],
                         color_discrete_sequence=COLORWAY + px.colors.qualitative.Set3,
                         title=f"Poles vs wins, {season_d}")
        fig.update_traces(textposition="top center", textfont=dict(size=9, color=MUTED))
        fig.update_layout(showlegend=False, xaxis_title="Pole positions", yaxis_title="Race wins")
        fig.update_traces(hovertemplate="%{text}<br>%{x} poles · %{y} wins<br>"
                                        "%{customdata[0]} championship points<extra></extra>")
        chart(fig, key="fig_ot_pw", height=380)

# ═════════════════════════════════════════════════════════════════════════════
# 5 · CROSS-ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    section("Does money buy the championship?",
            "Team budgets against the constructors' title, season by season.")

    champ = teams_df.copy()
    champ["Budget rank"] = champ.groupby("season")["operating_budget_usd_m"].rank(ascending=False)
    won = champ[champ["is_constructors_champion"] == 1]

    c1, c2 = st.columns([3, 2])
    with c1:
        f_teams2 = multi("Teams", sorted(teams_df["team_name"].unique()), "cx_teams")
        d = champ[champ["team_name"].isin(f_teams2)]
        fig = px.line(d, x="season", y="operating_budget_usd_m", color="team_name",
                      color_discrete_sequence=COLORWAY + px.colors.qualitative.Set3,
                      title="Operating budget by team, with title wins marked")
        fig.update_traces(line=dict(width=2))
        w = won[won["team_name"].isin(f_teams2)]
        fig.add_trace(go.Scatter(x=w["season"], y=w["operating_budget_usd_m"], mode="markers",
                                 name="Constructors' champion",
                                 marker=dict(color=AMBER, size=15, symbol="star",
                                             line=dict(color=ASPHALT, width=1))))
        fig.update_layout(xaxis_title="Season", yaxis_title="Operating budget ($M)",
                          legend=dict(orientation="h", y=-.14, title_text=""))
        chart(fig, key="fig_cx_budget", height=470)
    with c2:
        rank_counts = won["Budget rank"].value_counts().sort_index().reset_index()
        rank_counts.columns = ["Budget rank", "Titles"]
        fig = px.bar(rank_counts, x="Budget rank", y="Titles", color="Titles",
                     color_continuous_scale=HEAT, text_auto=True,
                     title="Where champions ranked on spending")
        fig.update_layout(coloraxis_showscale=False,
                          xaxis_title="Budget rank that season (1 = biggest spender)",
                          yaxis_title="Constructors' titles won")
        fig.update_traces(textposition="outside",
                          hovertemplate="Budget rank %{x}<br>%{y} titles<extra></extra>")
        chart(fig, key="fig_cx_rank", height=470)
        note(f"Of the {len(won)} constructors' titles recorded, "
             f"<b>{int((won['Budget rank'] <= 2).sum())}</b> went to a top-two spender. "
             f"Median rank of a champion: {won['Budget rank'].median():.0f}. "
             "Money is not sufficient, but the title almost never leaves the top of the budget table.")

    section("The sport's revenue against everything else",
            "Season-level series, indexed so shapes can be compared directly.")
    series_map = {
        "Sport revenue ($M)": business_df.set_index("season")["total_revenue_usd_m"],
        "Revenue per race ($M)": business_df.set_index("season")["Revenue per race"],
        "Global race viewers (M)": business_df.set_index("season")["global_avg_race_viewers_m"],
        "Rounds on the calendar": races_df.groupby("season").size(),
        "Avg hosting fee ($M)": circuits_df.groupby("season")["hosting_fee_usd_m_est"].mean(),
        "Avg attendance (k)": circuits_df.groupby("season")["weekend_attendance_k"].mean(),
        "Avg team budget ($M)": teams_df.groupby("season")["operating_budget_usd_m"].mean(),
        "Avg team surplus ($M)": teams_df.groupby("season")["Surplus"].mean(),
        "Win concentration (HHI)": races_df.groupby("season")["winner"].apply(
            lambda s: (s.value_counts(normalize=True) ** 2).sum()),
    }
    picked = st.multiselect("Series", list(series_map), key="cx_series",
                            default=["Sport revenue ($M)", "Avg hosting fee ($M)",
                                     "Avg team budget ($M)", "Global race viewers (M)"])
    picked = picked or ["Sport revenue ($M)", "Avg hosting fee ($M)"]
    idx = pd.DataFrame({k: series_map[k] for k in picked}).sort_index()
    base_year = st.select_slider("Index base year", options=list(idx.index),
                                 value=int(idx.index.min()), key="cx_base")
    indexed = idx / idx.loc[base_year] * 100

    c3, c4 = st.columns([3, 2])
    with c3:
        fig = go.Figure()
        for i, col in enumerate(indexed.columns):
            fig.add_trace(go.Scatter(x=indexed.index, y=indexed[col], name=col, mode="lines+markers",
                                     line=dict(width=3, color=COLORWAY[i % len(COLORWAY)])))
        fig.add_hline(y=100, line_dash="dot", line_color=MUTED)
        fig.update_layout(title=f"Indexed to {base_year} = 100", xaxis_title="Season",
                          yaxis_title=f"Index ({base_year} = 100)",
                          legend=dict(orientation="h", y=1.16, title_text="Series"))
        fig.update_traces(hovertemplate="Season %{x}<br>Index %{y:.0f}<extra>%{fullData.name}</extra>")
        chart(fig, key="fig_cx_index", height=460)
    with c4:
        corr = idx.corr()
        fig = px.imshow(corr, color_continuous_scale=DIVERGING, zmin=-1, zmax=1,
                        text_auto=".2f", aspect="auto", title="Correlation between the series")
        fig.update_layout(xaxis_title="", yaxis_title="",
                          coloraxis_colorbar=dict(title="Correlation"))
        chart(fig, key="fig_cx_corr", height=460)
        note("Correlation across 17 season-level points is suggestive, not causal — most of these "
             "series trend upward together, which inflates every pair.")

# ═════════════════════════════════════════════════════════════════════════════
# 6 · DATA & INTEGRITY
# ═════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    section("What the files actually cover", "Read this before quoting any total.")

    gap = audit["rev_gap_seasons"]
    if not gap.empty:
        rows = ", ".join(f"{int(r['season'])} (off by ${r['Reporting gap']:,.0f}M)"
                         for _, r in gap.iterrows())
        flag(f"<b>Revenue components do not reconcile</b> in {rows}. The four streams in "
             "<code>f1_business.csv</code> sum to more than the reported total, so the headline "
             "figure and the stacked breakdown disagree for those seasons. Every chart here uses "
             "the components as given and does not silently rescale them.")

    if audit["mix_fixed"]:
        sh = audit["mix_shares"]
        flag(f"<b>The revenue breakdown is derived, not measured.</b> Promotion, broadcast, "
             f"sponsorship and other hold a constant "
             f"{sh['race_promotion_fees_usd_m']:.0f}/{sh['broadcast_media_usd_m']:.0f}/"
             f"{sh['sponsorship_usd_m']:.0f}/{sh['other_revenue_usd_m']:.0f} split in all "
             f"{len(business_df)} seasons. Treat the streams as a scaled view of the total; any "
             "claim about one line growing faster than another is not supported by this file.")

    if audit["partial"]:
        flag(f"<b>Season(s) {', '.join(str(y) for y in audit['partial'])} are incomplete</b> — "
             f"{races_df.groupby('season').size().loc[audit['partial']].tolist()} rounds on file "
             "against a full calendar. Season totals for them are not comparable; the last complete "
             f"season is {audit['last_full']}.")

    flag(f"<b>Circuit economics covers {audit['econ_coverage']*100:.0f}% of races</b> "
         f"({audit['races_with_econ']} of {audit['races']}). Coverage is partial before 2022, so "
         "any total built from hosting fees understates those calendars. Per-race averages are safe; "
         "season sums are not.")

    flag(f"<b>Cost cap is blank for {audit['cap_missing']} team-seasons</b> — correctly, since no cap "
         "existed before 2021. It is kept as missing rather than zero. Within the capped seasons, "
         f"{audit['over_cap']} of {audit['cap_rows']} team-budgets sit above the limit, because "
         "operating budget here includes items the regulation excludes.")

    c1, c2 = st.columns(2)
    with c1:
        cov = coverage_df.reset_index()
        fig = px.bar(cov, x="season", y="Coverage", color="Coverage", text_auto=".0%",
                     color_continuous_scale=HEAT, range_color=[0, 1],
                     title="Share of races with circuit economics attached")
        fig.update_layout(yaxis_tickformat=".0%", coloraxis_showscale=False,
                          xaxis_title="Season",
                          yaxis_title="Races with fee & attendance data")
        fig.update_traces(textposition="outside",
                          hovertemplate="Season %{x}<br>%{y:.0%} of races covered<extra></extra>")
        chart(fig, key="fig_dt_cov", height=400)
    with c2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=business_df["season"], y=business_df["total_revenue_usd_m"],
                             name="Reported total", marker_color=AMBER))
        fig.add_trace(go.Scatter(x=business_df["season"], y=business_df["Parts total"],
                                 name="Sum of the four streams", mode="lines+markers",
                                 line=dict(color=TYRE_RED, width=3, dash="dash")))
        fig.update_layout(title="Reported revenue vs its own components",
                          xaxis_title="Season", yaxis_title="Revenue ($M)",
                          legend=dict(orientation="h", y=1.14))
        chart(fig, key="fig_dt_recon", height=400)

    section("Browse and export", "Every table, filtered and downloadable.")
    frames = {"Race results": races_df, "Circuit economics": circuits_df,
              "Constructor finances": teams_df, "Driver standings": drivers_df,
              "Sport P&L": business_df, "Races + circuit economics (joined)": race_econ}
    which = st.selectbox("Table", list(frames), key="dt_which")
    d = frames[which]
    if "season" in d.columns:
        yr = st.slider("Seasons", int(d["season"].min()), int(d["season"].max()),
                       (int(d["season"].min()), int(d["season"].max())), key="dt_years")
        d = d[d["season"].between(*yr)]
    table(d, height=430, key="tbl_dt")
    st.download_button(f"Download {which} (CSV)", d.to_csv(index=False).encode(),
                       file_name=f"{which.lower().replace(' ', '_')}.csv", mime="text/csv")

    section("Cleaning and derivation notes", "Everything this app changed or added.")
    st.markdown(
        f"""
- **No rows dropped.** All {audit['races']} races, {len(circuits_df)} circuit-seasons,
  {len(teams_df)} team-seasons, {len(drivers_df)} standings rows and {len(business_df)} P&L seasons
  are carried through.
- **`cost_cap_limit_usd_m` kept as missing** for pre-2021 seasons instead of being filled with 0.
- **Races joined to circuit economics** on `season` + `grand_prix`; the join is left, and the
  unmatched share is reported above rather than hidden.
- **Derived per team**: surplus (revenue − operating budget), margin, sponsorship share,
  budget-versus-cap.
- **Derived per circuit**: fee per attending fan, venue age, established-versus-new flag.
  Fee per fan is left blank where attendance is under 20k, so closed-door 2020 rounds do not
  produce absurd ratios.
- **Derived per race**: pole-to-win conversion, sprint flag, full podium string.
- **Derived per season**: win concentration (Herfindahl index of winners), title margin,
  revenue per race, year-on-year growth.
"""
    )

st.markdown(
    f"<hr class='rule'><div style='color:{MUTED};font-size:.72rem;font-family:JetBrains Mono,monospace;"
    f"letter-spacing:.12em;text-transform:uppercase;padding-top:.8rem'>"
    f"{audit['seasons'][0]}–{audit['seasons'][1]} · {audit['races']} races · "
    f"{len(teams_df)} team-seasons · {len(circuits_df)} circuit-seasons · "
    f"circuit economics coverage {audit['econ_coverage']*100:.0f}%</div>",
    unsafe_allow_html=True,
)
