"""
charts.py — Reusable Plotly chart helpers for the DC-Ops dashboard.
All charts share a consistent dark theme matching the KIO Networks branding.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ─── Shared layout defaults ──────────────────────────────────────────────────
_LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#E8EDF5"),
    margin=dict(l=40, r=20, t=50, b=40),
)

KIO_PALETTE = [
    "#00A0E3",  # KIO blue
    "#0066B2",  # darker blue
    "#00D4AA",  # teal / green
    "#FFB020",  # amber
    "#FF6B6B",  # coral / red
    "#A78BFA",  # lavender
    "#34D399",  # emerald
    "#F472B6",  # pink
]


def _apply_defaults(fig: go.Figure) -> go.Figure:
    fig.update_layout(**_LAYOUT_DEFAULTS)
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
    return fig


# ─── Gauge Chart ──────────────────────────────────────────────────────────────
def gauge_chart(value: float, title: str, suffix: str = "%",
                range_min: float = 99.9, range_max: float = 100.0,
                threshold: float | None = None) -> go.Figure:
    """Single gauge indicator."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": suffix, "font": {"size": 28}},
        title={"text": title, "font": {"size": 14}},
        gauge={
            "axis": {"range": [range_min, range_max], "tickcolor": "#E8EDF5"},
            "bar": {"color": "#00A0E3"},
            "bgcolor": "rgba(255,255,255,0.05)",
            "steps": [
                {"range": [range_min, range_min + (range_max - range_min) * 0.6], "color": "rgba(255,107,107,0.15)"},
                {"range": [range_min + (range_max - range_min) * 0.6, range_min + (range_max - range_min) * 0.85], "color": "rgba(255,176,32,0.15)"},
                {"range": [range_min + (range_max - range_min) * 0.85, range_max], "color": "rgba(0,160,227,0.15)"},
            ],
            "threshold": {
                "line": {"color": "#FFB020", "width": 2},
                "thickness": 0.75,
                "value": threshold or (range_min + (range_max - range_min) * 0.85),
            },
        },
    ))
    fig.update_layout(height=220, **_LAYOUT_DEFAULTS)
    return fig


# ─── Line Chart ───────────────────────────────────────────────────────────────
def line_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None,
               title: str = "", y_label: str = "") -> go.Figure:
    fig = px.line(df, x=x, y=y, color=color, title=title,
                  color_discrete_sequence=KIO_PALETTE, markers=True)
    fig.update_layout(yaxis_title=y_label, legend_title_text="")
    return _apply_defaults(fig)


# ─── Bar Chart ────────────────────────────────────────────────────────────────
def bar_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None,
              title: str = "", barmode: str = "group", orientation: str = "v",
              y_label: str = "") -> go.Figure:
    fig = px.bar(df, x=x, y=y, color=color, title=title, barmode=barmode,
                 orientation=orientation, color_discrete_sequence=KIO_PALETTE)
    fig.update_layout(yaxis_title=y_label, legend_title_text="")
    return _apply_defaults(fig)


# ─── Pie / Donut Chart ───────────────────────────────────────────────────────
def donut_chart(labels: list, values: list, title: str = "") -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.5,
        marker=dict(colors=KIO_PALETTE),
        textinfo="label+percent", textfont_size=12,
    ))
    fig.update_layout(title=title, showlegend=False, height=400, **_LAYOUT_DEFAULTS)
    return fig


# ─── Radar / Polar Chart ─────────────────────────────────────────────────────
def radar_chart(categories: list, values: list, title: str = "",
                fill_color: str = "rgba(0,160,227,0.25)",
                line_color: str = "#00A0E3") -> go.Figure:
    cats = categories + [categories[0]]
    vals = values + [values[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats, fill="toself",
        fillcolor=fill_color, line=dict(color=line_color, width=2),
    ))
    fig.update_layout(
        title=title, height=420,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.08)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        ),
        **_LAYOUT_DEFAULTS,
    )
    return fig


# ─── Scatter / Bubble Chart ──────────────────────────────────────────────────
def scatter_chart(df: pd.DataFrame, x: str, y: str, size: str | None = None,
                  color: str | None = None, text: str | None = None,
                  title: str = "") -> go.Figure:
    fig = px.scatter(df, x=x, y=y, size=size, color=color, text=text,
                     title=title, color_discrete_sequence=KIO_PALETTE)
    if text:
        fig.update_traces(textposition="top center")
    return _apply_defaults(fig)


# ─── Area Chart ───────────────────────────────────────────────────────────────
def area_chart(df: pd.DataFrame, x: str, y: list[str],
               title: str = "") -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(y):
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col], mode="lines", name=col.replace("_", " ").title(),
            fill="tonexty" if i > 0 else "tozeroy",
            line=dict(color=KIO_PALETTE[i % len(KIO_PALETTE)]),
        ))
    fig.update_layout(title=title)
    return _apply_defaults(fig)


# ─── Horizontal bar (for compliance checklists) ──────────────────────────────
def compliance_bar(df: pd.DataFrame, category_col: str, status_col: str,
                   title: str = "") -> go.Figure:
    summary = df.groupby([category_col, status_col]).size().reset_index(name="count")
    color_map = {"Compliant": "#00D4AA", "Implemented": "#00D4AA",
                 "Partial": "#FFB020", "Not Implemented": "#FF6B6B"}
    fig = px.bar(summary, x="count", y=category_col, color=status_col,
                 orientation="h", title=title,
                 color_discrete_map=color_map, barmode="stack")
    fig.update_layout(yaxis_title="", legend_title_text="")
    return _apply_defaults(fig)


# ─── Map (Scattergeo for Mexico) ─────────────────────────────────────────────
def mexico_map(df: pd.DataFrame, lat: str, lon: str, size: str,
               text: str, title: str = "") -> go.Figure:
    fig = px.scatter_geo(
        df, lat=lat, lon=lon, size=size, text=text,
        title=title, color_discrete_sequence=["#00A0E3"],
    )
    fig.update_geos(
        scope="north america",
        center=dict(lat=23.6, lon=-102.5),
        projection_scale=4.5,
        showland=True, landcolor="rgba(18,32,58,0.8)",
        showocean=True, oceancolor="rgba(10,22,40,0.9)",
        showlakes=False,
        showcountries=True, countrycolor="rgba(255,255,255,0.15)",
        showsubunits=True, subunitcolor="rgba(255,255,255,0.08)",
    )
    fig.update_traces(textposition="top center", textfont=dict(size=11, color="#E8EDF5"))
    fig.update_layout(height=500, **_LAYOUT_DEFAULTS)
    return fig
