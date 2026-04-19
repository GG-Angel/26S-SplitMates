import logging
import streamlit as st
from requests import HTTPError
from api.client import client
from modules.nav import SideBarLinks
from utils import highlight_color, parse_mysql_datetime, time_relative

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
        is_leader = group["group_leader"] == user_id
        group_name = f"👑 {group['name']}" if is_leader else f"{group['name']}"
        with cols[index % 2]:
            with st.container(border=True):
                st.subheader(group_name)
                st.write(f"📍 {group['city']}, {group['state']}")
                st.write(f"👥 {group['member_count']} members")

                if st.button("View Group", key=f"group_{group['group_id']}"):
                    st.session_state["group"] = group
                    st.switch_page("pages/02_Group_Dashboard.py")

if st.button("Create a Group", key="create_group", type="primary"):
    st.switch_page("pages/01_Group_Creation.py")

st.divider()
st.write("### Incoming Invitations")

pending_invites = client.get(f"users/{user_id}/invites", params={"pending": ""})

if not pending_invites:
    st.write(highlight_color("gray", "No pending invitations."))
else:
    with st.container(border=True):
        for invite in pending_invites:
            invite_id = invite["invitation_id"]
            with st.container(
                border=True,
                horizontal=True,
                horizontal_alignment="distribute",
                vertical_alignment="center",
            ):
                sent_at = time_relative(parse_mysql_datetime(invite["created_at"]))
                with st.container(border=False, gap="xxsmall"):
                    st.write(f"**{invite['group_name']}**")
                    st.write(highlight_color("gray", f"Invited {sent_at.lower()}"))

                with st.container(horizontal=True, border=False):
                    if st.button(
                        "Accept",
                        key=f"accept-inv-{invite_id}",
                        type="primary",
                        width="content",
                    ):
                        try:
                            client.put(f"users/{user_id}/invites/{invite_id}")
                            st.rerun()
                        except HTTPError:
                            st.error("Failed to accept invitation.")

                    if st.button(
                        "Decline", key=f"decline-inv-{invite_id}", width="content"
                    ):
                        try:
                            client.delete(f"users/{user_id}/invites/{invite_id}")
                            st.rerun()
                        except HTTPError:
                            st.error("Failed to decline invitation.")
