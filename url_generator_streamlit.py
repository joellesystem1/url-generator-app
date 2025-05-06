import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse

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

# --- Caching for Excel Processing ---
@st.cache_data
def load_and_process_excel(uploaded_file):
    df = pd.read_excel(uploaded_file, engine='openpyxl', skiprows=[0], dtype=str)
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
    return metrics_df

# --- Copy to Clipboard Helper ---
def copy_to_clipboard(text, label):
    st.code(text, language="text")
    copy_code = f"""
    <input type="text" value="{text}" id="{label}" style="position: absolute; left: -1000px;">
    <button onclick="navigator.clipboard.writeText(document.getElementById('{label}').value)">Copy</button>
    """
    st.markdown(copy_code, unsafe_allow_html=True)

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
    - Enter the live URL and a headline and segment (both required).
    - Fill in up to 6 force keys (A-F). Spaces will be replaced with plus signs.
    - Click any keyword below to fill the next force key.
    - Use the buttons below to generate different types of URLs.
    """)
    if st.button("Reset Force Keys"):
        reset_force_keys()
        st.rerun()

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
    params.append('s1paid={account.id}')
    params.append('s1placement={placement}')
    params.append('s1padid={ad.id}')
    params.append('s1particle=Cheap+Dental+Implants')
    params.append('s1pcid={campaign.id}')
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
        if not headline.strip() or not segment.strip():
            st.error("Both Headline and Segment are required.")
        else:
            sys1_url = build_system1_url(live_url, headline, segment, force_keys)
            st.session_state['sys1_url'] = sys1_url
    if 'sys1_url' in st.session_state and st.session_state['sys1_url']:
        st.success("System1 URL:")
        copy_to_clipboard(st.session_state['sys1_url'], "System1_URL")
with colB:
    if st.button("Generate Facebook URL"):
        if not headline.strip() or not segment.strip():
            st.error("Both Headline and Segment are required.")
        else:
            fb_url = build_fb_url(live_url, headline, segment, force_keys)
            st.session_state['fb_url'] = fb_url
    if 'fb_url' in st.session_state and st.session_state['fb_url']:
        st.success("Facebook URL:")
        copy_to_clipboard(st.session_state['fb_url'], "Facebook_URL")
with colC:
    if st.button("Generate Leadgen URL"):
        if not headline.strip() or not segment.strip():
            st.error("Both Headline and Segment are required.")
        else:
            leadgen_url = build_leadgen_url(live_url, headline, segment, force_keys)
            st.session_state['leadgen_url'] = leadgen_url
    if 'leadgen_url' in st.session_state and st.session_state['leadgen_url']:
        st.success("Leadgen URL:")
        copy_to_clipboard(st.session_state['leadgen_url'], "Leadgen_URL")

st.markdown("---")

# --- Keyword Metrics Dashboard ---
st.header("Keyword Metrics Dashboard")

uploaded_file = st.file_uploader("Upload Excel file (.xlsx or .xls)", type=["xlsx", "xls"])

if uploaded_file:
    try:
        metrics_df = load_and_process_excel(uploaded_file)
        st.success(f"File uploaded! {metrics_df.shape[0]} rows loaded.")
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
        filtered_df = metrics_df[metrics_df['query'].str.lower().str.contains(search_term.lower())].reset_index(drop=True)
        st.write("**Click a query below to fill the next available force key:**")
        max_rows = 30
        show_df = filtered_df.head(max_rows)
        for idx, row in show_df.iterrows():
            if st.button(row['query'], key=f"querybtn_{idx}"):
                fill_next_force_key(row['query'])
                st.rerun()
            st.caption(
                f"Avg Revenue: ${row['avg_revenue']} | "
                f"Total Revenue: ${row['total_revenue']} | "
                f"Avg RPC: ${row['avg_rpc']} | "
                f"Total RPC: ${row['total_rpc']} | "
                f"Avg Clicks: {row['avg_clicks']} | "
                f"Total Clicks: {row['total_clicks']}"
            )
        if len(filtered_df) > max_rows:
            st.info(f"Showing only the first {max_rows} results. Use the search box to narrow down.")
        st.write("**Current Force Keys:**")
        for i, val in enumerate(st.session_state['force_keys']):
            st.write(f"Force Key {chr(65+i)}: {val}")
    except Exception as e:
        st.error(f"Error processing file: {e}")
