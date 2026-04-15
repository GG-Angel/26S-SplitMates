import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# Accessing a REST API from Within Streamlit")

st.write("""
Simply retrieving data from a REST API running in a separate Docker container.

If the container isn't running, this page will fall back to dummy data.
""")

data = {}
try:
    data = requests.get('http://web-api:4000/data').json()
except requests.exceptions.RequestException as e:
    st.write("**Important**: Could not connect to sample API, so using dummy data.")
    data = {"a": {"b": "123", "c": "hello"}, "z": {"b": "456", "c": "goodbye"}}

st.dataframe(data)
