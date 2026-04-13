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

bills_assigned: list[dict] = client.get(
    f"/users/{user_id}/bills",
    params={"group_id": group_id, "unpaid": True},
)
amount_to_pay = sum([float(b["user_cost"]) for b in bills_assigned])

group_bills: list[dict] = client.get(f"/groups/{group_id}/bills")
bills_created = [b for b in group_bills if b["created_by"] == user_id]
amount_to_be_paid = sum([float(b["amount_remaining"]) for b in bills_created])


# --- Modals ---


@st.dialog("Bill Details", width="medium")
def bill_details_modal(bill: dict):
    is_creator = bill["created_by"] == user_id
    creator = "You" if is_creator else bill["creator_name"]

    st.subheader(bill["title"])
    st.write(f"Created by {creator}")

    created_at = parse_mysql_datetime(bill["created_at"])
    due_at = parse_mysql_datetime(bill["due_at"])
    total_cost = float(bill["total_cost"])
    amount_due = float(bill["amount_remaining"])

    cost_col_left, cost_col_right = st.columns(2)
    with cost_col_left:
        st.metric("Total Cost", f"${total_cost:,.2f}", border=True)
    with cost_col_right:
        st.metric("Amount Due", f"${amount_due:,.2f}", border=True)

    date_col_left, date_col_right = st.columns(2)
    with date_col_left:
        st.metric("Created", created_at.strftime("%b %d, %Y"), border=True)
    with date_col_right:
        due_label = (
            highlight_color("red", "Due (overdue)") if is_past_date(due_at) else "Due"
        )
        st.metric(due_label, due_at.strftime("%b %d, %Y"), border=True)

    st.write("**Assignees**")

    rows = []
    for a in bill["assignees"]:
        amount = float(a["split_percentage"]) * total_cost
        paid_at = parse_mysql_datetime(a["paid_at"]) if a["paid_at"] else None
        rows.append(
            {
                "Name": a["first_name"],
                "Amount": f"${amount:,.2f}",
                "Status": f"Paid {paid_at.strftime('%b %d, %Y')}"
                if paid_at
                else "No payment  ❌",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)

    if is_creator:
        if st.button(label="Delete Bill"):
            st.rerun()


@st.dialog("Create Bill", width="medium")
def create_bill_modal():
    # Title
    group_members: list[dict] = client.get(f"/groups/{group_id}/members")
    title = st.text_input("Title", placeholder="e.g. Electricity Bill")

    # Cost and Due Date
    col_cost, col_date, col_time = st.columns(3)
    with col_cost:
        total_cost = st.number_input(
            "Total Amount ($)", min_value=0.01, step=0.01, format="%.2f", value=0.01
        )
    with col_date:
        due_date = st.date_input("Due Date", min_value=date.today())
    with col_time:
        due_time = st.time_input("Due Time", value=time(0, 0), step=3600)

    st.divider()

    header_col, split_col = st.columns([3, 2])
    with header_col:
        st.write("**Assign to Members**")
    with split_col:
        split_btn = st.button("Split Equally", use_container_width=True)

    # Update percentage session state before rendering inputs
    if split_btn:
        checked_ids = [
            m["user_id"]
            for m in group_members
            if st.session_state.get(f"member_{m['user_id']}", False)
        ]
        if checked_ids:
            n = len(checked_ids)
            base = round(100.0 / n, 1)
            remainder = round(100.0 - base * (n - 1), 1)
            for i, mid in enumerate(checked_ids):
                st.session_state[f"pct_{mid}"] = remainder if i == 0 else base

    selected_members: dict[int, float] = {}
    for member in group_members:
        mid = member["user_id"]
        name = f"{member['first_name']} {member['last_name']}"
        col_name, col_pct = st.columns([3, 2])
        with col_name:
            checked = st.checkbox(name, key=f"member_{mid}")
        with col_pct:
            if checked:
                pct = st.number_input(
                    "split %",
                    min_value=0.1,
                    max_value=100.0,
                    step=0.1,
                    format="%.1f",
                    key=f"pct_{mid}",
                    label_visibility="collapsed",
                )
                selected_members[mid] = pct

    total_pct = sum(selected_members.values())
    if selected_members:
        if total_pct == 100.0:
            st.success(f"Total: {total_pct:.1f}%")
        else:
            st.warning(f"Total: {total_pct:.1f}% (must equal 100%)")

    if st.button("Create Bill", type="primary"):
        errors = []
        if not title.strip():
            errors.append("Title is required.")
        if not selected_members:
            errors.append("Assign the bill to at least one person.")
        elif abs(total_pct - 100.0) > 0.1:
            errors.append(f"Percentages must sum to 100% (currently {total_pct:.1f}%).")

        for err in errors:
            st.error(err)

        if not errors:
            assignees = [
                {"user_id": uid, "split_percentage": round(pct / 100, 4)}
                for uid, pct in selected_members.items()
            ]
            client.post(
                f"/groups/{group_id}/bills",
                json={
                    "group_id": group_id,
                    "user_id": user_id,
                    "title": title.strip(),
                    "total_cost": total_cost,
                    "due_at": datetime.combine(due_date, due_time).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "assignees": assignees,
                },
            )
            st.rerun()


# --- Content ---


st.title("Your Bills")

top_left_col, top_right_col = st.columns([3, 5])
with top_left_col:
    with st.container(border=True):
        st.metric("You owe", f"${amount_to_pay:,.2f}")
with top_right_col:
    with st.container(border=True, horizontal=True, vertical_alignment="center"):
        st.metric("You are owed", f"${amount_to_be_paid:,.2f}")
        if st.button(label="Create Bill", type="primary"):
            create_bill_modal()

left_col, right_col = st.columns(2)
with left_col:
    st.subheader("Bills to Pay")
    if bills_assigned:
        with st.container(border=True):
            for bill in bills_assigned:
                # cost and due date
                cost = bill["user_cost"]
                due_date = parse_mysql_datetime(bill["due_at"])
                cost_date_info = f"${cost}, due {time_relative(due_date).lower()}"
                cost_date_display = (
                    highlight_color("red", f"{cost_date_info} (overdue)")
                    if is_past_date(due_date)
                    else cost_date_info
                )

                # show who assigned this bill
                assigned_by = client.get(f"/users/{bill['created_by']}")
                assigned_by_display = highlight_color(
                    "gray", f"Assigned by {assigned_by['first_name']}"
                )

                with st.container(gap="xsmall"):
                    st.write(f"##### {bill['title']}")
                    st.write(cost_date_display)
                    st.write(assigned_by_display)
                with st.container(horizontal=True):
                    if st.button(
                        label="Mark as Paid",
                        key=f"pay_{bill['bill_id']}",
                        type="primary",
                    ):
                        client.put(f"/users/{user_id}/bills/{bill['bill_id']}/pay")
                        st.rerun()

    else:
        st.write(highlight_color("green", "You have no bills to pay. Good job!"))

with right_col:
    st.subheader("Bills You Created")
    for bill in bills_created:
        cost = bill["amount_remaining"]
        due_date = parse_mysql_datetime(bill["due_at"])
        cost_date_info = f"${cost}, due {time_relative(due_date).lower()}"
        cost_date_display = (
            highlight_color("red", f"{cost_date_info} (overdue)")
            if is_past_date(due_date)
            else cost_date_info
        )

        assigned_to = f"Awaiting Payments from {', '.join([a['first_name'] for a in bill['assignees'] if not a['paid_at']])}"
        assigned_to_display = highlight_color("gray", assigned_to)

        with st.container(border=True):
            with st.container(gap="xsmall"):
                st.write(f"##### {bill['title']}")
                st.write(cost_date_display)
                st.write(assigned_to_display)
            with st.container(width="content"):
                if st.button(
                    label="View Details", key=f"view_created_{bill['bill_id']}"
                ):
                    bill_details_modal(bill)
