import streamlit as st
import pyodbc
import pandas as pd
import os
from datetime import date, datetime, timedelta
import altair as alt  # 👈 For interactive charts

# -------------------------------
# Database connection
# -------------------------------
conn_str = (
    "Driver={MySQL ODBC 5.1 Driver};"
    "Server=192.168.15.197;"
    "Database=bcrm;"
    "UID=abpineda;"
    "PWD=$5ws38DF29nzU;"
)   

AGENT_MAP = {
    "PMXC": "MCCALUGAY", "PCAA": "CAAALBAR", "MBSM": "BDMENDOZA", "PICO": "ICOPRENARIO", "PSCP": "SCPRIETO", "PHED": "HPDALUDADO",
    "PAAG": "AGGUILLEN", "CGAM": "GAMARTINEZ", "QDMG": "DMGUINTO", "BRAA": "RAARANETA", "PMCY": "MECALUGAY", "QNJD": "NJDEGUZMAN",
    "GCAA": "CAABDULLA", "ZNOC": "NOCASAMAYOR", "QJRM": "JRMAGBATO", "ZSMR": "SERAVAL", "CADB": "ADBATILLER", "MCRS": "CBSIBAL",
    "PSLR": "SLREYES", "MRSG": "RSGAFFUD", "ICOD": "CODELACRUZ", "DEGE": "EHESMERALDA", "BNMB": "NMBARZA", "QADB": "ASBAUTISTA",
    "CHCE": "HCELENTORIO", "BMPA": "MPATOC", "MRID": "RIDELROSARIO", "MNRY": "ECMAGPALE", "BKSS": "KSSIBAYAN", "MRGA": "REACUNA",
    "BKNB": "KKBAYO", "PJAA": "JATAMONDONG", "TKER": "KVREVILLA", "ZCSA": "CSARNAEZ", "MRGZ": "RGZETA", "MAEO": "AEOFALSA",
    "PBMP": "MMPABONDIA", "MJSM": "JMSALOMON", "MJHD": "JHDELACRUZ", "CBGD": "BGDABUCOL", "CJGM": "JAMAGTULIS", "DADB": "ADBESINGA",
    "GASM": "AAMAMINASACAN", "PFTD": "FTDEVERA", "BLON": "LPNERIO",
}

# -------------------------------
# Load SQL from file
# -------------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
sql_file = os.path.join(base_dir, "queries", "pif_legal_payments.sql")

def read_sql_query(filename):
    with open(filename, "r") as file:
        return file.read()

base_query = read_sql_query(sql_file)

# -------------------------------
# Run query with params
# -------------------------------
@st.cache_data(show_spinner=False, ttl=600)
def run_query(start_date, end_date, status_filter):
    with pyodbc.connect(conn_str) as conn:
        return pd.read_sql_query(
            base_query,
            conn,
            params=[start_date, end_date, status_filter]
        )

# ---------- helpers ----------
def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    if "PAYMENT AMOUNT" in df.columns:
        df["PAYMENT AMOUNT"] = pd.to_numeric(df["PAYMENT AMOUNT"], errors="coerce").fillna(0.0)
    if "BRANCH" in df.columns:
        df["BRANCH"] = df["BRANCH"].fillna("UNPLACED").astype(str).str.strip()
    if "SUBSTATUS" in df.columns:
        df["SUBSTATUS"] = df["SUBSTATUS"].fillna("UNKNOWN").astype(str).str.strip()
    if "ACCOUNT NUMBER" in df.columns:
        df["ACCOUNT NUMBER"] = df["ACCOUNT NUMBER"].astype(str)
    return df

def _branch_substatus_table(df: pd.DataFrame, substatus_cols=None) -> pd.DataFrame:
    counts = (
        df.pivot_table(
            index="BRANCH",
            columns="SUBSTATUS",
            values="ACCOUNT NUMBER",
            aggfunc="nunique",
            fill_value=0
        )
    )
    if substatus_cols is not None:
        for col in substatus_cols:
            if col not in counts.columns:
                counts[col] = 0
        counts = counts[substatus_cols]

    amt = df.groupby("BRANCH", dropna=False)["PAYMENT AMOUNT"].sum().rename("Amount Collected")
    wide = counts.join(amt, how="outer").fillna(0)

    total_row = pd.DataFrame([wide.sum(numeric_only=True)], index=["Grand Total"])
    wide = pd.concat([wide, total_row], axis=0)

    for c in counts.columns:
        wide[c] = wide[c].astype(int)
    wide["Amount Collected"] = wide["Amount Collected"].astype(float)

    if "Grand Total" in wide.index:
        wide_no_total = wide.drop(index="Grand Total")
        wide = pd.concat([wide_no_total.sort_index(), wide.loc[["Grand Total"]]])
    return wide.reset_index().rename(columns={"index": "Placement"})

