import streamlit as st
import pyodbc
import pandas as pd

def read_sql_query(filename):
    with open(filename, 'r') as file:
        query = file.read()
    return query

conn_str = (
    "Driver={MySQL ODBC 5.1 Driver};"
    "Server=192.168.15.197;"
    "Database=bcrm;"
    "UID=abpineda;"
    "PWD=$5ws38DF29nzU;"
    )

conn = pyodbc.connect(conn_str)

# Read queries
cbs_remarks_query = read_sql_query('queries/cbs_remarks.sql')
masterlist_query = read_sql_query('queries/masterlist.sql')

# Run queries
cbs_remarks_df = pd.read_sql_query(cbs_remarks_query, conn)
masterlist_df = pd.read_sql_query(masterlist_query, conn)

# Display data in Streamlit
st.title("Database Query Results")
st.header("CBS Remarks")
st.dataframe(cbs_remarks_df)

st.header("Masterlist")
st.dataframe(masterlist_df)