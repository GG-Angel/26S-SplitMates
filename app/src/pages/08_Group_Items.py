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

items: list[dict] = client.get(f"groups/{group_id}/items")

# show owned items first
items.sort(
    key=lambda i: any(o["user_id"] == user_id for o in i["owners"]), reverse=True
)


# --- Content ---

st.title("Household Items")

with st.container(border=True, horizontal=True, vertical_alignment="center"):
    st.write(items)
    # st.metric(label="Items Owned", value=)

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Owned Items")

with right_col:
    st.subheader("Other Items")
