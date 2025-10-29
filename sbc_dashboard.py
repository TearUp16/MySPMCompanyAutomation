import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px

def sbc_dashboard():
    # ODBC Connection
    conn_str = (
        "Driver={MySQL ODBC 5.1 Driver};"
        "Server=192.168.15.197;"
        "Database=bcrm;"
        "UID=abpineda;"
        "PWD=$5ws38DF29nzU;"
    )
    conn = pyodbc.connect(conn_str)

    # Read your query from a .sql file
    with open("queries/sbc_for_pouts.sql", "r") as f:
        query = f.read()

    # Query the database
    df = pd.read_sql_query(query, conn)
    conn.close()

    # --- Data cleaning/processing ---
    for col in ['ENDO DATE', 'PULL OUT DATE', 'DateProcessed']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    df['Status'] = df['Days Activ'].apply(
        lambda x: 'FOR PULL OUT' if x == 'FOR PULL OUT' else 'Active'
    )

    # --- Title with Logo ---
    col_img, col_title = st.columns([1, 7])
    with col_img:
        st.image("security-bank-logo.jpg", width=120)
    with col_title:
        st.markdown(
            "<h1 style='padding-top:5px; margin-bottom:0px;'>SBC HOMELOAN</h1>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --- KPIs (all data) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Accounts", f"{len(df):,}")
    col2.metric("Outstanding Balance", f"₱ {df['OUTSTANDING BALANCE'].sum():,.2f}")
    col3.metric("FOR PULL OUT", df[df['Status']=='FOR PULL OUT'].shape[0])

    st.markdown("---")

    # --- Foldable Data Table ---
    with st.expander("Active Accounts Table", expanded=False):
        st.dataframe(df)

    # --- Existing Endorsements Histogram ---
    fig_endorse = px.histogram(
        df,
        x='ENDO DATE',
        nbins=30,
        title="Accounts Endorsed by Date",
        color_discrete_sequence=['#D4DF55']
    )
    st.plotly_chart(fig_endorse, use_container_width=True)
    st.markdown("---")

    # --- NEW: Pull-Outs Per Day ---
    st.subheader("Pull-Outs Per Day")

    # 1) Filter to pull-outs with a valid date
    pull_df = df[
        (df['Status'] == 'FOR PULL OUT') &
        (df['PULL OUT DATE'].notna())
    ].copy()

    if pull_df.empty:
        st.info("No pull-outs with valid dates to display.")
    else:
        # 2) Extract just the date and count
        pull_df['PullDate'] = pull_df['PULL OUT DATE'].dt.date
        daily_counts = (
            pull_df
            .groupby('PullDate')
            .size()
            .reset_index(name='PullOutCount')
        )

        # 3) Date‐range picker
        min_d = daily_counts['PullDate'].min()
        max_d = daily_counts['PullDate'].max()
        start_d, end_d = st.date_input(
            "Date range:",
            value=(min_d, max_d),
            min_value=min_d,
            max_value=max_d
        )

        mask = (daily_counts['PullDate'] >= start_d) & (daily_counts['PullDate'] <= end_d)
        filtered = daily_counts.loc[mask]

        # 4) Plot as a line chart with markers
        fig_pull = px.line(
            filtered,
            x='PullDate',
            y='PullOutCount',
            markers=True,
            title="Number of Pull-Outs per Day",
            labels={"PullDate":"Date", "PullOutCount":"# Pull-Outs"}
        )
        st.plotly_chart(fig_pull, use_container_width=True)

    st.markdown("---")

# If running as a standalone file, call the function
if __name__ == "__main__":
    sbc_dashboard()
