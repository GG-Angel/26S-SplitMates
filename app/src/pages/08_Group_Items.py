import logging
import streamlit as st
from api.client import client
from modules.nav import SideBarLinks
from utils import highlight_color

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

user = st.session_state["user"]
group = st.session_state["group"]
user_id = user["user_id"]
group_id = group["group_id"]

items: list[dict] = client.get(f"groups/{group_id}/items")
members: list[dict] = client.get(f"groups/{group_id}/members")

# show owned items first
items.sort(
    key=lambda i: any(o["user_id"] == user_id for o in i["owners"]), reverse=True
)

owned_items = [i for i in items if any(o["user_id"] == user_id for o in i["owners"])]


# --- Modals ---


@st.dialog("Create Item", width="medium")
def create_item_modal():
    name = st.text_input("Name", placeholder="e.g. Coffee Maker")
    picture_url = st.text_input("Picture URL (optional)", placeholder="https://...")

    member_options = {
        f"{'You' if m['user_id'] == user_id else m['first_name'] + ' ' + m['last_name']}": m[
            "user_id"
        ]
        for m in members
    }
    selected_labels = st.multiselect(
        "Owners",
        options=list(member_options.keys()),
        default=["You"] if "You" in member_options else [],
    )
    selected_owner_ids = [member_options[label] for label in selected_labels]

    if st.button("Create Item", type="primary"):
        cleaned_name = (name or "").strip()
        if not cleaned_name:
            st.error("Name is required.")
        else:
            client.post(
                f"groups/{group_id}/items",
                json={
                    "name": cleaned_name,
                    "picture_url": picture_url.strip() or None,
                    "created_by": user_id,
                    "owners": selected_owner_ids,
                },
            )
            st.rerun()


@st.dialog("Edit Item", width="medium")
def edit_item_modal(item: dict):
    name = st.text_input("Name", value=item["name"])
    picture_url = st.text_input(
        "Picture URL (optional)", value=item.get("picture_url") or ""
    )

    if st.button("Save Changes", type="primary"):
        cleaned_name = (name or "").strip()
        if not cleaned_name:
            st.error("Name is required.")
        else:
            client.put(
                f"groups/{group_id}/items/{item['item_id']}",
                json={
                    "name": cleaned_name,
                    "picture_url": picture_url.strip() or None,
                },
            )
            st.rerun()


@st.dialog("Delete Item", width="small")
def delete_item_modal(item: dict):
    st.write(f"Are you sure you want to delete **{item['name']}**?")
    st.write("This action cannot be undone.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Delete", type="primary", use_container_width=True):
            client.delete(f"groups/{group_id}/items/{item['item_id']}")
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


# --- Content ---

st.title("Household Items")

with st.container(border=True, horizontal=True, vertical_alignment="center"):
    st.metric(label="Items Owned", value=len(owned_items))
    st.metric(label="Total Items", value=len(items))
    if st.button(label="Create Item", type="primary"):
        create_item_modal()

cols = st.columns(spec=4, gap="small")

for i, item in enumerate(items):
    col = cols[i % len(cols)]
    is_owned = any(o["user_id"] == user_id for o in item["owners"])
    with col:
        with st.container(border=True):
            picture_url = (
                item.get("picture_url") or "https://placehold.co/200x100?text=No+Image"
            )
            label = f"👑 **{item['name']}**" if is_owned else f"**{item['name']}**"
            owned_by = highlight_color(
                "gray", f"Owned by {', '.join(o['first_name'] for o in item['owners'])}"
            )

            st.image(image=picture_url, width="stretch")
            with st.container(gap="xxsmall"):
                st.write(label)
                st.write(owned_by)

            if is_owned:
                with st.container(horizontal=True, gap="xsmall"):
                    if st.button("Edit", key=f"edit_{item['item_id']}"):
                        edit_item_modal(item)
                    if st.button("Delete", key=f"delete_{item['item_id']}"):
                        delete_item_modal(item)
