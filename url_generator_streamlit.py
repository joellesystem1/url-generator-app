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

    # --- Interactive Keyword Picker Table (AgGrid) ---
    st.subheader("Pick a keyword to add to Force Keys (search/filter above the table!)")

    gb = GridOptionsBuilder.from_dataframe(metrics_df)
    gb.configure_selection('single', use_checkbox=True)  # single row selection with checkbox
    grid_options = gb.build()

    grid_response = AgGrid(
        metrics_df,
        gridOptions=grid_options,
        update_mode='SELECTION_CHANGED',
        height=400,
        width='100%',
        fit_columns_on_grid_load=True
    )

    selected = grid_response['selected_rows']
    if selected:
        keyword = selected[0]['query']
        if st.button(f"Add '{keyword}' to next Force Key"):
            fill_next_force_key(keyword)
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
