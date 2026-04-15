import logging
import streamlit as st
from api.client import client
from modules.nav import SideBarLinks
from utils import (
    format_date,
    format_time,
    parse_mysql_datetime,
    time_relative,
)


logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

user = st.session_state["user"]
user_id = user["user_id"]

# --- Modals ---


@st.dialog("Confirm Deletion", width="small")
def delete_user_modal():
    st.write("Are you sure? This action is **not reversable.**")
    if st.button(label="Yes, Delete My Account", type="primary", width="stretch"):
        client.delete(f"/users/{user_id}")
        if st.session_state.get("group"):
            del st.session_state["user"]
        if st.session_state.get("group"):
            del st.session_state["group"]
        st.session_state["authenticated"] = False
        st.switch_page("Home.py")


# --- Content ---

st.title("User Settings")

joined_at = parse_mysql_datetime(user["created_at"])
st.subheader("Profile Information")
st.write(f"Name: {user['first_name']} {user['last_name']}")
st.write(f"Email: {user['email']}")
st.write(
    f"Joined {time_relative(joined_at)} on {format_date(joined_at)} at {format_time(joined_at)}"
)

st.divider()

if st.button(label="Delete Account"):
    delete_user_modal()
