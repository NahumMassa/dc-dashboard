"""
04_market.py — Market Intelligence page (Unit 4).
Covers: Mexico DC market size · Market share · Deployment models · Regional hotspots map.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_mexico_market, load_market_share,
    load_deployment_models, load_regional_hotspots,
)
from utils.charts import line_chart, bar_chart, donut_chart, mexico_map

st.set_page_config(page_title="Market · DC-Ops", page_icon="📊", layout="wide")

st.markdown("## 📊 Market Intelligence — Mexico Data Centers")
st.caption("Market sizing, competitive landscape, deployment models, and regional investment hotspots.")

# ─── Market Size ──────────────────────────────────────────────────────────────
st.markdown("### 💰 Mexico Data Center Market Size")
market_df = load_mexico_market()

m1, m2, m3 = st.columns(3)
m1.metric("2025 Market Size", f"${market_df[market_df['year']==2025]['market_size_usd_bn'].values[0]}B")
m2.metric("2030 Forecast", f"${market_df[market_df['year']==2030]['market_size_usd_bn'].values[0]}B")
m3.metric("CAGR 2025–2030", "16.3%")

st.plotly_chart(
    bar_chart(market_df, x="year", y="market_size_usd_bn",
              title="Mexico DC Market Size (USD Billions)", y_label="USD Billions"),
    use_container_width=True,
)

# ─── Market Share ─────────────────────────────────────────────────────────────
st.markdown("### 🏢 Competitive Landscape (2025)")
share_df = load_market_share()

s1, s2 = st.columns([1, 1])
with s1:
    st.plotly_chart(
        donut_chart(share_df["provider"].tolist(), share_df["share_pct"].tolist(),
                    title="Market Share by Provider"),
        use_container_width=True,
    )
with s2:
    st.dataframe(
        share_df.sort_values("share_pct", ascending=False),
        use_container_width=True, hide_index=True,
    )
    st.caption("KIO Networks leads the Mexican market with 36 facilities and 22% market share.")

# ─── Deployment Models ────────────────────────────────────────────────────────
st.markdown("### ☁️ Workload Deployment Models (% of Enterprises)")
deploy_df = load_deployment_models()

melted = deploy_df.melt(id_vars="model", var_name="year", value_name="adoption_pct")
melted["year"] = melted["year"].str.replace("adoption_", "").str.replace("_pct", "").str.upper()

st.plotly_chart(
    bar_chart(melted, x="model", y="adoption_pct", color="year",
              title="Deployment Model Adoption Trends", barmode="group",
              y_label="Adoption %"),
    use_container_width=True,
)

st.info("💡 **Key Trend:** Hybrid cloud adoption in Mexico is projected to grow from 20% (2023) to 52% (2028), driven by data sovereignty requirements and nearshoring demand.")

# ─── Regional Hotspots ────────────────────────────────────────────────────────
st.markdown("### 🗺️ Regional DC Hotspots in Mexico")
hotspots_df = load_regional_hotspots()

st.plotly_chart(
    mexico_map(hotspots_df, lat="lat", lon="lon", size="operational_mw",
               text="region", title="Data Center Capacity by Region (MW)"),
    use_container_width=True,
)

st.dataframe(
    hotspots_df[["region", "operational_mw", "pipeline_mw", "key_driver"]],
    use_container_width=True, hide_index=True,
)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data sources: Statista Mexico Data Center Market Report 2024, CBRE Latin America Data Center Trends, Mordor Intelligence, KIO Networks Annual Report.")
