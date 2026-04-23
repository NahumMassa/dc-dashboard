"""
05_emerging_tech.py — Emerging Technologies page (Unit 4).
Covers: Technology radar · Adoption timeline 2024-2030 · Strategic recommendations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_tech_radar, load_adoption_timeline
from utils.charts import scatter_chart, area_chart, KIO_PALETTE, _apply_defaults

st.set_page_config(page_title="Emerging Tech · DC-Ops", page_icon="🚀", layout="wide")

st.markdown("## 🚀 Emerging Technologies — Data Center Innovation")
st.caption("Technology radar assessment, adoption forecasts, and strategic recommendations for KIO Networks 2024–2030.")

# ─── Technology Radar ─────────────────────────────────────────────────────────
st.markdown("### 🎯 Technology Radar")
st.info("**Rings:** Adopt (ready now) → Trial (piloting) → Assess (watching) → Hold (wait)")

radar_df = load_tech_radar()

# Bubble chart: readiness vs impact, sized by target year proximity
current_year = 2026
radar_df["years_away"] = radar_df["target_year"] - current_year
radar_df["urgency"] = radar_df["years_away"].apply(lambda y: max(5, 30 - y * 5))

ring_order = {"Adopt": 0, "Trial": 1, "Assess": 2, "Hold": 3}
ring_colors = {"Adopt": "#00D4AA", "Trial": "#00A0E3", "Assess": "#FFB020", "Hold": "#FF6B6B"}

fig = px.scatter(
    radar_df, x="readiness_score", y="impact_score",
    size="urgency", color="ring", text="technology",
    color_discrete_map=ring_colors,
    title="Technology Readiness vs Business Impact",
    labels={"readiness_score": "Readiness Score", "impact_score": "Impact Score"},
)
fig.update_traces(textposition="top center", textfont_size=10)
_apply_defaults(fig)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# Radar detail table
st.markdown("**Technology Details**")

category_filter = st.multiselect(
    "Filter by category:",
    options=radar_df["category"].unique(),
    default=radar_df["category"].unique(),
)

filtered_radar = radar_df[radar_df["category"].isin(category_filter)]

def color_ring(val):
    colors = {"Adopt": "#00D4AA", "Trial": "#00A0E3", "Assess": "#FFB020", "Hold": "#FF6B6B"}
    return f"color: {colors.get(val, '#E8EDF5')}"

st.dataframe(
    filtered_radar[["technology", "category", "ring", "readiness_score", "impact_score", "target_year"]]
    .sort_values("readiness_score", ascending=False)
    .style.map(color_ring, subset=["ring"]),
    use_container_width=True, hide_index=True,
)

# ─── Adoption Timeline ───────────────────────────────────────────────────────
st.markdown("### 📈 Adoption Timeline — Latin American DCs (2024–2030)")
timeline_df = load_adoption_timeline()

tech_names = {
    "liquid_cooling": "Liquid Cooling",
    "ai_dcim": "AI-Driven DCIM",
    "digital_twins": "Digital Twins",
    "modular_dc": "Modular DCs",
    "edge_micro": "Edge Micro DCs",
    "renewable_onsite": "On-Site Renewables",
}

tech_cols = [c for c in timeline_df.columns if c != "year"]

selected_techs = st.multiselect(
    "Select technologies to display:",
    options=tech_cols,
    default=tech_cols,
    format_func=lambda x: tech_names.get(x, x),
)

if selected_techs:
    fig2 = go.Figure()
    for i, col in enumerate(selected_techs):
        fig2.add_trace(go.Scatter(
            x=timeline_df["year"], y=timeline_df[col],
            mode="lines+markers",
            name=tech_names.get(col, col),
            line=dict(color=KIO_PALETTE[i % len(KIO_PALETTE)], width=2),
            fill="tonexty" if i > 0 else "tozeroy",
            fillcolor=f"rgba({int(KIO_PALETTE[i % len(KIO_PALETTE)][1:3], 16)},{int(KIO_PALETTE[i % len(KIO_PALETTE)][3:5], 16)},{int(KIO_PALETTE[i % len(KIO_PALETTE)][5:7], 16)},0.08)",
        ))
    fig2.update_layout(
        title="Projected Technology Adoption (%)",
        yaxis_title="Adoption %",
        xaxis_title="Year",
    )
    _apply_defaults(fig2)
    fig2.update_layout(height=450)
    st.plotly_chart(fig2, use_container_width=True)

# ─── Strategic Recommendations ────────────────────────────────────────────────
st.markdown("### 💡 Strategic Recommendations for KIO Networks")

recs = [
    {
        "priority": "🔴 High",
        "title": "Accelerate Liquid Cooling Deployment",
        "desc": "AI/ML workloads in Querétaro require 30+ kW/rack. Direct-to-chip liquid cooling should be piloted in QRO-1 by Q3 2026 to capture hyperscale demand.",
        "timeline": "Q3 2026",
    },
    {
        "priority": "🔴 High",
        "title": "Deploy AI-Driven DCIM Platform",
        "desc": "Replace legacy BMS with an AI-powered DCIM (e.g., Nlyte, Sunbird) to reduce PUE by 8-12% and enable predictive maintenance across all 4 sites.",
        "timeline": "Q1 2026",
    },
    {
        "priority": "🟡 Medium",
        "title": "Pilot Digital Twin for QRO-1",
        "desc": "Build a CFD-based digital twin of QRO-1 to simulate airflow optimization and capacity planning scenarios before physical changes.",
        "timeline": "Q4 2026",
    },
    {
        "priority": "🟡 Medium",
        "title": "Expand Edge Micro DC Portfolio",
        "desc": "Deploy modular edge DCs in Mérida and Tijuana to serve nearshoring clients needing sub-5ms latency to US border.",
        "timeline": "2027",
    },
    {
        "priority": "🟢 Low",
        "title": "Quantum-Safe Encryption Readiness",
        "desc": "Begin cryptographic inventory and test post-quantum TLS across internal systems. NIST PQC standards finalized in 2024.",
        "timeline": "2028",
    },
]

for rec in recs:
    with st.expander(f"{rec['priority']} — {rec['title']} (Target: {rec['timeline']})"):
        st.markdown(rec["desc"])

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Sources: Uptime Institute Global DC Survey 2024, Gartner Hype Cycle for Data Center Infrastructure 2024, IDC Latin America Cloud Tracker, NIST Post-Quantum Cryptography Standards.")
