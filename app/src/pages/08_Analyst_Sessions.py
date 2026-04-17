import logging
import streamlit as st
import pandas as pd
from api.client import client
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide", page_title="SplitMates | User Sessions")
SideBarLinks()

sessions: list[dict] = client.get("/analyst/sessions") or []
engagement: list[dict] = client.get("/analyst/groups/engagement") or []

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
        .metric-label { color: #667085; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }
        .metric-value { color: #101828; font-size: 2.4rem; font-weight: 800; line-height: 1; margin-top: 0.15rem; }
        .metric-note { color: #475467; font-size: 0.85rem; margin-top: 0.45rem; }
        .panel {
            background: white;
            border: 1px solid #EAECF0;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }
        .panel-title { font-size: 1.15rem; font-weight: 700; margin-bottom: 0.75rem; color: #101828; }
        .data-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.65rem 0;
            border-bottom: 1px solid #EAECF0;
        }
        .data-row:last-child { border-bottom: none; }
        .data-label { font-weight: 600; font-size: 0.95rem; color: #101828; }
        .data-sub { color: #667085; font-size: 0.82rem; margin-top: 0.1rem; }
        .data-count { font-size: 1.4rem; font-weight: 800; color: #bd0b0b; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">User Sessions & Engagement</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Analyze session trends and how engagement scales with household size.</div>', unsafe_allow_html=True)

# --- Metric Cards ---
total_sessions = sum(r.get("total_sessions", 0) for r in sessions)
avg_duration = round(sum(r.get("avg_duration_mins", 0) for r in sessions) / len(sessions), 1) if sessions else 0
unique_users = len(set(r.get("user_id") for r in sessions))

col1, col2, col3 = st.columns(3)
cards = [
    ("TOTAL SESSIONS", total_sessions, "All time"),
    ("AVG SESSION (MIN)", avg_duration, "Per user"),
    ("ACTIVE USERS", unique_users, "With sessions"),
]
for col, (label, value, note) in zip((col1, col2, col3), cards):
    with col:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

left_col, right_col = st.columns(2, gap="large")

with left_col:
    st.markdown("<div class='panel'><div class='panel-title'>Activity by Hour of Day</div>", unsafe_allow_html=True)
    if sessions:
        df = pd.DataFrame(sessions)
        hourly = df.groupby("hour_of_day")["total_sessions"].sum().reset_index()
        hourly.columns = ["Hour", "Sessions"]
        st.bar_chart(hourly.set_index("Hour"), color="#bd0b0b")
    else:
        st.caption("No session data available.")
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown("<div class='panel'><div class='panel-title'>Avg Session Duration by User</div>", unsafe_allow_html=True)
    if sessions:
        df = pd.DataFrame(sessions)
        user_avg = df.groupby(["first_name", "last_name"])["avg_duration_mins"].mean().reset_index()
        for _, row in user_avg.iterrows():
            name = f"{row['first_name']} {row['last_name']}"
            duration = round(row["avg_duration_mins"], 1)
            st.markdown(
                f"""<div class="data-row">
                    <div class="data-label">{name}</div>
                    <div class="data-count">{duration} min</div>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.caption("No session data available.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='panel'><div class='panel-title'>Engagement by Household Size</div>", unsafe_allow_html=True)
if engagement:
    df_eng = pd.DataFrame(engagement)
    df_eng.columns = ["Household Size", "Total Groups", "Avg Chores", "Avg Completed", "Avg Bills", "Avg Events"]
    st.dataframe(df_eng, use_container_width=True, hide_index=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.line_chart(df_eng.set_index("Household Size")[["Avg Chores", "Avg Completed"]], color=["#bd0b0b", "#667085"])
else:
    st.caption("No engagement data available.")
st.markdown("</div>", unsafe_allow_html=True)
