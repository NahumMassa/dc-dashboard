"""
data_loader.py — Generates realistic data modeled after KIO Networks data centers.
KIO Networks is Mexico's largest data-center and managed-services provider,
operating Tier III / IV facilities in Querétaro, CDMX, Monterrey, and Guadalajara.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# ─── Constants ────────────────────────────────────────────────────────────────
KIO_SITES = {
    "Querétaro (QRO-1)": {"tier": "IV", "capacity_mw": 30, "lat": 20.5888, "lon": -100.3899},
    "CDMX (MEX-1)":      {"tier": "III+", "capacity_mw": 18, "lat": 19.4326, "lon": -99.1332},
    "Monterrey (MTY-1)":  {"tier": "III", "capacity_mw": 12, "lat": 25.6866, "lon": -100.3161},
    "Guadalajara (GDL-1)":{"tier": "III", "capacity_mw": 10, "lat": 20.6597, "lon": -103.3496},
}

MONTHS_LABELS = [
    "Jan-25", "Feb-25", "Mar-25", "Apr-25", "May-25", "Jun-25",
    "Jul-25", "Aug-25", "Sep-25", "Oct-25", "Nov-25", "Dec-25",
    "Jan-26", "Feb-26", "Mar-26",
]


# ─── Operations Data ─────────────────────────────────────────────────────────
def load_uptime_data() -> pd.DataFrame:
    """Monthly uptime % per site (SLA target = 99.995 for Tier IV, 99.982 for III)."""
    rows = []
    for site, info in KIO_SITES.items():
        base = 99.998 if info["tier"].startswith("IV") else 99.985
        for month in MONTHS_LABELS:
            uptime = round(min(100.0, base + np.random.uniform(-0.008, 0.005)), 4)
            rows.append({"site": site, "month": month, "uptime_pct": uptime, "tier": info["tier"]})
    return pd.DataFrame(rows)


def load_incident_log() -> pd.DataFrame:
    """Simulated incident log for the last 90 days."""
    severities = ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
    categories = [
        "Power — UPS failover", "Cooling — CRAH unit fault",
        "Network — BGP flap", "Power — Generator test failure",
        "Cooling — Chiller overtemp", "Security — Badge reader offline",
        "Network — Fiber cut (external)", "Power — PDU breaker trip",
        "Cooling — Humidity alarm", "Network — DDoS mitigation",
    ]
    statuses = ["Resolved", "Resolved", "Resolved", "Investigating", "Monitoring"]
    sites = list(KIO_SITES.keys())
    rows = []
    base_date = datetime(2026, 3, 20)
    for i in range(25):
        severity = random.choices(severities, weights=[5, 15, 40, 40])[0]
        ttrs = {"P1-Critical": (15, 60), "P2-High": (30, 180),
                "P3-Medium": (60, 480), "P4-Low": (120, 1440)}
        lo, hi = ttrs[severity]
        rows.append({
            "id": f"INC-{2026_0000 + i:07d}",
            "timestamp": (base_date - timedelta(days=random.randint(0, 90),
                                                 hours=random.randint(0, 23),
                                                 minutes=random.randint(0, 59))).strftime("%Y-%m-%d %H:%M"),
            "site": random.choice(sites),
            "severity": severity,
            "category": random.choice(categories),
            "status": random.choice(statuses),
            "ttr_minutes": random.randint(lo, hi),
        })
    df = pd.DataFrame(rows).sort_values("timestamp", ascending=False).reset_index(drop=True)
    return df


def load_mac_processes() -> pd.DataFrame:
    """Move / Add / Change requests summary per quarter."""
    data = {
        "quarter": ["Q1-2025", "Q2-2025", "Q3-2025", "Q4-2025", "Q1-2026"],
        "moves": [42, 38, 55, 47, 51],
        "adds": [128, 145, 162, 175, 190],
        "changes": [87, 92, 105, 98, 112],
        "avg_completion_days": [3.2, 2.9, 3.5, 2.7, 2.4],
    }
    return pd.DataFrame(data)


# ─── Energy Data ──────────────────────────────────────────────────────────────
def load_pue_data() -> pd.DataFrame:
    """Monthly PUE per site."""
    rows = []
    baselines = {"Querétaro (QRO-1)": 1.28, "CDMX (MEX-1)": 1.42,
                 "Monterrey (MTY-1)": 1.38, "Guadalajara (GDL-1)": 1.45}
    for site, base in baselines.items():
        for i, month in enumerate(MONTHS_LABELS):
            trend = -0.004 * i  # slight improvement over time
            noise = np.random.uniform(-0.02, 0.02)
            pue = round(max(1.05, base + trend + noise), 3)
            rows.append({"site": site, "month": month, "pue": pue})
    return pd.DataFrame(rows)


def load_energy_consumption() -> pd.DataFrame:
    """Monthly energy consumption in MWh per site."""
    rows = []
    base_mwh = {"Querétaro (QRO-1)": 8500, "CDMX (MEX-1)": 5200,
                "Monterrey (MTY-1)": 3600, "Guadalajara (GDL-1)": 2900}
    for site, base in base_mwh.items():
        for i, month in enumerate(MONTHS_LABELS):
            seasonal = 200 * np.sin(2 * np.pi * i / 12)  # summer peak
            growth = 40 * i
            noise = np.random.uniform(-150, 150)
            mwh = round(base + seasonal + growth + noise, 1)
            rows.append({"site": site, "month": month, "mwh": mwh})
    return pd.DataFrame(rows)


# ─── Security Data ────────────────────────────────────────────────────────────
def load_tia942_checklist() -> pd.DataFrame:
    """TIA-942 compliance checklist for the main facility."""
    items = [
        ("Architectural", "Dedicated data center space", "Compliant", "Tier IV"),
        ("Architectural", "Raised floor (min 60 cm)", "Compliant", "Tier IV"),
        ("Architectural", "Water/moisture detection", "Compliant", "Tier III+"),
        ("Electrical", "Redundant UPS (2N)", "Compliant", "Tier IV"),
        ("Electrical", "Dual utility feeds", "Compliant", "Tier IV"),
        ("Electrical", "Generator with 72h fuel", "Compliant", "Tier IV"),
        ("Electrical", "Automatic Transfer Switch", "Compliant", "Tier III+"),
        ("Mechanical", "N+1 cooling redundancy", "Compliant", "Tier III"),
        ("Mechanical", "Hot/cold aisle containment", "Compliant", "Tier III"),
        ("Mechanical", "Precision air conditioning", "Compliant", "Tier III"),
        ("Telecom", "Dual entrance rooms", "Compliant", "Tier IV"),
        ("Telecom", "Redundant backbone cabling", "Compliant", "Tier III"),
        ("Telecom", "Meet-me room available", "Compliant", "Tier III"),
        ("Fire Protection", "VESDA smoke detection", "Compliant", "Tier III"),
        ("Fire Protection", "Gas-based suppression (FM-200)", "Compliant", "Tier III"),
        ("Fire Protection", "Fire-rated walls (2h)", "Partial", "Tier III"),
    ]
    return pd.DataFrame(items, columns=["domain", "requirement", "status", "tier_level"])


def load_iso27001_controls() -> pd.DataFrame:
    """ISO 27001:2022 Annex A controls relevant to DC physical security."""
    items = [
        ("A.7.1", "Physical security perimeters", "Implemented", "Core"),
        ("A.7.2", "Physical entry controls", "Implemented", "Core"),
        ("A.7.3", "Securing offices, rooms, facilities", "Implemented", "Core"),
        ("A.7.4", "Physical security monitoring", "Implemented", "Core"),
        ("A.7.5", "Protecting against physical threats", "Implemented", "Core"),
        ("A.7.6", "Working in secure areas", "Implemented", "Core"),
        ("A.7.7", "Clear desk and clear screen", "Implemented", "Support"),
        ("A.7.8", "Equipment siting and protection", "Implemented", "Core"),
        ("A.7.9", "Security of assets off-premises", "Partial", "Support"),
        ("A.7.10", "Storage media", "Implemented", "Support"),
        ("A.7.11", "Supporting utilities", "Implemented", "Core"),
        ("A.7.12", "Cabling security", "Implemented", "Core"),
        ("A.7.13", "Equipment maintenance", "Implemented", "Core"),
        ("A.7.14", "Secure disposal or re-use", "Implemented", "Support"),
    ]
    return pd.DataFrame(items, columns=["control_id", "control_name", "status", "category"])


def load_physical_security() -> pd.DataFrame:
    """Physical security layers at QRO-1 facility."""
    layers = [
        ("Perimeter", "Anti-climb fencing (3 m) + razor wire", "Active", 1),
        ("Perimeter", "Vehicle bollards at entrance", "Active", 1),
        ("Perimeter", "CCTV — 120 cameras, 90-day retention", "Active", 1),
        ("Building", "Mantrap / airlock entry", "Active", 2),
        ("Building", "Biometric + badge access (multi-factor)", "Active", 2),
        ("Building", "24/7 on-site security guards", "Active", 2),
        ("Building", "Visitor escort policy", "Active", 2),
        ("Data Hall", "Cabinet-level electronic locks", "Active", 3),
        ("Data Hall", "In-row CCTV per aisle", "Active", 3),
        ("Data Hall", "Motion sensors after-hours", "Active", 3),
        ("Monitoring", "NOC — 24/7/365 staffed", "Active", 4),
        ("Monitoring", "SIEM integration for access logs", "Active", 4),
    ]
    return pd.DataFrame(layers, columns=["zone", "control", "status", "layer"])


# ─── Market Data (U4) ────────────────────────────────────────────────────────
def load_mexico_market() -> pd.DataFrame:
    """Mexico data-center market size (USD billions) — source-inspired by Statista / CBRE."""
    data = {
        "year": [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
        "market_size_usd_bn": [2.1, 2.4, 2.9, 3.4, 4.0, 4.7, 5.5, 6.4, 7.4, 8.6, 10.0],
        "yoy_growth_pct": [None, 14.3, 20.8, 17.2, 17.6, 17.5, 17.0, 16.4, 15.6, 16.2, 16.3],
    }
    return pd.DataFrame(data)


def load_market_share() -> pd.DataFrame:
    """Estimated market share of major DC providers in Mexico (2025)."""
    data = {
        "provider": [
            "KIO Networks", "Equinix", "Ascenty (Digital Realty)",
            "Odata", "IEnova / Sempra", "Telmex / Triara",
            "AWS / Azure / GCP (Hyperscale)", "Others",
        ],
        "share_pct": [22, 15, 12, 8, 7, 10, 18, 8],
        "facilities_mx": [36, 5, 4, 3, 3, 12, 6, 20],
    }
    return pd.DataFrame(data)


def load_deployment_models() -> pd.DataFrame:
    """Workload deployment model adoption in Mexico (% of enterprises)."""
    data = {
        "model": ["Colocation", "Public Cloud", "Hybrid Cloud", "On-Premises", "Edge"],
        "adoption_2023_pct": [35, 28, 20, 45, 5],
        "adoption_2025_pct": [40, 42, 35, 30, 12],
        "adoption_2028_pct": [42, 55, 52, 18, 25],
    }
    return pd.DataFrame(data)


def load_regional_hotspots() -> pd.DataFrame:
    """Key DC hubs in Mexico with investment pipeline."""
    data = {
        "region": ["Querétaro", "CDMX", "Monterrey", "Guadalajara", "Mérida", "Tijuana"],
        "operational_mw": [350, 280, 120, 85, 15, 30],
        "pipeline_mw": [200, 150, 80, 60, 40, 25],
        "key_driver": [
            "Hyperscale demand, favorable climate",
            "Enterprise & government proximity",
            "Nearshoring, US connectivity",
            "Tech talent pool, fintech hub",
            "Emerging market, subsea cable landing",
            "US border proximity, cross-border latency",
        ],
        "lat": [20.5888, 19.4326, 25.6866, 20.6597, 20.9674, 32.5149],
        "lon": [-100.3899, -99.1332, -100.3161, -103.3496, -89.5926, -117.0382],
    }
    return pd.DataFrame(data)


# ─── Emerging Tech Data (U4) ─────────────────────────────────────────────────
def load_tech_radar() -> pd.DataFrame:
    """Technology radar for DC innovation — readiness and impact scores."""
    techs = [
        ("Liquid Cooling (Direct-to-Chip)", "Cooling", "Trial", 85, 90, 2025),
        ("Immersion Cooling", "Cooling", "Assess", 60, 95, 2027),
        ("AI-Driven DCIM", "Operations", "Adopt", 90, 80, 2024),
        ("Digital Twins", "Operations", "Trial", 70, 75, 2026),
        ("Modular / Prefab DCs", "Construction", "Adopt", 88, 70, 2024),
        ("Small Nuclear Reactors (SMR)", "Power", "Hold", 20, 95, 2032),
        ("On-Site Solar + Battery", "Power", "Trial", 75, 65, 2025),
        ("Edge Micro DCs", "Architecture", "Adopt", 82, 70, 2024),
        ("400G / 800G Optics", "Network", "Trial", 78, 60, 2025),
        ("Quantum-Safe Encryption", "Security", "Assess", 40, 85, 2028),
        ("Robotic Maintenance", "Operations", "Assess", 35, 60, 2029),
        ("Water-Free Cooling", "Cooling", "Assess", 50, 80, 2027),
    ]
    return pd.DataFrame(techs, columns=[
        "technology", "category", "ring", "readiness_score", "impact_score", "target_year",
    ])


def load_adoption_timeline() -> pd.DataFrame:
    """Projected adoption % across Latin American DCs, 2024-2030."""
    data = {
        "year": [2024, 2025, 2026, 2027, 2028, 2029, 2030],
        "liquid_cooling": [8, 15, 25, 38, 50, 62, 72],
        "ai_dcim": [20, 35, 50, 62, 72, 80, 85],
        "digital_twins": [5, 10, 18, 28, 40, 52, 62],
        "modular_dc": [12, 20, 30, 40, 48, 55, 60],
        "edge_micro": [10, 18, 28, 38, 50, 58, 65],
        "renewable_onsite": [15, 22, 30, 40, 50, 60, 70],
    }
    return pd.DataFrame(data)
