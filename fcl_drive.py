import pandas as pd
import streamlit as st
import io
import os

COLUMNS_TO_COPY = [
    "AREA",
    "Ch Code",
    "HlidNo",
    "LastName",
    "FirstName",
    "MidName",
    "LastName, FirstName MidName",
    "ENDO DATE",
    "PROD TYPE",
    "BATCH_NO",
    "PresentAddress",
    "PermanentAddress",
    "Pri Area",
    "Pri City/Muni"
]

LUZON_AREAS = [
    "BAGUIO",
    "BATANGAS",
    "CALAMBA",
    "DAGUPAN",
    "LA UNION",
    "LAUNION",
    "MALOLOS",
    "PAMPANGA"
]

VISAYAS_AREAS = [
    "BACOLOD",
    "CEBU NORTH",
    "CEBUNORTH",
    "CEBU SOUTH",
    "CEBUSOUTH",
    "ILOILO",
    "ILO-ILO",
    "ILO ILO"
]

MINDANAO_AREAS = [
    "CAGAYAN",
    "CAGAYAN DE ORO",
    "DAVAO",
    "GEN SANTOS",
    "GENSAN",
    "GENERAL SANTOS",
    "PAGADIAN",
    "TAGUM",
    "ZAMBOANGA"
]

# Normalize area lists to uppercase and strip spaces
LUZON_AREAS = [a.upper().strip() for a in LUZON_AREAS]
VISAYAS_AREAS = [a.upper().strip() for a in VISAYAS_AREAS]
MINDANAO_AREAS = [a.upper().strip() for a in MINDANAO_AREAS]

def fcl_drive_for_input():
    container = st.container(border=True)
    container.subheader("FOR INPUT DATA IN FCL DRIVE")
    container.write("UPLOAD YOUR 'BCRM UPLOAD' FILE HERE")

    uploaded_file = container.file_uploader("Choose a file", type=["xls", "xlsx"], key="file_uploader")

    if uploaded_file:
        try:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            if file_extension == ".xls":
                df = pd.read_excel(uploaded_file, engine="xlrd", index_col=False)
            else:
                df = pd.read_excel(uploaded_file, engine="openpyxl", index_col=False)

            if "HlidNo" in df.columns:
                df["HlidNo"] = df["HlidNo"].astype(str)

        except Exception as e:
            container.error(f"Error reading Excel file: {e}")
        else:
            missing_cols = [col for col in COLUMNS_TO_COPY if col not in df.columns]
            if missing_cols:
                container.error(f"The following columns are missing in the uploaded file: {', '.join(missing_cols)}")
            else:
                cleaned_df = df[COLUMNS_TO_COPY].copy()
                cleaned_df["MidName"] = cleaned_df["MidName"].astype(str).str[0]

                # Normalize AREA column: uppercase, strip, replace multiple spaces with single space
                cleaned_df["AREA"] = (
                    cleaned_df["AREA"]
                    .astype(str)
                    .str.upper()
                    .str.strip()
                    .str.replace(r"\s+", " ", regex=True)
                )

                container.subheader("Cleaned Data")
                container.dataframe(cleaned_df)

                # Add a download button for the entire cleaned data
                output_all = io.BytesIO()
                with pd.ExcelWriter(output_all, engine='xlsxwriter') as writer:
                    cleaned_df.to_excel(writer, index=False, sheet_name="All Data")
                data_all = output_all.getvalue()

                container.download_button(
                    label="Download ALL",
                    data=data_all,
                    file_name="FCL_1ST_DRIVE.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                def create_excel_for_areas(area_list, file_label):
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        area_df = cleaned_df[cleaned_df["AREA"].isin(area_list)]
                        if not area_df.empty:
                            sheet_name = file_label[:31]
                            area_df.to_excel(writer, index=False, sheet_name=sheet_name)
                    return output.getvalue()

                for areas_group, label in [
                    (LUZON_AREAS, "LUZON"),
                    (VISAYAS_AREAS, "VISAYAS"),
                    (MINDANAO_AREAS, "MINDANAO")
                ]:
                    if cleaned_df['AREA'].isin(areas_group).any():
                        excel_data = create_excel_for_areas(areas_group, label)
                        container.download_button(
                            label=f"Download {label} Excel",
                            data=excel_data,
                            file_name=f"FCL {label}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        container.write(f"No data for {label}")
