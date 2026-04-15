import logging
from datetime import datetime
from typing import Any

import streamlit as st

from modules.admin_api import get_support_tickets, update_support_ticket
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide", page_title="SplitMates | Admin Tickets")
SideBarLinks()


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def fmt_dt(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", ""))
        except ValueError:
            return value
    if isinstance(value, datetime):
        return value.strftime("%b %d, %I:%M %p")
    return str(value)


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
        .ticket-page-title { font-size: 2.1rem; font-weight: 800; margin-bottom: 0.1rem; }
        .ticket-page-subtitle { color: #667085; font-size: 1rem; margin-bottom: 1rem; }
        .metric-card {
            background: white;
            border: 1px solid #EAECF0;
            border-radius: 20px;
            padding: 1rem 1rem 0.85rem 1rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
            height: 100%;
        }
        .metric-label { color: #667085; font-size: 0.83rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
        .metric-value { color: #101828; font-size: 2.4rem; font-weight: 800; line-height: 1; margin-top: 0.15rem; }
        .metric-note { color: #475467; font-size: 0.85rem; margin-top: 0.45rem; }
        .panel {
            background: white;
            border: 1px solid #EAECF0;
            border-radius: 20px;
            padding: 1rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }
        .panel-title { font-size: 1.12rem; font-weight: 700; margin-bottom: 0.35rem; }
        .ticket-row {
            padding: 0.8rem 0;
            border-bottom: 1px solid #EAECF0;
        }
        .ticket-row:last-child { border-bottom: none; }
        .ticket-title { font-weight: 700; color: #101828; font-size: 0.98rem; }
        .ticket-meta { color: #667085; font-size: 0.85rem; margin-top: 0.18rem; }
        .pill {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            margin-top: 0.3rem;
            margin-right: 0.35rem;
            background: #F2F4F7;
            color: #344054;
        }
        .pill-open { background: #ECFDF3; color: #027A48; }
        .pill-progress { background: #FEF3C7; color: #B54708; }
        .pill-closed { background: #EFF8FF; color: #175CD3; }
        .pill-high { background: #FEF3F2; color: #B42318; }
        .pill-medium { background: #FFFAEB; color: #B54708; }
        .pill-low { background: #ECFDF3; color: #027A48; }
        .detail-value { color: #101828; font-weight: 600; }
        .detail-label { color: #667085; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 700; }
        .ticket-divider { border-top: 1px solid #EAECF0; margin: 0.85rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="ticket-page-title">Support Tickets</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ticket-page-subtitle">Review user issues, filter by urgency, and update ticket status without leaving the page.</div>',
    unsafe_allow_html=True,
)

try:
    tickets = get_support_tickets() or []
except Exception as exc:
    st.error(f"Unable to load support tickets: {exc}")
    st.stop()

status_order = ["open", "in_progress", "closed"]
priority_order = ["high", "medium", "low"]
status_counts = {status: 0 for status in status_order}
priority_counts = {priority: 0 for priority in priority_order}
for ticket in tickets:
    status_counts[_as_text(ticket.get("status")).lower()] = status_counts.get(_as_text(ticket.get("status")).lower(), 0) + 1
    priority_counts[_as_text(ticket.get("priority")).lower()] = priority_counts.get(_as_text(ticket.get("priority")).lower(), 0) + 1

k1, k2, k3, k4 = st.columns(4)
with k1:
    _card("Total Tickets", len(tickets), "All support requests")
with k2:
    _card("Open", status_counts.get("open", 0), "Needs attention")
with k3:
    _card("In Progress", status_counts.get("in_progress", 0), "Being handled")
with k4:
    _card("High Priority", priority_counts.get("high", 0), "Urgent queue")

filter_col, list_col = st.columns([0.34, 0.66], gap="large")

selected_ticket_id = None
filtered_tickets: list[dict[str, Any]] = tickets

with filter_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Filters</div>', unsafe_allow_html=True)

    search_term = st.text_input("Search tickets", placeholder="Search title, description, or user id")
    selected_statuses = st.multiselect("Status", status_order, default=status_order)
    selected_priorities = st.multiselect("Priority", priority_order, default=priority_order)

    if search_term:
        search_term_lower = search_term.lower()
        filtered_tickets = [
            ticket
            for ticket in filtered_tickets
            if search_term_lower in _as_text(ticket.get("title")).lower()
            or search_term_lower in _as_text(ticket.get("description")).lower()
            or search_term_lower in _as_text(ticket.get("ticket_id")).lower()
            or search_term_lower in _as_text(ticket.get("submitted_by")).lower()
        ]

    filtered_tickets = [
        ticket
        for ticket in filtered_tickets
        if _as_text(ticket.get("status")).lower() in selected_statuses
        and _as_text(ticket.get("priority")).lower() in selected_priorities
    ]

    st.caption(f"Showing {len(filtered_tickets)} of {len(tickets)} tickets")

    if filtered_tickets:
        selected_ticket_id = st.selectbox(
            "Select ticket",
            [ticket["ticket_id"] for ticket in filtered_tickets],
            format_func=lambda ticket_id: f"#{ticket_id} — {next((t.get('title') or 'Untitled Ticket') for t in filtered_tickets if t.get('ticket_id') == ticket_id)}",
        )
        st.divider()
        st.markdown("<div class='panel-title'>Filtered List</div>", unsafe_allow_html=True)
        for ticket in filtered_tickets[:8]:
            status = _as_text(ticket.get("status")).lower()
            priority = _as_text(ticket.get("priority")).lower()
            status_class = {"open": "pill-open", "in_progress": "pill-progress", "closed": "pill-closed"}.get(status, "")
            priority_class = {"high": "pill-high", "medium": "pill-medium", "low": "pill-low"}.get(priority, "")
            st.markdown(
                f"""
                <div class="ticket-row">
                    <div class="ticket-title">{_as_text(ticket.get('title')) or 'Untitled Ticket'}</div>
                    <div class="ticket-meta">Ticket #{ticket.get('ticket_id')} • {_as_text(ticket.get('first_name'))} {_as_text(ticket.get('last_name'))} • {fmt_dt(ticket.get('created_at'))}</div>
                    <div>
                        <span class="pill {status_class}">{status.replace('_', ' ').title() if status else 'Unknown'}</span>
                        <span class="pill {priority_class}">{priority.title() if priority else 'Unknown'}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No tickets match the selected filters.")

    st.markdown("</div>", unsafe_allow_html=True)

with list_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Ticket Details</div>', unsafe_allow_html=True)

    if selected_ticket_id is None:
        st.caption("Pick a ticket from the filter panel to view and edit it here.")
    else:
        selected = next(ticket for ticket in filtered_tickets if ticket["ticket_id"] == selected_ticket_id)

        status = _as_text(selected.get("status")).lower() or "open"
        priority = _as_text(selected.get("priority")).lower() or "low"

        st.markdown(
            f"""
            <div class="ticket-row" style="padding-top:0;">
                <div class="ticket-title">{_as_text(selected.get('title')) or 'Untitled Ticket'}</div>
                <div class="ticket-meta">Submitted by user #{selected.get('submitted_by')} • Assigned to user #{selected.get('assigned_to')} • Created {fmt_dt(selected.get('created_at'))}</div>
                <div>
                    <span class="pill {('pill-open' if status == 'open' else 'pill-progress' if status == 'in_progress' else 'pill-closed')}">{status.replace('_', ' ').title()}</span>
                    <span class="pill {('pill-high' if priority == 'high' else 'pill-medium' if priority == 'medium' else 'pill-low')}">{priority.title()}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if selected.get("description"):
            st.markdown("<div class='ticket-divider'></div>", unsafe_allow_html=True)
            st.markdown("<div class='detail-label'>Description</div>", unsafe_allow_html=True)
            st.write(_as_text(selected.get("description")))

        left_detail, right_detail = st.columns(2)
        with left_detail:
            st.markdown("<div class='detail-label'>Resolved At</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='detail-value'>{fmt_dt(selected.get('resolved_at')) or '—'}</div>", unsafe_allow_html=True)
        with right_detail:
            st.markdown("<div class='detail-label'>Last Updated</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='detail-value'>{fmt_dt(selected.get('created_at')) or '—'}</div>", unsafe_allow_html=True)

        st.markdown("<div class='ticket-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>Edit Ticket</div>", unsafe_allow_html=True)

        with st.form("ticket_update_form"):
            edit_col1, edit_col2 = st.columns(2)
            with edit_col1:
                status_value = st.selectbox(
                    "Status",
                    status_order,
                    index=status_order.index(status) if status in status_order else 0,
                )
                priority_value = st.selectbox(
                    "Priority",
                    ["low", "medium", "high"],
                    index=["low", "medium", "high"].index(priority) if priority in ["low", "medium", "high"] else 0,
                )
                assigned_to = st.number_input(
                    "Assigned to user id",
                    min_value=1,
                    value=int(selected.get("assigned_to") or 1),
                )
            with edit_col2:
                title = st.text_input("Title", value=_as_text(selected.get("title")))
                resolved_at = st.text_input(
                    "Resolved at (YYYY-MM-DD HH:MM:SS or blank)",
                    value=fmt_dt(selected.get("resolved_at")),
                )
            description = st.text_area("Description", value=_as_text(selected.get("description")), height=140)
            submitted = st.form_submit_button("Save ticket changes", use_container_width=True)

        if submitted:
            payload = {
                "status": status_value,
                "priority": priority_value,
                "title": title,
                "description": description,
                "assigned_to": int(assigned_to),
                "resolved_at": resolved_at or None,
            }
            try:
                update_support_ticket(selected_ticket_id, payload)
                st.success("Ticket updated.")
                st.rerun()
            except Exception as exc:
                st.error(f"Unable to update ticket: {exc}")

    st.markdown("</div>", unsafe_allow_html=True)
