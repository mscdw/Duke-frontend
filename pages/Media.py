import streamlit as st
import json
from utils.api_logger import logged_request
from utils.setup import global_page_setup

st.set_page_config(page_title="Media Fetcher", layout="wide")
st.title("Avigilon Media Fetcher")

API_BASE = st.secrets.get("API_BASE", "http://localhost:8000/api")

st.sidebar.header("Media Fetch Settings")
camera_id = st.sidebar.text_input("Camera ID")
timestamp = st.sidebar.text_input("Timestamp (ISO 8601)")
format_option = st.sidebar.selectbox("Format", ["fmp4", "jpeg", "json"], index=0)

if st.sidebar.button("Fetch Media"):
    if not camera_id or not timestamp:
        st.error("Camera ID and Timestamp are required.")
    else:
        params = {
            "cameraId": camera_id,
            "t": timestamp,
            "format": format_option
        }
        with st.spinner("Fetching media from server..."):
            try:
                resp = logged_request("get", f"{API_BASE}/media", params=params)
                if format_option == "fmp4":
                    st.video(resp.content)
                elif format_option == "jpeg":
                    st.image(resp.content)
                elif format_option == "json":
                    try:
                        ndjson_lines = resp.content.decode('utf-8').splitlines()
                        for line in ndjson_lines:
                            if line.strip():
                                st.json(json.loads(line))
                    except Exception:
                        st.write(resp.content)
            except Exception as e:
                st.error(f"Failed to fetch media: {e}")

global_page_setup()
