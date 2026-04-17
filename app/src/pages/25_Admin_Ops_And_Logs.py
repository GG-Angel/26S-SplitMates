import logging
from datetime import datetime
from typing import Any

import streamlit as st

from modules.admin_api import create_app_version, get_app_versions, get_audit_logs
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide", page_title="SplitMates | Admin Updates & Audit Logs")
SideBarLinks()


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _fmt_dt(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", ""))
        except ValueError:
            return value
    if isinstance(value, datetime):
        return value.strftime("%b %d, %I:%M %p")
    return _as_text(value)


def _card(label: str, value: Any, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
        .page-title { font-size: 2.1rem; font-weight: 800; margin-bottom: 0.1rem; }
        .page-subtitle { color: #667085; font-size: 1rem; margin-bottom: 1rem; }
        .metric-card {
            background: #F8FAFC;
            border: 1px solid #EAECF0;
            border-radius: 12px;
            padding: 1rem 1rem 0.85rem 1rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
            height: 100%;
        }
        .metric-label { color: #667085; font-size: 0.83rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
        .metric-value { color: #101828; font-size: 2.2rem; font-weight: 800; line-height: 1; margin-top: 0.15rem; }
        .metric-note { color: #475467; font-size: 0.85rem; margin-top: 0.45rem; }
        .panel {
            background: #F8FAFC;
            border: 1px solid #EAECF0;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }
        .panel-title { font-size: 1.12rem; font-weight: 700; margin-bottom: 0.35rem; color: #101828; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">Updates & Audit Logs</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Track deployment versions with release summaries and review system audit activity.</div>',
    unsafe_allow_html=True,
)

try:
    versions = get_app_versions() or []
except Exception as exc:
    st.error(f"Unable to load app versions: {exc}")
    st.stop()

k1, k2, k3 = st.columns(3)
with k1:
    _card("Total Versions", len(versions), "Tracked app releases")
with k2:
    latest = versions[0]["version_number"] if versions else "—"
    _card("Latest Version", latest, "Most recent version number")
with k3:
    deployed_count = sum(1 for v in versions if _as_text(v.get("status")).lower() == "deployed")
    _card("Deployed", deployed_count, "Currently marked deployed")

left_col, right_col = st.columns([0.52, 0.48], gap="large")

with left_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Release Tracker</div>', unsafe_allow_html=True)

    st.dataframe(versions, use_container_width=True, hide_index=True)

    st.markdown('<div class="panel-title" style="margin-top:0.9rem;">Add Version / Push Summary</div>', unsafe_allow_html=True)
    with st.form("create_version_form"):
        vcol1, vcol2 = st.columns(2)
        with vcol1:
            version_number = st.number_input("Version number", min_value=1, step=1, value=1)
            deployed_by = st.number_input("Deployed by (user id)", min_value=1, step=1, value=1)
        with vcol2:
            status = st.selectbox("Status", ["staged", "deployed", "rolled_back", "deprecated"], index=1)
            deployed_at = st.text_input("Deployed at (YYYY-MM-DD HH:MM:SS or blank)", value="")

        release_notes = st.text_area(
            "Release summary (PR-style notes)",
            value="- What changed\n- Why it changed\n- Risk/rollback notes",
            height=140,
        )
        submit_version = st.form_submit_button("Save version summary", use_container_width=True)

    if submit_version:
        payload = {
            "version_number": int(version_number),
            "deployed_by": int(deployed_by),
            "status": status,
            "release_notes": release_notes,
            "deployed_at": deployed_at or None,
        }
        try:
            create_app_version(payload)
            st.success("Version summary saved.")
            st.rerun()
        except Exception as exc:
            st.error(f"Unable to save app version: {exc}")

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Audit Log Viewer</div>', unsafe_allow_html=True)

    ac1, ac2 = st.columns(2)
    with ac1:
        audit_user_id = st.text_input("Filter by user id", value="")
    with ac2:
        action_filter = st.selectbox("Action type", ["all", "create", "update", "delete"], index=0)

    user_id_param = int(audit_user_id) if audit_user_id.isdigit() else None
    action_param = None if action_filter == "all" else action_filter

    try:
        logs = get_audit_logs(user_id=user_id_param, action_type=action_param) or []
    except Exception as exc:
        st.error(f"Unable to load audit logs: {exc}")
        logs = []

    for row in logs:
        row["performed_at"] = _fmt_dt(row.get("performed_at"))

    st.caption(f"Showing {len(logs)} audit log records")
    st.dataframe(logs, use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)
