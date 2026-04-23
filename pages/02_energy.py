"""
02_energy.py — Energy & PUE page (Unit 3).
Covers: PUE trends · Energy consumption · Interactive PUE calculator.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_pue_data, load_energy_consumption
from utils.charts import line_chart, bar_chart, gauge_chart

st.set_page_config(page_title="Energy · DC-Ops", page_icon="⚡", layout="wide")

st.markdown("## ⚡ Energy & PUE — KIO Networks")
st.caption("Power Usage Effectiveness monitoring, energy consumption analytics, and PUE impact calculator.")

# ─── PUE Latest ───────────────────────────────────────────────────────────────
st.markdown("### 📊 Current PUE by Facility")
pue_df = load_pue_data()
latest_month = pue_df["month"].iloc[-1]
latest_pue = pue_df[pue_df["month"] == latest_month]

cols = st.columns(len(latest_pue))
for col, (_, row) in zip(cols, latest_pue.iterrows()):
    with col:
        st.plotly_chart(
            gauge_chart(
                value=row["pue"],
                title=row["site"],
                suffix="",
                range_min=1.0,
                range_max=2.0,
                threshold=1.4,
            ),
            use_container_width=True,
        )
        rating = "🟢 Excellent" if row["pue"] < 1.3 else ("🟡 Good" if row["pue"] < 1.5 else "🔴 Needs Improvement")
        st.caption(f"Rating: {rating}")

# ─── PUE Trend ────────────────────────────────────────────────────────────────
st.markdown("### 📈 PUE Trend (15 Months)")
st.plotly_chart(
    line_chart(pue_df, x="month", y="pue", color="site",
               title="Monthly PUE by Facility", y_label="PUE"),
    use_container_width=True,
)

# ─── Energy Consumption ──────────────────────────────────────────────────────
st.markdown("### 🔋 Energy Consumption")
energy_df = load_energy_consumption()

site_selection = st.multiselect(
    "Select facilities to compare:",
    options=energy_df["site"].unique(),
    default=energy_df["site"].unique(),
)

filtered_energy = energy_df[energy_df["site"].isin(site_selection)]

tab1, tab2 = st.tabs(["📈 Trend", "📊 Total by Site"])

with tab1:
    st.plotly_chart(
        line_chart(filtered_energy, x="month", y="mwh", color="site",
                   title="Monthly Energy Consumption (MWh)", y_label="MWh"),
        use_container_width=True,
    )

with tab2:
    totals = filtered_energy.groupby("site")["mwh"].sum().reset_index()
    totals.columns = ["site", "total_mwh"]
    st.plotly_chart(
        bar_chart(totals, x="site", y="total_mwh",
                  title="Total Energy Consumption by Facility (15 months)", y_label="MWh"),
        use_container_width=True,
    )

# ─── PUE Calculator (Interactive) ────────────────────────────────────────────
st.markdown("### 🧮 Interactive PUE Calculator")
st.info("**PUE = Total Facility Power ÷ IT Equipment Power.** A PUE of 1.0 means all power goes to IT equipment (ideal). Industry average is ~1.58.")

c1, c2 = st.columns(2)
with c1:
    it_load = st.slider("IT Equipment Load (kW)", min_value=100, max_value=10000, value=3000, step=100)
    cooling = st.slider("Cooling Systems (kW)", min_value=50, max_value=5000, value=900, step=50)
    lighting = st.slider("Lighting & Other (kW)", min_value=10, max_value=500, value=80, step=10)
    ups_loss = st.slider("UPS / PDU Losses (kW)", min_value=10, max_value=1000, value=150, step=10)

total_facility = it_load + cooling + lighting + ups_loss
calculated_pue = total_facility / it_load if it_load > 0 else 0

with c2:
    st.plotly_chart(
        gauge_chart(
            value=round(calculated_pue, 3),
            title="Calculated PUE",
            suffix="",
            range_min=1.0,
            range_max=3.0,
            threshold=1.4,
        ),
        use_container_width=True,
    )

    st.markdown(f"""
    | Component | Power (kW) | % of Total |
    |---|---|---|
    | IT Equipment | {it_load:,} | {it_load/total_facility*100:.1f}% |
    | Cooling | {cooling:,} | {cooling/total_facility*100:.1f}% |
    | Lighting & Other | {lighting:,} | {lighting/total_facility*100:.1f}% |
    | UPS / PDU Losses | {ups_loss:,} | {ups_loss/total_facility*100:.1f}% |
    | **Total Facility** | **{total_facility:,}** | **100%** |
    """)

    annual_cost_per_kwh = 0.085  # Mexico industrial rate (USD)
    annual_energy_mwh = total_facility * 8760 / 1000
    annual_cost = annual_energy_mwh * annual_cost_per_kwh * 1000
    st.metric("Est. Annual Energy Cost (USD)", f"${annual_cost:,.0f}")
    st.caption(f"Based on ${annual_cost_per_kwh}/kWh (Mexico industrial rate)")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data sources: KIO Networks sustainability reports, CFE industrial tariff schedules. PUE benchmarks per Uptime Institute 2024 Global Survey.")
