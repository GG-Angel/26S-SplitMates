import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Initialize sidebar
SideBarLinks()

st.title("NGO Profile")

# Get NGO ID from session state
ngo_id = st.session_state.get("selected_ngo_id")

if ngo_id is None:
    st.error("No NGO selected")
    if st.button("Return to NGO Directory"):
        st.switch_page("pages/14_NGO_Directory.py")
else:
    # API endpoint
    API_URL = f"http://web-api:4000/ngo/ngos/{ngo_id}"

    try:
        # Fetch NGO details
        response = requests.get(API_URL)

        if response.status_code == 200:
            ngo = response.json()

            # Display basic information
            st.header(ngo["Name"])

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Basic Information")
                st.write(f"**Country:** {ngo['Country']}")
                st.write(f"**Founded:** {ngo['Founding_Year']}")
                st.write(f"**Focus Area:** {ngo['Focus_Area']}")
                st.write(f"**Website:** [{ngo['Website']}]({ngo['Website']})")

            # Display projects
            if ngo.get("projects"):
                st.subheader("Projects")
                for project in ngo["projects"]:
                    with st.expander(
                        f"{project['Project_Name']} ({project['Focus_Area']})"
                    ):
                        budget = float(project["Budget"]) if project["Budget"] else 0.0
                        st.write(f"**Budget:** ${budget:,.2f}")
                        st.write(f"**Start Date:** {project['Start_Date']}")
                        st.write(f"**End Date:** {project['End_Date']}")
            else:
                st.info("No projects found for this NGO")

            # Display donors
            if ngo.get("donors"):
                st.subheader("Donors")
                for donor in ngo["donors"]:
                    with st.expander(f"{donor['Donor_Name']} ({donor['Donor_Type']})"):
                        donation = (
                            float(donor["Donation_Amount"])
                            if donor["Donation_Amount"]
                            else 0.0
                        )
                        st.write(f"**Donation Amount:** ${donation:,.2f}")
            else:
                st.info("No donors found for this NGO")

        elif response.status_code == 404:
            st.error("NGO not found")
        else:
            st.error(
                f"Error fetching NGO data: {response.json().get('error', 'Unknown error')}"
            )

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the API: {str(e)}")
        st.info("Please ensure the API server is running")

# Add a button to return to the NGO Directory
if st.button("Return to NGO Directory"):
    # Clear the selected NGO ID from session state
    if "selected_ngo_id" in st.session_state:
        del st.session_state["selected_ngo_id"]
    st.switch_page("pages/14_NGO_Directory.py")
