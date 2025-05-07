import streamlit as st
import pandas as pd

st.set_page_config(page_title="System1 Keyword Metrics Dashboard", layout="wide")
st.title("System1 Keyword Metrics Dashboard")

uploaded_file = st.file_uploader("Upload Excel file (.xlsx or .xls)", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, skiprows=[0])
    revenue_cols = df.columns[1:8]
    rpc_cols = df.columns[8:15]
    clicks_cols = df.columns[15:22]

    def clean_numeric(df, cols):
        data = df[cols].copy().astype(str)
        data = data.replace({
            r'[\$,]': '',
            r'^\s*$': '0',
            'nan': '0',
            '#N/A': '0',
            'None': '0',
            '-': '0'
        }, regex=True)
        return data.apply(pd.to_numeric, errors='coerce').fillna(0)

    revenue_data = clean_numeric(df, revenue_cols)
    rpc_data = clean_numeric(df, rpc_cols)
    clicks_data = clean_numeric(df, clicks_cols)
    queries = df.iloc[:, 0].fillna('').astype(str).str.strip()
    metrics_df = pd.DataFrame({
        'query': queries,
        'avg_revenue': revenue_data.mean(axis=1).round(2),
        'total_revenue': revenue_data.sum(axis=1).round(2),
        'avg_rpc': rpc_data.mean(axis=1).round(2),
        'total_rpc': rpc_data.sum(axis=1).round(2),
        'avg_clicks': clicks_data.mean(axis=1).round(0),
        'total_clicks': clicks_data.sum(axis=1).round(0)
    })
    invalid_queries = ['query', 'total', 'grand total', 'nan', '#n/a', '', ' ']
    metrics_df = metrics_df[~metrics_df['query'].str.lower().isin(invalid_queries)]

    st.success(f"File uploaded! {metrics_df.shape[0]} rows loaded.")

    st.subheader("Keyword Metrics Table (use the search/filter box at the top right of the table!)")
    st.dataframe(metrics_df, use_container_width=True)

    st.subheader("Overall Stats")
    total_rev = float(metrics_df['total_revenue'].sum())
    total_clk = float(metrics_df['total_clicks'].sum())
    total_rpc = float(metrics_df['total_rpc'].sum())
    avg_rpc_val = total_rev / total_clk if total_clk > 0 else 0
    st.write(f"**Total Revenue:** ${total_rev:,.2f}")
    st.write(f"**Total Clicks:** {int(total_clk):,}")
    st.write(f"**Total RPC:** ${total_rpc:,.2f}")
    st.write(f"**Average RPC:** ${avg_rpc_val:,.2f}")
else:
    st.info("Upload an Excel file to get started.")
