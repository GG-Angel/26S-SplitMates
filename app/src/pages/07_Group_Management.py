import logging
from requests import HTTPError
import streamlit as st
from api.client import client
from modules.nav import SideBarLinks
from utils import highlight_color, parse_mysql_datetime, time_relative


logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

user = st.session_state["user"]
group = st.session_state["group"]
user_id = user["user_id"]
group_id = group["group_id"]

members = client.get(f"/groups/{group_id}/members")
members.sort(key=lambda m: m["first_name"] + m["last_name"])

pending_invites = client.get(f"/groups/{group_id}/invites")

# --- Modals ---


@st.dialog("Confirm Deletion", width="small")
def delete_group_modal():
    st.write("Are you sure? This action is **not reversable.**")
    st.write(
        highlight_color(
            "gray",
            "You can transfer ownership instead if your roommates still need this group.",
        )
    )

    if st.button(label="Yes, Delete the Group", type="primary", width="stretch"):
        client.delete(f"/groups/{group_id}")
        del st.session_state["group"]
        st.switch_page("pages/00_User_Dashboard.py")


@st.dialog("Transfer Ownership", width="medium")
def transfer_ownership_modal():
    other_members = [m for m in members if m["user_id"] != user_id]

    if not other_members:
        st.warning("There are no other members to transfer ownership to.")
        return

    selected = st.selectbox(
        "Select new owner",
        options=other_members,
        format_func=lambda m: f"{m['first_name']} {m['last_name']}",
    )

    if selected and st.button("Transfer Ownership", type="primary", width="stretch"):
        client.put(
            f"/groups/{group_id}/owner", json={"new_owner_id": selected["user_id"]}
        )
        updated_group = client.get(f"/groups/{group_id}")
        st.session_state["group"] = updated_group
        st.switch_page("pages/02_Group_Dashboard.py")


# --- Content ---

# Invite User

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
            pending_invites = client.get(f"/groups/{group_id}/invites")  # refresh
            st.success("Invite sent!")
        except HTTPError as e:
            if e.response is not None:
                st.error(e.response.json()["error"])
            else:
                st.error("Failed to send invite. Please try again.")


# Roommates | Pending Invites

left_col, right_col = st.columns(2, gap="medium")

with left_col:
    st.subheader("Your Roommates")
    if members and len(members) > 1:  # > 1 to account for current user
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
                    joined_at = time_relative(parse_mysql_datetime(member["joined_at"]))
                    joined_at_display = highlight_color(
                        "gray", f"Joined {joined_at.lower()}"
                    )

                    with st.container(border=False, gap="xxsmall"):
                        st.write(f"**{name}**")
                        st.write(joined_at_display)

                    if st.button(
                        label="Kick", width="content", key=f"kick-{member_id}"
                    ):
                        client.delete(f"/groups/{group_id}/members/{member_id}")
                        st.rerun()
    else:
        st.write(highlight_color("gray", "No roommates."))

with right_col:
    st.subheader("Pending Invites")
    if pending_invites:
        with st.container(border=True, height=400):
            for invite in pending_invites:
                invite_id = invite["invitation_id"]
                with st.container(
                    border=True,
                    horizontal=True,
                    horizontal_alignment="distribute",
                    vertical_alignment="center",
                ):
                    name = f"{invite['first_name']} {invite['last_name']}"
                    sent_at = time_relative(parse_mysql_datetime(invite["created_at"]))
                    sent_at_display = highlight_color("gray", f"Sent {sent_at.lower()}")

                    with st.container(border=False, gap="xxsmall"):
                        st.write(f"**{name}**")
                        st.write(sent_at_display)

                    if st.button(
                        label="Cancel",
                        width="content",
                        key=f"cancel-inv-{invite_id}",
                    ):
                        client.delete(f"/groups/{group_id}/invites/{invite_id}")
                        st.rerun()
    else:
        st.write(highlight_color("gray", "No pending invites."))

# Bottom actions

st.divider()

with st.container(horizontal=True, width="stretch", horizontal_alignment="left"):
    if st.button("Transfer Ownership", disabled=len(members) <= 1):
        transfer_ownership_modal()

    if st.button("Delete Group"):
        delete_group_modal()
