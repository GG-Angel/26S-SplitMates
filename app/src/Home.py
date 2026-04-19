import logging
import requests
import streamlit as st

from modules.nav import SideBarLinks

logging.basicConfig(
    format="%(filename)s:%(lineno)s:%(levelname)s -- %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks(show_home=True)

# Initialize session state before calling SideBarLinks
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False


def login_as(user_id: int, persona_name: str, role: str = "roommate"):
    """Fetch user data from API and store in session state"""
    try:
        api_base_url = "http://web-api:4000"
        response = requests.get(f"{api_base_url}/users/{user_id}", timeout=5)
        response.raise_for_status()
        user_data = response.json()

        st.session_state["authenticated"] = True
        st.session_state["user"] = user_data
        st.session_state["role"] = role
        st.session_state["first_name"] = user_data.get("first_name", persona_name)

        logger.info(f"Logging in as {persona_name} (user_id={user_id}, role={role})")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch user data for user_id={user_id}: {e}")
        st.error(f"Could not connect to the server. Please try again. ({e})")
        return False


# --- Content ---

logger.info("Loading the Home Page")
st.title("Welcome to SplitMates!")
st.write("#### Which user would you like to log in as?")

if st.button(
    "Act as Joanna Miller, Roommate",
    type="primary",
    use_container_width=True,
    key="roommate_login",
):
    if login_as(user_id=9, persona_name="Roommate Leader", role="roommate"):
        st.switch_page("pages/00_User_Dashboard.py")

if st.button(
    "Act as Michele Collins, Roommate Leader",
    type="primary",
    use_container_width=True,
    key="roommate_leader_login",
):
    if login_as(user_id=23, persona_name="Roommate Leader", role="roommate"):
        st.switch_page("pages/00_User_Dashboard.py")

if st.button(
    "Act as Bob McDonald, System Administrator",
    type="primary",
    use_container_width=True,
    key="admin_login",
):
    if login_as(user_id=1, persona_name="System Administrator", role="administrator"):
        st.switch_page("pages/20_Admin_Home.py")

if st.button(
    "Act as Nicole Parks, Data Analyst",
    type="primary",
    use_container_width=True,
    key="data_analyst_login",
):
    if login_as(user_id=4, persona_name="Data Analyst", role="analyst"):
        st.switch_page("pages/06_Analyst_Dashboard.py")
