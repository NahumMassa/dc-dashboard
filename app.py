"""
app.py — Home page for the KIO Networks DC-Ops Dashboard.
Streamlit multi-page app entry point.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_uptime_data, load_pue_data, load_mexico_market,
    load_market_share, KIO_SITES,
)

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DC-Ops · KIO Networks",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar branding */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A1628 0%, #12203A 100%);
    }
    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #12203A 0%, #1A2D4A 100%);
        border: 1px solid rgba(0,160,227,0.2);
        border-radius: 10px;
        padding: 20px 24px;
        text-align: center;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #00A0E3;
        line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #8DA4BF;
        margin-top: 6px;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00A0E3, #00D4AA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-size: 1.05rem;
        color: #8DA4BF;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #E8EDF5;
        border-left: 3px solid #00A0E3;
        padding-left: 12px;
        margin: 1.5rem 0 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Kio_networks_logo.svg/320px-Kio_networks_logo.svg.png", width=180)
    st.markdown("---")
    st.caption("📊 **DC-Ops Dashboard**")
    st.caption("Multi-page monitoring for KIO Networks data-center operations, energy, security, and market intelligence.")
    st.markdown("---")
    st.caption("🎓 UPY · Data Centers · 2026")
    st.caption("Nahum Massa")

# ─── Hero Section ─────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🏢 KIO Networks — DC-Ops Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Real-time monitoring · Infrastructure analytics · Market intelligence</div>', unsafe_allow_html=True)

# ─── KPI Row ──────────────────────────────────────────────────────────────────
uptime_df = load_uptime_data()
pue_df = load_pue_data()
market_df = load_mexico_market()
share_df = load_market_share()

latest_uptime = uptime_df[uptime_df["month"] == uptime_df["month"].iloc[-1]]["uptime_pct"].mean()
latest_pue = pue_df[pue_df["month"] == pue_df["month"].iloc[-1]]["pue"].mean()
kio_share = share_df[share_df["provider"] == "KIO Networks"]["share_pct"].values[0]
total_mw = sum(s["capacity_mw"] for s in KIO_SITES.values())

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value">{latest_uptime:.3f}%</div>
        <div class="kpi-label">Avg. Uptime (latest)</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value">{latest_pue:.2f}</div>
        <div class="kpi-label">Avg. PUE (latest)</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value">{kio_share}%</div>
        <div class="kpi-label">Mexico Market Share</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value">{total_mw} MW</div>
        <div class="kpi-label">Total IT Capacity</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")

# ─── Overview Grid ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Facility Overview</div>', unsafe_allow_html=True)

sites_data = []
for site, info in KIO_SITES.items():
    site_uptime = uptime_df[(uptime_df["site"] == site) & (uptime_df["month"] == uptime_df["month"].iloc[-1])]["uptime_pct"].values
    site_pue = pue_df[(pue_df["site"] == site) & (pue_df["month"] == pue_df["month"].iloc[-1])]["pue"].values
    sites_data.append({
        "Facility": site,
        "Tier": info["tier"],
        "Capacity (MW)": info["capacity_mw"],
        "Uptime %": f"{site_uptime[0]:.4f}" if len(site_uptime) > 0 else "N/A",
        "PUE": f"{site_pue[0]:.3f}" if len(site_pue) > 0 else "N/A",
        "Status": "🟢 Operational",
    })

st.dataframe(pd.DataFrame(sites_data), use_container_width=True, hide_index=True)

# ─── Page Directory ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🗂️ Dashboard Pages</div>', unsafe_allow_html=True)

p1, p2, p3 = st.columns(3)
with p1:
    st.info("**01 · Operations**\n\nUptime SLA gauges, incident log, MAC processes")
    st.info("**04 · Market Intelligence**\n\nMexico DC market, deployment models, hotspots")
with p2:
    st.info("**02 · Energy & PUE**\n\nPUE trends, energy consumption, PUE calculator")
    st.info("**05 · Emerging Tech**\n\nTech radar, adoption timeline, recommendations")
with p3:
    st.info("**03 · Security & Compliance**\n\nTIA-942, ISO 27001, physical security layers")

st.caption("👈 Use the sidebar to navigate between pages.")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#5A6F8A; font-size:0.8rem;'>"
    "DC-Ops Dashboard · KIO Networks Case Study · UPY Data Centers 2026 · "
    "Data sources: KIO Networks, Statista, CBRE, Gartner"
    "</div>",
    unsafe_allow_html=True,
)
