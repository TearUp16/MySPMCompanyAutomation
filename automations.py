import streamlit as st
import pyodbc
import pandas as pd
from fcl_drive import fcl_drive_for_input
from fcl_drive2 import fcl_2nd_drive_for_input
from pif_mapping import pif_legal_mapping
from pif_web_import import pif_legal_website_import_file
from pif_autostat import autostat_fcl
from sbc_reshuff import sbc_reshuff
from sbc_autostat import sbc_autostat
from fcl_placement import fcl_placements
from fcl_branch_placement import fcl_branch_placement
from agent_taggings import agent_taggings
from for_update_cms import cms_splitter
from fcl_drives_web_reshuff import drives_and_agent_automation
from fcl_duplicate_checker import duplicate_checker

# CONNECTION TO QUERY------------------------------------------------------------------------------------------------
def read_sql_query(filename):
    with open(filename, 'r') as file:
        query = file.read()
    return query

# CREDENTIALS TO ODBC------------------------------------------------------------------------------------------------
conn_str = (
    "Driver={MySQL ODBC 5.1 Driver};"
    "Server=192.168.15.197;"
    "Database=bcrm;"
    "UID=abpineda;"
    "PWD=$5ws38DF29nzU;"
)

conn = pyodbc.connect(conn_str)

# SIDEBAR CAMPAIGN SELECTION------------------------------------------------------------------------------------------------
st.sidebar.title("CAMPAIGN AUTOMATIONS")
selected_category = st.sidebar.selectbox(
    "SELECT CAMPAIGN",
    ["FORECLOSURE", "SBC HOMELOAN"]
)
selected_task = st.sidebar.selectbox(
    "SELECT TASK",
    ["ENDORSEMENT", "PULLOUTS", "UPDATE CMS"]
)

# ENDORSEMENT FCL------------------------------------------------------------------------------------------------
if selected_task == "ENDORSEMENT":
    if selected_category == "FORECLOSURE":
        col_title, col_select = st.columns([3, 1])
        with col_title:
            st.title("FORECLOSURE")
        with col_select:
            selected_fcl_page = st.selectbox(
                "SELECT AUTOMATION",
                [
                    "PIF DUPLICATE CHECKER",
                    "PIF PLACEMENT",
                    "PIF DRIVES, RESHUFFLE & WEB IMPORT",
                    "PIF LEGAL MAPPING",
                    "PIF CMS BRANCH PLACEMENT"
                    
                    
                ],
                key="fcl_automation_select"
            )
        if selected_fcl_page == "PIF DUPLICATE CHECKER":
            duplicate_checker()
        elif selected_fcl_page == "PIF PLACEMENT":
            fcl_placements()
        elif selected_fcl_page == "PIF DRIVES, RESHUFFLE & WEB IMPORT":
            drives_and_agent_automation()
        elif selected_fcl_page == "PIF LEGAL MAPPING":
            pif_legal_mapping()
        elif selected_fcl_page == "PIF CMS BRANCH PLACEMENT":
            fcl_branch_placement()
        
        

    elif selected_category == "SBC HOMELOAN":
        # SBC HOMELOAN endorsement title and selectbox side by side
        col_title, col_select = st.columns([3, 1])
        with col_title:
            st.title("SBC HOMELOAN")
        with col_select:
            sbc_homeloan = st.selectbox(
                "SELECT AUTOMATION", 
                ["SBC ENDORSEMENT"], 
                key="sbc_endorsement_select"
            )

# PULLOUTS/AUTOSTATS FCL------------------------------------------------------------------------------------------------
elif selected_task == "PULLOUTS":
    if selected_category == "FORECLOSURE":
        col_title, col_select = st.columns([3, 1])
        with col_title:
            st.title("FORECLOSURE")
        with col_select:
            fcl_page = st.selectbox(
                "SELECT AUTOMATION",
                ["AUTOSTAT FOR FCL"],
                key="autostat_fcl_select"
            )
        if fcl_page == "AUTOSTAT FOR FCL":
            autostat_fcl()

    elif selected_category == "SBC HOMELOAN":
        col_title, col_select = st.columns([3, 1])
        with col_title:
            st.title("SBC HOMELOAN")
        with col_select:
            sbc_homeloan = st.selectbox(
                "SELECT AUTOMATION",
                ["FOR PULLOUT ACCOUNTS"],
                key="sbc_pulout_select"
            )
        if sbc_homeloan == "FOR PULLOUT ACCOUNTS":
            sbc_for_pouts_query = read_sql_query('queries/sbc_for_pouts.sql')
            sbc_for_pouts_remarks_df = pd.read_sql_query(sbc_for_pouts_query, conn)
            container = st.container(border=True)
    
            warning_needed = False

            # THIS CHECKS THE "FOR PULL OUT"------------------------------------------------------------------------------------------------
            if (sbc_for_pouts_remarks_df['Days Activ'] == 'FOR PULL OUT').any():
                warning_needed = True
            else:
                numeric_days = pd.to_numeric(sbc_for_pouts_remarks_df['Days Activ'], errors='coerce')
                if (numeric_days >= 16).any():
                    warning_needed = True

            if warning_needed:
                container.warning("⚠️ NOTE: There are accounts with 16 days or more (FOR PULL OUT).")

            container.subheader("SBC HL DATABASE")
            container.dataframe(sbc_for_pouts_remarks_df)

            container.download_button(
                label="DOWNLOAD DATABASE",
                data=sbc_for_pouts_remarks_df.to_csv(index=False).encode('utf-8'),
                file_name='SBC_REPORT.csv',
                mime='text/csv'
            )
            sbc_reshuff(sbc_for_pouts_remarks_df)
            sbc_autostat(sbc_for_pouts_remarks_df)

# UPDATE FCL------------------------------------------------------------------------------------------------
elif selected_task == "UPDATE CMS":
    if selected_category == "FORECLOSURE":
        cms_splitter()

# PTP SBC HOMELOAN------------------------------------------------------------------------------------------------
    elif selected_category == "SBC HOMELOAN":
        col_title, _ = st.columns([3, 1])
        with col_title:
            st.title("SBC HOMELOAN")
        st.write("COMING SOON")
