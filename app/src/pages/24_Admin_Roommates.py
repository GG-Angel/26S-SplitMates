import logging
from typing import Any

import streamlit as st

from modules.admin_api import (
    get_admin_users,
    get_user_bans,
    issue_user_ban,
    lift_user_ban,
    update_user_ban,
)
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide", page_title="SplitMates | Admin Roommates")
SideBarLinks()


def _as_text(value: Any) -> str:
    if value is None:
        return ""
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
        .page-title { font-size: 2.1rem; font-weight: 800; margin-bottom: 0.1rem; }
        .page-subtitle { color: #667085; font-size: 1rem; margin-bottom: 1rem; }
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
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            margin-top: 0.3rem;
            margin-right: 0.35rem;
            background: #F2F4F7;
            color: #344054;
        }
        .pill-admin { background: #ECFDF3; color: #027A48; }
        .pill-analyst { background: #EFF8FF; color: #175CD3; }
        .pill-active { background: #ECFDF3; color: #027A48; }
        .pill-inactive { background: #FFFAEB; color: #B54708; }
        .pill-suspended { background: #FEF3F2; color: #B42318; }
        .pill-pending { background: #F2F4F7; color: #344054; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">Roommates</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Browse user accounts, filter by status, and inspect role flags.</div>',
    unsafe_allow_html=True,
)

try:
    users = get_admin_users() or []
except Exception as exc:
    st.error(f"Unable to load users: {exc}")
    st.stop()

active_count = sum(1 for user in users if _as_text(user.get("account_status")).lower() == "active")
admin_count = sum(1 for user in users if bool(user.get("is_admin")))
analyst_count = sum(1 for user in users if bool(user.get("is_analyst")))

k1, k2, k3, k4 = st.columns(4)
with k1:
    _card("Total Users", len(users), "Accounts in system")
with k2:
    _card("Active", active_count, "Currently active")
with k3:
    _card("Admins", admin_count, "Admin-privileged users")
with k4:
    _card("Analysts", analyst_count, "Analyst-privileged users")

left_col, right_col = st.columns([0.36, 0.64], gap="large")

filtered_users: list[dict[str, Any]] = users
selected_user_id = None

with left_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Filters</div>', unsafe_allow_html=True)
    search_term = st.text_input("Search users", placeholder="Search name, email, or user id")
    status_options = sorted({_as_text(user.get("account_status")).lower() or "pending" for user in users}) or ["pending"]
    selected_statuses = st.multiselect("Account status", status_options, default=status_options)
    role_filter = st.selectbox("Role filter", ["all", "admins", "analysts", "standard users"], index=0)

    if search_term:
        needle = search_term.lower()
        filtered_users = [
            user
            for user in filtered_users
            if needle in _as_text(user.get("first_name")).lower()
            or needle in _as_text(user.get("last_name")).lower()
            or needle in _as_text(user.get("email")).lower()
            or needle in _as_text(user.get("user_id")).lower()
        ]

    filtered_users = [
        user
        for user in filtered_users
        if (_as_text(user.get("account_status")).lower() or "pending") in selected_statuses
    ]

    if role_filter == "admins":
        filtered_users = [user for user in filtered_users if bool(user.get("is_admin"))]
    elif role_filter == "analysts":
        filtered_users = [user for user in filtered_users if bool(user.get("is_analyst"))]
    elif role_filter == "standard users":
        filtered_users = [
            user for user in filtered_users if not bool(user.get("is_admin")) and not bool(user.get("is_analyst"))
        ]

    st.caption(f"Showing {len(filtered_users)} of {len(users)} users")

    if filtered_users:
        selected_user_id = st.selectbox(
            "Select user",
            [user["user_id"] for user in filtered_users],
            format_func=lambda user_id: f"#{user_id} — {next((_as_text(u.get('first_name')) + ' ' + _as_text(u.get('last_name'))).strip() or 'Unnamed User' for u in filtered_users if u.get('user_id') == user_id)}",
        )
        st.divider()
        st.markdown('<div class="panel-title">Filtered List</div>', unsafe_allow_html=True)
        for user in filtered_users[:10]:
            full_name = (_as_text(user.get("first_name")) + " " + _as_text(user.get("last_name"))).strip() or "Unnamed User"
            status = _as_text(user.get("account_status")).lower() or "pending"
            status_class = {
                "active": "pill-active",
                "inactive": "pill-inactive",
                "suspended": "pill-suspended",
                "pending": "pill-pending",
            }.get(status, "pill-pending")
            st.markdown(
                f"""
                <div class="row">
                    <div class="row-title">{full_name}</div>
                    <div class="row-meta">User #{user.get('user_id')} • {_as_text(user.get('email'))}</div>
                    <span class="pill {status_class}">{status.title()}</span>
                    {('<span class="pill pill-admin">Admin</span>' if bool(user.get('is_admin')) else '')}
                    {('<span class="pill pill-analyst">Analyst</span>' if bool(user.get('is_analyst')) else '')}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No users match the selected filters.")

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">User Details</div>', unsafe_allow_html=True)

    if selected_user_id is None:
        st.caption("Select a user from the left panel to inspect details.")
    else:
        selected = next(user for user in filtered_users if user["user_id"] == selected_user_id)
        full_name = (_as_text(selected.get("first_name")) + " " + _as_text(selected.get("last_name"))).strip() or "Unnamed User"
        status = _as_text(selected.get("account_status")).lower() or "pending"
        st.subheader(full_name)
        st.write(f"User #{selected.get('user_id')} • {_as_text(selected.get('email'))}")
        st.write(f"Created at: {_as_text(selected.get('created_at')) or 'N/A'}")
        role_labels: list[str] = []
        if bool(selected.get("is_admin")):
            role_labels.append("Admin")
        if bool(selected.get("is_analyst")):
            role_labels.append("Analyst")
        roles_text = ", ".join(role_labels) if role_labels else "Standard User"
        st.write(f"Status: {status.title()} | Roles: {roles_text}")

        st.divider()
        st.markdown('<div class="panel-title">Moderation Action: Ban User</div>', unsafe_allow_html=True)

        try:
            bans = get_user_bans(int(selected_user_id))
        except Exception as exc:
            bans = []
            st.warning(f"Unable to load ban history: {exc}")

        if bans:
            st.caption(f"Existing bans for user #{selected_user_id}")
            st.dataframe(bans, use_container_width=True, hide_index=True)
        else:
            st.caption(f"No bans found for user #{selected_user_id}.")

        if bans:
            action_col1, action_col2 = st.columns([0.5, 0.5], gap="large")
            with action_col1:
                selected_ban_id = st.selectbox(
                    "Select ban to manage",
                    [int(ban["ban_id"]) for ban in bans],
                    format_func=lambda ban_id: f"Ban #{ban_id}",
                )
                selected_ban = next(ban for ban in bans if int(ban["ban_id"]) == int(selected_ban_id))

                with st.form(f"manage_ban_{selected_user_id}_{selected_ban_id}"):
                    updated_reason = st.text_area(
                        "Edit reason",
                        value=_as_text(selected_ban.get("reasons")),
                        key=f"edit_reason_{selected_user_id}_{selected_ban_id}",
                    )
                    updated_expires_at = st.text_input(
                        "Edit expires at (YYYY-MM-DD HH:MM:SS or blank)",
                        value=_as_text(selected_ban.get("expires_at")),
                        key=f"edit_expires_{selected_user_id}_{selected_ban_id}",
                    )
                    edit_col, lift_col = st.columns(2)
                    with edit_col:
                        update_clicked = st.form_submit_button("Update ban", use_container_width=True)
                    with lift_col:
                        lift_clicked = st.form_submit_button("Lift ban", use_container_width=True)

                if update_clicked:
                    try:
                        update_user_ban(
                            int(selected_user_id),
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

                if lift_clicked:
                    try:
                        lift_user_ban(int(selected_user_id), int(selected_ban_id))
                        st.success(f"Ban #{selected_ban_id} lifted.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Unable to lift ban: {exc}")

            with action_col2:
                with st.form(f"issue_ban_roommate_{selected_user_id}"):
                    issued_by = st.number_input(
                        "Issued by (admin user id)",
                        min_value=1,
                        value=1,
                        key=f"issued_by_roommate_{selected_user_id}",
                    )
                    reasons = st.text_area(
                        "Ban reason",
                        value="Policy violation",
                        key=f"ban_reason_roommate_{selected_user_id}",
                    )
                    expires_at = st.text_input(
                        "Expires at (YYYY-MM-DD HH:MM:SS or blank)",
                        value="",
                        key=f"ban_expires_roommate_{selected_user_id}",
                    )
                    ban_submit = st.form_submit_button("Issue ban", use_container_width=True)

                if ban_submit:
                    payload = {
                        "issued_by": int(issued_by),
                        "reasons": reasons,
                        "expires_at": expires_at or None,
                    }
                    try:
                        issue_user_ban(int(selected_user_id), payload)
                        st.success(f"Ban issued for user #{selected_user_id}.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Unable to issue ban: {exc}")
        else:
            st.markdown("#### Issue Ban")
            with st.form(f"issue_ban_roommate_{selected_user_id}_full"):
                issued_by = st.number_input(
                    "Issued by (admin user id)",
                    min_value=1,
                    value=1,
                    key=f"issued_by_roommate_{selected_user_id}_full",
                )
                reasons = st.text_area(
                    "Ban reason",
                    value="Policy violation",
                    key=f"ban_reason_roommate_{selected_user_id}_full",
                )
                expires_at = st.text_input(
                    "Expires at (YYYY-MM-DD HH:MM:SS or blank)",
                    value="",
                    key=f"ban_expires_roommate_{selected_user_id}_full",
                )
                ban_submit = st.form_submit_button("Issue ban", use_container_width=True)

            if ban_submit:
                payload = {
                    "issued_by": int(issued_by),
                    "reasons": reasons,
                    "expires_at": expires_at or None,
                }
                try:
                    issue_user_ban(int(selected_user_id), payload)
                    st.success(f"Ban issued for user #{selected_user_id}.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Unable to issue ban: {exc}")

    st.markdown("</div>", unsafe_allow_html=True)
