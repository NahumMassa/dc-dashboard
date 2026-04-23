"""
01_operations.py — Operations page (Unit 3).
Covers: Uptime SLA gauges · Incident log · MAC processes.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_uptime_data, load_incident_log, load_mac_processes
from utils.charts import gauge_chart, line_chart, bar_chart

st.set_page_config(page_title="Operations · DC-Ops", page_icon="⚙️", layout="wide")

st.markdown("## ⚙️ Operations — KIO Networks")
st.caption("Uptime SLA monitoring, incident management, and MAC process tracking across all facilities.")

# ─── Uptime SLA Gauges ───────────────────────────────────────────────────────
st.markdown("### 📊 Uptime SLA — Latest Month")
uptime_df = load_uptime_data()
latest_month = uptime_df["month"].iloc[-1]
latest = uptime_df[uptime_df["month"] == latest_month]

cols = st.columns(len(latest))
for col, (_, row) in zip(cols, latest.iterrows()):
    sla_target = 99.995 if row["tier"].startswith("IV") else 99.982
    with col:
        st.plotly_chart(
            gauge_chart(
                value=row["uptime_pct"],
                title=row["site"],
                range_min=99.95,
                range_max=100.0,
                threshold=sla_target,
            ),
            use_container_width=True,
        )
        status = "✅ Above SLA" if row["uptime_pct"] >= sla_target else "⚠️ Below SLA"
        st.caption(f"SLA Target: {sla_target}% → {status}")

# ─── Uptime Trend ────────────────────────────────────────────────────────────
st.markdown("### 📈 Uptime Trend (15 Months)")
st.plotly_chart(
    line_chart(uptime_df, x="month", y="uptime_pct", color="site",
               title="Monthly Uptime % by Facility", y_label="Uptime %"),
    use_container_width=True,
)

# ─── Incident Log ────────────────────────────────────────────────────────────
st.markdown("### 🚨 Incident Log (Last 90 Days)")
incidents = load_incident_log()

# Filters (extra feature!)
f1, f2, f3 = st.columns(3)
with f1:
    sev_filter = st.multiselect("Filter by severity", incidents["severity"].unique(), default=incidents["severity"].unique())
with f2:
    site_filter = st.multiselect("Filter by site", incidents["site"].unique(), default=incidents["site"].unique())
with f3:
    status_filter = st.multiselect("Filter by status", incidents["status"].unique(), default=incidents["status"].unique())

filtered = incidents[
    (incidents["severity"].isin(sev_filter)) &
    (incidents["site"].isin(site_filter)) &
    (incidents["status"].isin(status_filter))
]

# Summary metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Incidents", len(filtered))
m2.metric("P1 Critical", len(filtered[filtered["severity"] == "P1-Critical"]))
m3.metric("Avg TTR (min)", f"{filtered['ttr_minutes'].mean():.0f}" if len(filtered) > 0 else "N/A")
m4.metric("Open Cases", len(filtered[filtered["status"] != "Resolved"]))

# Color code severity
def highlight_severity(val):
    colors = {"P1-Critical": "#FF6B6B", "P2-High": "#FFB020", "P3-Medium": "#00A0E3", "P4-Low": "#00D4AA"}
    return f"color: {colors.get(val, '#E8EDF5')}"

st.dataframe(
    filtered.style.map(highlight_severity, subset=["severity"]),
    use_container_width=True,
    hide_index=True,
    height=350,
)

# Download button (extra feature!)
st.download_button(
    "📥 Export Incidents CSV",
    data=filtered.to_csv(index=False),
    file_name="kio_incidents_export.csv",
    mime="text/csv",
)

# ─── MAC Processes ────────────────────────────────────────────────────────────
st.markdown("### 🔄 MAC Processes (Move · Add · Change)")
mac_df = load_mac_processes()

st.plotly_chart(
    bar_chart(
        mac_df.melt(id_vars="quarter", value_vars=["moves", "adds", "changes"],
                     var_name="type", value_name="count"),
        x="quarter", y="count", color="type",
        title="MAC Requests per Quarter", barmode="group", y_label="Request Count",
    ),
    use_container_width=True,
)

st.markdown("**Average Completion Time (days)**")
st.dataframe(mac_df[["quarter", "avg_completion_days"]], use_container_width=True, hide_index=True)
