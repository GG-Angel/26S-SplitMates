import logging
from datetime import datetime
from typing import Any, cast

import requests
import streamlit as st

from modules.admin_api import get_admin_summary
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide", page_title="SplitMates | Admin Dashboard")
SideBarLinks()


def _safe_dt(dt_value):
    if not dt_value:
        return ""
    if isinstance(dt_value, str):
        try:
            dt_value = datetime.fromisoformat(dt_value.replace("Z", ""))
        except ValueError:
            return dt_value
    if isinstance(dt_value, datetime):
        return dt_value.strftime("%b %d, %I:%M %p")
    return str(dt_value)


@st.cache_data(ttl=30)
def load_summary():
    return get_admin_summary()


fallback_summary: dict[str, Any] = {
    "total_users": 0,
    "active_households": 0,
    "open_tickets": 0,
    "inactive_users": 0,
    "urgent_tickets": 0,
    "urgent_message": "No urgent tickets right now",
    "recent_tickets": [],
    "recent_activity": [],
}

summary: dict[str, Any] = dict(fallback_summary)
error = None
try:
    summary = load_summary() or fallback_summary
except (requests.RequestException, ValueError) as exc:
    error = str(exc)

st.markdown(
    """
    <style>
        .admin-title { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.1rem; }
        .admin-subtitle { color: #667085; font-size: 1rem; margin-top: 0; }
        .metric-card {
            background: #1E293B !important;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1rem 1rem 0.85rem 1rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            height: 100%;
            color: #F1F5F9;
        }
        .metric-label { color: #94A3B8 !important; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.04em; }
        .metric-value { color: #F1F5F9 !important; font-size: 2.6rem; font-weight: 800; line-height: 1; margin-top: 0.15rem; }
        .metric-note { color: #CBD5E1 !important; font-size: 0.85rem; margin-top: 0.45rem; }
        .panel {
            background: #1E293B !important;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1rem 1rem 0.6rem 1rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            height: 100%;
            color: #F1F5F9;
        }
        .panel-title { font-size: 1.15rem; font-weight: 700; margin-bottom: 0.5rem; color: #F1F5F9 !important; }
        .ticket-row, .activity-row {
            padding: 0.75rem 0;
            border-bottom: 1px solid #334155;
        }
        .ticket-row:last-child, .activity-row:last-child { border-bottom: none; }
        .row-title { font-weight: 600; font-size: 0.98rem; margin-bottom: 0.1rem; color: #F1F5F9 !important; }
        .row-meta { color: #94A3B8 !important; font-size: 0.86rem; }
        .pill {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 700;
            background: #334155;
            color: #CBD5E1;
            margin-top: 0.25rem;
        }
        .pill-urgent { background: #4C0519; color: #FCA5A5; }
        .pill-open { background: #064E3B; color: #6EE7B7; }
        .pill-resolved { background: #1E3A5F; color: #93C5FD; }
        .pill-closed { background: #334155; color: #CBD5E1; }
        .banner {
            background: #4C0519;
            border: 1px solid #991B1B;
            color: #FCA5A5;
            border-radius: 16px;
            padding: 0.9rem 1rem;
            font-weight: 600;
            margin: 0.5rem 0 1rem 0;
        }
        .sidebar-faux-header { font-size: 1.35rem; font-weight: 800; margin-top: 0.4rem; }
        .sidebar-user { color: #94A3B8; font-weight: 600; margin: 0.2rem 0 0.8rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="admin-title">Welcome back, {}!</div>'.format(st.session_state.get("first_name", "Admin")), unsafe_allow_html=True)

if error:
    st.warning("Dashboard summary is temporarily unavailable. Showing fallback values.")

col1, col2, col3, col4 = st.columns(4)

cards = [
    ("TOTAL USERS", summary.get("total_users", 0), "+12 this week"),
    ("ACTIVE HOUSEHOLDS", summary.get("active_households", 0), "+4 this week"),
    ("OPEN TICKETS", summary.get("open_tickets", 0), f"{summary.get('urgent_tickets', 0)} urgent"),
    ("INACTIVE USERS", summary.get("inactive_users", 0), "30+ days"),
]

for col, (label, value, note) in zip((col1, col2, col3, col4), cards):
    with col:
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
    f"<div class='banner'>{summary.get('urgent_message', 'No urgent tickets right now')}</div>",
    unsafe_allow_html=True,
)

left_col, right_col = st.columns(2)

with left_col:
    st.markdown("<div class='panel'><div class='panel-title'>Recent Tickets</div>", unsafe_allow_html=True)
    recent_tickets = cast(list[dict[str, Any]], summary.get("recent_tickets", []))
    if not recent_tickets:
        st.caption("No support tickets found yet.")
    else:
        for ticket in recent_tickets:
            priority_class = "pill-urgent" if ticket.get("priority") == "high" else ""
            ticket_status = str(ticket.get("status") or "")
            status_class = {
                "open": "pill-open",
                "closed": "pill-closed",
            }.get(ticket_status, "pill-resolved")
            st.markdown(
                f"""
                <div class="ticket-row">
                    <div class="row-title">{str(ticket.get('title') or 'Untitled Ticket')}</div>
                    <div class="row-meta">Ticket #{ticket.get('ticket_id')} • {str(ticket.get('first_name') or '')} {str(ticket.get('last_name') or '')} • {_safe_dt(ticket.get('created_at'))}</div>
                    <div style="margin-top:0.35rem;">
                        <span class="pill {priority_class}">{str(ticket.get('priority') or '').title()}</span>
                        <span class="pill {status_class}">{str(ticket.get('status') or '').replace('_', ' ').title()}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown("<div class='panel'><div class='panel-title'>Recent Activity</div>", unsafe_allow_html=True)
    recent_activity = cast(list[dict[str, Any]], summary.get("recent_activity", []))
    if not recent_activity:
        st.caption("No audit activity found yet.")
    else:
        for item in recent_activity:
            st.markdown(
                f"""
                <div class="activity-row">
                    <div class="row-title">{str(item.get('details') or 'Activity')}</div>
                    <div class="row-meta">{str(item.get('first_name') or '')} {str(item.get('last_name') or '')} • {str(item.get('action_type') or '').title()} on {str(item.get('target_table') or '')} #{item.get('target_id', '')}</div>
                    <div class="row-meta">{_safe_dt(item.get('performed_at'))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)
