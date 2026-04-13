from decimal import Decimal
import logging
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

bills_assigned = client.get(f"/users/{user_id}/bills?group_id={group_id}")
group_bills = client.get(f"/groups/{group_id}/bills")
bills_created = [b for b in group_bills if b["created_by"] == user_id]

amount_to_pay = sum([float(b["user_cost"]) for b in bills_assigned])
amount_to_be_paid = sum([float(b["amount_remaining"]) for b in bills_created])

# --- Content ---

st.title("Your Bills")

top_col_left, top_col_right = st.columns([3, 5])
with top_col_left:
    with st.container(border=True):
        st.metric("You owe", f"${amount_to_pay:,.2f}")
with top_col_right:
    with st.container(border=True):
        st.metric("You are owed", f"${amount_to_be_paid:,.2f}")



st.write(group_bills)