def _align_columns_for_variance(df_last: pd.DataFrame, df_curr: pd.DataFrame):
    exclude = {"Placement", "Amount Collected"}
    subs_last = [c for c in df_last.columns if c not in exclude]
    subs_curr = [c for c in df_curr.columns if c not in exclude]
    all_subs = sorted(set(subs_last) | set(subs_curr))
    base_cols = ["Placement"] + all_subs + ["Amount Collected"]

    def _reindex(df):
        out = df.copy()
        for col in all_subs:
            if col not in out.columns:
                out[col] = 0
        if "Amount Collected" not in out.columns:
            out["Amount Collected"] = 0.0
        return out[[c for c in base_cols if c in out.columns]]

    return _reindex(df_last), _reindex(df_curr), base_cols

def _variance_table(df_last: pd.DataFrame, df_curr: pd.DataFrame) -> pd.DataFrame:
    last_aligned, curr_aligned, order = _align_columns_for_variance(df_last, df_curr)

    merged = pd.merge(
        last_aligned, curr_aligned,
        on="Placement", how="outer",
        suffixes=("_LAST", "_CURR")
    ).fillna(0)

    var_rows = {"Placement": merged["Placement"]}
    for col in order[1:]:
        last_col = f"{col}_LAST"
        curr_col = f"{col}_CURR"
        if last_col in merged and curr_col in merged:
            var_rows[col] = merged[curr_col] - merged[last_col]

    variance = pd.DataFrame(var_rows)

    totals = variance[variance["Placement"] != "Grand Total"]
    total_row = pd.DataFrame([{**{"Placement": "Grand Total"},
                               **{c: totals[c].sum() for c in totals.columns if c != "Placement"}}])
    variance = pd.concat([variance[variance["Placement"] != "Grand Total"], total_row], ignore_index=True)

    for c in variance.columns:
        if c != "Placement":
            if c == "Amount Collected":
                variance[c] = variance[c].astype(float)
            else:
                variance[c] = variance[c].round().astype(int)
    return variance

def _style_variance(df: pd.DataFrame):
    def colorize(v):
        if isinstance(v, (int, float)):
            if v > 0:
                return "color: #00c853;"
            if v < 0:
                return "color: #e53935;"
        return ""
    fmt = {c: "{:+,.0f}" for c in df.columns if c not in ("Placement", "Amount Collected")}
    fmt["Amount Collected"] = "{:+,.2f}"
    return df.style.applymap(colorize, subset=[c for c in df.columns if c != "Placement"]).format(fmt)

