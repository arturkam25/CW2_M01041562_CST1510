import streamlit as st
from app.data.schema import create_tables

st.set_page_config(page_title="Multi-Domain Intelligence Platform", layout="wide")

# Initialize DB tables
create_tables()

st.title("📊 Multi-Domain Intelligence Platform")
st.write("Use the left sidebar to navigate between modules.")

st.info("Go to **Users Management** via the sidebar (left side).")
