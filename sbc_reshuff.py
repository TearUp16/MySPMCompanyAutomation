import streamlit as st
from io import BytesIO
from datetime import datetime
import pandas as pd
import openpyxl

def df_to_xlsx_download(df, container):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1', header=False)
    output.seek(0)

    today_str = datetime.today().strftime('%Y.%m.%d')
    filename = f'POUT {today_str}.xlsx'

    container.download_button(
        label="DOWNLOAD POUTS",
        data=output,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def sbc_reshuff(df):
    container = st.container(border=True)
    container.subheader("FOR RESHUFF")
    filtered_df = df[df['Days Activ'] == 'FOR PULL OUT'].copy()

    if filtered_df.empty:
        container.info("No accounts with 'FOR PULL OUT' status found.")
        return

    filtered_df['POUT'] = 'POUT'
    
    container.dataframe(filtered_df[['CH CODE', 'POUT']])
    df_to_xlsx_download(filtered_df[['CH CODE', 'POUT']], container)
