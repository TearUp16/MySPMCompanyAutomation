import pandas as pd
import streamlit as st
import io
from datetime import datetime
import os

# Define the mapping with the original column names and desired aliases.
mapping = [
    {"source": "CH CODE", "alias": "Old I.C.", "additional": False},
    {"source": "HLIDNO", "alias": "Old I.C. / Account", "additional": False},
    {"source": "LASTNAME, FIRSTNAME MIDNAME", "alias": "Name", "additional": False},
    {"source": None, "alias": "Card No", "additional": True},
    {"source": "BRANCH", "alias": "Placement", "additional": False},
    {"source": None, "alias": "Cycle", "additional": True},
    {"source": "BATCH_NO", "alias": "Product Type", "additional": False},
    {"source": "DPD", "alias": "DPD", "additional": False},
    {"source": "OUTBALANCE", "alias": "Amount", "additional": False},
    {"source": "AMOUNTDUE", "alias": "Total Due", "additional": False},
    {"source": None, "alias": "Principal", "additional": True},
    {"source": "ENDORSEDATE", "alias": "Assign Date", "additional": False},
    {"source": "EMAIL", "alias": "Email", "additional": False},
    {"source": None, "alias": "Date Of Birth", "additional": True},
    {"source": "PULLOUT DATE", "alias": "Expiry Date", "additional": False},
    {"source": "INTRATE", "alias": "Interest", "additional": False},
    {"source": "LASTPAYDATE", "alias": "Last Pay Date", "additional": False},
    {"source": "LASTPAYAMT", "alias": "Last Pay Amount", "additional": False},
    {"source": None, "alias": "Credit Limit", "additional": True},
    {"source": None, "alias": "Write Off Date", "additional": True},
    {"source": None, "alias": "Write Off Date_2", "additional": True},
    {"source": None, "alias": "Write Off Date_3", "additional": True},
    {"source": None, "alias": "Company Name", "additional": True},
    {"source": "AGENT CODE/AGENT USER", "alias": "Collector User Name", "additional": False},
    {"source": "CELLPHONE", "alias": "phone1", "additional": False},
    {"source": "HOMEPHONE", "alias": "phone2", "additional": False},
    {"source": "EMPLOYERCONTACNO", "alias": "phone3", "additional": False},
    {"source": None, "alias": "phone4", "additional": True},
    {"source": None, "alias": "phone5", "additional": True},
    {"source": "PRIMARY ADDRESS", "alias": "address1", "additional": False},
    {"source": "SECONDARY ADDRESS", "alias": "address2", "additional": False},
    {"source": "TERTIARY ADDRESS", "alias": "address3", "additional": False},
    {"source": "PRI CITY/MUNI", "alias": "address4", "additional": False},
    {"source": "SEC CITY/MUNI", "alias": "address5", "additional": False},
    {"source": "PROG_CD", "alias": "PROG_CD", "additional": False},
    {"source": "GROUPING", "alias": "GROUPING", "additional": False},
    {"source": "AMORT1", "alias": "AMORT1", "additional": False},
    {"source": "AMORT2", "alias": "AMORT2", "additional": False},
    {"source": "DATEBEG", "alias": "DATEBEG", "additional": False}
]

def pif_legal_mapping():
    container = st.container(border=True)
    container.subheader("PIF LEGAL MAPPING")
    container.write("UPLOAD YOUR 'DATABASE' SHEET VALUES HERE")

    uploaded_file2 = container.file_uploader("Choose a file", type=["xls", "xlsx", "xlsm"], key="file_uploader2")

    if uploaded_file2:
        try:
            file_extension = os.path.splitext(uploaded_file2.name)[1].lower()
            if file_extension == ".xls":
                df = pd.read_excel(uploaded_file2, engine="xlrd")
            elif file_extension == ".xlsm":
                df = pd.read_excel(uploaded_file2, engine="openpyxl")
            else:
                df = pd.read_excel(uploaded_file2)

            df.columns = df.columns.map(str)

            if "HLIDNO" in df.columns:
                df["HLIDNO"] = df["HLIDNO"].astype(str)
            if "ENDORSEDATE" in df.columns:
                df["ENDORSEDATE"] = pd.to_datetime(df["ENDORSEDATE"]).dt.strftime("%m/%d/%Y")
            if "PULLOUT DATE" in df.columns:
                df["PULLOUT DATE"] = pd.to_datetime(df["PULLOUT DATE"]).dt.strftime("%m/%d/%Y")

        except Exception as e:
            container.error(f"Error reading Excel file: {e}")
        else:
            new_data = {}
            missing_columns = []
            for m in mapping:
                if m["additional"]:
                    new_data[m["alias"]] = ""   
                else:
                    if m["source"] in df.columns:
                        new_data[m["alias"]] = df[m["source"]]
                    else:
                        container.warning(f"Column '{m['source']}' not found. Filling '{m['alias']}' with empty values.")
                        new_data[m["alias"]] = ""
            if missing_columns:
                missing_columns = list(set(missing_columns))  # Remove duplicates
                container.warning(f"The following required columns were not found: {', '.join(missing_columns)}")
            
            mapped_df = pd.DataFrame(new_data)

            container.subheader("Mapped Data")
            container.dataframe(mapped_df)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                mapped_df.to_excel(writer, index=False, sheet_name="Mapped Data")
            processed_data = output.getvalue()

            current_date = datetime.today().strftime('%Y-%m-%d')
            file_name = f"PIF FCL AS {current_date}.xlsx"

            container.download_button(
                label="Download File",
                data=processed_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )