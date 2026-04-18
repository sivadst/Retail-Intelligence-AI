import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats as scipy_stats

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Retail Intelligence AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = ["#4f6ef7", "#8b5cf6", "#06d6a0", "#f59e0b", "#ef4444", "#38bdf8", "#fb923c"]

PLOT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color="#6b7280", size=11),
    margin=dict(l=0, r=0, t=36, b=0),
    xaxis=dict(gridcolor="#1e2540", linecolor="#1e2540", zerolinecolor="#1e2540", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#1e2540", linecolor="#1e2540", zerolinecolor="#1e2540", tickfont=dict(size=10)),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)", font=dict(size=10)),
    hoverlabel=dict(bgcolor="#0d1120", bordercolor="#1e2540", font_size=11, font_family="DM Mono, monospace"),
    title_font=dict(family="Syne, sans-serif", size=14, color="#c7d0f8"),
)

# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --bg:       #060910;
    --surface:  #0b0f1e;
    --surface2: #0f1526;
    --border:   #1a2040;
    --border2:  #222b4a;
    --a1:       #4f6ef7;
    --a2:       #8b5cf6;
    --a3:       #06d6a0;
    --text:     #dde3f8;
    --text2:    #8892b8;
    --muted:    #4a5270;
    --warn:     #f59e0b;
    --danger:   #ef4444;
    --success:  #06d6a0;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stHeader"], [data-testid="stDecoration"] { display: none !important; }
#MainMenu, footer { display: none !important; }
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--a1); border-radius: 2px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: 'DM Mono', monospace !important; }
[data-testid="stSidebar"] label { color: var(--text2) !important; font-size: 11px !important; letter-spacing: 1px; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: rgba(79,110,247,0.2) !important; color: var(--a1) !important;
    border: 1px solid rgba(79,110,247,0.3) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div {
    background: var(--surface2) !important; border-color: var(--border2) !important; color: var(--text) !important;
}
.sidebar-header {
    font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 700;
    color: var(--text); letter-spacing: 2px; text-transform: uppercase;
    padding: 4px 0 16px; border-bottom: 1px solid var(--border); margin-bottom: 20px;
}
.sidebar-section { font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--muted); margin: 20px 0 8px; }
.filter-badge {
    display: inline-block; background: rgba(79,110,247,0.12);
    border: 1px solid rgba(79,110,247,0.25); color: var(--a1);
    font-size: 9px; padding: 2px 8px; border-radius: 100px; letter-spacing: 1px; margin-top: 4px;
}

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #0b0f1e 0%, #0f163a 45%, #130c2e 100%);
    border: 1px solid var(--border); border-radius: 16px; padding: 36px 48px; margin-bottom: 8px;
    position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -100px; right: -60px; width: 360px; height: 360px;
    background: radial-gradient(circle, rgba(79,110,247,0.13) 0%, transparent 65%); pointer-events: none;
}
.hero::after {
    content: ''; position: absolute; bottom: -80px; left: 25%; width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 65%); pointer-events: none;
}
.hero-eyebrow { font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: var(--a1); margin-bottom: 8px; }
.hero-title {
    font-family: 'Syne', sans-serif; font-size: 38px; font-weight: 800;
    background: linear-gradient(90deg, #fff 0%, #a5b4fc 55%, #c4b5fd 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; margin: 0;
}
.hero-sub { font-size: 12px; color: var(--muted); margin-top: 8px; letter-spacing: 2px; }
.hero-meta { display: flex; gap: 16px; margin-top: 18px; align-items: center; flex-wrap: wrap; }
.hero-badge {
    background: rgba(79,110,247,0.12); border: 1px solid rgba(79,110,247,0.28);
    color: var(--a1); font-size: 9px; letter-spacing: 2px; padding: 3px 10px; border-radius: 100px;
}
.hero-stat { font-size: 11px; color: var(--muted); }
.hero-stat strong { color: var(--text2); }

/* ── Section heading ── */
.section-head { display: flex; align-items: center; gap: 10px; margin: 28px 0 16px; }
.section-num { font-size: 9px; letter-spacing: 2px; color: var(--a1); border: 1px solid rgba(79,110,247,0.25); padding: 2px 7px; border-radius: 4px; }
.section-title { font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 700; color: var(--text2); letter-spacing: 1px; text-transform: uppercase; }
.section-line { flex: 1; height: 1px; background: var(--border); }

/* ── Metric cards ── */
.metric-card {
    background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
    padding: 22px 24px 18px; position: relative; overflow: hidden;
    transition: border-color 0.25s, box-shadow 0.25s;
}
.metric-card:hover { border-color: rgba(79,110,247,0.5); box-shadow: 0 0 24px rgba(79,110,247,0.08); }
.metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.mc-blue::before   { background: linear-gradient(90deg, #4f6ef7, transparent); }
.mc-purple::before { background: linear-gradient(90deg, #8b5cf6, transparent); }
.mc-green::before  { background: linear-gradient(90deg, #06d6a0, transparent); }
.mc-red::before    { background: linear-gradient(90deg, #ef4444, transparent); }
.mc-amber::before  { background: linear-gradient(90deg, #f59e0b, transparent); }
.metric-icon { font-size: 18px; margin-bottom: 10px; opacity: 0.7; }
.metric-label { font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 700; color: var(--text); line-height: 1; }
.metric-sub { font-size: 10px; color: var(--muted); margin-top: 6px; }
.metric-delta { font-size: 10px; padding: 1px 7px; border-radius: 100px; display: inline-block; margin-top: 6px; }
.delta-pos { background: rgba(6,214,160,0.1); color: var(--success); }
.delta-neg { background: rgba(239,68,68,0.1); color: var(--danger); }

/* ── Executive Summary ── */
.exec-summary {
    background: linear-gradient(135deg, #0b0f22 0%, #10142e 100%);
    border: 1px solid var(--border2); border-radius: 16px; padding: 28px 32px; margin-bottom: 8px;
    position: relative; overflow: hidden;
}
.exec-summary::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--a1), var(--a2));
}
.exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; }
.exec-block-label { font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--muted); margin-bottom: 10px; }
.exec-summary-text { font-size: 13px; color: var(--text2); line-height: 1.8; }
.exec-critical {
    background: rgba(239,68,68,0.07); border: 1px solid rgba(239,68,68,0.2);
    border-radius: 10px; padding: 14px 16px;
}
.exec-critical-label { font-size: 9px; letter-spacing: 2px; color: var(--danger); text-transform: uppercase; margin-bottom: 6px; }
.exec-critical-text { font-size: 12px; color: #f8a0a0; line-height: 1.6; }
.exec-action-item {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 8px 0; border-bottom: 1px solid var(--border);
}
.exec-action-item:last-child { border-bottom: none; }
.exec-action-num { font-family: 'Syne', sans-serif; font-size: 11px; color: var(--a1); font-weight: 700; flex-shrink: 0; margin-top: 1px; }
.exec-action-text { font-size: 11px; color: var(--text2); line-height: 1.55; }

/* ── Health Score ── */
.health-card {
    background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
    padding: 28px 28px 24px; text-align: center; position: relative; overflow: hidden;
}
.health-score-ring {
    width: 120px; height: 120px; margin: 0 auto 16px;
    position: relative; display: flex; align-items: center; justify-content: center;
}
.health-score-num {
    font-family: 'Syne', sans-serif; font-size: 36px; font-weight: 800;
    line-height: 1; position: relative; z-index: 1;
}
.health-label { font-size: 9px; letter-spacing: 3px; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
.health-status {
    font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; margin-top: 4px;
}
.health-breakdown { margin-top: 16px; }
.health-sub-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 5px 0; border-bottom: 1px solid var(--border); font-size: 10px;
}
.health-sub-row:last-child { border-bottom: none; }
.health-sub-label { color: var(--muted); letter-spacing: 1px; }
.health-sub-score { font-weight: 600; }

/* ── Predictive insight ── */
.predict-card {
    background: linear-gradient(135deg, rgba(139,92,246,0.07) 0%, rgba(79,110,247,0.05) 100%);
    border: 1px solid rgba(139,92,246,0.22); border-radius: 16px;
    padding: 24px 28px; position: relative; overflow: hidden;
}
.predict-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--a2), var(--a1));
}
.predict-label { font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--a2); margin-bottom: 14px; }
.predict-value { font-family: 'Syne', sans-serif; font-size: 30px; font-weight: 800; color: var(--text); line-height: 1; }
.predict-sub { font-size: 11px; color: var(--muted); margin-top: 6px; line-height: 1.6; }
.predict-trend { font-size: 11px; margin-top: 12px; padding: 8px 12px; border-radius: 8px; }
.trend-up   { background: rgba(6,214,160,0.08); color: var(--success); border: 1px solid rgba(6,214,160,0.2); }
.trend-down { background: rgba(239,68,68,0.08); color: var(--danger);  border: 1px solid rgba(239,68,68,0.2); }
.trend-flat { background: rgba(245,158,11,0.08); color: var(--warn);   border: 1px solid rgba(245,158,11,0.2); }

/* ── What-If panel ── */
.whatif-card {
    background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 24px 28px;
}
.whatif-title { font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 700; color: var(--text2); letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }
.whatif-sub { font-size: 10px; color: var(--muted); margin-bottom: 16px; }
.compare-row {
    display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 14px;
}
.compare-box { background: var(--surface2); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }
.compare-box.highlight { border-color: rgba(79,110,247,0.35); background: rgba(79,110,247,0.06); }
.compare-label { font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
.compare-value { font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 700; color: var(--text); }
.compare-sub { font-size: 10px; color: var(--muted); margin-top: 3px; }
.compare-delta { font-size: 11px; margin-top: 8px; padding: 3px 9px; border-radius: 100px; display: inline-block; }

/* ── Insight strip ── */
.insight-strip {
    background: linear-gradient(135deg, rgba(79,110,247,0.07) 0%, rgba(139,92,246,0.05) 100%);
    border: 1px solid rgba(79,110,247,0.18); border-radius: 14px; padding: 18px 22px; margin-bottom: 10px;
    display: flex; align-items: flex-start; gap: 14px;
}
.insight-icon { font-size: 20px; flex-shrink: 0; margin-top: 2px; }
.insight-body { flex: 1; }
.insight-tag { font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--a1); margin-bottom: 4px; }
.insight-text { font-size: 12px; color: var(--text2); line-height: 1.65; }
.insight-strip.critical { background: rgba(239,68,68,0.06); border-color: rgba(239,68,68,0.22); border-left: 3px solid var(--danger); }
.insight-strip.critical .insight-tag { color: var(--danger); }
.insight-strip.warn { background: rgba(245,158,11,0.06); border-color: rgba(245,158,11,0.22); border-left: 3px solid var(--warn); }
.insight-strip.warn .insight-tag { color: var(--warn); }
.insight-strip.ok { background: rgba(6,214,160,0.05); border-color: rgba(6,214,160,0.2); border-left: 3px solid var(--success); }
.insight-strip.ok .insight-tag { color: var(--success); }
.insight-strip.pinned {
    background: linear-gradient(135deg, rgba(239,68,68,0.09) 0%, rgba(139,92,246,0.06) 100%);
    border: 2px solid rgba(239,68,68,0.35); border-left: 4px solid var(--danger);
    box-shadow: 0 0 32px rgba(239,68,68,0.08);
}
.insight-strip.pinned .insight-tag { color: var(--danger); font-size: 10px; }
.insight-strip.pinned .insight-text { font-size: 13px; color: var(--text); }

/* ── Chart wrapper ── */
.chart-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 20px 20px 8px; }
.chart-title { font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; color: var(--text2); letter-spacing: 1px; text-transform: uppercase; margin-bottom: 3px; }
.chart-sub { font-size: 10px; color: var(--muted); margin-bottom: 10px; }

/* ── Alert box ── */
.alert-box { background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.22); border-left: 3px solid var(--warn); border-radius: 10px; padding: 14px 18px; margin-bottom: 8px; }
.alert-title { font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; color: var(--warn); margin-bottom: 3px; }
.alert-body { font-size: 11px; color: var(--muted); line-height: 1.65; }

/* ── Rec card ── */
.rec-card {
    background: linear-gradient(135deg, rgba(79,110,247,0.06) 0%, rgba(139,92,246,0.04) 100%);
    border: 1px solid rgba(79,110,247,0.18); border-radius: 12px; padding: 18px 22px; margin-bottom: 10px;
    position: relative; overflow: hidden;
}
.rec-card::after {
    content: attr(data-num); position: absolute; right: 18px; top: 50%; transform: translateY(-50%);
    font-family: 'Syne', sans-serif; font-size: 52px; font-weight: 800;
    color: rgba(79,110,247,0.06); line-height: 1; pointer-events: none;
}
.rec-tag { font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--a1); border: 1px solid rgba(79,110,247,0.25); padding: 2px 8px; border-radius: 100px; display: inline-block; margin-bottom: 7px; }
.rec-text { font-size: 12px; color: var(--text2); line-height: 1.7; max-width: 92%; }

/* ── Upload ── */
[data-testid="stFileUploader"] { background: var(--surface) !important; border: 1px dashed var(--border2) !important; border-radius: 10px !important; }
[data-testid="stFileUploader"]:hover { border-color: var(--a1) !important; }
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* ── Footer ── */
.footer { margin-top: 52px; padding-top: 20px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
.footer-text { font-size: 10px; color: var(--muted); letter-spacing: 1.5px; }

.js-plotly-plot .plotly, .js-plotly-plot .plotly .main-svg { background: transparent !important; }

/* Slider overrides */
[data-testid="stSlider"] > div > div > div > div { background: var(--a1) !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def make_sample() -> pd.DataFrame:
    np.random.seed(42)
    n = 400
    cats    = ["Electronics", "Furniture", "Clothing", "Food & Bev", "Sports"]
    regions = ["North", "South", "East", "West"]
    df = pd.DataFrame({
        "Category": np.random.choice(cats, n),
        "Region":   np.random.choice(regions, n),
        "Sales":    np.random.uniform(50, 2500, n).round(2),
        "Profit":   np.random.uniform(-250, 900, n).round(2),
        "Discount": np.random.uniform(0, 0.65, n).round(3),
        "Quantity": np.random.randint(1, 25, n),
        "Month":    np.random.randint(1, 13, n),
    })
    mask = df["Discount"] > 0.35
    df.loc[mask, "Profit"] -= df.loc[mask, "Sales"] * 0.45
    return df


def load_data(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    df.columns = [c.strip().title().replace(" ", "_") for c in df.columns]
    return df


def validate(df: pd.DataFrame):
    missing = {"Sales", "Profit", "Discount", "Category"} - set(df.columns)
    if missing:
        st.error(f"Missing required columns: {missing}")
        st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# CORE STATS
# ═══════════════════════════════════════════════════════════════════════════════
def compute_stats(df: pd.DataFrame) -> dict:
    total_sales  = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    n            = len(df)
    loss_txns    = int((df["Profit"] < 0).sum())
    return dict(
        total_sales  = total_sales,
        total_profit = total_profit,
        n            = n,
        loss_txns    = loss_txns,
        avg_discount = df["Discount"].mean(),
        margin       = total_profit / total_sales * 100 if total_sales else 0,
        loss_pct     = loss_txns / n * 100 if n else 0,
        avg_order    = total_sales / n if n else 0,
        hd_loss      = df[(df["Discount"] > 0.35) & (df["Profit"] < 0)],
        worst_cat    = df.groupby("Category")["Profit"].sum().idxmin(),
        best_cat     = df.groupby("Category")["Profit"].sum().idxmax(),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH SCORE
# ═══════════════════════════════════════════════════════════════════════════════
def compute_health_score(s: dict) -> dict:
    # Margin component (0–40 pts): 20%+ margin = 40, 0% = 0
    margin_score = min(40, max(0, s["margin"] / 20 * 40))
    # Loss rate component (0–35 pts): 0% loss = 35, 50%+ = 0
    loss_score   = min(35, max(0, (1 - s["loss_pct"] / 50) * 35))
    # Discount discipline (0–25 pts): avg disc <= 0.2 = 25, 0.6+ = 0
    disc_score   = min(25, max(0, (1 - s["avg_discount"] / 0.6) * 25))

    total = int(margin_score + loss_score + disc_score)
    if total >= 70:
        status, color = "Healthy",  "#06d6a0"
    elif total >= 40:
        status, color = "At Risk",  "#f59e0b"
    else:
        status, color = "Critical", "#ef4444"

    return dict(
        score         = total,
        status        = status,
        color         = color,
        margin_score  = int(margin_score),
        loss_score    = int(loss_score),
        disc_score    = int(disc_score),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PREDICTIVE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
def compute_prediction(df: pd.DataFrame, s: dict) -> dict:
    """Simple OLS: profit ~ discount. Predicts profit at current avg discount trend."""
    x = df["Discount"].values
    y = df["Profit"].values
    slope, intercept, r, p_val, _ = scipy_stats.linregress(x, y)

    # Project: if average discount drifts +2pp next period
    future_disc = s["avg_discount"] + 0.02
    pred_avg_profit_per_order = intercept + slope * future_disc
    pred_total_profit = pred_avg_profit_per_order * s["n"]
    pred_margin = pred_total_profit / s["total_sales"] * 100 if s["total_sales"] else 0

    delta = pred_total_profit - s["total_profit"]
    direction = "up" if delta > 0 else "down" if delta < -0.01 * abs(s["total_profit"]) else "flat"

    return dict(
        pred_profit  = pred_total_profit,
        pred_margin  = pred_margin,
        delta        = delta,
        direction    = direction,
        r_squared    = r ** 2,
        slope        = slope,
        future_disc  = future_disc,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# WHAT-IF SIMULATION
# ═══════════════════════════════════════════════════════════════════════════════
def simulate(df: pd.DataFrame, s: dict, new_disc_cap: float, price_uplift: float) -> dict:
    """Simulate impact of capping discounts and applying a price uplift."""
    df_sim = df.copy()

    # Cap discounts: orders above cap are set to cap, profit recovered proportionally
    excess = (df_sim["Discount"] - new_disc_cap).clip(lower=0)
    df_sim["Profit"] = df_sim["Profit"] + excess * df_sim["Sales"]

    # Price uplift: increases sales and profit proportionally
    df_sim["Sales"]  = df_sim["Sales"]  * (1 + price_uplift / 100)
    df_sim["Profit"] = df_sim["Profit"] * (1 + price_uplift / 100)

    sim_profit = df_sim["Profit"].sum()
    sim_sales  = df_sim["Sales"].sum()
    sim_margin = sim_profit / sim_sales * 100 if sim_sales else 0

    return dict(
        sim_profit = sim_profit,
        sim_sales  = sim_sales,
        sim_margin = sim_margin,
        profit_delta = sim_profit - s["total_profit"],
        margin_delta = sim_margin - s["margin"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
def build_executive_summary(s: dict, health: dict, pred: dict) -> dict:
    margin   = s["margin"]
    loss_pct = s["loss_pct"]
    hd_loss  = s["hd_loss"]
    recoverable = abs(hd_loss["Profit"].sum())

    # Narrative
    health_phrase = {"Healthy": "operating within healthy parameters",
                     "At Risk": "showing early warning signs",
                     "Critical": "in a critical state requiring immediate action"}[health["status"]]
    summary = (
        f"The portfolio of <strong>{s['n']:,} transactions</strong> is {health_phrase} "
        f"with a current net margin of <strong>{margin:.1f}%</strong>. "
        f"Net profit stands at <strong>${s['total_profit']:,.0f}</strong> across "
        f"<strong>${s['total_sales']:,.0f}</strong> in total sales. "
        f"<strong>{loss_pct:.1f}%</strong> of orders are loss-generating, "
        f"and the average discount rate of <strong>{s['avg_discount']*100:.1f}%</strong> "
        f"{'exceeds the recommended 25% ceiling' if s['avg_discount'] > 0.25 else 'is within acceptable range'}."
    )

    # Critical issue
    if len(hd_loss) > 0:
        critical = (f"{len(hd_loss)} transactions are generating negative profit at "
                    f">35% discount — representing <strong>${recoverable:,.0f}</strong> in recoverable losses.")
    elif loss_pct > 30:
        critical = f"Over {loss_pct:.0f}% of all orders are unprofitable — systemic pricing failure."
    elif margin < 5:
        critical = f"Portfolio margin of {margin:.1f}% is critically thin — one adverse quarter risks insolvency."
    else:
        critical = f"No single critical issue detected. Primary focus should be margin optimisation."

    # Prioritised actions
    actions = []
    if len(hd_loss) > 0:
        actions.append(f"Cap all discounts at 25% to recover an estimated <strong>${recoverable:,.0f}</strong> in profit.")
    if loss_pct > 15:
        actions.append(f"Audit {int(s['loss_txns']):,} loss-generating orders and enforce minimum-margin rules.")
    actions.append(f"Scale <strong>{s['best_cat']}</strong> inventory — your highest-margin category.")
    if margin < 15:
        actions.append(f"Review <strong>{s['worst_cat']}</strong> pricing strategy — lowest margin segment.")

    return dict(summary=summary, critical=critical, actions=actions[:3])


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS / RENDERERS
# ═══════════════════════════════════════════════════════════════════════════════
def section(num: str, title: str):
    st.markdown(f"""
    <div class="section-head">
        <span class="section-num">{num}</span>
        <span class="section-title">{title}</span>
        <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)


def metric_card(label, value, sub, color, icon, delta=None, delta_pos=True):
    delta_html = (f'<span class="metric-delta {"delta-pos" if delta_pos else "delta-neg"}">{delta}</span>'
                  if delta else "")
    return f"""
    <div class="metric-card mc-{color}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{sub}</div>
        {delta_html}
    </div>"""


def insight_strip(tag, text, kind="info", icon="💡"):
    return f"""
    <div class="insight-strip {kind}">
        <div class="insight-icon">{icon}</div>
        <div class="insight-body">
            <div class="insight-tag">{tag}</div>
            <div class="insight-text">{text}</div>
        </div>
    </div>"""


def apply_plot(fig, **kwargs):
    fig.update_layout(**{**PLOT_BASE, **kwargs})
    return fig


def render_health_gauge(score: int, color: str, status: str):
    """SVG donut gauge for health score."""
    pct  = score / 100
    r    = 52
    circ = 2 * np.pi * r
    dash = pct * circ
    gap  = circ - dash
    # background ring color
    bg_color = "#1a2040"
    svg = f"""
    <div class="health-score-ring">
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="{r}" fill="none" stroke="{bg_color}" stroke-width="10"/>
        <circle cx="60" cy="60" r="{r}" fill="none" stroke="{color}" stroke-width="10"
          stroke-dasharray="{dash:.1f} {gap:.1f}"
          stroke-dashoffset="{circ/4:.1f}"
          stroke-linecap="round"
          style="transition: stroke-dasharray 0.8s ease;"/>
      </svg>
      <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center;">
        <div class="health-score-num" style="color:{color}">{score}</div>
        <div style="font-size:8px; letter-spacing:1px; color:var(--muted); margin-top:2px;">/ 100</div>
      </div>
    </div>
    <div class="health-status" style="color:{color}">{status}</div>"""
    return svg


# ═══════════════════════════════════════════════════════════════════════════════
# CHARTS
# ═══════════════════════════════════════════════════════════════════════════════
def chart_sales_by_category(df: pd.DataFrame):
    cat = df.groupby("Category")["Sales"].sum().reset_index().sort_values("Sales")
    fig = go.Figure(go.Bar(
        x=cat["Sales"], y=cat["Category"], orientation="h",
        marker=dict(color=cat["Sales"], colorscale=[[0, "#1a2040"], [0.5, "#4f6ef7"], [1, "#8b5cf6"]], line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.0f}<extra></extra>",
        text=[f"${v:,.0f}" for v in cat["Sales"]], textposition="outside", textfont=dict(size=10, color="#6b7280"),
    ))
    apply_plot(fig, title="Sales by Category", bargap=0.32, xaxis=dict(**PLOT_BASE["xaxis"], showgrid=False))
    fig.update_yaxes(tickfont=dict(size=11, color="#8892b8"))
    return fig


def chart_discount_profit(df: pd.DataFrame):
    fig = px.scatter(df, x="Discount", y="Profit", color="Category",
                     opacity=0.65, color_discrete_sequence=PALETTE, custom_data=["Category", "Sales"])
    fig.update_traces(
        marker=dict(size=7, line=dict(width=0.5, color="rgba(0,0,0,0.3)")),
        hovertemplate="<b>%{customdata[0]}</b><br>Discount: %{x:.1%}<br>Profit: $%{y:,.0f}<extra></extra>",
    )
    # Regression line
    x = df["Discount"].values
    y = df["Profit"].values
    slope, intercept, *_ = scipy_stats.linregress(x, y)
    xr = np.linspace(x.min(), x.max(), 80)
    yr = intercept + slope * xr
    fig.add_trace(go.Scatter(x=xr, y=yr, mode="lines", name="Trend",
                             line=dict(color="rgba(139,92,246,0.55)", width=2, dash="dot"),
                             hoverinfo="skip"))
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(239,68,68,0.45)", line_width=1.5,
                  annotation_text="Break-even", annotation_font_size=9,
                  annotation_font_color="rgba(239,68,68,0.6)")
    apply_plot(fig, title="Discount vs Profit", xaxis=dict(**PLOT_BASE["xaxis"], tickformat=".0%"))
    return fig


def chart_profit_by_category(df: pd.DataFrame):
    cat = df.groupby("Category")["Profit"].sum().reset_index().sort_values("Profit")
    colors = [PALETTE[4] if v < 0 else PALETTE[0] for v in cat["Profit"]]
    fig = go.Figure(go.Bar(
        x=cat["Profit"], y=cat["Category"], orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.0f}<extra></extra>",
        text=[f"${v:,.0f}" for v in cat["Profit"]], textposition="outside", textfont=dict(size=10, color="#6b7280"),
    ))
    apply_plot(fig, title="Profit by Category", bargap=0.32, xaxis=dict(**PLOT_BASE["xaxis"], showgrid=False))
    fig.add_vline(x=0, line_color="rgba(255,255,255,0.08)", line_width=1)
    fig.update_yaxes(tickfont=dict(size=11, color="#8892b8"))
    return fig


def chart_discount_distribution(df: pd.DataFrame):
    fig = px.histogram(df, x="Discount", nbins=20, color_discrete_sequence=["#4f6ef7"], opacity=0.8)
    fig.add_vline(x=0.35, line_dash="dot", line_color="rgba(239,68,68,0.5)",
                  annotation_text="Risk (35%)", annotation_font_size=9,
                  annotation_font_color="rgba(239,68,68,0.7)")
    apply_plot(fig, title="Discount Distribution", xaxis=dict(**PLOT_BASE["xaxis"], tickformat=".0%"), bargap=0.05)
    fig.update_traces(marker_line_width=0)
    return fig


def chart_whatif_comparison(s: dict, sim: dict):
    cats    = ["Current", "Simulated"]
    profits = [s["total_profit"], sim["sim_profit"]]
    margins = [s["margin"], sim["sim_margin"]]
    colors  = [PALETTE[0], PALETTE[2] if sim["sim_profit"] > s["total_profit"] else PALETTE[4]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cats, y=profits, name="Net Profit",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"${v:,.0f}" for v in profits], textposition="outside",
        textfont=dict(size=11, color="#8892b8"),
        hovertemplate="%{x}<br>Profit: $%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=cats, y=margins, name="Margin %", yaxis="y2", mode="markers+lines",
        marker=dict(size=10, color=PALETTE[1]), line=dict(color=PALETTE[1], width=2, dash="dot"),
        hovertemplate="%{x}<br>Margin: %{y:.1f}%<extra></extra>",
    ))
    apply_plot(fig, title="Current vs Simulated",
               yaxis2=dict(overlaying="y", side="right", tickformat=".1f", ticksuffix="%",
                           gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, color=PALETTE[1])),
               bargap=0.45, legend=dict(orientation="h", y=-0.12))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════
def generate_insights(df: pd.DataFrame, s: dict) -> list:
    insights = []
    hd_loss     = s["hd_loss"]
    recoverable = abs(hd_loss["Profit"].sum())

    if len(hd_loss) > 0:
        insights.append(dict(kind="critical", icon="🔴", tag="Critical · Discount–Loss Correlation",
            text=f"<strong>{len(hd_loss)} transactions</strong> ({len(hd_loss)/s['n']*100:.1f}%) exceed 35% discount "
                 f"and generate negative profit. Capping at 25% could recover <strong>${recoverable:,.0f}</strong>."))
    elif s["loss_pct"] > 25:
        insights.append(dict(kind="critical", icon="🔴", tag="Critical · High Loss Rate",
            text=f"<strong>{s['loss_pct']:.1f}%</strong> of all transactions are unprofitable — exceeds the 25% threshold."))

    if s["margin"] < 10:
        insights.append(dict(kind="warn", icon="🟡", tag="Warning · Thin Margin",
            text=f"Overall margin is <strong>{s['margin']:.1f}%</strong>, below the 15–20% benchmark. "
                 f"Review <strong>{s['worst_cat']}</strong>, your weakest category."))
    else:
        insights.append(dict(kind="ok", icon="🟢", tag="Healthy · Margin",
            text=f"Overall margin is <strong>{s['margin']:.1f}%</strong>. "
                 f"<strong>{s['best_cat']}</strong> leads performance — consider scaling its allocation."))

    if s["loss_pct"] > 15:
        insights.append(dict(kind="warn", icon="🟡", tag="Warning · Loss Concentration",
            text=f"<strong>{int(s['loss_txns']):,} orders</strong> ({s['loss_pct']:.1f}%) are running at a loss. "
                 f"Segment by rep, region, and discount tier."))

    insights.append(dict(kind="info", icon="📈", tag="Opportunity · Top Performer",
        text=f"<strong>{s['best_cat']}</strong> generates the highest total profit. "
             f"Increasing allocation here is likely your highest-ROI lever."))
    return insights


def generate_recs(s: dict) -> list:
    hd_loss     = s["hd_loss"]
    recoverable = abs(hd_loss["Profit"].sum())
    return [
        dict(num="01", tag="Discount Guardrail",
             text=f"Enforce a hard <strong>25% discount ceiling</strong> in your POS/ERP. "
                  f"{len(hd_loss)} loss-generating high-discount orders detected — "
                  f"estimated recoverable profit: <strong>${recoverable:,.0f}</strong>."),
        dict(num="02", tag="Category Rebalancing",
             text=f"Reallocate budget away from <strong>{s['worst_cat']}</strong> (lowest margin) toward "
                  f"<strong>{s['best_cat']}</strong>. A 10% shift compounds significantly over a quarter."),
        dict(num="03", tag="Loss Transaction Audit",
             text=f"Flag all <strong>{int(s['loss_txns']):,}</strong> loss transactions for review. "
                  f"Cross-segment by region, rep, and discount tier. Implement minimum-margin guardrails."),
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════════════════════════

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">⚡ Decision Engine v4.0</div>
    <h1 class="hero-title">Retail Intelligence AI</h1>
    <div class="hero-sub">Detect &nbsp;·&nbsp; Analyze &nbsp;·&nbsp; Decide</div>
    <div class="hero-meta">
        <span class="hero-badge">EXECUTIVE INTELLIGENCE LAYER</span>
        <span class="hero-badge">WHAT-IF SIMULATION</span>
        <span class="hero-badge">PREDICTIVE ENGINE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Data load ─────────────────────────────────────────────────────────────────
section("01", "Data Source")
uploaded = st.file_uploader("Upload your retail CSV dataset", type=["csv"], label_visibility="collapsed")
if uploaded:
    df_raw = load_data(uploaded)
    validate(df_raw)
    st.success(f"✓ Loaded **{len(df_raw):,}** rows · {df_raw.shape[1]} columns", icon="📊")
else:
    df_raw = make_sample()
    st.info("Using demo dataset (400 rows). Upload a CSV with Sales, Profit, Discount, Category columns.", icon="ℹ️")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙ Filters</div>', unsafe_allow_html=True)
    categories = sorted(df_raw["Category"].unique().tolist())
    sel_cats = st.multiselect("Category", categories, default=categories, placeholder="All categories")

    st.markdown('<div class="sidebar-section">Discount Range</div>', unsafe_allow_html=True)
    d_min, d_max = float(df_raw["Discount"].min()), float(df_raw["Discount"].max())
    disc_range = st.slider("Discount", d_min, d_max, (d_min, d_max), format="%.2f", label_visibility="collapsed")

    st.markdown('<div class="sidebar-section">Profit Range</div>', unsafe_allow_html=True)
    p_min, p_max = float(df_raw["Profit"].min()), float(df_raw["Profit"].max())
    prof_range = st.slider("Profit", p_min, p_max, (p_min, p_max), format="$%.0f", label_visibility="collapsed")

    has_region = "Region" in df_raw.columns
    if has_region:
        st.markdown('<div class="sidebar-section">Region</div>', unsafe_allow_html=True)
        regions = sorted(df_raw["Region"].unique().tolist())
        sel_regions = st.multiselect("Region", regions, default=regions, placeholder="All regions", label_visibility="collapsed")
    else:
        sel_regions = None

    st.markdown("---")
    preview_n = (
        df_raw["Category"].isin(sel_cats if sel_cats else categories) &
        df_raw["Discount"].between(*disc_range) &
        df_raw["Profit"].between(*prof_range)
    ).sum()
    st.markdown(f'<span class="filter-badge">▸ {preview_n:,} rows match</span>', unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if sel_cats:
    df = df[df["Category"].isin(sel_cats)]
df = df[df["Discount"].between(*disc_range) & df["Profit"].between(*prof_range)]
if sel_regions and has_region:
    df = df[df["Region"].isin(sel_regions)]

if df.empty:
    st.warning("No data matches current filters — adjust the sidebar.", icon="⚠️")
    st.stop()

# ── Compute all stats once ────────────────────────────────────────────────────
s      = compute_stats(df)
health = compute_health_score(s)
pred   = compute_prediction(df, s)
exec_s = build_executive_summary(s, health, pred)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 02 — EXECUTIVE INTELLIGENCE LAYER
# ═══════════════════════════════════════════════════════════════════════════════
section("02", "Executive Intelligence")

st.markdown(f"""
<div class="exec-summary">
    <div class="exec-grid">
        <div>
            <div class="exec-block-label">Executive Summary</div>
            <div class="exec-summary-text">{exec_s['summary']}</div>
        </div>
        <div>
            <div class="exec-block-label">Most Critical Issue</div>
            <div class="exec-critical">
                <div class="exec-critical-label">⚠ Priority Alert</div>
                <div class="exec-critical-text">{exec_s['critical']}</div>
            </div>
        </div>
        <div>
            <div class="exec-block-label">Prioritised Actions</div>
            {''.join(f'<div class="exec-action-item"><span class="exec-action-num">#{i+1}</span><span class="exec-action-text">{a}</span></div>' for i, a in enumerate(exec_s['actions']))}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 03 — HEALTH SCORE + PREDICTIVE INSIGHT
# ═══════════════════════════════════════════════════════════════════════════════
section("03", "Business Health & Prediction")

hcol1, hcol2, hcol3 = st.columns([1, 1.8, 1.8])

with hcol1:
    gauge_svg = render_health_gauge(health["score"], health["color"], health["status"])
    st.markdown(f"""
    <div class="health-card">
        <div class="health-label">Business Health Score</div>
        {gauge_svg}
        <div class="health-breakdown">
            <div class="health-sub-row">
                <span class="health-sub-label">Margin</span>
                <span class="health-sub-score" style="color:{health['color']}">{health['margin_score']}/40</span>
            </div>
            <div class="health-sub-row">
                <span class="health-sub-label">Loss Rate</span>
                <span class="health-sub-score" style="color:{health['color']}">{health['loss_score']}/35</span>
            </div>
            <div class="health-sub-row">
                <span class="health-sub-label">Discount Discipline</span>
                <span class="health-sub-score" style="color:{health['color']}">{health['disc_score']}/25</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

with hcol2:
    direction_map = {
        "up":   ("trend-up",   "▲ Improving",  "If current trends hold (+2pp discount drift), profit is projected to increase."),
        "down": ("trend-down", "▼ Declining",  "If discount rates continue rising, profit is projected to deteriorate further."),
        "flat": ("trend-flat", "→ Stable",     "Profit trajectory is approximately flat under current discount trends."),
    }
    t_class, t_label, t_desc = direction_map[pred["direction"]]
    delta_sign = "+" if pred["delta"] >= 0 else ""
    st.markdown(f"""
    <div class="predict-card" style="height:100%;">
        <div class="predict-label">🔮 Predictive Insight · Next Period Estimate</div>
        <div class="predict-value">${pred['pred_profit']:,.0f}</div>
        <div class="predict-sub">
            Projected net profit if avg discount drifts to <strong>{pred['future_disc']*100:.1f}%</strong><br>
            Projected margin: <strong>{pred['pred_margin']:.1f}%</strong> &nbsp;·&nbsp; Model R²: <strong>{pred['r_squared']:.2f}</strong>
        </div>
        <div class="predict-trend {t_class}">
            {t_label} &nbsp;·&nbsp; {t_desc}
        </div>
        <div style="font-size:11px; color:var(--muted); margin-top:10px;">
            Δ vs current: <strong style="color:{'var(--success)' if pred['delta']>=0 else 'var(--danger)'}">{delta_sign}${abs(pred['delta']):,.0f}</strong>
        </div>
    </div>""", unsafe_allow_html=True)

with hcol3:
    # Most critical insight pinned
    insights_all = generate_insights(df, s)
    critical_ins = next((i for i in insights_all if i["kind"] == "critical"), insights_all[0])
    st.markdown(f"""
    <div style="height:100%;">
        <div style="font-size:9px; letter-spacing:2px; text-transform:uppercase; color:var(--danger); margin-bottom:10px;">🔴 Top Priority Issue</div>
        <div class="insight-strip pinned" style="height:calc(100% - 28px); box-sizing:border-box;">
            <div class="insight-icon">{critical_ins['icon']}</div>
            <div class="insight-body">
                <div class="insight-tag">{critical_ins['tag']}</div>
                <div class="insight-text">{critical_ins['text']}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 04 — METRICS
# ═══════════════════════════════════════════════════════════════════════════════
section("04", "Key Metrics")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(metric_card("Total Sales", f"${s['total_sales']:,.0f}", f"{s['n']:,} transactions", "blue", "💰"), unsafe_allow_html=True)
with c2:
    is_pos = s["total_profit"] >= 0
    st.markdown(metric_card("Net Profit", f"${s['total_profit']:,.0f}", f"Margin {s['margin']:.1f}%",
        "green" if is_pos else "red", "📈" if is_pos else "📉",
        delta=f"{'▲' if is_pos else '▼'} {abs(s['margin']):.1f}% margin", delta_pos=is_pos), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Loss Orders", f"{s['loss_txns']:,}", f"{s['loss_pct']:.1f}% of orders",
        "red" if s["loss_pct"] > 20 else "amber", "⚠️",
        delta="High risk" if s["loss_pct"] > 25 else "Moderate" if s["loss_pct"] > 15 else "Acceptable",
        delta_pos=s["loss_pct"] <= 15), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("Avg Discount", f"{s['avg_discount']*100:.1f}%", "Across filtered orders",
        "amber" if s["avg_discount"] > 0.3 else "purple", "🏷️",
        delta="Above threshold" if s["avg_discount"] > 0.35 else "Within range",
        delta_pos=s["avg_discount"] <= 0.35), unsafe_allow_html=True)
with c5:
    st.markdown(metric_card("Avg Order Value", f"${s['avg_order']:,.0f}", "Per transaction", "blue", "🛒"), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 05 — TOP INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════
section("05", "Top Insights")
for ins in generate_insights(df, s):
    st.markdown(insight_strip(ins["tag"], ins["text"], ins["kind"], ins["icon"]), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 06 — VISUAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
section("06", "Visual Analysis")
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="chart-card"><div class="chart-title">Sales by Category</div><div class="chart-sub">Total revenue contribution per segment</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_sales_by_category(df), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="chart-card"><div class="chart-title">Discount vs Profit</div><div class="chart-sub">Scatter with OLS regression trend line</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_discount_profit(df), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    st.markdown('<div class="chart-card"><div class="chart-title">Profit by Category</div><div class="chart-sub">Net margin performance — red = loss</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_profit_by_category(df), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="chart-card"><div class="chart-title">Discount Distribution</div><div class="chart-sub">Frequency of discount levels — risk threshold at 35%</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_discount_distribution(df), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 07 — WHAT-IF SIMULATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
section("07", "What-If Simulation Engine")

st.markdown('<div class="whatif-card">', unsafe_allow_html=True)
st.markdown('<div class="whatif-title">Scenario Simulator</div><div class="whatif-sub">Adjust parameters below to model the impact on profit and margin in real time.</div>', unsafe_allow_html=True)

wi_c1, wi_c2, wi_c3 = st.columns([1, 1, 2])
with wi_c1:
    disc_cap = st.slider("Max Discount Cap (%)", min_value=5, max_value=60,
                         value=25, step=1, format="%d%%",
                         help="Simulate capping all discounts at this level")
with wi_c2:
    price_uplift = st.slider("Price Uplift (%)", min_value=0, max_value=30,
                             value=0, step=1, format="%d%%",
                             help="Simulate a uniform price increase across all orders")

sim = simulate(df, s, disc_cap / 100, price_uplift)

with wi_c3:
    profit_delta_sign = "+" if sim["profit_delta"] >= 0 else ""
    margin_delta_sign = "+" if sim["margin_delta"] >= 0 else ""
    profit_color = "var(--success)" if sim["profit_delta"] >= 0 else "var(--danger)"
    margin_color = "var(--success)" if sim["margin_delta"] >= 0 else "var(--danger)"
    st.markdown(f"""
    <div class="compare-row">
        <div class="compare-box">
            <div class="compare-label">Current Profit</div>
            <div class="compare-value">${s['total_profit']:,.0f}</div>
            <div class="compare-sub">Margin: {s['margin']:.1f}%</div>
        </div>
        <div class="compare-box highlight">
            <div class="compare-label">Simulated Profit</div>
            <div class="compare-value" style="color:var(--a1)">${sim['sim_profit']:,.0f}</div>
            <div class="compare-sub">Margin: {sim['sim_margin']:.1f}%</div>
            <span class="compare-delta" style="background:{'rgba(6,214,160,0.1)' if sim['profit_delta']>=0 else 'rgba(239,68,68,0.1)'}; color:{profit_color}">
                {profit_delta_sign}${abs(sim['profit_delta']):,.0f} profit &nbsp;·&nbsp; {margin_delta_sign}{abs(sim['margin_delta']):.1f}pp margin
            </span>
        </div>
    </div>""", unsafe_allow_html=True)

st.plotly_chart(chart_whatif_comparison(s, sim), use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 08 — ALERTS
# ═══════════════════════════════════════════════════════════════════════════════
section("08", "Active Alerts")
hd_loss      = s["hd_loss"]
alerts_fired = 0

if len(hd_loss) > 0:
    alerts_fired += 1
    st.markdown(f"""<div class="alert-box"><div class="alert-title">⚠ High-Discount Loss Detected</div>
        <div class="alert-body"><strong>{len(hd_loss)}</strong> transactions ({len(hd_loss)/s['n']*100:.1f}%)
        exceed 35% discount with negative profit. Use the simulator above to model the recovery impact.</div></div>""",
        unsafe_allow_html=True)
if s["total_profit"] < 0:
    alerts_fired += 1
    st.markdown("""<div class="alert-box"><div class="alert-title">⚠ Portfolio-Level Profit Deficit</div>
        <div class="alert-body">Overall net profit is negative. Reprice or discontinue underperforming SKUs.</div></div>""",
        unsafe_allow_html=True)
if s["loss_pct"] > 25:
    alerts_fired += 1
    st.markdown(f"""<div class="alert-box"><div class="alert-title">⚠ Loss Rate Exceeds 25%</div>
        <div class="alert-body">More than a quarter of orders are unprofitable — structural pricing issues detected.</div></div>""",
        unsafe_allow_html=True)
if alerts_fired == 0:
    st.markdown(insight_strip("All Clear", "No critical alerts. Portfolio health looks stable.", "ok", "✅"),
                unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 09 — AI RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════════
section("09", "AI Recommendations")
for r in generate_recs(s):
    st.markdown(f"""<div class="rec-card" data-num="{r['num']}">
        <span class="rec-tag">✦ {r['tag']}</span>
        <div class="rec-text">{r['text']}</div>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — DATA EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
section("10", "Data Explorer")
with st.expander(f"View filtered dataset — {s['n']:,} rows", expanded=False):
    st.dataframe(
        df.style.format({"Sales": "${:,.2f}", "Profit": "${:,.2f}", "Discount": "{:.1%}"})
          .background_gradient(subset=["Profit"], cmap="RdYlGn"),
        use_container_width=True, height=340,
    )
    _, dl_col = st.columns([4, 1])
    with dl_col:
        st.download_button("⬇ Export CSV", df.to_csv(index=False).encode(),
                           "filtered_data.csv", "text/csv", use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <span class="footer-text">RETAIL INTELLIGENCE AI &nbsp;·&nbsp; DECISION ENGINE v4.0</span>
    <span class="footer-text">Streamlit &nbsp;·&nbsp; Plotly &nbsp;·&nbsp; SciPy &nbsp;·&nbsp; Pandas</span>
</div>
""", unsafe_allow_html=True)