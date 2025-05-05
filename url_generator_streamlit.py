import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse

st.set_page_config(page_title="URL Generator & Keyword Dashboard", layout="wide")
st.title("System1 URL Generator & Keyword Dashboard")

# --- URL Generator Section ---
st.header("URL Generator")

col1, col2 = st.columns(2)

with col1:
    live_url = st.text_input("Live URL", "")
    headline = st.text_input("Headline (optional)", "")
    segment = st.text_input("Segment (optional)", "")
    force_keys = [st.text_input(f"Force Key {chr(65+i)}", "", key=f"forceKey{i}") for i in range(6)]

with col2:
    st.markdown("#### How to use:")
    st.markdown("""
    - Enter the live URL and (optionally) a headline and segment.
    - Fill in up to 6 force keys (A-F). Spaces will be replaced with plus signs.
    - Click **Generate URL** to get your campaign URL.
    """)
    
    if st.button("Generate URL"):
        # Build parameters
        params = []
        for i, key in enumerate(force_keys):
            if key.strip():
                params.append(f"forceKey{chr(65+i)}={key.strip().replace(' ', '+')}")
        if segment.strip():
            params.append(f"segment={segment.strip().replace(' ', '+')}")
        if headline.strip():
            params.append(f"headline={headline.strip().replace(' ', '+')}")
        # Tracking params
        article_name = ''
        if live_url:
            try:
                path = live_url.split('/')
                article = next((p for p in path if 'en-us' in p), '').split('-en-us')[0]
                article_name = ' '.join(word.capitalize() for word in article.split('-')) if article else ''
            except Exception:
                article_name = ''
        tracking_params = {
            's1paid': '{account.id}',
            's1placement': '{placement}',
            's1padid': '{ad.id}',
            's1particle': article_name.replace(' ', '+') if article_name else '',
            's1pcid': '{campaign.id}'
        }
        for k, v in tracking_params.items():
            if v:
                params.append(f"{k}={v}")
        if live_url:
            url = f"{live_url}?{'&'.join(params)}"
            st.success(f"Generated URL:")
            st.code(url, language="text")
        else:
            st.error("Please enter a Live URL.")

st.markdown("---")

# --- Excel Upload & Keyword Dashboard ---
st.header("Keyword Metrics Dashboard")

uploaded_file = st.file_uploader("Upload Excel file (.xlsx or .xls)", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Read Excel, skip first row (dates), use second row as header
        df = pd.read_excel(uploaded_file, engine='openpyxl', skiprows=[0], dtype=str)
        st.success(f"File uploaded! {df.shape[0]} rows loaded.")
        
        # Columns: A: QUERY, B-H: NET_REVENUE, I-O: RPC, P-V: CLICKS
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
        
        st.subheader("Overall Stats")
        total_rev = float(metrics_df['total_revenue'].sum())
        total_clk = float(metrics_df['total_clicks'].sum())
        total_rpc = float(metrics_df['total_rpc'].sum())
        avg_rpc_val = total_rev / total_clk if total_clk > 0 else 0
        st.write(f"**Total Revenue:** ${total_rev:,.2f}")
        st.write(f"**Total Clicks:** {int(total_clk):,}")
        st.write(f"**Total RPC:** ${total_rpc:,.2f}")
        st.write(f"**Average RPC:** ${avg_rpc_val:,.2f}")
        
        st.subheader("Keyword Table (click to fill force keys)")
        st.dataframe(metrics_df, use_container_width=True)
        
        st.markdown("---")
        st.write("**Click a keyword below to fill the next available force key:**")
        force_keys_state = st.session_state.get('force_keys', ["" for _ in range(6)])
        force_key_index = st.session_state.get('force_key_index', 0)
        
        for idx, row in metrics_df.iterrows():
            if st.button(row['query']):
                # Fill next force key
                force_keys_state[force_key_index] = row['query'].replace(' ', '+')
                force_key_index = (force_key_index + 1) % 6
                st.session_state['force_keys'] = force_keys_state
                st.session_state['force_key_index'] = force_key_index
                st.experimental_rerun()
        
        st.write("**Current Force Keys:**")
        for i, val in enumerate(force_keys_state):
            st.write(f"Force Key {chr(65+i)}: {val}")
    except Exception as e:
        st.error(f"Error processing file: {e}") 