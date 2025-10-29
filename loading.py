import streamlit as st
import time

st.title("Loading Animation Example")

with st.spinner("Loading... Please wait"):
    time.sleep(3)  # Simulate a 3-second loading delay

st.success("Done! Here's your content.")
