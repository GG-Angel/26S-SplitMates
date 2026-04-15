import logging
import streamlit as st
import pandas as pd
from api.client import client
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

audit_logs: list[dict] = client.get("/analyst/audit-logs")
completed_chores: list[dict] = client.get("/analyst/chores/completed")

# --- Content ---

st.title("Feature Usage")
st.write("Track which features and actions are used most across the platform.")

st.divider()

left_col, right_col = st.columns(2, gap="medium")

with left_col:
    st.subheader("Audit Log Activity")
    if audit_logs:
        df = pd.DataFrame(audit_logs)
        df.columns = ["Action Type", "Target Table", "Total Uses"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.write("**By Target Table**")
        table_totals = df.groupby("Target Table")["Total Uses"].sum().reset_index()
        table_totals = table_totals.sort_values("Total Uses", ascending=False)
        st.bar_chart(table_totals.set_index("Target Table"))
    else:
        st.write("No audit log data available.")

with right_col:
    st.subheader("Chore Completion Trends")
    if completed_chores:
        df_chores = pd.DataFrame(completed_chores)
        df_chores.columns = ["Title", "Effort", "Times Completed"]
        st.dataframe(df_chores, use_container_width=True, hide_index=True)

        st.write("**By Effort Level**")
        effort_totals = df_chores.groupby("Effort")["Times Completed"].sum().reset_index()
        st.bar_chart(effort_totals.set_index("Effort"))
    else:
        st.write("No completed chore data available.")
