import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
from collections import defaultdict


# ==========================================================
# COMBINED AUTOMATION: DRIVES_WEB_IMPORT + AGENT_TAGGINGS
# ==========================================================
def drives_and_agent_automation():
    st.title("DRIVES | WEB | RESHUFFLE AUTOMATION")

    # ==========================================================
    # CONSTANTS AND MAPPINGS
    # ==========================================================
    COLUMNS_TO_COPY_1ST = [
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
        "BAGUIO", "BATANGAS", "CALAMBA", "DAGUPAN",
        "LA UNION", "LAUNION", "MALOLOS", "PAMPANGA"
    ]
    VISAYAS_AREAS = [
        "BACOLOD", "CEBU NORTH", "CEBUNORTH", "CEBU SOUTH",
        "CEBUSOUTH", "ILOILO", "ILO-ILO", "ILO ILO"
    ]
    MINDANAO_AREAS = [
        "CAGAYAN", "CAGAYAN DE ORO", "DAVAO", "GEN SANTOS",
        "GENSAN", "GENERAL SANTOS", "PAGADIAN", "TAGUM", "ZAMBOANGA"
    ]

    LUZON_AREAS = [a.upper().strip() for a in LUZON_AREAS]
    VISAYAS_AREAS = [a.upper().strip() for a in VISAYAS_AREAS]
    MINDANAO_AREAS = [a.upper().strip() for a in MINDANAO_AREAS]

    COLUMNS_TO_COPY_2ND = [
        "HlidNo",
        "LastName, FirstName MidName",
        "BRANCH",
        "ENDO DATE"
    ]

    branch_agent_map = {
        "BATANGAS LEGAL": ["BNMB"],
        "CALAMBA LEGAL": ["CADB"],
        "MALOLOS LEGAL": ["MCDM", "MAEO", "PMAO"],
        "PAMPANGA LEGAL": ["PGJO", "PGMM", "BKNB"],
        "BAGUIO LEGAL": ["PSOA"],
        "DAGUPAN LEGAL": ["PSOA"],
        "LA UNION LEGAL": ["PSOA"],
        "BACOLOD LEGAL": ["BRAA","BJGG", "BCAM"],
        "CEBU NORTH LEGAL": ["CHCE", "CGAM"],
        "CEBU SOUTH LEGAL": ["CGAM", "CHCE"],
        "ILO-ILO LEGAL": ["ICOD"],
        "CAGAYAN DE ORO LEGAL": ["CKCT"],
        "DAVAO LEGAL": ["DLMB", "ZNOC", "GCAA"],
        "GEN SANTOS LEGAL": ["GFBH"],
        "PAGADIAN LEGAL": ["ZSMR"],
        "TAGUM LEGAL": ["TKER"],
        "ZAMBOANGA LEGAL": ["ZCSA"]
    }
    branch_agent_map_up = {k.strip().upper(): v for k, v in branch_agent_map.items()}

    ncr_account_type_map = {
        "FCL PEJF": "QRAR",
        "FCL NOF": "QRAR",
        "FCL 2ND": "QYOP",
        "FCL 3RD": "QCCS"
    }

    # ==========================================================
    # FILE UPLOAD
    # ==========================================================
    container = st.container(border=True)
    uploaded_file = st.file_uploader("📤 Upload BCRM Upload File", type=["xls", "xlsx"])
    if not uploaded_file:
        st.info("Please upload an Excel file to start processing.")
        st.stop()

    # Read Excel
    try:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension == ".xls":
            df = pd.read_excel(uploaded_file, engine="xlrd", index_col=False)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl", index_col=False)

        if "HlidNo" in df.columns:
            df["HlidNo"] = df["HlidNo"].astype(str)
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        st.stop()

    st.success("✅ File uploaded successfully!")

    # ==========================================================
    # SECTION 1: FCL 1ST DRIVE (Fixed + Full Table)
    # ==========================================================
    st.subheader("📘 FCL 1st Drive Output")

    missing_cols_1st = [col for col in COLUMNS_TO_COPY_1ST if col not in df.columns]
    if missing_cols_1st:
        st.warning(f"⚠️ Missing columns for FCL 1st Drive: {', '.join(missing_cols_1st)}")
    else:
        cleaned_df_1st = df[COLUMNS_TO_COPY_1ST].copy()
        cleaned_df_1st["MidName"] = cleaned_df_1st["MidName"].astype(str).str[0]
        cleaned_df_1st["AREA"] = (
            cleaned_df_1st["AREA"]
            .astype(str)
            .str.upper()
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

        st.dataframe(cleaned_df_1st, use_container_width=True)

        # Download all data
        output_all = io.BytesIO()
        with pd.ExcelWriter(output_all, engine='xlsxwriter') as writer:
            cleaned_df_1st.to_excel(writer, index=False, sheet_name="All Data")
        data_all = output_all.getvalue()

        st.download_button(
            label="⬇️ Download ALL (FCL 1st Drive)",
            data=data_all,
            file_name="FCL_1ST_DRIVE.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Helper to create area-based Excel
        def create_excel_for_areas(area_list, file_label):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                area_df = cleaned_df_1st[cleaned_df_1st["AREA"].isin(area_list)]
                if not area_df.empty:
                    sheet_name = file_label[:31]
                    area_df.to_excel(writer, index=False, sheet_name=sheet_name)
            return output.getvalue()

        # Generate and show area-specific download buttons
        for areas_group, label in [
            (LUZON_AREAS, "LUZON"),
            (VISAYAS_AREAS, "VISAYAS"),
            (MINDANAO_AREAS, "MINDANAO")
        ]:
            if cleaned_df_1st["AREA"].isin(areas_group).any():
                excel_data = create_excel_for_areas(areas_group, label)
                st.download_button(
                    label=f"⬇️ Download {label} Excel",
                    data=excel_data,
                    file_name=f"FCL {label}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.write(f"No data for {label}")

    # ==========================================================
    # SECTION 2: FCL 2ND DRIVE
    # ==========================================================
    st.subheader("📗 FCL 2nd Drive Output")

    missing_cols_2nd = [col for col in COLUMNS_TO_COPY_2ND if col not in df.columns]
    if missing_cols_2nd:
        st.warning(f"⚠️ Missing columns for FCL 2nd Drive: {', '.join(missing_cols_2nd)}")
    else:
        cleaned_df_2nd = df[COLUMNS_TO_COPY_2ND].copy()
        st.dataframe(cleaned_df_2nd, use_container_width=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            cleaned_df_2nd.to_excel(writer, index=False, sheet_name="Cleaned Data")
        processed_data = output.getvalue()

        st.download_button(
            label="⬇️ Download File (FCL 2nd Drive)",
            data=processed_data,
            file_name="FOR_INPUT_IN_FCL_2ND_DRIVE.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # ==========================================================
    # SECTION 3: PIF LEGAL WEBSITE IMPORT
    # ==========================================================
    st.subheader("📙 PIF Legal Website Import File")

    if "Ch Code" in df.columns and "ACCOUNT_TYPE" in df.columns:
        df_pif = df.copy()
        df_pif['CH_CODE'] = df_pif['Ch Code']

        def add_columns(row):
            if row['ACCOUNT_TYPE'] in ['FCL NOF', 'FCL PEJF']:
                row['STAGE'] = 1
                row['TYPE'] = 'DEF'
            elif row['ACCOUNT_TYPE'] == 'FCL 2ND':
                row['STAGE'] = 2
                row['TYPE'] = 'ADV'
            elif row['ACCOUNT_TYPE'] == 'FCL 3RD':
                row['STAGE'] = 3
                row['TYPE'] = 'ADV'
            return row

        df_pif = df_pif.apply(add_columns, axis=1)
        df_cleaned_pif = df_pif[['CH_CODE', 'STAGE', 'TYPE']]

        st.dataframe(df_cleaned_pif, use_container_width=True)

        cleaned_csv = df_cleaned_pif.to_csv(index=False).encode('utf-8')
        current_date = datetime.today().strftime('%m.%d.%Y')
        file_name1 = f"FOR_{current_date}_ENDO.csv"

        st.download_button(
            label="⬇️ Download File (PIF Legal Website Import)",
            data=cleaned_csv,
            file_name=file_name1,
            mime="text/csv"
        )
    else:
        st.warning("⚠️ Missing columns for PIF Legal Website Import (requires 'Ch Code' and 'ACCOUNT_TYPE').")

    # ==========================================================
    # SECTION 4: AGENT TAGGING (RESHUFFLE)
    # ==========================================================
    st.subheader("📒 PIF LEGAL RESHUFFLE (Agent Tagging)")

    df.columns = [c.strip().upper() for c in df.columns]
    required_cols = ["HLIDNO", "CH CODE", "BRANCH", "ACCOUNT_TYPE"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.warning(f"⚠️ Missing required columns for agent tagging: {', '.join(missing)}")
        return

    for col in ["HLIDNO", "CH CODE", "BRANCH", "ACCOUNT_TYPE"]:
        df[col] = df[col].astype(str).str.strip().str.upper()

    df["_BRANCH_NORM"] = df["BRANCH"].replace(r"\s+", " ", regex=True)
    counters = defaultdict(int)
    assigned = []

    for _, row in df.iterrows():
        branch = row["_BRANCH_NORM"]
        acct_type = row["ACCOUNT_TYPE"]

        if branch == "NCR":
            agent = ncr_account_type_map.get(acct_type)
            assigned.append(agent)
        else:
            codes = branch_agent_map_up.get(branch)
            if codes:
                idx = counters[branch] % len(codes)
                assigned.append(codes[idx])
                counters[branch] += 1
            else:
                assigned.append(None)

    df["AGENT CODE"] = assigned

    unmatched = sorted({v for v, a in zip(df["_BRANCH_NORM"], assigned) if a is None and v.strip() != ""})
    if unmatched:
        st.warning("⚠️ These BRANCH or ACCOUNT_TYPE values did NOT match your mapping:")
        st.write(unmatched)

    out_df = df.drop(columns=["_BRANCH_NORM"]).copy()
    short_df = out_df[["CH CODE", "AGENT CODE"]]
    short_df = short_df[short_df["CH CODE"].notna() & (short_df["CH CODE"].str.strip() != "")]

    full_output = io.BytesIO()
    with pd.ExcelWriter(full_output, engine="xlsxwriter") as writer:
        out_df.to_excel(writer, index=False)
    full_output.seek(0)

    short_output = io.BytesIO()
    with pd.ExcelWriter(short_output, engine="xlsxwriter") as writer:
        short_df.to_excel(writer, index=False, header=False)
    short_output.seek(0)

    st.download_button(
        label="⬇️ Download UPDATED FILE (with Agent Code)",
        data=full_output.getvalue(),
        file_name="updated_agent_codes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.download_button(
        label="⬇️ Download FOR RESHUFFLE (CH CODE + Agent Code only, no header)",
        data=short_output.getvalue(),
        file_name="for_reshuffle.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ==========================================================
# RUN APP
# ==========================================================
if __name__ == "__main__":
    st.set_page_config(page_title="FCL Automation Tool", layout="centered")
    drives_and_agent_automation()
