import datetime
import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Initialize sidebar
SideBarLinks()

st.title("Add New NGO")

# Initialize session state for modal
if "show_success_modal" not in st.session_state:
    st.session_state.show_success_modal = False
if "success_ngo_name" not in st.session_state:
    st.session_state.success_ngo_name = ""
if "reset_form" not in st.session_state:
    st.session_state.reset_form = False
if "form_key_counter" not in st.session_state:
    st.session_state.form_key_counter = 0

# Define the success dialog function
@st.dialog("Success")
def show_success_dialog(ngo_name):
    st.markdown(f"### {ngo_name} has been successfully added to the system!")
    
    # Create two buttons side by side
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Return to NGO Directory", use_container_width=True):
            st.session_state.show_success_modal = False
            st.session_state.success_ngo_name = ""
            st.switch_page("pages/14_NGO_Directory.py")
    
    with col2:
        if st.button("Add Another NGO", use_container_width=True):
            st.session_state.show_success_modal = False
            st.session_state.success_ngo_name = ""
            st.session_state.reset_form = True
            st.rerun()

# Handle form reset
if st.session_state.reset_form:
    st.session_state.form_key_counter += 1
    st.session_state.reset_form = False

# API endpoint
API_URL = "http://web-api:4000/ngo/ngos"

# Create a form for NGO details with dynamic key to force reset
with st.form(f"add_ngo_form_{st.session_state.form_key_counter}"):
    st.subheader("NGO Information")

    # Required fields
    name = st.text_input("Organization Name *")
    country = st.text_input("Country *")
    current_year = datetime.date.today().year
    founding_year = st.number_input(
        "Founding Year *", min_value=1800, max_value=current_year, value=current_year
    )
    focus_area = st.text_input("Focus Area *")
    website = st.text_input("Website URL *")

    # Form submission button
    submitted = st.form_submit_button("Add NGO")

    if submitted:
        # Validate required fields
        if not all([name, country, founding_year, focus_area, website]):
            st.error("Please fill in all required fields marked with *")
        else:
            # Prepare the data for API
            ngo_data = {
                "Name": name,
                "Country": country,
                "Founding_Year": int(founding_year),
                "Focus_Area": focus_area,
                "Website": website,
            }

            try:
                # Send POST request to API
                response = requests.post(API_URL, json=ngo_data)

                if response.status_code == 201:
                    # Store NGO name and show modal
                    st.session_state.show_success_modal = True
                    st.session_state.success_ngo_name = name
                    st.rerun()
                else:
                    st.error(
                        f"Failed to add NGO: {response.json().get('error', 'Unknown error')}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the API: {str(e)}")
                st.info("Please ensure the API server is running")

# Show success modal if NGO was added successfully
if st.session_state.show_success_modal:
    show_success_dialog(st.session_state.success_ngo_name)

# Add a button to return to the NGO Directory
if st.button("Return to NGO Directory"):
    st.switch_page("pages/14_NGO_Directory.py")
