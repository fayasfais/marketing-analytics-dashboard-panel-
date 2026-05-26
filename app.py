"""
Marketing Analytics Dashboard
A professional Streamlit dashboard for marketing performance analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
import os

# ── Config ─────────────────────────────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title=os.getenv("APP_TITLE", "Marketing Analytics Dashboard"),
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CURRENCY = os.getenv("CURRENCY_SYMBOL", "$")
DATA_PATH = os.getenv("DATA_PATH", "data/marketing_data.csv")

# ── Colour palette ──────────────────────────────────────────────────────────────
PALETTE = {
    "primary":   "#6366F1",   # indigo
    "secondary": "#EC4899",   # pink
    "success":   "#10B981",   # emerald
    "warning":   "#F59E0B",   # amber
    "info":      "#3B82F6",   # blue
    "channels": ["#6366F1", "#EC4899", "#10B981", "#F59E0B", "#3B82F6"],
    "regions":  ["#8B5CF6", "#F472B6", "#34D399", "#FBBF24", "#60A5FA"],
}

# ── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #1e1b4b 0%, #1e1e2e 100%);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px;
    padding: 24px 28px;
    text-align: left;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366F1, #EC4899);
}
.kpi-label  { color: #94a3b8; font-size: 13px; font-weight: 500; letter-spacing: .05em; text-transform: uppercase; margin-bottom: 6px; }
.kpi-value  { color: #f1f5f9; font-size: 32px; font-weight: 700; line-height: 1; margin-bottom: 6px; }
.kpi-delta  { font-size: 13px; font-weight: 500; }
.kpi-delta.positive { color: #10B981; }
.kpi-delta.negative { color: #f43f5e; }

/* Section headers */
.section-header {
    color: #e2e8f0;
    font-size: 18px;
    font-weight: 600;
    margin: 8px 0 4px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(99,102,241,0.2);
}

/* Sidebar */
section[data-testid="stSidebar"] { background-color: #0f0f1a; }
section[data-testid="stSidebar"] label { color: #94a3b8 !important; }

/* Main background */
.stApp { background-color: #0d0d1a; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Plotly chart backgrounds */
.js-plotly-plot .plotly .svg-container { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Data loading ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df["month"]       = df["date"].dt.to_period("M").astype(str)
    df["week"]        = df["date"].dt.isocalendar().week.astype(int)
    df["roas"]        = (df["revenue"] / df["spend"]).round(2)
    df["cpc"]         = (df["spend"]   / df["clicks"].replace(0, np.nan)).round(2)
    df["cpa"]         = (df["spend"]   / df["conversions"].replace(0, np.nan)).round(2)
    return df

df_full = load_data(DATA_PATH)

# ── Sidebar filters ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")

    # Date range
    min_date = df_full["date"].min().date()
    max_date = df_full["date"].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)

    st.markdown("---")

    # Channel
    channels = sorted(df_full["channel"].unique())
    sel_channels = st.multiselect("Channels", channels, default=channels)

    # Region
    regions = sorted(df_full["region"].unique())
    sel_regions = st.multiselect("Regions", regions, default=regions)

    # Campaign
    campaigns = sorted(df_full["campaign"].unique())
    sel_campaigns = st.multiselect("Campaigns", campaigns, default=campaigns)

    st.markdown("---")
    st.markdown("**Primary Metric**")
    primary_metric = st.selectbox("", ["revenue", "conversions", "clicks", "impressions", "spend"], label_visibility="collapsed")

    st.markdown("---")
    st.caption("Marketing Analytics Dashboard v1.0")

# ── Apply filters ───────────────────────────────────────────────────────────────
if len(date_range) == 2:
    start_d, end_d = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_d, end_d = df_full["date"].min(), df_full["date"].max()

df = df_full[
    (df_full["date"] >= start_d) &
    (df_full["date"] <= end_d) &
    (df_full["channel"].isin(sel_channels)) &
    (df_full["region"].isin(sel_regions)) &
    (df_full["campaign"].isin(sel_campaigns))
].copy()

# ── KPI helpers ─────────────────────────────────────────────────────────────────
def fmt_currency(v): return f"{CURRENCY}{v:,.0f}"
def fmt_number(v):   return f"{v:,.0f}"
def fmt_pct(v):      return f"{v:.2f}%"
def fmt_x(v):        return f"{v:.2f}x"

def kpi_card(label: str, value: str, delta: str | None = None, positive: bool = True) -> str:
    delta_html = ""
    if delta:
        cls = "positive" if positive else "negative"
        arrow = "↑" if positive else "↓"
        delta_html = f'<div class="kpi-delta {cls}">{arrow} {delta}</div>'
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>"""

