import logging
from datetime import datetime
from typing import Any

import streamlit as st

from modules.admin_api import (
    get_user_bans,
    get_user_reports,
    issue_user_ban,
    lift_user_ban,
    update_user_ban,
    update_user_report,
)
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide", page_title="SplitMates | Admin User Reports")
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
        .metric-value { color: #101828; font-size: 2.4rem; font-weight: 800; line-height: 1; margin-top: 0.15rem; }
        .metric-note { color: #475467; font-size: 0.85rem; margin-top: 0.45rem; }
        .panel {
            background: #F8FAFC;
            border: 1px solid #EAECF0;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }
        .panel-title { font-size: 1.12rem; font-weight: 700; margin-bottom: 0.35rem; color: #101828; }
        .row {
            padding: 0.8rem 0;
            border-bottom: 1px solid #EAECF0;
        }
        .row:last-child { border-bottom: none; }
        .row-title { font-weight: 700; color: #101828; font-size: 0.98rem; }
        .row-meta { color: #667085; font-size: 0.85rem; margin-top: 0.18rem; }
        .pill {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 8px;
            font-size: 0.76rem;
            font-weight: 700;
            margin-top: 0.3rem;
            margin-right: 0.35rem;
            background: #F2F4F7;
            color: #344054;
        }
        .pill-pending { background: #FEF3F2; color: #B42318; }
        .pill-review { background: #FFFAEB; color: #B54708; }
        .pill-resolved { background: #ECFDF3; color: #027A48; }
        .pill-dismissed { background: #EFF8FF; color: #175CD3; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">User Reports</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Moderate report queue with fast filters and in-place status updates.</div>',
    unsafe_allow_html=True,
)


try:
    reports = get_user_reports() or []
except Exception as exc:
    st.error(f"Unable to load user reports: {exc}")
    st.stop()

status_order = ["pending", "under_review", "resolved", "dismissed"]
status_counts = {s: 0 for s in status_order}
for report in reports:
    key = _as_text(report.get("status")).lower() or "pending"
    status_counts[key] = status_counts.get(key, 0) + 1

k1, k2, k3, k4 = st.columns(4)
with k1:
    _card("Total Reports", len(reports), "All submissions")
with k2:
    _card("Pending", status_counts.get("pending", 0), "Awaiting triage")
with k3:
    _card("Under Review", status_counts.get("under_review", 0), "Investigation in progress")
with k4:
    _card("Resolved", status_counts.get("resolved", 0), "Completed cases")

left_col, right_col = st.columns([0.36, 0.64], gap="large")

filtered_reports: list[dict[str, Any]] = reports
selected_report_id = None

with left_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Filters</div>', unsafe_allow_html=True)
    search_term = st.text_input("Search reports", placeholder="Search reason, report id, or user id")
    selected_statuses = st.multiselect("Status", status_order, default=status_order)

    if search_term:
        needle = search_term.lower()
        filtered_reports = [
            report
            for report in filtered_reports
            if needle in _as_text(report.get("reason")).lower()
            or needle in _as_text(report.get("report_id")).lower()
            or needle in _as_text(report.get("reported_user")).lower()
            or needle in _as_text(report.get("reported_by")).lower()
        ]

    filtered_reports = [
        report
        for report in filtered_reports
        if (_as_text(report.get("status")).lower() or "pending") in selected_statuses
    ]

    st.caption(f"Showing {len(filtered_reports)} of {len(reports)} reports")

    if filtered_reports:
        selected_report_id = st.selectbox(
            "Select report",
            [report["report_id"] for report in filtered_reports],
            format_func=lambda report_id: f"#{report_id} — {next((_as_text(r.get('reason')) or 'No reason') for r in filtered_reports if r.get('report_id') == report_id)}",
        )
        st.divider()
        st.markdown('<div class="panel-title">Filtered List</div>', unsafe_allow_html=True)
        for report in filtered_reports[:8]:
            status = _as_text(report.get("status")).lower() or "pending"
            status_class = {
                "pending": "pill-pending",
                "under_review": "pill-review",
                "resolved": "pill-resolved",
                "dismissed": "pill-dismissed",
            }.get(status, "")
            st.markdown(
                f"""
                <div class="row">
                    <div class="row-title">Report #{report.get('report_id')}</div>
                    <div class="row-meta">Against user #{report.get('reported_user')} • By user #{report.get('reported_by')} • {fmt_dt(report.get('created_at'))}</div>
                    <div class="row-meta">{_as_text(report.get('reason')) or 'No reason provided'}</div>
                    <span class="pill {status_class}">{status.replace('_', ' ').title()}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No reports match the selected filters.")

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Report Details</div>', unsafe_allow_html=True)

    if selected_report_id is None:
        st.caption("Pick a report from the left panel to review and update it.")
    else:
        selected = next(report for report in filtered_reports if report["report_id"] == selected_report_id)

        st.markdown(
            f"""
            <div class="row" style="padding-top:0;">
                <div class="row-title">Report #{selected.get('report_id')}</div>
                <div class="row-meta">Reported user #{selected.get('reported_user')} • Reported by user #{selected.get('reported_by')}</div>
                <div class="row-meta">Created {fmt_dt(selected.get('created_at'))} • Reviewed {fmt_dt(selected.get('reviewed_at')) or 'Not reviewed yet'}</div>
                <div class="row-meta">Reason: {_as_text(selected.get('reason')) or 'No reason provided'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("report_update_form"):
            status = st.selectbox(
                "Status",
                status_order,
                index=status_order.index(_as_text(selected.get("status")).lower() or "pending"),
            )
            reviewed_by = st.number_input("Reviewed by user id", min_value=1, value=int(selected.get("reviewed_by") or 1))
            reviewed_at = st.text_input("Reviewed at (YYYY-MM-DD HH:MM:SS or blank)", value=fmt_dt(selected.get("reviewed_at")))
            submitted = st.form_submit_button("Save report changes", use_container_width=True)

        if submitted:
            payload = {
                "status": status,
                "reviewed_by": int(reviewed_by),
                "reviewed_at": reviewed_at or None,
            }
            try:
                update_user_report(selected_report_id, payload)
                st.success("Report updated.")
                st.rerun()
            except Exception as exc:
                st.error(f"Unable to update report: {exc}")

        st.divider()
        st.markdown('<div class="panel-title">Moderation Action: Ban User</div>', unsafe_allow_html=True)
        reported_user_id = int(selected.get("reported_user") or 0)

        if reported_user_id > 0:
            ban_col1, ban_col2 = st.columns([0.58, 0.42])
            with ban_col1:
                try:
                    bans = get_user_bans(reported_user_id)
                except Exception as exc:
                    bans = []
                    st.warning(f"Unable to load ban history: {exc}")

                if bans:
                    st.caption(f"Existing bans for user #{reported_user_id}")
                    st.dataframe(bans, use_container_width=True, hide_index=True)

                    selected_ban_id = st.selectbox(
                        "Select ban to edit/lift",
                        [int(ban["ban_id"]) for ban in bans],
                        format_func=lambda ban_id: f"Ban #{ban_id}",
                        key=f"report_ban_select_{selected_report_id}",
                    )
                    selected_ban = next(ban for ban in bans if int(ban["ban_id"]) == int(selected_ban_id))

                    with st.form(f"manage_report_ban_{selected_report_id}_{selected_ban_id}"):
                        updated_reason = st.text_area(
                            "Edit ban reason",
                            value=_as_text(selected_ban.get("reasons")),
                            key=f"report_edit_reason_{selected_report_id}_{selected_ban_id}",
                        )
                        updated_expires_at = st.text_input(
                            "Edit expires at (YYYY-MM-DD HH:MM:SS or blank)",
                            value=_as_text(selected_ban.get("expires_at")),
                            key=f"report_edit_expires_{selected_report_id}_{selected_ban_id}",
                        )
                        bcol1, bcol2 = st.columns(2)
                        with bcol1:
                            update_ban_submit = st.form_submit_button("Update selected ban", use_container_width=True)
                        with bcol2:
                            lift_ban_submit = st.form_submit_button("Lift selected ban", use_container_width=True)

                    if update_ban_submit:
                        try:
                            update_user_ban(
                                reported_user_id,
                                int(selected_ban_id),
                                {
                                    "reasons": updated_reason,
                                    "expires_at": updated_expires_at or None,
                                },
                            )
                            st.success(f"Ban #{selected_ban_id} updated.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Unable to update ban: {exc}")

                    if lift_ban_submit:
                        try:
                            lift_user_ban(reported_user_id, int(selected_ban_id))
                            st.success(f"Ban #{selected_ban_id} lifted.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Unable to lift ban: {exc}")
                else:
                    st.caption(f"No bans found for user #{reported_user_id}.")

            with ban_col2:
                with st.form(f"issue_ban_from_report_{selected_report_id}"):
                    issued_by = st.number_input(
                        "Issued by (admin user id)",
                        min_value=1,
                        value=1,
                        key=f"issued_by_report_{selected_report_id}",
                    )
                    reasons = st.text_area(
                        "Ban reason",
                        value=f"Escalated from report #{selected_report_id}",
                        key=f"ban_reason_report_{selected_report_id}",
                    )
                    expires_at = st.text_input(
                        "Expires at (YYYY-MM-DD HH:MM:SS or blank)",
                        value="",
                        key=f"ban_expires_report_{selected_report_id}",
                    )
                    ban_submit = st.form_submit_button("Issue ban", use_container_width=True)

                if ban_submit:
                    payload = {
                        "issued_by": int(issued_by),
                        "reasons": reasons,
                        "expires_at": expires_at or None,
                    }
                    try:
                        issue_user_ban(reported_user_id, payload)
                        st.success(f"Ban issued for user #{reported_user_id}.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Unable to issue ban: {exc}")
        else:
            st.caption("Reported user id is missing for this report.")

    st.markdown("</div>", unsafe_allow_html=True)
