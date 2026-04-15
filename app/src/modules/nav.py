# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator
# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st

from utils import highlight_color


def user_navs():
    user = st.session_state.get("user")

    if not user:
        return

    if st.sidebar.button(label=user["first_name"], icon="👤"):
        st.switch_page("pages/10_User_Profile.py")

    if st.sidebar.button(label="Your Groups", icon="🏠"):
        if "group" in st.session_state:
            del st.session_state["group"]
        st.switch_page("pages/00_User_Dashboard.py")


def group_navs():
    group = st.session_state["group"]
    st.sidebar.write(f"### {group['name']}")
    st.sidebar.page_link("pages/02_Group_Dashboard.py", label="Dashboard", icon="📊")
    st.sidebar.page_link("pages/05_Group_Bills.py", label="Bills", icon="💰")
    st.sidebar.page_link("pages/06_Group_Chores.py", label="Chores", icon="🧹")
    st.sidebar.page_link("pages/03_Group_Events.py", label="Events", icon="📅")
    if st.session_state["user"]["user_id"] == st.session_state["group"]["group_leader"]:
        st.sidebar.page_link(
            "pages/07_Group_Management.py", label="Management", icon="🛠️"
        )


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
        st.sidebar.header(f"*{highlight_color('red', 'SplitMates')}*")
        user_navs()
        st.sidebar.divider()

    # TODO: display other buttons when the user is looking in a group
    # TODO: display other buttons based on role (sysadmin, data analyst)

    if "group" in st.session_state and st.session_state["group"]:
        group_navs()
        st.sidebar.divider()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            if "user" in st.session_state:
                del st.session_state["user"]
            if "authenticated" in st.session_state:
                del st.session_state["authenticated"]
            if "group" in st.session_state:
                del st.session_state["group"]
            st.switch_page("Home.py")
