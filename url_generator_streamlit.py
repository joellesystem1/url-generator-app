import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="System1 URL Generator & Keyword Dashboard", layout="wide")
st.title("System1 URL Generator & Keyword Dashboard")

# --- Session State for Force Keys ---
if 'force_keys' not in st.session_state:
    st.session_state['force_keys'] = ["" for _ in range(6)]
if 'force_key_index' not in st.session_state:
    st.session_state['force_key_index'] = 0

def fill_next_force_key(value):
    idx = st.session_state['force_key_index']
    st.session_state['force_keys'][idx] = value.replace(' ', '+')
    st.session_state['force_key_index'] = (idx + 1) % 6

def reset_force_keys():
    st.session_state['force_keys'] = ["" for _ in range(6)]
    st.session_state['force_key_index'] = 0

# --- URL Generator Section ---
st.header("URL Generator")

col1, col2 = st.columns([2, 1])

with col1:
    live_url = st.text_input("Live URL", "")
    headline = st.text_input("Headline", "")
    segment = st.text_input("Segment", "")
    force_keys = []
    for i in range(6):
        val = st.text_input(f"Force Key {chr(65+i)}", st.session_state['force_keys'][i], key=f"forceKey{i}")
        force_keys.append(val)
        st.session_state['force_keys'][i] = val

with col2:
    st.markdown("#### How to use:")
    st.markdown("""
    - Enter the live URL and (optionally) a headline and segment.
    - Fill in up to 6 force keys (A-F). Spaces will be replaced with plus signs.
    - Click any keyword below to fill the next force key.
    - Use the buttons below to generate different types of URLs.
    """)
    if st.button("Reset Force Keys"):
        reset_force_keys()
        st.experimental_rerun()

# --- URL Generation Logic ---
def build_system1_url(live_url, headline, segment, force_keys):
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
        return f"{live_url}?{'&'.join(params)}"
    return ""

def build_fb_url(live_url, headline, segment, force_keys):
    params = []
    for i, key in enumerate(force_keys):
        if key.strip():
            params.append(f"forceKey{chr(65+i)}={key.strip().replace(' ', '+')}")
    if segment.strip():
        params.append(f"segment={segment.strip().replace(' ', '+')}")
    if headline.strip():
        params.append(f"headline={headline.strip().replace(' ', '+')}")
    # Tracking params
    params.append('s1paid={account.id}')
    params.append('s1placement={placement}')
    params.append('s1padid={ad.id}')
    params.append('s1particle=Cheap+Dental+Implants')
    params.append('s1pcid={campaign.id}')
    # Facebook params
    params.append('fbid={1234567890}')
    params.append('fbland={PageView}')
    params.append('fbserp={Add+To+Wishlist}')
    params.append('fbclick={Purchase}')
    params.append('fbclid={click_id}')
    if live_url:
        return f"{live_url}?{'&'.join(params)}"
    return ""

def build_leadgen_url(live_url, headline, segment, force_keys):
    params = []
    for i, key in enumerate(force_keys):
        if key.strip():
            params.append(f"forceKey{chr(65+i)}={key.strip().replace(' ', '+')}")
    seg = segment.strip() or 'rsoc.dp.topictracking.001'
    params.append(f"segment={seg}")
    params.append(f"headline={headline.strip().replace(' ', '+') if headline.strip() else 'Need+dental+implants'}")
    params.append('s1paid={account.id}')
    # Article from headline or URL
    article = headline
    if not article and live_url:
        try:
            urlPath = live_url.split('/')
            article = next((p for p in urlPath if 'en-us' in p), '').split('-en-us')[0]
            article = ' '.join(word.capitalize() for word in article.split('-')) if article else ''
        except Exception:
            article = ''
    params.append(f"s1particle={article.replace(' ', '+') if article else 'Cheap+Dental+Implants'}")
    params.append('s1pcid={campaign.id}')
    if live_url:
        return f"{live_url}?{'&'.join(params)}"
    return ""

# --- URL Generator Buttons ---
sys1_url = fb_url = leadgen_url = ""
colA, colB, colC = st.columns(3)
with colA:
    if st.button("Generate System1 URL"):
        sys1_url = build_system1_url(live_url, headline, segment, force_keys)
        st.session_state['sys1_url'] = sys1_url
    if 'sys1_url' in st.session_state and st.session_state['sys1_url']:
        st.success("System1 URL:")
        st.code(st.session_state['sys1_url'], language="text")
with colB:
    if st.button("Generate Facebook URL"):
        fb_url = build_fb_url(live_url, headline, segment, force_keys)
        st.session_state['fb_url'] = fb_url
    if 'fb_url' in st.session_state and st.session_state['fb_url']:
        st.success("Facebook URL:")
        st.code(st.session_state['fb_url'], language="text")
with colC:
    if st.button("Generate Leadgen URL"):
        leadgen_url = build_leadgen_url(live_url, headline, segment, force_keys)
        st.session_state['leadgen_url'] = leadgen_url
    if 'leadgen_url' in st.session_state and st.session_state['leadgen_url']:
        st.success("Leadgen URL:")
        st.code(st.session_state['leadgen_url'], language="text")

st.markdown("---")

