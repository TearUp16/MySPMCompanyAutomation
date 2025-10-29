import pandas as pd
import streamlit as st
from datetime import datetime
import io

def process_file(uploaded_file):
    df = pd.read_excel(uploaded_file, header=None)

    # to rename the first column to 'chCode'
    df.columns = ['chCode']
    
    # Columns
    df['status'] = 'RETURNS'
    df['substatus'] = 'PULLOUT'
    df['amount'] = ''
    df['start_date'] = ''
    df['end_date'] = ''
    df['or_number'] = ''
    df['notes'] = "PULLED OUT - RE ENDO AS"
    df['new_address'] = ''
    df['new_contact'] = ''
    df['agent'] = 'POUT'
    
    df['barcode_date'] = datetime.now().strftime('%m/%d/%y %I:%M %p')
    
    return df

def autostat_fcl():
    container = st.container(border=True)
    container.subheader("FCL AUTOSTAT")
    container.write("UPLOAD YOUR EXCEL FILE HERE")

    # Uploader
    uploaded_file = container.file_uploader("Choose a file", type=["xlsx"])
    
    if uploaded_file is not None:
        df = process_file(uploaded_file)

        # Choices for account type
        special_choices = ["FCL PEJF", "FCL NOF", "FCL 2ND", "FCL 3RD"]
        user_choice = container.selectbox("Account Type", special_choices)
        user_date = container.date_input("Select Date")

        # Apply the user's choices to the special column
        df['notes'] = df['notes'] + f" {user_choice} {user_date.strftime('%m/%d/%Y')}"

        container.write("Processed Data:")
        container.dataframe(df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)

        container.download_button(
            label="Download File",
            data=output,
            file_name="AUTOSTAT_POUT.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
