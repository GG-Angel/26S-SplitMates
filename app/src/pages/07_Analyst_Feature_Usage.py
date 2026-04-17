import logging
import streamlit as st
from api.client import client
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide", page_title="SplitMates | Feature Usage")
SideBarLinks()

audit_logs: list[dict] = client.get("/analyst/audit-logs") or []
completed_chores: list[dict] = client.get("/analyst/chores/completed") or []
sessions: list[dict] = client.get("/analyst/sessions") or []
inactive_users: list[dict] = client.get("/analyst/users/inactive") or []

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
        .pill {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 700;
        }
        .pill-low { background: #ECFDF3; color: #027A48; }
        .pill-medium { background: #FFFAEB; color: #B54708; }
        .pill-high { background: #FEF3F2; color: #B42318; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">Feature Usage Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Track which features and actions are used most across the platform.</div>', unsafe_allow_html=True)

# --- Metric Cards ---
total_sessions = sum(r.get("total_sessions", 0) for r in sessions)
avg_session = round(sum(r.get("avg_duration_mins", 0) for r in sessions) / len(sessions), 1) if sessions else 0
active_users = len(set(r.get("user_id") for r in sessions))
inactive_count = len(inactive_users)

col1, col2, col3, col4 = st.columns(4)
cards = [
    ("TOTAL SESSIONS", total_sessions, "All time"),
    ("AVG SESSION (MIN)", avg_session, "Per user"),
    ("ACTIVE USERS", active_users, "With sessions"),
    ("INACTIVE USERS", inactive_count, "30+ days"),
]
for col, (label, value, note) in zip((col1, col2, col3, col4), cards):
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
    st.markdown("<div class='panel'><div class='panel-title'>Audit Log Activity</div>", unsafe_allow_html=True)
    if audit_logs:
        for row in audit_logs[:10]:
            action = str(row.get("action_type", "")).title()
            table = str(row.get("target_table", ""))
            count = row.get("total_uses", 0)
            st.markdown(
                f"""<div class="data-row">
                    <div>
                        <div class="data-label">{table}</div>
                        <div class="data-sub">{action}</div>
                    </div>
                    <div class="data-count">{count}</div>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.caption("No audit log data available.")
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown("<div class='panel'><div class='panel-title'>Chore Completion Trends</div>", unsafe_allow_html=True)
    if completed_chores:
        for row in completed_chores[:10]:
            title = str(row.get("title", ""))
            effort = str(row.get("effort", "medium"))
            count = row.get("times_completed", 0)
            st.markdown(
                f"""<div class="data-row">
                    <div>
                        <div class="data-label">{title}</div>
                        <div class="data-sub"><span class="pill pill-{effort}">{effort.capitalize()}</span></div>
                    </div>
                    <div class="data-count">{count}x</div>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.caption("No completed chore data available.")
    st.markdown("</div>", unsafe_allow_html=True)
