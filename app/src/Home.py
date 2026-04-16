import logging
import requests
import streamlit as st
from modules.nav import SideBarLinks

logging.basicConfig(
    format="%(filename)s:%(lineno)s:%(levelname)s -- %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks()

# if a user is at this page, we assume they are not authenticated
st.session_state["authenticated"] = False


def login_as(user_id: int, persona_name: str, role: str = "roommate"):
    """Fetch user data from API and store in session state"""
    try:
        API_BASE_URL = "http://web-api:4000"
        response = requests.get(f"{API_BASE_URL}/users/{user_id}", timeout=5)
        response.raise_for_status()
        user_data = response.json()

        st.session_state["authenticated"] = True
        st.session_state["user"] = user_data
        st.session_state["role"] = role

        logger.info(f"Logging in as {persona_name} (user_id={user_id})")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch user data for user_id={user_id}: {e}")
        st.error(f"Could not connect to the server. Please try again. ({e})")


# --- Content ---

logger.info("Loading the Home Page")
st.title("Welcome to SplitMates!")
st.write("#### Which user would you like to log in as?")

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.

if st.button(
    "Act as Laurie, a Roommate Group Leader",
    type="primary",
    width="stretch",
):
    login_as(user_id=5, persona_name="Roommate Leader")
    st.switch_page("pages/00_User_Dashboard.py")

if st.button(
    "Act as Bob, a Roommate",
    type="primary",
    width="stretch",
):
    login_as(user_id=1, persona_name="Roommate")
    st.switch_page("pages/00_User_Dashboard.py")

if st.button(
    "Act as Tina Belcher, Data Analyst",
    type="primary",
    use_container_width=True,
):
    login_as(user_id=2, persona_name="Data Analyst", role="analyst")
    st.switch_page("pages/07_Analyst_Feature_Usage.py")
