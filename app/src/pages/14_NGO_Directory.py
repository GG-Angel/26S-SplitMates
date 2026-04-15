import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Initialize sidebar
SideBarLinks()

st.title("NGO Directory")

# API endpoint
API_URL = "http://web-api:4000/ngo/ngos"

# Create filter columns
col1, col2, col3 = st.columns(3)

# Get unique values for filters from the API
try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        ngos = response.json()

        # Extract unique values for filters
        countries = sorted(list(set(ngo["Country"] for ngo in ngos)))
        focus_areas = sorted(list(set(ngo["Focus_Area"] for ngo in ngos)))
        founding_years = sorted(list(set(ngo["Founding_Year"] for ngo in ngos)))

        # Create filters
        with col1:
            selected_country = st.selectbox("Filter by Country", ["All"] + countries)

        with col2:
            selected_focus = st.selectbox("Filter by Focus Area", ["All"] + focus_areas)

        with col3:
            selected_year = st.selectbox(
                "Filter by Founding Year",
                ["All"] + [str(year) for year in founding_years],
            )

        # Build query parameters
        params = {}
        if selected_country != "All":
            params["country"] = selected_country
        if selected_focus != "All":
            params["focus_area"] = selected_focus
        if selected_year != "All":
            params["founding_year"] = selected_year

        # Get filtered data
        filtered_response = requests.get(API_URL, params=params)
        if filtered_response.status_code == 200:
            filtered_ngos = filtered_response.json()

            # Display results count
            st.write(f"Found {len(filtered_ngos)} NGOs")

            # Create expandable rows for each NGO
            for ngo in filtered_ngos:
                with st.expander(f"{ngo['Name']} ({ngo['Country']})"):
                    info_col, contact_col = st.columns(2)

                    with info_col:
                        st.write("**Basic Information**")
                        st.write(f"**Country:** {ngo['Country']}")
                        st.write(f"**Founded:** {ngo['Founding_Year']}")
                        st.write(f"**Focus Area:** {ngo['Focus_Area']}")

                    with contact_col:
                        st.write("**Contact Information**")
                        st.write(f"**Website:** [{ngo['Website']}]({ngo['Website']})")

                    # Add a button to view full profile
                    if st.button("View Full Profile", key=f"view_{ngo['NGO_ID']}"):
                        st.session_state["selected_ngo_id"] = ngo["NGO_ID"]
                        st.switch_page("pages/16_NGO_Profile.py")

    else:
        st.error("Failed to fetch NGO data from the API")

except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running on http://web-api:4000")