# --- Keyword Metrics Dashboard ---
st.header("Keyword Metrics Dashboard")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl', skiprows=[0], dtype=str)
        st.success(f"File uploaded! {df.shape[0]} rows loaded.")
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
        st.subheader("Search & Click to Fill Force Keys")
        search_term = st.text_input("Search keywords...", "")
        filtered_df = metrics_df[metrics_df['query'].str.lower().str.contains(search_term.lower())]
        st.dataframe(filtered_df, use_container_width=True)
        st.write("**Click a keyword below to fill the next available force key:**")
        max_buttons = 50
        for idx, row in filtered_df.head(max_buttons).iterrows():
            if st.button(row['query'], key=f"kwbtn_{idx}"):
                fill_next_force_key(row['query'])
                st.rerun()
            st.markdown(
                f"<div style='font-weight:bold; font-size:1.1em;'>"
                f"Avg Revenue: ${row['avg_revenue']} &nbsp; | &nbsp; "
                f"Avg RPC: ${row['avg_rpc']}"
                f"</div>",
                unsafe_allow_html=True
            )
        if len(filtered_df) > max_buttons:
            st.info(f"Showing only the first {max_buttons} keywords. Use the search box to narrow down.")
        st.write("**Current Force Keys:**")
        for i, val in enumerate(st.session_state['force_keys']):
            st.write(f"Force Key {chr(65+i)}: {val}")
        if not metrics_df.empty and len(metrics_df.columns) > 0:
            gb = GridOptionsBuilder.from_dataframe(metrics_df)
            gb.configure_selection('single', use_checkbox=True)
            grid_options = gb.build()
            AgGrid(
                metrics_df,
                gridOptions=grid_options,
                update_mode='SELECTION_CHANGED',
                height=400,
                width='100%',
                fit_columns_on_grid_load=True
            )
        else:
            st.warning("No data to display in the table. Please check your Excel file and column names.")
    except Exception as e:
        st.error(f"Error processing file: {e}") 
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="System1 URL Generator & Keyword Dashboard", layout="wide")
st.title("System1 URL Generator & Keyword Dashboard")

# --- Session State for Force Keys ---
if 'force_keys' not in st.session_state:
    st.session_state['force_keys'] = [""] * 6
if 'force_key_index' not in st.session_state:
    st.session_state['force_key_index'] = 0

def fill_next_force_key(value):
    idx = st.session_state['force_key_index']
    st.session_state['force_keys'][idx] = value.replace(' ', '+')
    st.session_state['force_key_index'] = (idx + 1) % 6

def reset_force_keys():
    st.session_state['force_keys'] = [""] * 6
    st.session_state['force_key_index'] = 0

# --- Upload Excel ---
st.header("Upload an Excel file to get started.")
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

metrics_df = None

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    # Try to find the right columns, or rename as needed
    # Expecting columns: 'query', 'avg_revenue', 'total_revenue', 'avg_rpc', 'total_rpc', 'avg_clicks', 'total_clicks'
    # If your columns are named differently, adjust here:
    expected_cols = ['query', 'avg_revenue', 'total_revenue', 'avg_rpc', 'total_rpc', 'avg_clicks', 'total_clicks']
    df.columns = [c.lower().strip() for c in df.columns]
    # Try to match columns
    col_map = {}
    for col in expected_cols:
        for c in df.columns:
            if col in c:
                col_map[c] = col
    df = df.rename(columns=col_map)
    # Only keep expected columns
    metrics_df = df[[col for col in expected_cols if col in df.columns]].copy()
    st.success(f"File uploaded! {metrics_df.shape[0]} rows loaded.")

    # --- Interactive Keyword Metrics Table (AgGrid) ---
    st.subheader("Keyword Metrics Table (search/filter above the table!)")
    gb = GridOptionsBuilder.from_dataframe(metrics_df)
    gb.configure_selection('single', use_checkbox=True)  # single row selection with checkbox
    grid_options = gb.build()

    AgGrid(
        metrics_df,
        gridOptions=grid_options,
        update_mode='SELECTION_CHANGED',
        height=400,
        width='100%',
        fit_columns_on_grid_load=True
    )

    # --- Clickable Top 30 High Performing Keywords Section with Search ---
    st.subheader("Click a keyword below to fill the next available force key (Top 30 High Performing Keywords by Avg Revenue and Avg RPC):")

    # Calculate a performance score (sum of ranks for avg_revenue and avg_rpc)
    metrics_df['performance_score'] = (
        metrics_df['avg_revenue'].rank(ascending=False, method='min') +
        metrics_df['avg_rpc'].rank(ascending=False, method='min')
    )

    # Get top 30 by combined performance score (lower is better)
    top_keywords = metrics_df.sort_values('performance_score').head(30)

    # --- Add a search filter ---
    search_term = st.text_input("Search top keywords...").lower()
    if search_term:
        filtered_keywords = top_keywords[top_keywords['query'].str.lower().str.contains(search_term)]
    else:
        filtered_keywords = top_keywords

    # Display as clickable buttons with only Avg Revenue and Avg RPC
    for idx, row in filtered_keywords.iterrows():
        st.markdown(
            f"**Avg Revenue:** ${row['avg_revenue']:.2f} &nbsp; | &nbsp; "
            f"**Avg RPC:** ${row['avg_rpc']:.2f}"
        )
        if st.button(row['query'], key=f"kwbtn_{idx}_{row['query']}"):
            fill_next_force_key(row['query'])
            st.experimental_rerun()

    st.write("### Force Keys")
    cols = st.columns(6)
    for i, key in enumerate(['A', 'B', 'C', 'D', 'E', 'F']):
        with cols[i]:
            st.text_input(f"Force Key {key}", value=st.session_state['force_keys'][i], key=f'forceKey{key}')

    if st.button("Reset Force Keys"):
        reset_force_keys()
        st.experimental_rerun()
else:
    st.info("Upload an Excel file to get started.")
