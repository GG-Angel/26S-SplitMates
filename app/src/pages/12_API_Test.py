import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

SideBarLinks()

st.write("# Accessing a REST API from Within Streamlit")
"""
Simply retrieving data from a REST api running in a separate Docker Container.

If the container isn't running, this will be very unhappy.  But the Streamlit app 
should not totally die. 
"""

data = {} 
try:
  data = requests.get('http://web-api:4000/data').json()
except requests.exceptions.RequestException as e:
  st.write("**Important**: Could not connect to sample api, so using dummy data.")
  data = {"a":{"b": "123", "c": "hello"}, "z": {"b": "456", "c": "goodbye"}}

st.dataframe(data)
