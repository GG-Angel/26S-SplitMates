import logging
import requests
import streamlit as st
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

API_BASE_URL = "http://web-api:4000"

st.title("Create a New Group")

name = st.text_input("Name")
address = st.text_input("Address")

col1, col2, col3 = st.columns([3, 1, 2])
with col1:
    city = st.text_input("City")
with col2:
    state = st.text_input("State")
with col3:
    zip_code = st.text_input("ZIP Code")



if st.button("Create Group", type="primary"):
    if not all([name, address, city, state, zip_code]):
        st.error("Please fill in all fields.")
    else:
        try:
            payload = {
                "user_id": st.session_state["user"]["user_id"],
                "name": name,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": int(zip_code),
            }
            response = requests.post(f"{API_BASE_URL}/groups/", json=payload, timeout=5)
            if response.status_code == 201:
                st.switch_page("pages/00_User_Dashboard.py")
            else:
                st.error("Failed to create group.")
        except ValueError:
            st.error("ZIP Code must be a number.")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the server: {e}")