def section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

# ── Derived KPIs ────────────────────────────────────────────────────────────────
total_revenue    = df["revenue"].sum()
total_spend      = df["spend"].sum()
total_conversions= df["conversions"].sum()
total_clicks     = df["clicks"].sum()
total_impressions= df["impressions"].sum()
avg_roas         = (total_revenue / total_spend) if total_spend > 0 else 0
avg_ctr          = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
avg_cvr          = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
avg_cpa          = (total_spend / total_conversions) if total_conversions > 0 else 0

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<h1 style='color:#f1f5f9; font-size:28px; font-weight:700; margin-bottom:4px;'>
  📊 Marketing Analytics Dashboard
</h1>
<p style='color:#64748b; font-size:14px; margin-bottom:24px;'>
  Real-time insights across channels, campaigns, and regions
</p>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  KPI CARDS — ROW 1
# ══════════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("Total Revenue",    fmt_currency(total_revenue),  "vs previous period", True),  unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Total Spend",      fmt_currency(total_spend),    None),                        unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("Conversions",      fmt_number(total_conversions),"vs previous period", True),  unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("ROAS",             fmt_x(avg_roas),              "return on ad spend", True),  unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

c5, c6, c7, c8 = st.columns(4)
with c5:
    st.markdown(kpi_card("Impressions",      fmt_number(total_impressions), None),                        unsafe_allow_html=True)
with c6:
    st.markdown(kpi_card("Clicks",           fmt_number(total_clicks),      None),                        unsafe_allow_html=True)
with c7:
    st.markdown(kpi_card("Avg. CTR",         fmt_pct(avg_ctr),              None),                        unsafe_allow_html=True)
