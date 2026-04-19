import logging
import streamlit as st
import pandas as pd
from api.client import client
from modules.nav import SideBarLinks
from utils import parse_mysql_datetime

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide", page_title="SplitMates | Inactive Users")
SideBarLinks()

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
        .metric-value-red { color: #bd0b0b; font-size: 2.4rem; font-weight: 800; line-height: 1; margin-top: 0.15rem; }
        .metric-note { color: #475467; font-size: 0.85rem; margin-top: 0.45rem; }
        .panel {
            background: white;
            border: 1px solid #EAECF0;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }
        .panel-title { font-size: 1.15rem; font-weight: 700; margin-bottom: 0.75rem; color: #101828; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">Inactive Users</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Monitor user dropoff and identify accounts that have gone inactive.</div>', unsafe_allow_html=True)
if st.button("🔄 Refresh Data"):
    st.rerun()

total = len(inactive_users)
truly_inactive = len([u for u in inactive_users if u.get("account_status") == "inactive"])
at_risk = len([u for u in inactive_users if u.get("account_status") == "active"])

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""<div class="metric-card">
            <div class="metric-label">TOTAL FLAGGED</div>
            <div class="metric-value">{total}</div>
            <div class="metric-note">Users flagged for inactivity</div>
        </div>""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""<div class="metric-card">
            <div class="metric-label">INACTIVE ACCOUNTS</div>
            <div class="metric-value-red">{truly_inactive}</div>
            <div class="metric-note">Account status: inactive</div>
        </div>""",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""<div class="metric-card">
            <div class="metric-label">AT RISK (14+ DAYS)</div>
            <div class="metric-value">{at_risk}</div>
            <div class="metric-note">No session in 14+ days</div>
        </div>""",
        unsafe_allow_html=True,
    )

if st.button("🔄 Refresh Data"):
    st.rerun()
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='panel-title' style='font-size:1.15rem;font-weight:700;color:white;margin-bottom:0.75rem;'>User Engagement Table</div>", unsafe_allow_html=True)

if inactive_users:
    status_filter = st.selectbox("Filter by Status", ["All", "inactive", "active"])
    display = [u for u in inactive_users if status_filter == "All" or u.get("account_status") == status_filter]

    rows = []
    for u in display:
        last = u.get("last_session")
        try:
            last_fmt = parse_mysql_datetime(last).strftime("%b %d, %Y") if last else "Never"
        except Exception:
            last_fmt = "Never"
        rows.append({
            "First Name": u.get("first_name", ""),
            "Last Name": u.get("last_name", ""),
            "Email": u.get("email", ""),
            "Status": u.get("account_status", ""),
            "Last Session": last_fmt,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False)
    st.download_button(
        label="Export CSV",
        data=csv,
        file_name="inactive_users.csv",
        mime="text/csv",
    )
else:
    st.caption("No inactive users found.")


