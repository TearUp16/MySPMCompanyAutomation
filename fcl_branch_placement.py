import streamlit as st
import pandas as pd
import io
import datetime

def fcl_branch_placement():
    container = st.container(border=True)
    container.subheader("CMS BRANCH PLACEMENT")

    # today’s date string
    today_str = datetime.datetime.now().strftime("%Y-%m-%d").upper()

    # 1) Upload
    uploaded = container.file_uploader("Upload your CMS for uploading file", type=["xls", "xlsx"])
    if not uploaded:
        container.info("Please upload an Excel file to proceed.")
        st.stop()

    # 2) Read & clean, forcing Old I.C. / Account to string
    df = pd.read_excel(
        uploaded,
        engine="openpyxl",
        header=0,
        dtype={"Old I.C. / Account": str}
    )
    df.columns = [c.strip() for c in df.columns]

    if "Placement" not in df.columns or "Old I.C. / Account" not in df.columns:
        container.error(
            f"Required columns not found.\n"
            f"Available columns: {df.columns.tolist()}"
        )
        st.stop()

    # 3) Normalize for case-insensitive grouping
    df["_pl_lower"] = df["Placement"].astype(str).str.lower()
    placements = sorted(df["_pl_lower"].dropna().unique())

    container.markdown(f"**Found {len(placements)} placement(s):** " +
                ", ".join([p.upper() for p in placements]))

    # 4) One Excel download per placement, with Text format on Old I.C. / Account
    for pl in placements:
        # drop our helper column and filter
        subset = df[df["_pl_lower"] == pl].drop(columns=["_pl_lower"]).copy()

        # ensure pandas col is str
        subset["Old I.C. / Account"] = subset["Old I.C. / Account"].astype(str)

        # build Excel in memory
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            sheet_name = pl.title().replace("LEGAL", "").strip()[:31]  # no “Legal”, max 31 chars
            subset.to_excel(writer, index=False, sheet_name=sheet_name)

            # grab workbook & worksheet for formatting
            book  = writer.book
            ws    = writer.sheets[sheet_name]

            # make a Text format
            text_fmt = book.add_format({'num_format': '@'})

            # get index of Old I.C. / Account
            col_idx = subset.columns.get_loc("Old I.C. / Account")
            # apply text format to the entire column
            ws.set_column(col_idx, col_idx, None, text_fmt)

        buffer.seek(0)

        # filename all caps, with today’s date
        clean_name = pl.replace("legal", "").strip().upper()
        filename = f"PIF FCL {clean_name} {today_str}.xlsx"

        container.download_button(
            label=f"⬇️ Download “{clean_name}” Excel ({len(subset)} rows)",
            data=buffer.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=pl
        )
