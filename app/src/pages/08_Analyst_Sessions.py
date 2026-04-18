import logging
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import Counter
from api.client import client
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide", page_title="SplitMates | User Sessions")
SideBarLinks()

sessions: list[dict] = client.get("/analyst/sessions") or []

st.markdown(
    """
    <style>
        .page-title { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.1rem; }
        .page-subtitle { color: #667085; font-size: 1rem; margin-top: 0; margin-bottom: 1.5rem; }
        .metric-card {
            background: white;
            border: 1px solid #EAECF0;
            border-radius: 12px;
            padding: 1rem 1rem 0.85rem 1rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
            height: 100%;
        }
        .metric-label {
            color: #667085;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .metric-value {
            color: #101828;
            font-size: 2.4rem;
            font-weight: 800;
            line-height: 1;
            margin-top: 0.15rem;
        }
        .metric-note { color: #475467; font-size: 0.85rem; margin-top: 0.45rem; }
        .panel {
            background: white;
            border: 1px solid #EAECF0;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }
        .panel-title {
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            color: #101828;
        }
        .data-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.55rem 0;
            border-bottom: 1px solid #F2F4F7;
        }
        .data-row:last-child { border-bottom: none; }
        .user-name {
            color: #ffffff;
            font-weight: 500;
            font-size: 0.92rem;
        }
        .duration-badge {
            color: #E31B1B;
            font-weight: 700;
            font-size: 0.92rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="page-title">User Sessions &amp; Engagement</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="page-subtitle">Analyze session trends and how engagement scales with household size.</p>',
    unsafe_allow_html=True,
)

# ── Metrics ───────────────────────────────────────────────────────────────────
total_sessions = len(sessions)
durations = [float(r.get("avg_duration_mins", 0)) for r in sessions if r.get("avg_duration_mins") is not None]
avg_duration = round(sum(durations) / len(durations), 1) if durations else 0
active_users = len(set(r.get("user_id") for r in sessions if r.get("user_id")))

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Sessions</div>
            <div class="metric-value">{total_sessions}</div>
            <div class="metric-note">All time</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Avg Session (min)</div>
            <div class="metric-value">{avg_duration}</div>
            <div class="metric-note">Per user</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Active Users</div>
            <div class="metric-value">{active_users}</div>
            <div class="metric-note">With sessions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1.1, 0.9])

# Activity by Hour of Day — clean bar chart
with col_left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Activity by Hour of Day</div>', unsafe_allow_html=True)

    hour_counts: Counter = Counter()
    for r in sessions:
        raw_hour = r.get("hour_of_day")
        if raw_hour is not None:
            try:
                hour_counts[int(raw_hour)] += 1
            except (ValueError, TypeError):
                pass

    if hour_counts:
        hours_sorted = sorted(hour_counts.keys())
        counts = [hour_counts[h] for h in hours_sorted]
        hour_labels = [f"{h:02d}:00" for h in hours_sorted]

        fig_bar = go.Figure(
            go.Bar(
                x=hour_labels,
                y=counts,
                marker_color="#E31B1B",
                hovertemplate="%{x}<br>Sessions: %{y}<extra></extra>",
            )
        )
        fig_bar.update_layout(
            margin=dict(l=0, r=0, t=10, b=40),
            height=280,
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(
                title="Hour of Day",
                tickfont=dict(size=11),
                tickangle=-45,
                showgrid=False,
                linecolor="#EAECF0",
            ),
            yaxis=dict(
                title="Sessions",
                tickfont=dict(size=11),
                showgrid=True,
                gridcolor="#F2F4F7",
                linecolor="#EAECF0",
            ),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No hourly data available.")

    st.markdown("</div>", unsafe_allow_html=True)

# Avg Session Duration by User — sorted largest to smallest, white user names
with col_right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Avg Session Duration by User</div>', unsafe_allow_html=True)

    # Build per-user avg duration
    user_durations: dict[str, list[float]] = {}
    for r in sessions:
        uid = r.get("user_id")
        first = r.get("first_name", "")
        last = r.get("last_name", "")
        dur = r.get("avg_duration_mins")
        if uid and dur is not None:
            name = f"{first} {last}".strip() or f"User {uid}"
            user_durations.setdefault(name, []).append(float(dur))

    user_avg = {name: round(sum(vals) / len(vals), 1) for name, vals in user_durations.items()}

    # Sort largest to smallest
    sorted_users = sorted(user_avg.items(), key=lambda x: x[1], reverse=True)

    if sorted_users:
        rows_html = ""
        for name, avg in sorted_users:
            rows_html += f"""
            <div class="data-row">
                <span class="user-name">{name}</span>
                <span class="duration-badge">{avg} min</span>
            </div>
            """
        st.markdown(rows_html, unsafe_allow_html=True)
    else:
        st.info("No session duration data available.")

    st.markdown("</div>", unsafe_allow_html=True)
