# test_secrets.py
import streamlit as st

st.write("GOOGLE_API_KEY from secrets:", st.secrets.get("GOOGLE_API_KEY", "Not found"))