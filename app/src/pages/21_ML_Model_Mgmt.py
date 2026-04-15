import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

SideBarLinks()

st.title('App Administration Page')

st.write('## Model 1 Maintenance')

if st.button("Train Model 01", type='primary', use_container_width=True):
    # TODO: wire this to a POST /train route on the API that triggers retraining
    st.info("Training route not yet implemented.")

if st.button('Test Model 01', type='primary', use_container_width=True):
    # TODO: wire this to a GET /test route on the API
    st.info("Testing route not yet implemented.")

if st.button('Model 1 - get predicted value for 10, 25',
             type='primary',
             use_container_width=True):
    results = requests.get('http://web-api:4000/prediction/10/25').json()
    st.dataframe(results)
