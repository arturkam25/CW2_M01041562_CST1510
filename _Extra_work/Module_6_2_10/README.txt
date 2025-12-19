Project Description

The Welcome Survey Analysis application is a tool for Exploratory Data Analysis (EDA) built in Python and powered by Streamlit.
The project allows you to quickly load data from a CSV file, clean and filter it, assess data quality, and generate interactive visualisations.

The project was developed specifically for analysing one training dataset.

The dataset contains binary values (0 and 1), which indicate whether a respondent belongs to a given category or not.

Main Features
Load the provided sample CSV file
Automatic detection of column types (numeric, categorical, binary)

Data overview:
number of rows and columns
column names
data types
dataset preview

Data quality report:
missing values
duplicates
basic statistics for numeric columns
Interactive filtering of categorical and numeric fields

Visualisations (Plotly charts):
histograms
pie charts
bar charts
stacked bar charts
box plots

Additional computed fields:
age estimate
experience estimate
age groups
experience groups

Requirements
This application requires:
Python 3.10 or later

The following Python packages:
streamlit
pandas
numpy
plotly

How to Run the Application

Open a terminal in the project folder
(the folder containing app.py)
Run the Streamlit application:
streamlit run app.py
The app will open automatically in your browser at:
http://localhost:8501