with c8:
    st.markdown(kpi_card("Avg. CPA",         fmt_currency(avg_cpa),         None),                        unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  REVENUE TREND
# ══════════════════════════════════════════════════════════════════════════════
section("📈 Revenue & Spend Trend")

trend = (df.groupby("month")[["revenue", "spend"]]
           .sum()
           .reset_index()
           .sort_values("month"))
trend["profit"] = trend["revenue"] - trend["spend"]

fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

fig_trend.add_trace(go.Bar(
    x=trend["month"], y=trend["revenue"],
    name="Revenue", marker_color=PALETTE["primary"],
    opacity=0.85,
), secondary_y=False)

fig_trend.add_trace(go.Bar(
    x=trend["month"], y=trend["spend"],
    name="Spend", marker_color=PALETTE["secondary"],
    opacity=0.75,
), secondary_y=False)

fig_trend.add_trace(go.Scatter(
    x=trend["month"], y=trend["profit"],
    name="Profit", mode="lines+markers",
    line=dict(color=PALETTE["success"], width=2.5),
    marker=dict(size=7),
), secondary_y=True)

fig_trend.update_layout(
    barmode="group",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#94a3b8",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=30, b=0),
    height=320,
    xaxis=dict(gridcolor="rgba(99,102,241,0.08)", tickangle=-30),
    yaxis=dict(gridcolor="rgba(99,102,241,0.08)", tickprefix=CURRENCY),
    yaxis2=dict(tickprefix=CURRENCY, showgrid=False),
    hovermode="x unified",
)

st.plotly_chart(fig_trend, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CHANNEL PERFORMANCE  +  CAMPAIGN ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
section("📡 Channel Performance & Campaign Analysis")
col_left, col_right = st.columns(2)

# ── Channel donut ───────────────────────────────────────────────────────────
with col_left:
    ch = (df.groupby("channel")[[primary_metric]]
            .sum()
            .reset_index()
            .sort_values(primary_metric, ascending=False))

    fig_ch = px.pie(
        ch, values=primary_metric, names="channel",
        hole=0.58,
        color_discrete_sequence=PALETTE["channels"],
    )
    fig_ch.update_traces(
        textposition="outside", textinfo="percent+label",
        textfont_size=12,
        marker=dict(line=dict(color="#0d0d1a", width=3)),
    )
    fig_ch.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        height=340,
        title=dict(text=f"Channel Share — {primary_metric.capitalize()}", font_size=14, x=0.01),
        annotations=[dict(
            text=f"<b>{fmt_number(ch[primary_metric].sum())}</b>",
            x=0.5, y=0.5, font_size=16,
            showarrow=False, font_color="#f1f5f9",
        )],
    )
    st.plotly_chart(fig_ch, use_container_width=True)

# ── Campaign horizontal bar ─────────────────────────────────────────────────
with col_right:
    camp = (df.groupby("campaign")[["revenue", "spend", "conversions"]]
              .sum()
              .reset_index())
    camp["roas"] = (camp["revenue"] / camp["spend"]).round(2)
    camp = camp.sort_values("revenue", ascending=True).tail(10)

    fig_camp = go.Figure()
    fig_camp.add_trace(go.Bar(
        x=camp["revenue"], y=camp["campaign"],
        orientation="h", name="Revenue",
        marker=dict(color=PALETTE["primary"], line=dict(width=0)),
    ))
    fig_camp.add_trace(go.Bar(
        x=camp["spend"], y=camp["campaign"],
        orientation="h", name="Spend",
        marker=dict(color=PALETTE["secondary"], line=dict(width=0)),
    ))
    fig_camp.update_layout(
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        legend=dict(orientation="h", y=1.05, x=0),
        margin=dict(l=0, r=20, t=40, b=0),
        height=340,
        xaxis=dict(gridcolor="rgba(99,102,241,0.1)", tickprefix=CURRENCY),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont_size=11),
        title=dict(text="Campaign Revenue vs Spend", font_size=14, x=0.01),
    )
    st.plotly_chart(fig_camp, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CHANNEL METRICS HEATMAP  +  ROAS BAR
# ══════════════════════════════════════════════════════════════════════════════
section("🔥 Channel Metrics Deep Dive")
col_a, col_b = st.columns([3, 2])

with col_a:
    heat_data = (df.groupby(["channel", "month"])["revenue"]
                   .sum()
                   .reset_index())
    heat_pivot = heat_data.pivot(index="channel", columns="month", values="revenue").fillna(0)

    fig_heat = px.imshow(
        heat_pivot,
        color_continuous_scale="Viridis",
        aspect="auto",
        labels=dict(color=f"Revenue ({CURRENCY})"),
    )
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        margin=dict(l=0, r=0, t=40, b=0),
        height=300,
        title=dict(text="Revenue Heatmap — Channel × Month", font_size=14, x=0.01),
        coloraxis_colorbar=dict(tickprefix=CURRENCY, tickfont_color="#94a3b8"),
        xaxis=dict(tickangle=-35),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with col_b:
    roas_ch = (df.groupby("channel").apply(
        lambda x: (x["revenue"].sum() / x["spend"].sum()) if x["spend"].sum() > 0 else 0
    ).reset_index(name="roas").sort_values("roas", ascending=True))

    colors = [PALETTE["success"] if v >= 3 else PALETTE["warning"] if v >= 2 else PALETTE["secondary"]
              for v in roas_ch["roas"]]

    fig_roas = go.Figure(go.Bar(
        x=roas_ch["roas"], y=roas_ch["channel"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.2f}x" for v in roas_ch["roas"]],
        textposition="outside",
        textfont=dict(color="#f1f5f9", size=12),
    ))
    fig_roas.add_vline(x=3, line_dash="dash", line_color=PALETTE["success"], opacity=0.6,
                       annotation_text="Target 3×", annotation_font_color=PALETTE["success"])
    fig_roas.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        margin=dict(l=0, r=60, t=40, b=0),
        height=300,
        xaxis=dict(gridcolor="rgba(99,102,241,0.1)", title="ROAS"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        title=dict(text="ROAS by Channel", font_size=14, x=0.01),
        showlegend=False,
    )
    st.plotly_chart(fig_roas, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  REGIONAL BREAKDOWN
# ══════════════════════════════════════════════════════════════════════════════
section("🌍 Regional Performance")
col_r1, col_r2 = st.columns(2)

with col_r1:
    reg = (df.groupby("region")[["revenue", "spend", "conversions", "impressions"]]
             .sum()
             .reset_index())
    reg["roas"] = (reg["revenue"] / reg["spend"]).round(2)
    reg["cpa"]  = (reg["spend"]  / reg["conversions"]).round(2)

    fig_reg = px.bar(
        reg.sort_values("revenue", ascending=False),
        x="region", y="revenue",
        color="region",
        color_discrete_sequence=PALETTE["regions"],
        text="revenue",
    )
    fig_reg.update_traces(
        texttemplate=f"{CURRENCY}%{{text:,.0f}}",
        textposition="outside",
        textfont_size=11,
        marker_line_width=0,
    )
    fig_reg.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        margin=dict(l=0, r=0, t=40, b=0),
        height=320,
        title=dict(text="Revenue by Region", font_size=14, x=0.01),
        showlegend=False,
        yaxis=dict(gridcolor="rgba(99,102,241,0.1)", tickprefix=CURRENCY),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_reg, use_container_width=True)

with col_r2:
    fig_scatter = px.scatter(
        reg,
        x="spend", y="revenue",
        size="conversions",
        color="region",
        text="region",
        color_discrete_sequence=PALETTE["regions"],
        size_max=50,
        hover_data={"roas": True, "cpa": True},
    )
    fig_scatter.update_traces(
        textposition="top center",
        textfont_size=10,
        marker=dict(opacity=0.85, line=dict(width=1, color="#0d0d1a")),
    )
    # Diagonal break-even line
    max_val = max(reg["spend"].max(), reg["revenue"].max()) * 1.1
    fig_scatter.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val],
        mode="lines", name="Break-even",
        line=dict(color="#64748b", dash="dash", width=1.5),
    ))
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        margin=dict(l=0, r=0, t=40, b=0),
        height=320,
        title=dict(text="Spend vs Revenue Bubble (size = conversions)", font_size=14, x=0.01),
        xaxis=dict(gridcolor="rgba(99,102,241,0.1)", tickprefix=CURRENCY),
        yaxis=dict(gridcolor="rgba(99,102,241,0.1)", tickprefix=CURRENCY),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  FUNNEL + CTR/CVR LINE
