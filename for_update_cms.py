import streamlit as st
import pandas as pd
from io import BytesIO

def cms_splitter():
    container = st.container(border=True)
    container.title("VOLARE FOR UPDATE ENDO DATE")
    uploaded_file = container.file_uploader("Upload your Excel file", type=["xls", "xlsx"])

    if uploaded_file:
        try:
            # Read first sheet
            df = pd.read_excel(uploaded_file, sheet_name=0)

            # Extract needed columns: A, T, AB, BK
            cols_to_extract = [0, 19, 27, 62]  # A=0, T=19, AB=27, BK=62
            df_extracted = df.iloc[:, cols_to_extract]
            df_extracted.columns = ["Account No.", "Assign Date", "Expiry Date", "Placement"]

            # Format columns
            df_extracted["Account No."] = df_extracted["Account No."].astype(str)
            df_extracted["Assign Date"] = pd.to_datetime(
                df_extracted["Assign Date"], errors="coerce"
            ).dt.strftime("%m/%d/%Y")
            df_extracted["Expiry Date"] = pd.to_datetime(
                df_extracted["Expiry Date"], errors="coerce"
            ).dt.strftime("%m/%d/%Y")

            container.subheader("Preview of extracted columns:")
            container.dataframe(df_extracted)

            # Split by Placement
            placements = df_extracted["Placement"].dropna().unique()

            for place in placements:
                subset = df_extracted[df_extracted["Placement"] == place][
                    ["Account No.", "Assign Date", "Expiry Date"]
                ]

                # Save to Excel in memory
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    subset.to_excel(writer, index=False, sheet_name="Data")

                    # Apply formats
                    workbook = writer.book
                    worksheet = writer.sheets["Data"]

                    text_format = workbook.add_format({"num_format": "@"})
                    date_format = workbook.add_format({"num_format": "mm/dd/yyyy"})

                    worksheet.set_column("A:A", None, text_format)  # Account No. as text
                    worksheet.set_column("B:C", None, date_format)  # Dates as short date

                container.download_button(
                    label=f"Download for Placement: {place}",
                    data=output.getvalue(),
                    file_name=f"placement_{place}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        except Exception as e:
            container.error(f"Error processing file: {e}")

