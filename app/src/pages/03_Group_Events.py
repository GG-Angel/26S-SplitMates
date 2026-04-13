import streamlit as st
from datetime import datetime
from api.client import client
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

group = st.session_state["group"]
group_id = group["group_id"]

events = client.get(f"groups/{group_id}/events")

st.title("Events")

if st.button("Create Event", type="primary"):
    st.switch_page("pages/04_Create_Event.py")

if not events:
    st.write("No events yet.")
else:
    cols = st.columns(2)
    for index, event in enumerate(events):
        with cols[index % 2]:
            with st.container(border=True):
                st.subheader(event["title"])
                starts = datetime.strptime(event["starts_at"], "%a, %d %b %Y %H:%M:%S %Z")
                ends = datetime.strptime(event["ends_at"], "%a, %d %b %Y %H:%M:%S %Z")
                st.write(f"**From:** {starts.strftime('%b %d, %Y %I:%M %p')}")
                st.write(f"**To:** {ends.strftime('%b %d, %Y %I:%M %p')}")
                st.write(f"**Created by:** {event['first_name']} {event['last_name']}")
                if event["is_private"]:
                    st.caption("Private")
