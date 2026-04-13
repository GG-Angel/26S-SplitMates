import streamlit as st
from api.client import client
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

st.title("Create Event")

group = st.session_state["group"]
group_id = group["group_id"]
user_id = st.session_state["user"]["user_id"]

title = st.text_input("Title")
starts_date = st.date_input("Start Date")
starts_time = st.time_input("Start Time")
ends_date = st.date_input("End Date")
ends_time = st.time_input("End Time")
is_private = st.checkbox("Private event")

if st.button("Create", type="primary"):
    if not title:
        st.error("Please enter a title.")
    elif f"{ends_date} {ends_time}" <= f"{starts_date} {starts_time}":
        st.error("End must be after start.")
    else:
        client.post(f"groups/{group_id}/events", json={
            "user_id": user_id,
            "title": title,
            "starts_at": f"{starts_date} {starts_time}",
            "ends_at": f"{ends_date} {ends_time}",
            "is_private": is_private,
        })
        st.switch_page("pages/03_Group_Events.py")
