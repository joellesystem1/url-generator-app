import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

# THIS MUST BE THE FIRST STREAMLIT COMMAND!
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

# --- URL Builder Section ---
st.header("URL Builder")
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
    params.append('s1paid={account.id}')
    params.append('s1placement={placement}')
    params.append('s1padid={ad.id}')
    params.append('s1particle=Cheap+Dental+Implants')
    params.append('s1pcid={campaign.id}')
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
    params.append('s1particle=Cheap+Dental+Implants')
    params.append('s1pcid={campaign.id}')
    if live_url:
        return f"{live_url}?{'&'.join(params)}"
    return ""

# --- URL Generator Buttons ---
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
        df = pd.read_excel(uploaded_file)
        st.success(f"File uploaded! {df.shape[0]} rows loaded.")
        # Expecting columns: 'query', 'avg_revenue', 'avg_rpc'
        df.columns = [c.lower().strip() for c in df.columns]
        if 'query' not in df.columns or 'avg_revenue' not in df.columns or 'avg_rpc' not in df.columns:
            st.error("Excel file must have columns: 'query', 'avg_revenue', 'avg_rpc'")
        else:
            st.subheader("Search & Click to Fill Force Keys")
            search_term = st.text_input("Search keywords...", "")
            filtered_df = df[df['query'].str.lower().str.contains(search_term.lower())]
            st.dataframe(filtered_df, use_container_width=True)
            st.write("**Click a keyword below to fill the next available force key:**")
            max_buttons = 50
            for idx, row in filtered_df.head(max_buttons).iterrows():
                st.markdown(
                    f"<div style='font-weight:bold; font-size:1.1em;'>"
                    f"Avg Revenue: ${row['avg_revenue']} &nbsp; | &nbsp; "
                    f"Avg RPC: ${row['avg_rpc']}"
                    f"</div>",
                    unsafe_allow_html=True
                )
                if st.button(row['query'], key=f"kwbtn_{idx}"):
                    fill_next_force_key(row['query'])
                    st.rerun()
            if len(filtered_df) > max_buttons:
                st.info(f"Showing only the first {max_buttons} keywords. Use the search box to narrow down.")
            st.write("**Current Force Keys:**")
            for i, val in enumerate(st.session_state['force_keys']):
                st.write(f"Force Key {chr(65+i)}: {val}")
            # Show AgGrid table for metrics
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_selection('single', use_checkbox=True)
            grid_options = gb.build()
            AgGrid(
                df,
                gridOptions=grid_options,
                update_mode='SELECTION_CHANGED',
                height=400,
                width='100%',
                fit_columns_on_grid_load=True
            )
    except Exception as e:
        st.error(f"Error processing file: {e}")