# ══════════════════════════════════════════════════════════════════════════════
section("🔁 Conversion Funnel & Rate Trends")
col_f1, col_f2 = st.columns([1, 2])

with col_f1:
    funnel_vals = [
        df["impressions"].sum(),
        df["clicks"].sum(),
        df["conversions"].sum(),
    ]
    fig_funnel = go.Figure(go.Funnel(
        y=["Impressions", "Clicks", "Conversions"],
        x=funnel_vals,
        textinfo="value+percent initial",
        marker=dict(color=[PALETTE["primary"], PALETTE["info"], PALETTE["success"]]),
        connector=dict(line=dict(color="#0d0d1a", width=3)),
    ))
    fig_funnel.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        margin=dict(l=0, r=0, t=40, b=0),
        height=300,
        title=dict(text="Marketing Funnel", font_size=14, x=0.01),
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_f2:
    rate_trend = (df.groupby("month").apply(lambda x: pd.Series({
        "ctr": (x["clicks"].sum() / x["impressions"].sum() * 100) if x["impressions"].sum() > 0 else 0,
        "cvr": (x["conversions"].sum() / x["clicks"].sum() * 100) if x["clicks"].sum() > 0 else 0,
    })).reset_index().sort_values("month"))

    fig_rates = go.Figure()
    fig_rates.add_trace(go.Scatter(
        x=rate_trend["month"], y=rate_trend["ctr"],
        name="CTR (%)", mode="lines+markers",
        line=dict(color=PALETTE["info"], width=2.5),
        marker=dict(size=7), fill="tozeroy", fillcolor=f"rgba(59,130,246,0.08)",
    ))
    fig_rates.add_trace(go.Scatter(
        x=rate_trend["month"], y=rate_trend["cvr"],
        name="CVR (%)", mode="lines+markers",
        line=dict(color=PALETTE["success"], width=2.5),
        marker=dict(size=7), fill="tozeroy", fillcolor=f"rgba(16,185,129,0.08)",
    ))
    fig_rates.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        margin=dict(l=0, r=0, t=40, b=0),
        height=300,
        title=dict(text="CTR & Conversion Rate Trends", font_size=14, x=0.01),
        xaxis=dict(gridcolor="rgba(99,102,241,0.08)", tickangle=-30),
        yaxis=dict(gridcolor="rgba(99,102,241,0.08)", ticksuffix="%"),
        legend=dict(orientation="h", y=1.05, x=0),
        hovermode="x unified",
    )
    st.plotly_chart(fig_rates, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DATA TABLE
# ══════════════════════════════════════════════════════════════════════════════
section("📋 Detailed Data Table")

col_t1, col_t2, col_t3 = st.columns([2, 2, 2])
with col_t1:
    group_by = st.selectbox("Group by", ["None (raw)", "channel", "region", "campaign", "month"])
with col_t2:
    sort_col = st.selectbox("Sort by", ["revenue", "spend", "conversions", "impressions", "roas", "ctr"])
with col_t3:
    sort_dir = st.radio("Order", ["Descending", "Ascending"], horizontal=True)

if group_by == "None (raw)":
    display_df = df[["date","channel","campaign","region","impressions","clicks",
                      "conversions","revenue","spend","roas","ctr","cpa"]].copy()
    display_df = display_df.sort_values(sort_col if sort_col in display_df.columns else "revenue",
                                        ascending=(sort_dir == "Ascending"))
else:
    agg_cols = {
        "impressions":"sum","clicks":"sum","conversions":"sum",
        "revenue":"sum","spend":"sum",
    }
    display_df = df.groupby(group_by).agg(agg_cols).reset_index()
    display_df["roas"] = (display_df["revenue"] / display_df["spend"]).round(2)
    display_df["ctr"]  = (display_df["clicks"]  / display_df["impressions"] * 100).round(2)
    display_df["cpa"]  = (display_df["spend"]   / display_df["conversions"]).round(2)
    col_to_sort = sort_col if sort_col in display_df.columns else "revenue"
    display_df = display_df.sort_values(col_to_sort, ascending=(sort_dir == "Ascending"))

# Format for display
fmt_df = display_df.copy()
for c in ["revenue","spend","cpa"]:
    if c in fmt_df.columns:
        fmt_df[c] = fmt_df[c].apply(lambda v: f"{CURRENCY}{v:,.0f}")
for c in ["impressions","clicks","conversions"]:
    if c in fmt_df.columns:
        fmt_df[c] = fmt_df[c].apply(lambda v: f"{v:,.0f}")
if "roas" in fmt_df.columns:
    fmt_df["roas"] = fmt_df["roas"].apply(lambda v: f"{v:.2f}x")
if "ctr" in fmt_df.columns:
    fmt_df["ctr"] = fmt_df["ctr"].apply(lambda v: f"{v:.2f}%")

st.dataframe(fmt_df, use_container_width=True, height=380)

# Download
csv_bytes = display_df.to_csv(index=False).encode()
st.download_button(
    label="⬇️  Download filtered data as CSV",
    data=csv_bytes,
    file_name="marketing_analytics_export.csv",
    mime="text/csv",
)

# ── Footer ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-top:40px; text-align:center; color:#334155; font-size:12px;'>
  Marketing Analytics Dashboard · Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
