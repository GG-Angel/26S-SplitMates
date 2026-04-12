# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st


# ---- General ----------------------------------------------------------------


def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


# ---- Sidebar assembly -------------------------------------------------------


def SideBarLinks(show_home=False):
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

    if show_home:
        home_nav()

    if st.session_state["authenticated"]:
        # TODO: display other buttons once user is logged in
        pass

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["user"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
