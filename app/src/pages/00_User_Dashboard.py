import logging
import streamlit as st
from api.client import client
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

user = st.session_state["user"]
user_id = user["user_id"]
user_groups = client.get(f"users/{user_id}/groups")

# --- Content ---

st.title(f"Hi, {user['first_name']}!")
st.write("### Your Groups")

if not user_groups:
    st.write("You are not in any groups yet.")
else:
    cols = st.columns(2)
    for index, group in enumerate(user_groups):
        with cols[index % 2]:
            with st.container(border=True):
                st.subheader(group["name"])
                st.write(f"📍 {group['city']}, {group['state']}")
                st.write(f"👥 {group['member_count']} members")

                if st.button("View Group", key=f"group_{group['group_id']}"):
                    st.session_state["group"] = group
                    st.switch_page("pages/02_Group_Dashboard.py")

if st.button("Create a Group", key="create_group", type="primary"):
    st.switch_page("pages/01_Group_Creation.py")
