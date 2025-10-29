import pandas as pd
import streamlit as st
from datetime import datetime

def pif_legal_website_import_file():
    def clean_data(uploaded_file3):
        df = pd.read_excel(uploaded_file3)
        df['CH_CODE'] = df['Ch Code']

        def add_columns(row):
            if row['ACCOUNT_TYPE'] == 'FCL NOF' or row['ACCOUNT_TYPE'] == 'FCL PEJF':
                row['STAGE'] = 1
                row['TYPE'] = 'DEF'
            elif row['ACCOUNT_TYPE'] == 'FCL 2ND':
                row['STAGE'] = 2
                row['TYPE'] = 'ADV'
            elif row['ACCOUNT_TYPE'] == 'FCL 3RD':
                row['STAGE'] = 3
                row['TYPE'] = 'ADV'
            return row
        
        df = df.apply(add_columns, axis=1)
        df_cleaned = df[['CH_CODE', 'STAGE', 'TYPE']]
        return df_cleaned
    
    container = st.container(border=True)

    container.subheader("PIF LEGAL WEBSITE IMPORT FILE")
    container.write("UPLOAD YOUR 'BCRM UPLOAD' FILE HERE")

    uploaded_file3 = container.file_uploader("Choose a file", type=["xls", "xlsx"], key="file_uploader3")

    if uploaded_file3 is not None:
        cleaned_df = clean_data(uploaded_file3)

        container.write("Cleaned Data Preview:")
        container.dataframe(cleaned_df)

        container.write("Download CSV file:")

        cleaned_csv = cleaned_df.to_csv(index=False).encode('utf-8')

        current_date = datetime.today().strftime('%m.%d.%Y')
        file_name1 = f"FOR {current_date} - ENDO.csv"

        container.download_button(
            label="Download File",
            data=cleaned_csv,
            file_name=file_name1,
            mime="text/csv"
        )