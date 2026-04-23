"""
03_security.py — Security & Compliance page (Unit 3).
Covers: TIA-942 compliance · ISO 27001 controls · Physical security layers.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_tia942_checklist, load_iso27001_controls, load_physical_security,
)
from utils.charts import compliance_bar, radar_chart

st.set_page_config(page_title="Security · DC-Ops", page_icon="🔒", layout="wide")

st.markdown("## 🔒 Security & Compliance — KIO Networks")
st.caption("TIA-942 / ISO 27001 compliance status and physical security controls for the Querétaro (QRO-1) Tier IV facility.")


def color_status(val):
    if val == "Compliant" or val == "Implemented":
        return "background-color: rgba(0,212,170,0.15); color: #00D4AA"
    elif val == "Partial":
        return "background-color: rgba(255,176,32,0.15); color: #FFB020"
    return "background-color: rgba(255,107,107,0.15); color: #FF6B6B"


# ─── TIA-942 Compliance ──────────────────────────────────────────────────────
st.markdown("### 📋 TIA-942 Compliance Checklist")
tia_df = load_tia942_checklist()

total = len(tia_df)
compliant = len(tia_df[tia_df["status"] == "Compliant"])
partial = len(tia_df[tia_df["status"] == "Partial"])

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Requirements", total)
m2.metric("Compliant ✅", compliant)
m3.metric("Partial ⚠️", partial)
m4.metric("Compliance Rate", f"{compliant/total*100:.1f}%")

col_chart, col_table = st.columns([1, 1])
with col_chart:
    st.plotly_chart(
        compliance_bar(tia_df, "domain", "status", title="TIA-942 Compliance by Domain"),
        use_container_width=True,
    )
with col_table:
    st.dataframe(
        tia_df.style.map(color_status, subset=["status"]),
        use_container_width=True, hide_index=True, height=400,
    )

# ─── ISO 27001 Controls ──────────────────────────────────────────────────────
st.markdown("### 🛡️ ISO 27001:2022 — Physical Security Controls (Annex A.7)")
iso_df = load_iso27001_controls()

iso_impl = len(iso_df[iso_df["status"] == "Implemented"])
c1, c2 = st.columns(2)
c1.metric("Controls Implemented", f"{iso_impl}/{len(iso_df)}")
c2.metric("Implementation Rate", f"{iso_impl/len(iso_df)*100:.1f}%")

col1, col2 = st.columns([1, 1])
with col1:
    st.plotly_chart(
        compliance_bar(iso_df, "category", "status", title="ISO 27001 A.7 by Category"),
        use_container_width=True,
    )
with col2:
    st.dataframe(
        iso_df.style.map(color_status, subset=["status"]),
        use_container_width=True, hide_index=True,
    )

# ─── Physical Security Layers ────────────────────────────────────────────────
st.markdown("### 🏗️ Physical Security Layers — QRO-1 Facility")
phys_df = load_physical_security()

zones = phys_df["zone"].unique().tolist()
zone_counts = [len(phys_df[phys_df["zone"] == z]) for z in zones]
max_count = max(zone_counts)
zone_scores = [round(c / max_count * 100) for c in zone_counts]

r1, r2 = st.columns([1, 1])
with r1:
    st.plotly_chart(
        radar_chart(zones, zone_scores, title="Security Coverage by Zone (%)"),
        use_container_width=True,
    )
with r2:
    st.markdown("**Defense-in-Depth Model**")
    for layer_num in sorted(phys_df["layer"].unique()):
        layer_items = phys_df[phys_df["layer"] == layer_num]
        zone_name = layer_items["zone"].iloc[0]
        icons = {"Perimeter": "🔲", "Building": "🏢", "Data Hall": "🖥️", "Monitoring": "📡"}
        icon = icons.get(zone_name, "🔒")
        with st.expander(f"{icon} Layer {layer_num} — {zone_name} ({len(layer_items)} controls)", expanded=(layer_num == 1)):
            for _, row in layer_items.iterrows():
                st.markdown(f"- ✅ {row['control']}")

# ─── Download ─────────────────────────────────────────────────────────────────
st.markdown("---")
d1, d2 = st.columns(2)
with d1:
    st.download_button("📥 Export TIA-942 (CSV)", tia_df.to_csv(index=False), "kio_tia942.csv", "text/csv")
with d2:
    st.download_button("📥 Export ISO 27001 (CSV)", iso_df.to_csv(index=False), "kio_iso27001.csv", "text/csv")

st.caption("Reference: TIA-942-B (2017), ISO/IEC 27001:2022 Annex A, Uptime Institute Tier Classification.")
