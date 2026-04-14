import logging
from datetime import date, time, datetime
import streamlit as st
from api.client import client
from modules.nav import SideBarLinks
from utils import (
    highlight_color,
    is_past_date,
    parse_mysql_datetime,
    time_relative,
)

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

user = st.session_state["user"]
group = st.session_state["group"]
user_id = user["user_id"]
group_id = group["group_id"]

chores: list[dict] = client.get(
    f"/groups/{group_id}/chores", params={"incomplete_only": True}
)
members: list[dict] = client.get(f"/groups/{group_id}/members")


# --- Modals ---


@st.dialog("Chore Details", width="medium")
def chore_details_modal(chore: dict):
    st.subheader(chore["title"])

    effort_colors = {"low": "green", "medium": "orange", "high": "red"}
    effort = chore["effort"]
    st.write(
        highlight_color(
            effort_colors.get(effort, "gray"), f"Effort: {effort.capitalize()}"
        )
    )

    due_at = parse_mysql_datetime(chore["due_at"]) if chore.get("due_at") else None
    completed_at = (
        parse_mysql_datetime(chore["completed_at"])
        if chore.get("completed_at")
        else None
    )

    col_left, col_right = st.columns(2)
    with col_left:
        if due_at:
            due_label = (
                highlight_color("red", "Due (overdue)")
                if is_past_date(due_at) and not completed_at
                else "Due"
            )
            st.metric(due_label, due_at.strftime("%b %d, %Y"), border=True)
        else:
            st.metric("Due", "No due date", border=True)
    with col_right:
        if completed_at:
            st.metric("Completed", completed_at.strftime("%b %d, %Y"), border=True)
        else:
            st.metric("Status", highlight_color("orange", "Incomplete"), border=True)

    created_by_name = (
        "You"
        if chore["created_by"] == user_id
        else chore["first_name"] + " " + chore["last_name"]
    )
    created_by = f"Created by {created_by_name}"
    created_by_display = highlight_color("gray", created_by)
    st.write(created_by_display)

    st.divider()

    if not completed_at:
        if st.button("Mark as Complete", type="primary", use_container_width=True):
            client.put(f"/groups/chores/{chore['chore_id']}/complete")
            st.rerun()


@st.dialog("Create Chore", width="medium")
def create_chore_modal():
    title = st.text_input("Title", placeholder="e.g. Take Out Trash")

    col_effort, col_date, col_time = st.columns(3)
    with col_effort:
        effort = st.selectbox("Effort", ["low", "medium", "high"])
    with col_date:
        due_date = st.date_input("Due Date", min_value=date.today())
    with col_time:
        due_time = st.time_input("Due Time", value=time(0, 0), step=3600)

    if st.button("Create Chore", type="primary"):
        cleaned_title = (title or "").strip()
        if not cleaned_title:
            st.error("Title is required.")
        else:
            client.post(
                f"/groups/{group_id}/chores",
                json={
                    "user_id": user_id,
                    "title": cleaned_title,
                    "effort": effort,
                    "due_at": datetime.combine(due_date, due_time).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "assignees": [],
                },
            )
            st.rerun()


@st.dialog("Edit Chore", width="medium")
def edit_chore_modal(chore: dict):
    title = st.text_input("Title", value=chore["title"])
    effort = st.selectbox(
        "Effort",
        ["low", "medium", "high"],
        index=["low", "medium", "high"].index(chore["effort"]),
    )

    due_at = parse_mysql_datetime(chore["due_at"]) if chore.get("due_at") else None
    col_date, col_time = st.columns(2)
    with col_date:
        due_date = st.date_input(
            "Due Date", value=due_at.date() if due_at else date.today()
        )
    with col_time:
        due_time = st.time_input(
            "Due Time", value=due_at.time() if due_at else time(0, 0), step=3600
        )

    if st.button("Save Changes", type="primary"):
        cleaned_title = (title or "").strip()
        if not cleaned_title:
            st.error("Title is required.")
        else:
            client.put(
                f"/groups/chores/{chore['chore_id']}",
                json={
                    "title": cleaned_title,
                    "effort": effort,
                    "due_at": datetime.combine(due_date, due_time).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                },
            )
            st.rerun()


# --- Content ---


st.title("Household Chores")

with st.container(border=True, horizontal=True, vertical_alignment="center"):
    st.metric("Pending Chores", len(chores))
    if st.button("Create Chore", type="primary"):
        create_chore_modal()

st.divider()

if chores:
    effort_colors = {"low": "green", "medium": "orange", "high": "red"}
    cols = st.columns(3)
    for i, chore in enumerate(chores):
        is_creator = chore["created_by"] == user_id
        completed_at = chore.get("completed_at")
        due_at = parse_mysql_datetime(chore["due_at"]) if chore.get("due_at") else None
        effort = chore["effort"]

        with cols[i % 3]:
            with st.container(border=True):
                with st.container(gap="xsmall"):
                    st.write(f"##### {chore['title']}")
                    st.write(
                        highlight_color(
                            effort_colors.get(effort, "gray"),
                            f"Effort: {effort.capitalize()}",
                        )
                    )
                    created_by_name = (
                        "You"
                        if chore["created_by"] == user_id
                        else chore["first_name"] + " " + chore["last_name"]
                    )
                    created_by = f"Created by {created_by_name}"
                    created_by_display = highlight_color("gray", created_by)
                    st.write(created_by_display)
                    if due_at:
                        due_display = (
                            highlight_color(
                                "red", f"Due {time_relative(due_at).lower()} (overdue)"
                            )
                            if is_past_date(due_at) and not completed_at
                            else f"Due {time_relative(due_at).lower()}"
                        )
                        st.write(due_display)
                    if completed_at:
                        st.write(highlight_color("green", "✓ Completed"))

                with st.container(horizontal=True):
                    if not completed_at:
                        if st.button(
                            "Complete",
                            key=f"complete_{chore['chore_id']}",
                            type="primary",
                        ):
                            client.put(f"/groups/chores/{chore['chore_id']}/complete")
                            st.rerun()
                    if st.button("View", key=f"view_{chore['chore_id']}"):
                        chore_details_modal(chore)
                    if is_creator:
                        if st.button("Edit", key=f"edit_{chore['chore_id']}"):
                            edit_chore_modal(chore)
                        if st.button("Delete", key=f"delete_{chore['chore_id']}"):
                            client.delete(f"/groups/chores/{chore['chore_id']}")
                            st.rerun()
else:
    st.write(highlight_color("gray", "No chores in this group yet."))
