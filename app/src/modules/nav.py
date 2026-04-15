# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import base64
from pathlib import Path

import streamlit as st


# ---- General ----------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


# ---- Role: pol_strat_advisor ------------------------------------------------

def pol_strat_home_nav():
    st.sidebar.page_link(
        "pages/00_Pol_Strat_Home.py", label="Political Strategist Home", icon="👤"
    )


def world_bank_viz_nav():
    st.sidebar.page_link(
        "pages/01_World_Bank_Viz.py", label="World Bank Visualization", icon="🏦"
    )


def map_demo_nav():
    st.sidebar.page_link("pages/02_Map_Demo.py", label="Map Demonstration", icon="🗺️")


# ---- Role: usaid_worker -----------------------------------------------------

def usaid_worker_home_nav():
    st.sidebar.page_link(
        "pages/10_USAID_Worker_Home.py", label="USAID Worker Home", icon="🏠"
    )


def ngo_directory_nav():
    st.sidebar.page_link("pages/14_NGO_Directory.py", label="NGO Directory", icon="📁")


def add_ngo_nav():
    st.sidebar.page_link("pages/15_Add_NGO.py", label="Add New NGO", icon="➕")


def prediction_nav():
    st.sidebar.page_link(
        "pages/11_Prediction.py", label="Regression Prediction", icon="📈"
    )


def api_test_nav():
    st.sidebar.page_link("pages/12_API_Test.py", label="Test the API", icon="🛜")


def classification_nav():
    st.sidebar.page_link(
        "pages/13_Classification.py", label="Classification Demo", icon="🌺"
    )


# ---- Role: administrator ----------------------------------------------------

def admin_home_nav():
    st.sidebar.page_link("pages/20_Admin_Home.py", label="System Admin", icon="🏠")


def admin_tickets_nav():
    st.sidebar.page_link("pages/21_Admin_Tickets.py", label="Tickets", icon="🎫")


def admin_user_reports_nav():
    st.sidebar.page_link("pages/22_Admin_User_Reports.py", label="User Reports", icon="📝")


def admin_groups_nav():
    st.sidebar.page_link("pages/23_Admin_Groups.py", label="Roommate Groups", icon="👥")


def admin_roommates_nav():
    st.sidebar.page_link("pages/24_Admin_Roommates.py", label="Roommates", icon="🧑‍🤝‍🧑")


def admin_ops_nav():
    st.sidebar.page_link("pages/25_Admin_Ops_And_Logs.py", label="Updates & Audit Logs", icon="🧾")


def ml_model_mgmt_nav():
    st.sidebar.page_link(
        "pages/21_ML_Model_Mgmt.py", label="ML Model Management", icon="🏢"
    )


def clickable_logo_nav():
    """Render clickable sidebar logo that routes to Home.py (root persona selector)."""
    logo_path = Path(__file__).resolve().parents[1] / "assets" / "logo.png"
    try:
        logo_b64 = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
        st.sidebar.markdown(
            f"""
            <a href="/" target="_self" title="Go to SplitMates Home">
                <img src="data:image/png;base64,{logo_b64}" width="150" />
            </a>
            """,
            unsafe_allow_html=True,
        )
    except OSError:
        # Fallback if file path resolution fails.
        st.sidebar.image("assets/logo.png", width=150)


# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # Clickable logo at the top routes to Home persona selector.
    clickable_logo_nav()

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "pol_strat_advisor":
            pol_strat_home_nav()
            world_bank_viz_nav()
            map_demo_nav()

        if st.session_state["role"] == "usaid_worker":
            usaid_worker_home_nav()
            ngo_directory_nav()
            add_ngo_nav()
            prediction_nav()
            api_test_nav()
            classification_nav()

        if st.session_state["role"] == "administrator":
            st.sidebar.markdown(f"**{st.session_state.get('first_name', 'Admin')}**")
            admin_home_nav()
            admin_tickets_nav()
            admin_user_reports_nav()
            admin_groups_nav()
            admin_roommates_nav()
            admin_ops_nav()

    # Add extra breathing room on root persona selector page.
    if show_home:
        st.sidebar.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # About link appears at the bottom for all roles
    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
