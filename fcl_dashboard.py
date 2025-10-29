import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

def fcl_dashboard():
    conn_str = (
        "Driver={MySQL ODBC 5.1 Driver};"
        "Server=192.168.15.197;"
        "Database=bcrm;"
        "UID=abpineda;"
        "PWD=$5ws38DF29nzU;"
    )
    conn = pyodbc.connect(conn_str)

    def read_sql_query(filepath):
        with open(filepath, 'r') as file:
            return file.read()

    # load full masterlist
    query_masterlist = read_sql_query('queries/fcl_masterlist.sql')
    df_masterlist = pd.read_sql_query(query_masterlist, conn)

    query_masterlist2 = read_sql_query('queries/pif_legal_payments_dashboard.sql')
    df_masterlist2 = pd.read_sql_query(query_masterlist2, conn)

    # ─── Global Style (Pag-IBIG aligned) ───
    bg_color = '#2E2F3B'
    palette = {
        "primary":   "#1A237E",  # Deep Blue
        "secondary": "#3949AB",  # Bright Blue
        "highlight": "#00BCD4",  # Cyan/Teal
        "accent":    "#FFD600",  # Yellow/Gold
        "neutral":   "#B0BEC5",  # Gray
    }

    # Layout: image | title | selectbox
    col_img, col_title, col_select = st.columns([0.6, 5.0, 1])
    with col_img:
        st.image("pag ibig.png", width=90)
    with col_title:
        st.markdown(f"""
            <h1 style="
                text-align: left;
                padding: 10px;
                color: white;
                font-family: Arial, sans-serif;
                margin-bottom: 0px;
            ">
                FORECLOSURE
            </h1>
        """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    with col_select:
        account_types = sorted(df_masterlist['ACCOUNT TYPE'].dropna().unique().tolist())
        selected_account_type = st.selectbox("", ['All'] + account_types)

    # Filter by selection
    filtered_df = (
        df_masterlist
        if selected_account_type == 'All'
        else df_masterlist[df_masterlist['ACCOUNT TYPE'] == selected_account_type]
    )

    # Summary metrics
    num_accounts      = filtered_df.shape[0]
    total_amount_due  = filtered_df['AMOUNT DUE'].sum()
    total_out_balance = filtered_df['OUT BALANCE'].sum()

    # Active Accounts table
    with st.expander("Active Accounts Table"):
        st.dataframe(filtered_df.reset_index(drop=True), height=400)

    # KPI cards (cyan unified)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(f"""
            <div style="background-color: {bg_color};
                        padding: 20px; border-radius: 8px;
                        text-align: center;">
                <h3 style='color: white; margin-bottom: 5px;'>Active Accounts</h3>
                <p style='font-size: 24px; color: {palette['highlight']}; margin: 0;'>{num_accounts:,}</p>
            </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
            <div style="background-color: {bg_color};
                        padding: 20px; border-radius: 8px;
                        text-align: center;">
                <h3 style='color: white; margin-bottom: 5px;'>Principal Balance</h3>
                <p style='font-size: 24px; color: {palette['highlight']}; margin: 0;'>₱ {total_amount_due:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown(f"""
            <div style="background-color: {bg_color};
                        padding: 20px; border-radius: 8px;
                        text-align: center;">
                <h3 style='color: white; margin-bottom: 5px;'>Outstanding Balance</h3>
                <p style='font-size: 24px; color: {palette['highlight']}; margin: 0;'>₱ {total_out_balance:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # Prepare data for main charts
    summary_df = filtered_df.groupby('ACCOUNT TYPE')['AMOUNT DUE'].sum().reset_index()
    out_balance_summary = filtered_df.groupby('ACCOUNT TYPE')['OUT BALANCE'].sum().reset_index()
    out_balance_summary['hover_text'] = out_balance_summary['OUT BALANCE'].apply(lambda x: f"₱ {x:,.0f}")

    # compute maxes (safely)
    max_left = summary_df['AMOUNT DUE'].max() if not summary_df.empty else 0
    max_right = out_balance_summary['OUT BALANCE'].max() if not out_balance_summary.empty else 0

    # Left Chart: Principal Balance (bar graph with labels)
    fig_left = px.bar(
        summary_df,
        x='ACCOUNT TYPE',
        y='AMOUNT DUE',
        title='Principal Balance by Account Type',
        color_discrete_sequence=[palette['highlight']],
        template='plotly_dark',
        labels={'ACCOUNT TYPE': 'Account Type', 'AMOUNT DUE': 'Principal Balance'},
        text='AMOUNT DUE'
    )
    fig_left.update_traces(
        texttemplate="₱%{text:,.0f}",
        textposition="outside",
        textfont=dict(size=12),
        cliponaxis=False
    )
    if max_left > 0:
        fig_left.update_yaxes(range=[0, max_left * 1.18], automargin=True)
    fig_left.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode='show',
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color='white', size=12),
        xaxis_tickangle=-10,
        height=380,
        margin=dict(t=120, b=80, l=60, r=40),
        showlegend=False
    )

    # Right Chart: Outstanding Balance (peso format)
    out_balance_summary['highlight'] = (
        True if selected_account_type == 'All'
        else out_balance_summary['ACCOUNT TYPE'] == selected_account_type
    )
    fig_right = px.bar(
        out_balance_summary,
        x='ACCOUNT TYPE',
        y='OUT BALANCE',
        color=out_balance_summary['highlight'].map({True: palette['highlight'], False: palette['neutral']}),
        color_discrete_map='identity',
        title='Outstanding Balance by Account Type',
        template='plotly_dark',
        labels={'ACCOUNT TYPE': 'Account Type', 'OUT BALANCE': 'Outstanding Balance'},
        text='OUT BALANCE'
    )
    fig_right.update_traces(
        texttemplate="₱%{text:,.0f}",
        textposition="outside",
        textfont=dict(size=12),
        hovertemplate="Account Type: %{x}<br>Outstanding Balance: ₱%{y:,.0f}<extra></extra>",
        cliponaxis=False
    )
    if max_right > 0:
        fig_right.update_yaxes(range=[0, max_right * 1.18], automargin=True)
    fig_right.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode='show',
        yaxis_title='Outstanding Balance',
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color='white', size=12),
        xaxis_tickangle=-10,
        height=380,
        margin=dict(t=120, b=80, l=60, r=40),
        showlegend=False
    )

    # ─── Horizontal charts by Placement ───
    counts_by_placement = (
        filtered_df
        .assign(PLACEMENT=filtered_df['PLACEMENT'].fillna('UNPLACED'))
        .groupby('PLACEMENT', dropna=False)
        .size()
        .reset_index(name='Active Accounts')
        .sort_values('Active Accounts', ascending=True)
    )
    outbal_by_placement = (
        filtered_df
        .assign(PLACEMENT=filtered_df['PLACEMENT'].fillna('UNPLACED'))
        .groupby('PLACEMENT', dropna=False)['OUT BALANCE']
        .sum()
        .reset_index()
        .rename(columns={'OUT BALANCE': 'Total Out Balance'})
        .sort_values('Total Out Balance', ascending=True)
    )

    def _bar_height(n_rows, base=240, per=28, cap=600):
        return max(base, min(cap, base + per * n_rows))

    fig_count_placement = px.bar(
        counts_by_placement,
        x='Active Accounts',
        y='PLACEMENT',
        orientation='h',
        title='Active Accounts by Placement',
        template='plotly_dark',
        color_discrete_sequence=[palette['highlight']],
        labels={'PLACEMENT': 'Placement', 'Active Accounts': 'Count'},
        text='Active Accounts'
    )
    fig_count_placement.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        textfont=dict(size=11),
        cliponaxis=False
    )
    fig_count_placement.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color='white', size=12),
        margin=dict(t=90, b=40, l=80, r=40),
        height=_bar_height(len(counts_by_placement)),
        xaxis_title='Count',
        yaxis_title='Placement'
    )

    fig_outbal_placement = px.bar(
        outbal_by_placement,
        x='Total Out Balance',
        y='PLACEMENT',
        orientation='h',
        title='Outstanding Balance by Placement',
        template='plotly_dark',
        color_discrete_sequence=[palette['highlight']],
        labels={'PLACEMENT': 'Placement', 'Total Out Balance': 'Outstanding Balance'},
        text='Total Out Balance'
    )
    fig_outbal_placement.update_traces(
        texttemplate="₱%{x:,.0f}",
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="Placement: %{y}<br>Outstanding Balance: ₱%{x:,.0f}<extra></extra>",
        cliponaxis=False
    )
    fig_outbal_placement.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color='white', size=12),
        margin=dict(t=90, b=40, l=80, r=40),
        height=_bar_height(len(outbal_by_placement)),
        xaxis_title='Outstanding Balance',
        yaxis_title='Placement'
    )

    col_counts_1, col_counts_2 = st.columns(2)
    with col_counts_1:
        st.plotly_chart(fig_count_placement, use_container_width=True)
    with col_counts_2:
        st.plotly_chart(fig_outbal_placement, use_container_width=True)

    # ─── Endorsed Leads Over Time ───
    if 'ENDORSE DATE' in filtered_df.columns:
        filtered_df['ENDORSE DATE'] = pd.to_datetime(filtered_df['ENDORSE DATE'], errors='coerce')
        filtered_df = filtered_df.dropna(subset=['ENDORSE DATE'])

        endorsed_over_time = (
            filtered_df
            .groupby(filtered_df['ENDORSE DATE'].dt.to_period('M').astype(str))
            .size()
            .reset_index(name='Leads Endorsed')
        )
        max_end = endorsed_over_time['Leads Endorsed'].max() if not endorsed_over_time.empty else 0
        fig_endorsed = px.bar(
            endorsed_over_time,
            x='ENDORSE DATE',
            y='Leads Endorsed',
            title='Accounts Endorsed Over Time',
            color_discrete_sequence=[palette['highlight']],
            template='plotly_dark',
            labels={'Leads Endorsed':'No. of Accs. Endorsed','ENDORSE DATE':'Date of Endorsement'},
            text='Leads Endorsed'
        )
        fig_endorsed.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            textfont=dict(size=11),
            cliponaxis=False
        )
        if max_end > 0:
            fig_endorsed.update_yaxes(range=[0, max_end * 1.12], automargin=True)
        fig_endorsed.update_layout(
            uniformtext_minsize=11,
            uniformtext_mode='show',
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            font=dict(color='white', size=12),
            height=380,
            margin=dict(t=110, b=80, l=60, r=40),
            xaxis_tickangle=-35
        )
        st.plotly_chart(fig_endorsed, use_container_width=True)

        # Daily line (2025)
        df_daily = filtered_df[filtered_df['ENDORSE DATE'].dt.year == 2025].copy()
        daily_counts = (
            df_daily
            .groupby(df_daily['ENDORSE DATE'].dt.date)
            .size()
            .reset_index(name='Daily Endorsed')
            .rename(columns={'ENDORSE DATE':'Date'})
        )
        max_daily = daily_counts['Daily Endorsed'].max() if not daily_counts.empty else 0
        fig_daily = px.line(
            daily_counts,
            x='Date',
            y='Daily Endorsed',
            title='Accounts Endorsed Per Day (2025)',
            markers=True,
            template='plotly_dark',
            labels={'Daily Endorsed':'# Endorsed','Date':'Date'},
            text='Daily Endorsed'
        )
        fig_daily.update_traces(
            texttemplate="%{text:,}",
            textposition="top center",
            textfont=dict(size=10),
            line=dict(color=palette['highlight'], width=3),
            marker=dict(color=palette['highlight'], size=8, line=dict(color=palette['accent'], width=2)),
            cliponaxis=False
        )
        if max_daily > 0:
            fig_daily.update_yaxes(range=[0, max_daily * 1.12], automargin=True)
        fig_daily.update_layout(
            uniformtext_minsize=10,
            uniformtext_mode='show',
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            font=dict(color='white', size=12),
            xaxis_tickformat='%Y-%m-%d',
            height=380,
            margin=dict(t=110, b=80, l=60, r=40)
        )
        st.plotly_chart(fig_daily, use_container_width=True)

    # ─── NEW: Payment Amount by Month (2025 only) ───
    if 'PAYMENT DATE' in df_masterlist2.columns and 'PAYMENT AMOUNT' in df_masterlist2.columns:
        df_masterlist2['PAYMENT DATE'] = pd.to_datetime(df_masterlist2['PAYMENT DATE'], errors='coerce')
        payments_2025 = df_masterlist2[df_masterlist2['PAYMENT DATE'].dt.year == 2025].copy()

        payments_monthly = (
            payments_2025
            .groupby(payments_2025['PAYMENT DATE'].dt.to_period('M'))
            ['PAYMENT AMOUNT']
            .sum()
            .reset_index()
        )
        payments_monthly['PAYMENT DATE'] = payments_monthly['PAYMENT DATE'].astype(str)

        fig_payments = px.bar(
            payments_monthly,
            x='PAYMENT DATE',
            y='PAYMENT AMOUNT',
            title='Total Payments Per Month (2025)',
            color_discrete_sequence=[palette['highlight']],
            template='plotly_dark',
            labels={'PAYMENT DATE': 'Month', 'PAYMENT AMOUNT': 'Total Payment (₱)'},
            text='PAYMENT AMOUNT'
        )
        fig_payments.update_traces(
            texttemplate="₱%{text:,.0f}",
            textposition="outside",
            textfont=dict(size=11),
            cliponaxis=False
        )
        max_pay = payments_monthly['PAYMENT AMOUNT'].max() if not payments_monthly.empty else 0
        if max_pay > 0:
            fig_payments.update_yaxes(range=[0, max_pay * 1.12], automargin=True)
        fig_payments.update_layout(
            uniformtext_minsize=11,
            uniformtext_mode='show',
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            font=dict(color='white', size=12),
            height=380,
            margin=dict(t=110, b=80, l=60, r=40),
            xaxis_tickangle=-35
        )
        st.plotly_chart(fig_payments, use_container_width=True)

    # ─── Render the two main charts ───
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_left, use_container_width=True)
    with col2:
        st.plotly_chart(fig_right, use_container_width=True)
