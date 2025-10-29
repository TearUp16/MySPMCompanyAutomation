import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Accounts per Batch Visualization", layout="wide")

st.title("📊 Accounts per Batch Visualization")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("Preview of Data")
    st.dataframe(df.head())

    # --- SELECT COLUMN ---
    st.subheader("Select Columns")
    batch_col = st.selectbox("Select the Batch Number column", df.columns)
    account_col = st.selectbox("Select the Account column", df.columns)

    # --- AGGREGATE DATA ---
    grouped = df.groupby(batch_col)[account_col].nunique().reset_index()
    grouped.columns = ["Batch No", "Number of Accounts"]

    # --- TOTAL ACCOUNTS ---
    total_accounts = grouped["Number of Accounts"].sum()

    st.markdown(f"### 🧾 Total Accounts Across All Batches: **{total_accounts:,}**")

    st.subheader("Summary Table")
    st.dataframe(grouped)

    # --- PLOT ---
    st.subheader("Visualization")
    fig = px.bar(
        grouped,
        x="Batch No",
        y="Number of Accounts",
        title="Accounts per Batch Number",
        text="Number of Accounts",
        color="Batch No",
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(xaxis_title="Batch Number", yaxis_title="Number of Accounts")

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👆 Please upload your Excel file to begin.")
