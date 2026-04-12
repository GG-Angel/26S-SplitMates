import logging
import requests
from datetime import datetime
import streamlit as st
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

API_BASE_URL = "http://web-api:4000"
user_id = st.session_state["user"]["user_id"]

st.title("Your Dashboard")

if st.button("make-group-placeholder"):
    st.switch_page("pages/01_Group_Creation.py")

# Fetch bills and chores assigned to this user
try:
    bills_resp = requests.get(f"{API_BASE_URL}/users/{user_id}/bills", timeout=5)
    bills_resp.raise_for_status()
    bills = bills_resp.json()
except requests.exceptions.RequestException as e:
    st.error(f"Could not load bills: {e}")
    bills = []

try:
    chores_resp = requests.get(f"{API_BASE_URL}/users/{user_id}/chores", timeout=5)
    chores_resp.raise_for_status()
    chores = chores_resp.json()
except requests.exceptions.RequestException as e:
    st.error(f"Could not load chores: {e}")
    chores = []

# Summary totals
unpaid = [b for b in bills if not b["paid_at"]]
total_owed = sum(float(b["total_cost"]) * float(b["split_percentage"]) for b in unpaid)

col1, col2 = st.columns([2, 5])
with col1:
    st.metric("You currently owe", f"${total_owed:,.2f}")

st.divider()

col_expenses, col_chores, col_assigned = st.columns(3)

with col_expenses:
    st.subheader("Pending Expenses")
    now = datetime.now()
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
                if c["due_at"]:
                    due = datetime.strptime(c["due_at"], "%a, %d %b %Y %H:%M:%S %Z")
                    overdue = due < now
                    due_str = "overdue" if overdue else f"due {due.strftime('%Y-%m-%d')}"
                    if overdue:
                        st.markdown(f":red[{due_str}]")
                    else:
                        st.write(due_str)
                st.write(f"Effort: {c['effort']}")
    else:
        st.write("No upcoming chores.")

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
