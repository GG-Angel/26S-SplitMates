import logging
import streamlit as st
import pandas as pd
from api.client import client
from modules.nav import SideBarLinks
from utils import parse_mysql_datetime

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

inactive_users: list[dict] = client.get("/analyst/users/inactive")

# --- Content ---

st.title("Inactive Users")
st.write("Monitor user dropoff and identify accounts that have gone inactive.")

st.divider()

if inactive_users:
    df = pd.DataFrame(inactive_users)

    total = len(df)
    truly_inactive = len(df[df["account_status"] == "inactive"])
    at_risk = len(df[df["account_status"] == "active"])

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Total Flagged Users", total)
    with metric_col2:
        st.metric("Inactive Accounts", truly_inactive)
    with metric_col3:
        st.metric("At Risk (30+ days)", at_risk)

    st.divider()

    left_col, right_col = st.columns([2, 1], gap="medium")

    with left_col:
        st.subheader("User Table")

        status_filter = st.selectbox("Filter by Status", ["All", "inactive", "active"])

        display_df = df.copy()
        if status_filter != "All":
            display_df = display_df[display_df["account_status"] == status_filter]

        display_df["last_session"] = display_df["last_session"].apply(
            lambda x: parse_mysql_datetime(x).strftime("%b %d, %Y") if x else "Never"
        )
        display_df = display_df[["first_name", "last_name", "email", "account_status", "last_session"]]
        display_df.columns = ["First Name", "Last Name", "Email", "Status", "Last Session"]

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Export CSV",
            data=csv,
            file_name="inactive_users.csv",
            mime="text/csv",
        )

    with right_col:
        st.subheader("Status Breakdown")
        status_counts = df["account_status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        st.dataframe(status_counts, use_container_width=True, hide_index=True)

else:
    st.write("No inactive users found.")
