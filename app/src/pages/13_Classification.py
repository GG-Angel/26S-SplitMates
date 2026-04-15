import logging
logger = logging.getLogger(__name__)
import streamlit as st
import pandas as pd
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.write("""
# Simple Iris Flower Prediction App

This example is borrowed from [The Data Professor](https://github.com/dataprofessor/streamlit_freecodecamp/tree/main/app_7_classification_iris)
         
This app predicts the **Iris flower** type!
""")

st.sidebar.header('User Input Parameters')

# Below, different user inputs are defined.  When you view the UI, 
# notice that they are in the sidebar. 
def user_input_features():
    sepal_length = st.sidebar.slider('Sepal length', 4.3, 7.9, 5.4)
    sepal_width = st.sidebar.slider('Sepal width', 2.0, 4.4, 3.4)
    petal_length = st.sidebar.slider('Petal length', 1.0, 6.9, 1.3)
    petal_width = st.sidebar.slider('Petal width', 0.1, 2.5, 0.2)
    data = {'sepal_length': sepal_length,
            'sepal_width': sepal_width,
            'petal_length': petal_length,
            'petal_width': petal_width}
    features = pd.DataFrame(data, index=[0])
    return features

# get a data frame with the input features from the user
df = user_input_features()

# show the exact values the user entered in a table.
st.subheader('User Input parameters')
st.write(df)

# load the standard iris dataset and generate a 
# random forest classifier 
iris = datasets.load_iris()
X = iris.data
Y = iris.target
clf = RandomForestClassifier()

# fit the model
clf.fit(X, Y)

# use the values entered by the user for prediction
prediction = clf.predict(df)
prediction_proba = clf.predict_proba(df)

st.subheader('Class labels and their corresponding index number')
st.write(iris.target_names)

st.subheader('Prediction')
st.write(iris.target_names[prediction])

st.subheader('Prediction Probability')
st.write(prediction_proba)