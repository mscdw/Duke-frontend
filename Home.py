import streamlit as st
from utils.styles import apply_global_styles

st.set_page_config(page_title="Avigilon UI", layout="wide")
st.title("Avigilon API & Events Dashboard")
apply_global_styles()

st.markdown("""
Welcome to the Avigilon API Explorer and Events Dashboard.

- Use the sidebar to navigate between endpoint dashboards.

**Pages:**
- Endpoints: Interact with all Avigilon API endpoints.
- Events: Visualize events from all servers.
- Appearances: Visulaize appearance events from all servers.
""")
