import logging
import streamlit as st
from modules.nav import SideBarLinks

logging.basicConfig(
    format="%(filename)s:%(lineno)s:%(levelname)s -- %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks(show_home=True)

# if a user is at this page, we assume they are not authenticated
st.session_state["authenticated"] = False

# --- Page Content ---

logger.info("Loading the Home Page")
st.title("SplitMates Home Page")
st.write("#### Hi! As which user would you like to log in?")

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.

if st.button(
    "Act as Gary, a Roommate Group Leader",
    type="primary",
    use_container_width=True,
):
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = 20
    st.session_state["first_name"] = "John"

    logger.info("Logging in as Roommate Leader Persona")
    # st.switch_page("pages/....py")
