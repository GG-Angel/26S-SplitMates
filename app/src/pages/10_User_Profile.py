import logging
from requests import HTTPError
import streamlit as st
from api.client import client
from modules.nav import SideBarLinks
from utils import highlight_color, parse_mysql_datetime, time_relative


logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")
SideBarLinks()

user = st.session_state["user"]
user_id = user["user_id"]
