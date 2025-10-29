import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime


def duplicate_checker(
    masterlist_path=r"C:\Users\SPM\Documents\Save Files Here\abpineda\CAMPAIGNS\FCL\PIF LEGAL MASTERLIST 2024-2025.xlsx",
    masterlist_sheet="DATABASE (V2)"
):
    """
    Streamlit app for checking duplicate account numbers against a masterlist.
    You can integrate this into your main Streamlit page by importing and calling:
        fcl_duplicate_checker_app()
    """

    # --- Streamlit Page Setup ---
    st.title("🏦 FCL Duplicate Account Checker")

    # --- Helper: Detect Header Row ---
    def detect_header_row(file_path, sheet_name):
        """Find which row contains 'ACCOUNT NUMBER'."""
        try:
            preview = pd.read_excel(file_path, sheet_name=sheet_name, nrows=15, header=None)
            for i, row in preview.iterrows():
                if row.astype(str).str.contains("ACCOUNT NUMBER", case=False, na=False).any():
                    return i
            return None
        except Exception as e:
            st.error(f"⚠️ Error detecting masterlist header row: {e}")
            return None

    # --- Helper: Load Masterlist ---
    def load_masterlist():
        """Load the masterlist Excel file."""
        if not os.path.exists(masterlist_path):
            st.error(f"❌ Masterlist not found at: {masterlist_path}")
            return None

        try:
            header_row = detect_header_row(masterlist_path, masterlist_sheet)
            if header_row is None:
                st.error("❌ Could not find 'ACCOUNT NUMBER' header in masterlist.")
                return None

            df = pd.read_excel(masterlist_path, sheet_name=masterlist_sheet, header=header_row)
            df.columns = df.columns.str.strip().str.upper()

            required_cols = {"ACCOUNT NUMBER", "LEADS CHCODE"}
            if not required_cols.issubset(set(df.columns)):
                st.error("❌ Masterlist must contain 'ACCOUNT NUMBER' and 'LEADS CHCODE' columns.")
                st.write("🧩 Columns found:", list(df.columns))
                return None

            return df
        except Exception as e:
            st.error(f"⚠️ Error loading masterlist: {e}")
            return None

    # --- Helper: Find HLIDNO Sheet ---
    def find_hlidno_sheet(uploaded_file):
        """Find the sheet with an 'HLIDNO' column."""
        try:
            xls = pd.ExcelFile(uploaded_file)
            for sheet in xls.sheet_names:
                df_preview = pd.read_excel(xls, sheet_name=sheet, nrows=10)
                df_preview.columns = df_preview.columns.str.strip().str.upper()
                if "HLIDNO" in df_preview.columns:
                    return sheet
            return None
        except Exception as e:
            st.error(f"⚠️ Error detecting HLIDNO sheet: {e}")
            return None

    # --- File Upload ---
    boss_file = st.file_uploader("📤 Upload File to Check", type=["xlsx", "xls"])

    if not boss_file:
        st.info("👆 Please upload a file to begin.")
        return

    masterlist = load_masterlist()
    if masterlist is None:
        return

    try:
        # Detect the correct sheet
        target_sheet = find_hlidno_sheet(boss_file)
        if target_sheet is None:
            st.error("❌ Could not find any sheet containing an 'HLIDNO' column.")
            return

        df = pd.read_excel(boss_file, sheet_name=target_sheet)
        df.columns = df.columns.str.strip().str.upper()
        st.info(f"✅ Using sheet: **{target_sheet}**")

        # --- Find Duplicates ---
        duplicates = df[df["HLIDNO"].astype(str)
                        .isin(masterlist["ACCOUNT NUMBER"].astype(str))]

        if duplicates.empty:
            st.success("🎉 No duplicate accounts found!")
            return

        # --- Merge Results ---
        result = pd.merge(
            duplicates,
            masterlist,
            left_on="HLIDNO",
            right_on="ACCOUNT NUMBER",
            how="left"
        )

        st.warning(f"⚠️ Found {len(result)} duplicate account numbers.")
        st.dataframe(
            result[["HLIDNO", "LEADS CHCODE", "FULL NAME"]],
            use_container_width=True
        )

        # --- Prepare Output Files ---
        leads_only = result[["LEADS CHCODE"]].drop_duplicates()

        output1 = io.BytesIO()
        with pd.ExcelWriter(output1, engine="openpyxl") as writer:
            leads_only.to_excel(writer, index=False, header=False, sheet_name="LEADS_CHCODE_ONLY")
        output1.seek(0)

        leads_pout = leads_only.copy()
        leads_pout["POUT"] = "POUT"

        output2 = io.BytesIO()
        with pd.ExcelWriter(output2, engine="openpyxl") as writer:
            leads_pout.to_excel(writer, index=False, header=False, sheet_name="LEADS_CHCODE_POUT")
        output2.seek(0)

        current_date = datetime.today().strftime('%Y-%m-%d')
        file_name = f"FCL POUT {current_date}.xlsx"

        # --- Download Buttons ---
        st.download_button(
            label="⬇️ LEADS CHCODE Only (Excel)",
            data=output1,
            file_name="FOR AUTOSTAT.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.download_button(
            label="⬇️ LEADS CHCODE + POUT (Excel)",
            data=output2,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"⚠️ Error processing file: {e}")
