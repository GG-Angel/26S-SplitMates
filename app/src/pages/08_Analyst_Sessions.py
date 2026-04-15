import logging
import streamlit as st
import pandas as pd
from api.client import client
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

sessions: list[dict] = client.get("/analyst/sessions")
engagement: list[dict] = client.get("/analyst/groups/engagement")

# --- Content ---

st.title("User Sessions & Engagement")
st.write("Analyze session trends and how engagement scales with household size.")

st.divider()

if sessions:
    df = pd.DataFrame(sessions)

    total_sessions = int(df["total_sessions"].sum())
    avg_duration = round(float(df["avg_duration_mins"].mean()), 1)
    unique_users = int(df["user_id"].nunique())

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Total Sessions", total_sessions)
    with metric_col2:
        st.metric("Avg Session (min)", avg_duration)
    with metric_col3:
        st.metric("Active Users", unique_users)

    st.divider()

    left_col, right_col = st.columns(2, gap="medium")

    with left_col:
        st.subheader("Activity by Hour of Day")
        hourly = df.groupby("hour_of_day")["total_sessions"].sum().reset_index()
        hourly.columns = ["Hour", "Sessions"]
        st.bar_chart(hourly.set_index("Hour"))

    with right_col:
        st.subheader("Avg Session Duration by User")
        user_avg = df.groupby(["first_name", "last_name"])["avg_duration_mins"].mean().reset_index()
        user_avg["Name"] = user_avg["first_name"] + " " + user_avg["last_name"]
        user_avg = user_avg[["Name", "avg_duration_mins"]].rename(
            columns={"avg_duration_mins": "Avg Duration (min)"}
        )
        st.dataframe(user_avg, use_container_width=True, hide_index=True)

else:
    st.write("No session data available.")

st.divider()

st.subheader("Engagement by Household Size")
if engagement:
    df_eng = pd.DataFrame(engagement)
    df_eng.columns = [
        "Household Size", "Total Groups", "Avg Chores",
        "Avg Completed Chores", "Avg Bills", "Avg Events"
    ]
    st.dataframe(df_eng, use_container_width=True, hide_index=True)

    st.write("**Avg Chores vs Household Size**")
    st.line_chart(df_eng.set_index("Household Size")[["Avg Chores", "Avg Completed Chores"]])
else:
    st.write("No engagement data available.")
