import logging
from requests import HTTPError
import streamlit as st
from api.client import client
from modules.nav import SideBarLinks


logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

user = st.session_state["user"]
group = st.session_state["group"]
user_id = user["user_id"]
group_id = group["group_id"]

members = client.get(f"/groups/{group_id}/members")
members.sort(key=lambda m: m["first_name"] + m["last_name"])

# --- Invite User ---

st.subheader("Invite a Roommate")
with st.container(border=True):
    with st.container(
        horizontal=True,
        horizontal_alignment="distribute",
        vertical_alignment="center",
    ):
        invite_email = st.text_input(
            label="",
            label_visibility="collapsed",
            placeholder="Enter email",
            max_chars=75,
        )
        send_invite_btn = st.button(label="Send", type="primary")

    if send_invite_btn:
        try:
            client.post(f"/groups/{group_id}/invites", json={"email": invite_email})
            st.rerun()
        except HTTPError:
            st.error(f"User with email '{invite_email}' does not exist")


# --- Roommates | Pending Invites ---

left_col, right_col = st.columns(2, gap="medium")

with left_col:
    st.subheader("Your Roommates")
    with st.container(border=True, height=400):
        for member in members:
            member_id = member["user_id"]
            if member_id == user_id:
                continue

            with st.container(
                border=True,
                horizontal=True,
                horizontal_alignment="distribute",
                vertical_alignment="center",
            ):
                name = f"{member['first_name']} {member['last_name']}"
                st.write(f"**{name}**")
                if st.button(label="Kick", width="content", key=f"kick-{member_id}"):
                    # TODO: implement kicking a roommate
                    st.rerun()

with right_col:
    st.subheader("Pending Invites")
    with st.container(border=True, height=400):
        for invite in [1, 2, 3]:
            with st.container(
                border=True,
                horizontal=True,
                horizontal_alignment="distribute",
                vertical_alignment="center",
            ):
                name = "some name"
                st.write(f"**{name}**")
                if st.button(
                    label="Cancel", width="content", key=f"cancel-inv-{invite}"
                ):
                    client.delete(f"/groups/{group_id}/invites/{invite}")
                    st.rerun()

# --- Bottom actions ---

st.divider()

with st.container(horizontal=True, width="stretch", horizontal_alignment="left"):
    # TODO: make functional
    if st.button("Transfer Ownership"):
        st.switch_page("pages/02_Group_Dashboard.py")

    if st.button("Delete Group"):
        del st.session_state["group"]
        st.switch_page("pages/00_User_Dashboard.py")
