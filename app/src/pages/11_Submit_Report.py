import streamlit as st

from modules.admin_api import get_admin_users, submit_user_report
from modules.nav import SideBarLinks

st.set_page_config(layout="wide", page_title="SplitMates | Submit Report")
SideBarLinks()

st.markdown(
    """
    <style>
        .page-title { font-size: 2.1rem; font-weight: 800; margin-bottom: 0.1rem; }
        .page-subtitle { color: #667085; font-size: 1rem; margin-bottom: 1.5rem; }
        .panel {
            background: #F8FAFC;
            border: 1px solid #EAECF0;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }
        .panel-title { font-size: 1.12rem; font-weight: 700; margin-bottom: 0.35rem; color: #101828; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">Submit a Report</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Report another user for misconduct or policy violations. All reports are reviewed by admins.</div>',
    unsafe_allow_html=True,
)

user = st.session_state.get("user", {})
reported_by = user.get("user_id")

try:
    all_users = get_admin_users() or []
except Exception:
    all_users = []

reportable = [u for u in all_users if u.get("user_id") != reported_by]

with st.form("submit_report_form"):
    if reportable:
        user_options = {
            u["user_id"]: f"{u.get('first_name', '')} {u.get('last_name', '')}".strip() or f"User #{u['user_id']}"
            for u in reportable
        }
        selected_user_id = st.selectbox(
            "Select user to report",
            options=list(user_options.keys()),
            format_func=lambda uid: user_options[uid],
        )
    else:
        st.warning("No other users found.")
        selected_user_id = None

    reason = st.text_area(
        "Reason for report",
        placeholder="Describe the issue clearly and factually...",
        height=150,
    )
    submitted = st.form_submit_button("Submit Report", use_container_width=True)

if submitted:
    if selected_user_id is None:
        st.error("No user selected.")
    elif not reason.strip():
        st.error("Please provide a reason for the report.")
    else:
        try:
            submit_user_report({
                "reported_user": int(selected_user_id),
                "reported_by": reported_by,
                "reason": reason.strip(),
            })
            st.success("Your report has been submitted and will be reviewed by an admin.")
        except Exception as exc:
            st.error(f"Unable to submit report: {exc}")
