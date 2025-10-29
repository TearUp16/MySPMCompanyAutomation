import streamlit as st
import pandas as pd
import io
from collections import defaultdict

def agent_taggings():
    container = st.container(border=True)
    container.subheader("PIF LEGAL RESHUFFLE")

    # --- Branch to agent mapping ---
    branch_agent_map = {
        "BATANGAS LEGAL": ["BNMB"],
        "CALAMBA LEGAL": ["CADB"],
        "MALOLOS LEGAL": ["MCDM", "MAEO", "PMAO"],
        "PAMPANGA LEGAL": ["PGJO", "PGMM", "BKNB"],
        "BAGUIO LEGAL": ["PSOA"],
        "DAGUPAN LEGAL": ["PSOA"],
        "LA UNION LEGAL": ["PSOA"],
        "BACOLOD LEGAL": ["BJGG", "BCAM", "BRAA"],
        "CEBU NORTH LEGAL": ["CHCE", "CGAM"],
        "CEBU SOUTH LEGAL": ["CGAM", "CHCE"],
        "ILO-ILO LEGAL": ["ICOD"],
        "CAGAYAN DE ORO LEGAL": ["CKCT"],
        "DAVAO LEGAL": ["DLMB", "ZNOC", "GCAA"],
        "GEN SANTOS LEGAL": ["GFBH"],
        "PAGADIAN LEGAL": ["ZSMR"],
        "TAGUM LEGAL": ["TKER"],
        "ZAMBOANGA LEGAL": ["ZCSA"]
        # NCR handled separately below
    }
    branch_agent_map_up = {k.strip().upper(): v for k, v in branch_agent_map.items()}

    # --- NCR ACCOUNT_TYPE-based mapping ---
    ncr_account_type_map = {
        "FCL PEJF": "QRAR",
        "FCL NOF": "QRAR",
        "FCL 2ND": "QYOP",
        "FCL 3RD": "QCCS"
    }

    # --- Upload Excel file ---
    uploaded_file = container.file_uploader("Upload Excel file", type=["xlsx", "xls"])
    if not uploaded_file:
        container.info("Please upload an Excel file (.xlsx/.xls) containing HLIDNO, CH CODE, BRANCH, and ACCOUNT_TYPE columns.")
        st.stop()

    # --- Read Excel ---
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        container.error(f"Could not read the uploaded file: {e}")
        st.stop()

    # --- Normalize column names ---
    df.columns = [c.strip().upper() for c in df.columns]

    # --- Validate required columns ---
    required_cols = ["HLIDNO", "CH CODE", "BRANCH", "ACCOUNT_TYPE"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        container.error(f"Missing required columns: {', '.join(missing)}")
        container.write("Detected columns:", list(df.columns))
        st.stop()

    # --- Clean up text values ---
    for col in ["HLIDNO", "CH CODE", "BRANCH", "ACCOUNT_TYPE"]:
        df[col] = df[col].astype(str).str.strip().str.upper()

    # --- Normalize branch for mapping ---
    df["_BRANCH_NORM"] = df["BRANCH"].replace(r"\s+", " ", regex=True)

    # --- Assign Agent Code ---
    counters = defaultdict(int)
    assigned = []

    for _, row in df.iterrows():
        branch = row["_BRANCH_NORM"]
        acct_type = row["ACCOUNT_TYPE"]

        # NCR uses special mapping based on ACCOUNT_TYPE
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

    # --- Show unmatched branches ---
    unmatched = sorted({v for v, a in zip(df["_BRANCH_NORM"], assigned) if a is None and v.strip() != ""})
    if unmatched:
        container.warning("These BRANCH or ACCOUNT_TYPE values did NOT match your mapping:")
        st.write(unmatched)

    # --- Prepare outputs ---
    out_df = df.drop(columns=["_BRANCH_NORM"]).copy()

    # Short output: CH CODE + AGENT CODE only, no header
    short_df = out_df[["CH CODE", "AGENT CODE"]]
    # Drop empty CH CODEs if any
    short_df = short_df[short_df["CH CODE"].notna() & (short_df["CH CODE"].str.strip() != "")]

    # --- Write Excel outputs ---
    full_output = io.BytesIO()
    with pd.ExcelWriter(full_output, engine="xlsxwriter") as writer:
        out_df.to_excel(writer, index=False)
    full_output.seek(0)

    short_output = io.BytesIO()
    with pd.ExcelWriter(short_output, engine="xlsxwriter") as writer:
        short_df.to_excel(writer, index=False, header=False)
    short_output.seek(0)

    # --- Download buttons ---
    container.download_button(
        label="⬇️ Download UPDATED FILE (with Agent Code)",
        data=full_output.getvalue(),
        file_name="updated_agent_codes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    container.download_button(
        label="⬇️ Download FOR RESHUFFLE (CH CODE + Agent Code only, no header)",
        data=short_output.getvalue(),
        file_name="for_reshuffle.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- Run app ---
if __name__ == "__main__":
    st.set_page_config(page_title="PIF Legal Reshuffle", layout="centered")
    agent_taggings()
