# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator
# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st


def user_dashboard_nav():
    st.sidebar.page_link("pages/00_User_Dashboard.py", label="Home", icon="🏠")


def SideBarLinks():
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # Logo appears at the top of the sidebar on every page
    # st.sidebar.image("assets/logo.png", width=150)
    # TODO: make logo

    # if no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if st.session_state["authenticated"]:
        user_dashboard_nav()

        # TODO: display other buttons when the user is looking in a group
        # TODO: display other buttons based on role (sysadmin, data analyst)

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["user"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
