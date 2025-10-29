import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO
import os

def sbc_pout_monitoring():
    # ---------------------------
    # Database connection + query
    # ---------------------------
    def sbc_hl_monitoring():
        conn_str = (
            "Driver={MySQL ODBC 5.1 Driver};"
            "Server=192.168.15.197;"
            "Database=bcrm;"
            "UID=abpineda;"
            "PWD=$5ws38DF29nzU;"
        )
        conn = pyodbc.connect(conn_str)

        # ✅ Point to queries/ folder
        BASE_DIR = os.path.dirname(__file__)
        sql_file = os.path.join(BASE_DIR, "queries", "sbc_monitoring.sql")

        print("🔎 Looking for SQL file at:", sql_file)  # debug log

        with open(sql_file, "r") as f:
            query = f.read()

        df = pd.read_sql(query, conn)
        conn.close()
        return df


    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    # ---------------------------
    # Streamlit Page
    # ---------------------------
    st.title("SBC MONITORING REPORT")

    df = sbc_hl_monitoring()

    pulled_out_df = df[df["STATUS"] == "PULLED OUT"].copy()
    active_df = df[df["STATUS"] != "PULLED OUT"].copy()

    # ---------------------------
    # Filter for pulled out
    # ---------------------------
    pulled_out_df["PULL OUT DATE"] = pd.to_datetime(pulled_out_df["PULL OUT DATE"], errors="coerce")

    # ✅ Use only valid dates (drop NaT)
    valid_dates = pulled_out_df["PULL OUT DATE"].dropna()

    if not valid_dates.empty:
        min_date = valid_dates.min()
        max_date = valid_dates.max()

        # ✅ Default range = latest month only
        start_of_latest_month = max_date.replace(day=1)
        end_of_latest_month = max_date

        # Two side-by-side inputs
        col1, col2 = st.columns(2)
        start_date = col1.date_input(
            "Start date:",
            value=start_of_latest_month,
            min_value=min_date,
            max_value=max_date
        )
        end_date = col2.date_input(
            "End date:",
            value=end_of_latest_month,
            min_value=min_date,
            max_value=max_date
        )

        # Apply filter
        pulled_out_df = pulled_out_df[
            (pulled_out_df["PULL OUT DATE"] >= pd.to_datetime(start_date)) &
            (pulled_out_df["PULL OUT DATE"] <= pd.to_datetime(end_date))
        ]

    # Pulled Out table
    st.subheader("PULLED OUT")
    st.dataframe(pulled_out_df, use_container_width=True)
    st.download_button(
        label="DOWNLOAD PULLOUTS",
        data=convert_df_to_excel(pulled_out_df),
        file_name="sbc_hl_pouts.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Active table
    st.subheader("ACTIVE ACCOUNTS")
    st.dataframe(active_df, use_container_width=True)
    st.download_button(
        label="DOWNLOAD ACTIVE ACCOUNTS",
        data=convert_df_to_excel(active_df),
        file_name="sbc_hl_latest.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
