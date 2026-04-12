import logging
import streamlit as st
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

st.title(f"Welcome, {st.session_state['user']['first_name']}")

for k, v in st.session_state["user"].items():
    st.write(f"{k}: {v}")
