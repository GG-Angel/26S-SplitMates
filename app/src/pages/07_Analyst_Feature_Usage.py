import logging
import streamlit as st
import streamlit.components.v1 as components
from api.client import client
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide", page_title="SplitMates | Feature Usage")
SideBarLinks()

audit_logs: list[dict] = client.get("/analyst/audit-logs") or []
sessions: list[dict] = client.get("/analyst/sessions") or []
inactive_users: list[dict] = client.get("/analyst/users/inactive") or []

st.markdown(
    """
    <style>
        .page-subtitle { color: #9ca3af; font-size: 1rem; margin-top: 0; margin-bottom: 1.5rem; }
        h1 { font-size: 2.2rem !important; font-weight: 700 !important; margin-bottom: 0.1rem !important; }
        .metric-card {
            background: #262730;
            border: 1px solid rgba(250,250,250,0.1);
            border-radius: 12px;
            padding: 1rem 1rem 0.85rem 1rem;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
            height: 100%;
        }
        .metric-label { color: #9ca3af; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }
        .metric-value { color: #fafafa; font-size: 2.4rem; font-weight: 800; line-height: 1; margin-top: 0.15rem; }
        .metric-note { color: #8b95a1; font-size: 0.85rem; margin-top: 0.45rem; }
        .white-panel {
            background: #262730;
            border: 1px solid rgba(250,250,250,0.1);
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }
        .panel-title { font-size: 1.15rem; font-weight: 700; margin-bottom: 0.75rem; color: #fafafa; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Feature Usage Overview")
st.markdown('<div class="page-subtitle">Track which features and actions are used most across the platform.</div>', unsafe_allow_html=True)

# --- Metric Cards ---
total_sessions = sum(int(r.get("total_sessions", 0)) for r in sessions)
avg_session = round(sum(float(r.get("avg_duration_mins", 0)) for r in sessions) / len(sessions), 1) if sessions else 0
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

# LEFT — Audit Log Activity (fully self-contained white panel)
with left_col:
    if audit_logs:
        rows_html = ""
        for row in audit_logs[:10]:
            action = str(row.get("action_type", "")).title()
            table  = str(row.get("target_table", ""))
            count  = row.get("total_uses", 0)
            rows_html += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:0.65rem 0;border-bottom:1px solid rgba(250,250,250,0.08);">
                <div>
                    <div style="font-weight:600;font-size:0.95rem;color:#fafafa;">{table}</div>
                    <div style="color:#9ca3af;font-size:0.82rem;margin-top:0.1rem;">{action}</div>
                </div>
                <div style="font-size:1.4rem;font-weight:800;color:#bd0b0b;">{count}</div>
            </div>"""
        panel_html = f"""
        <div style="background:#262730;border:1px solid rgba(250,250,250,0.1);border-radius:12px;
                    padding:1.25rem;box-shadow:0 1px 2px rgba(0,0,0,0.2);font-family:sans-serif;">
            <div style="font-size:1.15rem;font-weight:700;color:#fafafa;margin-bottom:0.75rem;">
                Audit Log Activity
            </div>
            {rows_html}
        </div>"""
        components.html(panel_html, height=60 + len(audit_logs[:10]) * 62, scrolling=False)
    else:
        st.markdown('<div class="white-panel"><div class="panel-title">Audit Log Activity</div><p style="color:#9ca3af">No audit log data available.</p></div>', unsafe_allow_html=True)

# RIGHT — Feature Clicks as horizontal bar chart
with right_col:
    feature_clicks = [
        ("chores / Create",  7),
        ("groups / Create",  6),
        ("chores / Delete",  5),
        ("events / Create",  5),
        ("bills / Update",   5),
        ("users / Create",   3),
        ("items / Delete",   3),
    ]
    max_val = max(c for _, c in feature_clicks)
    bars_html = ""
    for label, count in feature_clicks:
        pct = round((count / max_val) * 100)
        bars_html += f"""
        <div style="margin-bottom:0.85rem;">
            <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                <span style="font-weight:600;font-size:0.9rem;color:#fafafa;">{label}</span>
                <span style="font-weight:700;font-size:0.9rem;color:#bd0b0b;">{count}</span>
            </div>
            <div style="background:rgba(250,250,250,0.1);border-radius:4px;height:10px;width:100%;">
                <div style="background:#E31B1B;border-radius:4px;height:10px;width:{pct}%;"></div>
            </div>
        </div>"""
    panel_html = f"""
    <div style="background:#262730;border:1px solid rgba(250,250,250,0.1);border-radius:12px;
                padding:1.25rem;box-shadow:0 1px 2px rgba(0,0,0,0.2);font-family:sans-serif;">
        <div style="font-size:1.15rem;font-weight:700;color:#fafafa;margin-bottom:1rem;">
            Feature Clicks
        </div>
        {bars_html}
    </div>"""
    components.html(panel_html, height=60 + len(feature_clicks) * 58, scrolling=False)
