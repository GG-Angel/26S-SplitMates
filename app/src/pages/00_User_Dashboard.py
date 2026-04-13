import logging
import requests
from datetime import datetime
import streamlit as st
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

API_BASE_URL = "http://web-api:4000"
user = st.session_state["user"]
user_id = user["user_id"]

# user_groups =

# --- Content ---

st.title(f"Hi, {user['first_name']}!")
st.write("### Your Groups")
