import logging
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

bills_assigned = client.get(
    f"/users/{user_id}/bills",
    params={"group_id": group_id, "unpaid": True},
)
group_bills = client.get(f"/groups/{group_id}/bills")
bills_created = [b for b in group_bills if b["created_by"] == user_id]

amount_to_pay = sum([float(b["user_cost"]) for b in bills_assigned])
amount_to_be_paid = sum([float(b["amount_remaining"]) for b in bills_created])

# --- Content ---

st.title("Your Bills")

top_left_col, top_right_col = st.columns([3, 5])
with top_left_col:
    with st.container(border=True):
        st.metric("You owe", f"${amount_to_pay:,.2f}")
with top_right_col:
    with st.container(border=True, horizontal=True, vertical_alignment="center"):
        st.metric("You are owed", f"${amount_to_be_paid:,.2f}")
        st.button(label="Create Bill", type="primary")

left_col, right_col = st.columns(2)
with left_col:
    st.subheader("Bills to Pay")
    with st.container(border=True):
        for bill in bills_assigned:
            # cost and due date
            cost = bill["user_cost"]
            due_date = parse_mysql_datetime(bill["due_at"])
            cost_date_info = f"${cost}, {time_relative(due_date).lower()}"
            cost_date_display = (
                highlight_color("red", cost_date_info)
                if is_past_date(due_date)
                else cost_date_info
            )

            # show who assigned this bill
            assigned_by = client.get(f"/users/{bill['created_by']}")
            assigned_by_display = f"Assigned by {assigned_by['first_name']}"

            with st.container(
                border=True,
                horizontal=True,
                vertical_alignment="top",
                horizontal_alignment="distribute",
            ):
                with st.container(gap="xsmall"):
                    st.write(f"##### {bill['title']}")
                    st.write(cost_date_display)
                    st.write(assigned_by_display)
                with st.container(width="content"):
                    if st.button(label="Mark as Paid"):
                        client.delete("/")
                        pass

with right_col:
    st.subheader("Bills You Created")
    with st.container(border=True):
        for bill in bills_created:
            with st.container(border=True):
                st.write(bill)
