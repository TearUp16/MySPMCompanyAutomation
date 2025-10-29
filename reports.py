import streamlit as st
import pyodbc
from fcl_payments_ptp import fcl_payments_ptp
from sbc_hl_pout_monitoring import sbc_pout_monitoring

# Database connection
conn_str = (
    "Driver={MySQL ODBC 5.1 Driver};"
    "Server=192.168.15.197;"
    "Database=bcrm;"
    "UID=abpineda;"
    "PWD=$5ws38DF29nzU;"
)
conn = pyodbc.connect(conn_str)

# SIDEBAR CAMPAIGN SELECTION------------------------------------------------------------------------------------------------
selected_category = st.sidebar.selectbox(
    "SELECT REPORT",
    ["PIF FCL (PAYMENTS & PTP)", "SBC HOMELOAN(PULL OUTS)"]
)

if selected_category == "PIF FCL (PAYMENTS & PTP)":
    fcl_payments_ptp()
elif selected_category == "SBC HOMELOAN(PULL OUTS)":
    sbc_pout_monitoring()