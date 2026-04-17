# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import base64
from pathlib import Path

import streamlit as st

from utils import highlight_color


# ---- General ----------------------------------------------------------------


def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


# ---- Role: roommate ---------------------------------------------------------


def user_navs():
    user = st.session_state.get("user")

    if not user:
        return

    if st.sidebar.button(label=user["first_name"], icon="👤"):
        st.switch_page("pages/10_User_Settings.py")

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
    st.sidebar.page_link("pages/08_Group_Items.py", label="Items", icon="📦")
    if st.session_state["user"]["user_id"] == st.session_state["group"]["group_leader"]:
        st.sidebar.page_link(
            "pages/07_Group_Management.py", label="Management", icon="🛠️"
        )


def admin_home_nav():
    st.sidebar.page_link("pages/20_Admin_Home.py", label="System Admin", icon="🏠")


def admin_tickets_nav():
    st.sidebar.page_link("pages/21_Admin_Tickets.py", label="Tickets", icon="🎫")


def admin_user_reports_nav():
    st.sidebar.page_link(
        "pages/22_Admin_User_Reports.py", label="User Reports", icon="📝"
    )


def admin_groups_nav():
    st.sidebar.page_link("pages/23_Admin_Groups.py", label="Roommate Groups", icon="👥")


def admin_roommates_nav():
    st.sidebar.page_link(
        "pages/24_Admin_Roommates.py", label="Roommates", icon="🧑‍🤝‍🧑"
    )


def admin_ops_nav():
    st.sidebar.page_link(
        "pages/25_Admin_Ops_And_Logs.py", label="Updates & Audit Logs", icon="🧾"
    )


# ---- Sidebar assembly -------------------------------------------------------


def SideBarLinks(show_home=False):
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    # Roommate navigation
    if st.session_state["authenticated"]:
        st.sidebar.header(f"*{highlight_color('red', 'SplitMates')}*")
        if st.session_state.get("role") == "roommate":
            user_navs()
            st.sidebar.divider()

    if "group" in st.session_state and st.session_state["group"]:
        group_navs()
        st.sidebar.divider()

    # Admin navigation
    if st.session_state.get("user", {}).get("is_admin"):
        st.sidebar.markdown(f"**{st.session_state.get('first_name', 'Admin')}**")
        admin_home_nav()
        admin_tickets_nav()
        admin_user_reports_nav()
        admin_groups_nav()
        admin_roommates_nav()
        admin_ops_nav()
        st.sidebar.divider()

    # Add extra breathing room on root persona selector page.
    if show_home:
        st.sidebar.markdown(
            "<div style='height: 1.25rem;'></div>", unsafe_allow_html=True
        )

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            for key in ["user", "authenticated", "group", "role"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("Home.py")
