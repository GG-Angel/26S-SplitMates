# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator
# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st

# icon="🏠"
def my_groups_nav():
    if st.sidebar.button(label="Your Groups"):
        if "group" in st.session_state:
            del st.session_state["group"]
        st.switch_page("pages/00_User_Dashboard.py")


# icon="📊", icon="💰, icon="🧹",  icon="📅"
def group_navs():
    group = st.session_state["group"]
    st.sidebar.write(f"### {group['name']}")
    st.sidebar.page_link("pages/02_Group_Dashboard.py", label="Dashboard",)
    st.sidebar.page_link("pages/02_Group_Dashboard.py", label="Bills",)
    st.sidebar.page_link("pages/02_Group_Dashboard.py", label="Chores",)
    st.sidebar.page_link("pages/03_Group_Events.py", label="Events",)


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
        my_groups_nav()
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
