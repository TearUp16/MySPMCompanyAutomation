import streamlit as st
import pandas as pd
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

def filter_batch(df, keyword):
    filtered_df = df[df['BATCH_NO'].str.contains(keyword, case=False, na=False)].copy()
    
    # Format datetime columns to MM/DD/YYYY
    for col in filtered_df.select_dtypes(include=['datetime', 'datetime64']).columns:
        filtered_df[col] = filtered_df[col].dt.strftime('%m/%d/%Y')
    
    # Convert HLIDNO to string to avoid scientific notation
    if 'HLIDNO' in filtered_df.columns:
        filtered_df['HLIDNO'] = filtered_df['HLIDNO'].apply(lambda x: '{:.0f}'.format(x) if pd.notnull(x) else '')
    
    return filtered_df

def fcl_placements():
    container = st.container(border=True)
    container.subheader("FCL PLACEMENTS")
    container.write("UPLOAD ENDORSEMENT FILE HERE")

    uploaded_file = container.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file:
        xls = pd.ExcelFile(uploaded_file)

        # Try loading the 2nd sheet first
        try:
            df = pd.read_excel(xls, sheet_name=1)
            sheet_used = xls.sheet_names[1]
        except Exception:
            df = None
            sheet_used = None

        # If no df or no BATCH_NO column, try 1st sheet
        if df is None or 'BATCH_NO' not in df.columns:
            try:
                df = pd.read_excel(xls, sheet_name=0)
                sheet_used = xls.sheet_names[0]
            except Exception:
                df = None
                sheet_used = None

        if df is None or 'BATCH_NO' not in df.columns:
            container.error("Could not find 'BATCH_NO' column in the first two sheets. Please check your file.")
        else:
            container.write(f"Processing sheet: {sheet_used}")
            keywords = ['NOF', 'PEJF', 'COS-SEC', 'COS-REG']
            for kw in keywords:
                filtered_df = filter_batch(df, kw)
                container.write(f"Rows containing '{kw}': {len(filtered_df)}")
                if not filtered_df.empty:
                    data_xlsx = to_excel(filtered_df)
                    st.download_button(
                        label=f"Download {kw} data",
                        data=data_xlsx,
                        file_name=f"FCL ENDO REGION {kw}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    container.write(f"No rows found with '{kw}'")