# -------------------------------
# Streamlit UI
# -------------------------------
def fcl_payments_ptp():
    st.title("PAYMENTS & PTP")

    page = st.sidebar.selectbox("Select Page", ["TABLES", "CHARTS & GRAPHS", "MONTHLY COMPARISON"])
    today = date.today()
    first_of_month = today.replace(day=1)

    status_choice = st.selectbox("STATUS", ["Payment", "PTP"])

    # ---------- Top range pickers: only for TABLES & CHARTS ----------
    if page != "MONTHLY COMPARISON":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=first_of_month)
        with col2:
            end_date = st.date_input("End Date", value=today)

        if start_date > end_date:
            st.error("⚠️ Start date must be before End date.")
            return

        df = run_query(start_date, end_date, status_choice)

        if not df.empty and "AGENTS" in df.columns:
            df["AGENTS"] = df["AGENTS"].map(AGENT_MAP).fillna(df["AGENTS"])

        # Ensure proper dtypes for downstream charts
        if not df.empty:
            df = _coerce_types(df)
            # Coerce datetime columns safely
            if "PAYMENT DATE" in df.columns:
                df["PAYMENT DATE"] = pd.to_datetime(df["PAYMENT DATE"], errors="coerce")

            if "LATEST REMARKS DATE" in df.columns:
                df["LATEST REMARKS DATE"] = pd.to_datetime(df["LATEST REMARKS DATE"], errors="coerce")
    else:
        # placeholder so downstream checks don't fail
        df = pd.DataFrame()

    # ---------------- Page 3: Monthly Comparison ----------------
    if page == "MONTHLY COMPARISON":
        st.subheader("Monthly Comparison by Branch & Substatus")

        # Four pickers side by side in one row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            prev_start = st.date_input("Previous Period Start", value=first_of_month - timedelta(days=31))
        with c2:
            prev_end = st.date_input("Previous Period End", value=first_of_month - timedelta(days=1))
        with c3:
            curr_start = st.date_input("Current Period Start", value=first_of_month)
        with c4:
            curr_end = st.date_input("Current Period End", value=today)

        if prev_start > prev_end or curr_start > curr_end:
            st.error("⚠️ Invalid date ranges.")
            return

        prev_start_dt = datetime.combine(prev_start, datetime.min.time())
        prev_end_dt_excl = datetime.combine(prev_end + timedelta(days=1), datetime.min.time())
        curr_start_dt = datetime.combine(curr_start, datetime.min.time())
        curr_end_dt_excl = datetime.combine(curr_end + timedelta(days=1), datetime.min.time())

        df_last = run_query(prev_start_dt, prev_end_dt_excl, status_choice)
        df_curr = run_query(curr_start_dt, curr_end_dt_excl, status_choice)

        if not df_last.empty:
            df_last = _coerce_types(df_last)
        if not df_curr.empty:
            df_curr = _coerce_types(df_curr)

        all_subs = sorted(set(df_last["SUBSTATUS"].unique().tolist() if not df_last.empty else []) |
                          set(df_curr["SUBSTATUS"].unique().tolist() if not df_curr.empty else []))

        tbl_last = _branch_substatus_table(df_last, substatus_cols=all_subs) if not df_last.empty else pd.DataFrame(columns=["Placement"] + all_subs + ["Amount Collected"])
        tbl_curr = _branch_substatus_table(df_curr, substatus_cols=all_subs) if not df_curr.empty else pd.DataFrame(columns=["Placement"] + all_subs + ["Amount Collected"])

        left, right = st.columns(2)
        with left:
            st.subheader("Previous Period")
            st.dataframe(
                tbl_last.style.format({**{s: "{:,.0f}" for s in all_subs}, "Amount Collected": "{:,.2f}"}),
                use_container_width=True,
                height=600
            )
        with right:
            st.subheader("Current Period")
            st.dataframe(
                tbl_curr.style.format({**{s: "{:,.0f}" for s in all_subs}, "Amount Collected": "{:,.2f}"}),
                use_container_width=True,
                height=600
            )

        variance = _variance_table(tbl_last, tbl_curr)

        st.markdown("### 🔢 Variance Table (Current − Previous)")
        st.dataframe(
            _style_variance(variance),
            use_container_width=True,
            height=700
        )

        # ===== Amount Variance Chart with VALUE LABELS =====
        st.markdown("### 📊 Amount Variance Chart")
        var_chart_data = variance[variance["Placement"] != "Grand Total"].copy()
        var_chart_data["Sign"] = var_chart_data["Amount Collected"].apply(lambda x: "Positive" if x >= 0 else "Negative")

        bars = (
            alt.Chart(var_chart_data)
            .mark_bar()
            .encode(
                x=alt.X("Amount Collected:Q", axis=alt.Axis(format="~s")),
                y=alt.Y("Placement:N", sort="-x"),
                color=alt.Color("Sign:N", scale=alt.Scale(domain=["Positive","Negative"], range=["#00c853","#e53935"])),
                tooltip=[
                    alt.Tooltip("Placement:N"),
                    alt.Tooltip("Amount Collected:Q", format=",")
                ]
            )
        )

        labels = (
            alt.Chart(var_chart_data)
            .mark_text(align="left", baseline="middle", dx=5, color="white")
            .encode(
                x=alt.X("Amount Collected:Q"),
                y=alt.Y("Placement:N", sort="-x"),
                text=alt.Text("Amount Collected:Q", format=",")
            )
        )

        chart = (bars + labels).properties(height=450)
        st.altair_chart(chart, use_container_width=True)

    # ---------------- Page 1: Tables ----------------
    if page == "TABLES" and not df.empty:
        st.dataframe(df, use_container_width=True)

        pivot_branch = (
            df.pivot_table(
                index="BRANCH",
                values="PAYMENT AMOUNT",
                aggfunc=["count", "sum"],
                fill_value=0
            )
            .reset_index()
        )
        pivot_branch.columns = ["BRANCH", "PAYMENT COUNT", "TOTAL PAYMENTS"]
        pivot_branch.loc[len(pivot_branch)] = [
            "TOTAL",
            pivot_branch["PAYMENT COUNT"].sum(),
            pivot_branch["TOTAL PAYMENTS"].sum(),
        ]

        pivot_user = (
            df.pivot_table(
                index="AGENTS",
                values="PAYMENT AMOUNT",
                aggfunc=["count", "sum"],
                fill_value=0
            )
            .reset_index()
        )
        pivot_user.columns = ["AGENT", "PAYMENT COUNT", "TOTAL PAYMENTS"]
        pivot_user.loc[len(pivot_user)] = [
            "TOTAL",
            pivot_user["PAYMENT COUNT"].sum(),
            pivot_user["TOTAL PAYMENTS"].sum(),
        ]

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Payments by Branch")
            st.dataframe(
                pivot_branch.style.format({
                    "PAYMENT COUNT": "{:,.0f}",
                    "TOTAL PAYMENTS": "{:,.2f}"
                }),
                use_container_width=True,
                height= 600
            )
        with c2:
            st.subheader("Payments per Agent")
            st.dataframe(
                pivot_user.style.format({
                    "PAYMENT COUNT": "{:,.0f}",
                    "TOTAL PAYMENTS": "{:,.2f}"
                }),
                use_container_width=True,
                height= 600
            )

    # ---------------- Page 2: Charts & Graphs ----------------
    elif page == "CHARTS & GRAPHS" and not df.empty:
        st.subheader("Payments by Branch (Total Amount)")

        pivot_branch = (
            df.pivot_table(index="BRANCH", values="PAYMENT AMOUNT", aggfunc="sum", fill_value=0)
            .reset_index()
            .rename(columns={"PAYMENT AMOUNT": "TOTAL PAYMENTS"})
        )
        branch_data = pivot_branch

        # ===== Branch bar chart with VALUE LABELS =====
        bars_branch = (
            alt.Chart(branch_data)
            .mark_bar()
            .encode(
                x=alt.X("BRANCH:N", sort="-y", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("TOTAL PAYMENTS:Q", axis=alt.Axis(format="~s")),
                tooltip=[alt.Tooltip("BRANCH:N"), alt.Tooltip("TOTAL PAYMENTS:Q", format=",")]
            )
            .properties(width=800, height=400)
        )
        labels_branch = (
            alt.Chart(branch_data)
            .mark_text(align="center", baseline="bottom", dy=-5, color="white")
            .encode(
                x=alt.X("BRANCH:N", sort="-y"),
                y=alt.Y("TOTAL PAYMENTS:Q"),
                text=alt.Text("TOTAL PAYMENTS:Q", format=",")
            )
        )
        st.altair_chart(bars_branch + labels_branch, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Trend of Payments Over Time")
            # Drop NaT payment dates before grouping to avoid .dt errors
            df_trend_src = df.dropna(subset=["PAYMENT DATE"])
            df_trend = (
                df_trend_src.groupby(df_trend_src["PAYMENT DATE"].dt.date)["PAYMENT AMOUNT"]
                .sum()
                .reset_index()
                .rename(columns={"PAYMENT DATE": "DATE", "PAYMENT AMOUNT": "TOTAL PAYMENTS"})
            )
            chart_trend = (
                alt.Chart(df_trend)
                .mark_line(point=True)
                .encode(
                    x=alt.X("DATE:T", axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y("TOTAL PAYMENTS:Q", axis=alt.Axis(format="~s")),
                    tooltip=[
                        alt.Tooltip("DATE:T"),
                        alt.Tooltip("TOTAL PAYMENTS:Q", format=",")
                    ]
                )
                .properties(width=400, height=300)
            )
            st.altair_chart(chart_trend, use_container_width=True)

        with col2:
            st.subheader("Payments per Agent (Count)")

            pivot_user = (
                df.pivot_table(index="AGENTS", values="PAYMENT AMOUNT", aggfunc="count", fill_value=0)
                .reset_index()
                .rename(columns={"PAYMENT AMOUNT": "PAYMENT COUNT", "AGENTS": "AGENT"})
            )
            agent_data = pivot_user

            # ===== Agent bar chart with VALUE LABELS =====
            bars_agent = (
                alt.Chart(agent_data)
                .mark_bar()
                .encode(
                    x=alt.X("AGENT:N", sort="-y", axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y("PAYMENT COUNT:Q", axis=alt.Axis(format="~s")),
                    tooltip=[alt.Tooltip("AGENT:N"), alt.Tooltip("PAYMENT COUNT:Q", format=",")]
                )
                .properties(width=400, height=300)
            )
            labels_agent = (
                alt.Chart(agent_data)
                .mark_text(align="center", baseline="bottom", dy=-5, color="white")
                .encode(
                    x=alt.X("AGENT:N", sort="-y"),
                    y=alt.Y("PAYMENT COUNT:Q"),
                    text=alt.Text("PAYMENT COUNT:Q", format=",")
                )
            )
            st.altair_chart(bars_agent + labels_agent, use_container_width=True)

# Run the app
if __name__ == "__main__":
    fcl_payments_ptp()
