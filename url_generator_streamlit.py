import streamlit as st
import pandas as pd
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

# --- Keyword Metrics Dashboard ---
st.header("Keyword Metrics Dashboard")

uploaded_file = st.file_uploader("Upload a CSV or Excel file with keyword metrics", type=["csv", "xlsx", "xls"])
top_n = st.number_input("How many top keywords to show?", min_value=1, max_value=50, value=10)

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    # Find the QUERY column
    query_col = [col for col in df.columns if 'query' in col.lower()]
    if not query_col:
        st.error("No 'QUERY' column found in your file.")
        st.stop()
    query_col = query_col[0]
    # Find all NET_REVENUE columns
    net_revenue_cols = [col for col in df.columns if 'net_revenue' in col.lower()]
    if not net_revenue_cols:
        st.error("No 'NET_REVENUE' columns found in your file.")
        st.stop()
    # Clean and sum net revenue columns
    df['total_net_revenue'] = df[net_revenue_cols].replace('[\\$,]', '', regex=True).apply(pd.to_numeric, errors='coerce').sum(axis=1)
    # Remove empty/invalid queries
    df = df[df[query_col].notnull() & (df[query_col].astype(str).str.strip() != "")]
    # Sort and show top N
    top_keywords = df[[query_col, 'total_net_revenue']].sort_values('total_net_revenue', ascending=False).head(top_n)
    st.dataframe(top_keywords.rename(columns={query_col: "Keyword", "total_net_revenue": "Total Net Revenue"}))
else:
    st.info("Upload a CSV or Excel file to see top performing keywords.")

st.markdown("---")
