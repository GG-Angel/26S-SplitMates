import logging
from datetime import datetime, timedelta
import streamlit as st
from api.client import client
from modules.nav import SideBarLinks
from utils import highlight_color

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

user = st.session_state["user"]
user_id = user["user_id"]
group = st.session_state["group"]
group_id = group["group_id"]

bills = client.get(f"groups/{group_id}/members/{user_id}/bills")
chores = client.get(f"users/{user_id}/chores", params={"group_id": group_id})
events = client.get(f"groups/{group_id}/events")
leaderboard = client.get(f"groups/{group_id}/chores/leaderboard")


st.title("Your Dashboard")


# Summary totals
unpaid = [b for b in bills if not b["paid_at"]]
total_owed = sum(float(b["total_cost"]) * float(b["split_percentage"]) for b in unpaid)

now = datetime.now()
two_weeks_out = now + timedelta(days=14)
upcoming_events = [
    e for e in events
    if datetime.strptime(e["starts_at"], "%a, %d %b %Y %H:%M:%S %Z") <= two_weeks_out
]

col1, col2 = st.columns([2, 5])
with col1:
    st.metric("You currently owe", f"${total_owed:,.2f}")

with col2:
    if upcoming_events:
        n = min(len(upcoming_events[:3]), 3)
        filler = max(1, 4 - n)
        _, title_col = st.columns([filler, n])
        with title_col:
            st.markdown("##### Upcoming Events")
        all_cols = st.columns([filler] + [1] * n)
        for i, e in enumerate(upcoming_events[:3]):
            with all_cols[i + 1]:
                starts = datetime.strptime(e["starts_at"], "%a, %d %b %Y %H:%M:%S %Z")
                is_today = starts.date() == now.date()
                if is_today:
                    st.success(f"**{e['title']}**  \n:green[**Today**] · {starts.strftime('%b %d, %Y')} at {starts.strftime('%-I:%M %p')}", icon=None)
                else:
                    with st.container(border=True):
                        st.caption(f"**{e['title']}**  \n{starts.strftime('%b %d, %Y')} at {starts.strftime('%-I:%M %p')}")
        if len(upcoming_events) > 3:
            _, btn_col = st.columns([filler, n])
            with btn_col:
                if st.button("See All"):
                    st.switch_page("pages/03_Group_Events.py")
    else:
        _, text_col = st.columns([3, 1])
        with text_col:
            st.markdown("##### Upcoming Events")
            st.caption("No upcoming household events.")

st.divider()

col_expenses, col_chores, col_assigned = st.columns(3)

with col_expenses:
    st.subheader("Pending Expenses")
    if unpaid:
        for b in sorted(unpaid, key=lambda b: b["due_at"]):
            with st.container(border=True):
                st.write(f"**{b['title']}**")
                amount = float(b["total_cost"]) * float(b["split_percentage"])
                due = datetime.strptime(b["due_at"], "%a, %d %b %Y %H:%M:%S %Z")
                overdue = due < now
                due_str = "overdue" if overdue else f"due {due.strftime('%Y-%m-%d')}"
                label = f"${amount:,.2f} — {due_str}"
                if overdue:
                    st.markdown(f":red[{label}]")
                else:
                    st.write(label)
    else:
        st.write("No pending expenses.")

with col_chores:
    st.subheader("Upcoming Chores")
    if chores:
        for c in chores:
            with st.container(border=True):
                st.write(f"**{c['title']}**")
                if c["assignment_type"] == "assigned":
                    st.caption("Assigned to you")
                else:
                    st.caption("Communal")
                if c["due_at"]:
                    due = datetime.strptime(c["due_at"], "%a, %d %b %Y %H:%M:%S %Z")
                    overdue = due < now
                    due_str = (
                        "overdue" if overdue else f"due {due.strftime('%Y-%m-%d')}"
                    )
                    if overdue:
                        st.markdown(f":red[{due_str}]")
                    else:
                        st.write(due_str)
                effort_colors = {"low": "green", "medium": "orange", "high": "red"}
                st.write(highlight_color(effort_colors.get(c["effort"], "gray"), f"Effort: {c['effort'].capitalize()}"))
    else:
        st.write("No upcoming chores.")

    st.subheader("Chore Points")
    if leaderboard:
        rank_colors = {0: "#FFD700", 1: "#C0C0C0", 2: "#CD7F32"}
        for i, entry in enumerate(leaderboard):
            with st.container(border=True):
                if i in rank_colors:
                    st.markdown(
                        f"<span style='color:{rank_colors[i]}'><b>{i + 1}. {entry['first_name']}</b></span>"
                        f" — {entry['chore_points']} pts",
                        unsafe_allow_html=True,
                    )
                else:
                    st.write(f"**{i + 1}. {entry['first_name']}** — {entry['chore_points']} pts")
    else:
        st.write("No completed chores yet.")

with col_assigned:
    st.subheader("Bills You Assigned")
    assigned = [b for b in bills if b["created_by"] == user_id]
    if assigned:
        for b in assigned:
            with st.container(border=True):
                st.write(f"**{b['title']}**")
                st.write(f"${float(b['total_cost']):,.2f}")
    else:
        st.write("No bills assigned by you.")

st.divider()


@st.dialog("Leave Group")
def confirm_leave():
    st.write(f"Are you sure you want to leave **{group['name']}**?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Yes, leave", type="primary", use_container_width=True):
            client.delete(f"groups/{group_id}/members/{user_id}")
            del st.session_state["group"]
            st.switch_page("pages/00_User_Dashboard.py")
    with c2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


if st.button("Leave Group", type="primary"):
    confirm_leave()
