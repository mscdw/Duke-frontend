import streamlit as st
from datetime import datetime
from utils.api_logger import logged_request
from utils.setup import global_page_setup
from PIL import Image
import io

st.set_page_config(page_title="Face Watchlist Events", layout="wide")
st.title("Face Watchlist Events Dashboard")

API_URL = st.secrets.get("API_URL", "http://localhost:8000/api")

st.sidebar.header("Face Watchlist Event Search Settings")

if 'servers' not in st.session_state:
    try:
        servers_resp = logged_request("get", f"{API_URL}/servers")
        servers = []
        if servers_resp.ok:
            servers_data = servers_resp.json()
            servers_list = servers_data.get("result", {}).get("servers", [])
            servers = [(s.get("name"), s.get("id")) for s in servers_list]
        st.session_state['servers'] = servers
    except Exception:
        st.session_state['servers'] = []
servers = st.session_state['servers']

server_id = st.sidebar.selectbox("Server ID", options=[s[1] for s in servers], format_func=lambda x: next((name for name, id_ in servers if id_ == x), x))
from_date = st.sidebar.date_input("From Date", datetime(2025, 6, 1))
to_date = st.sidebar.date_input("To Date", datetime(2025, 6, 30))
from_time = datetime.combine(from_date, datetime.min.time()).isoformat() + ".000Z"
to_time = datetime.combine(to_date, datetime.min.time()).isoformat() + ".000Z"
limit = st.sidebar.number_input("Limit",  value=50, min_value=1, max_value=1000)
search_clicked = st.sidebar.button("Search Face Events")

if 'face_events' not in st.session_state:
    st.session_state['face_events'] = None
if 'face_events_token' not in st.session_state:
    st.session_state['face_events_token'] = None
if 'face_event_image_cache' not in st.session_state:
        st.session_state['face_event_image_cache'] = {}    

if search_clicked:
    params = {
        "query_type": "TIME_RANGE",
        "from_time": from_time,
        "to_time": to_time,
        "serverId": server_id,
        "limit": limit,
        "eventTopics": "DEVICE_FACE_MATCH_START"
    }
    with st.spinner("Fetching face events from server..."):
        try:
            resp = logged_request("get", f"{API_URL}/events-search", params=params)
            resp.raise_for_status()
            data = resp.json()
            events = data['result']['events']
            token = data['result'].get('token')
            if not events:
                st.session_state['face_events'] = None
                st.session_state['face_events_token'] = None
                st.info("No face match events found for the given parameters.")
            else:
                st.session_state['face_events'] = events
                st.session_state['face_events_token'] = token
        except Exception as e:
            st.session_state['face_events'] = None
            st.session_state['face_events_token'] = None
            st.error(f"Failed to fetch face events: {e}")

def display_face_event_media(event, image_cache):
    camera_id = event.get('cameraId')
    timestamp = event.get('timestamp')
    objectId = event.get('objectId')
    thisId = event.get('thisId')
    roi = event.get('faceRoi')
    if not (camera_id and timestamp and roi):
        st.warning("Missing cameraId, timestamp, or faceRoi for media fetch.")
        return None, None
    cache_key = f"{objectId}_{thisId}"
    if cache_key in image_cache:
        image, cropped = image_cache[cache_key]
    else:
        params = {
            'cameraId': camera_id,
            't': timestamp,
            'format': 'jpeg'
        }
        with st.spinner("Fetching and displaying image and ROI..."):
            try:
                media_resp = logged_request("get", f"{API_URL}/media", params=params)
                media_resp.raise_for_status()
                image = Image.open(io.BytesIO(media_resp.content))
                # buffered = io.BytesIO()
                # image.save(buffered, format="JPEG")
                # img_b64 = base64.b64encode(buffered.getvalue()).decode()
                width, height = image.size
                left = int(roi['left'] * width)
                top = int(roi['top'] * height)
                right = int(roi['right'] * width)
                bottom = int(roi['bottom'] * height)
                cropped = image.crop((left, top, right, bottom))
                # buffered = io.BytesIO()
                # cropped.save(buffered, format="JPEG")
                # cropped_b64 = base64.b64encode(buffered.getvalue()).decode()
                image_cache[cache_key] = (image, cropped)
            except Exception as e:
                st.error(f"Failed to fetch/crop image: {e}")
                return None, None
    return image, cropped
    # st.text_area("Base64 of Full Image", img_b64, height=150, key=f"full_img_b64_{thisId}")
    # st.text_area("Base64 of Cropped Image", cropped_b64, height=150, key=f"cropped_img_b64_{thisId}")

if st.session_state.get('face_events') is not None:
    image_cache = st.session_state['face_event_image_cache']
    for idx, event in enumerate(st.session_state['face_events']):
        st.markdown(f"### Event {idx + 1}")
        cols = st.columns([3, 4, 1])
        image, cropped = display_face_event_media(event, image_cache)
        with cols[0]:
            st.json(event)
        with cols[1]:
            if image is not None:
                st.image(image, caption="Full Image")
        with cols[2]:
            if cropped is not None:
                st.image(cropped, caption="Cropped ROI Image")
    if st.session_state.get('face_events_token'):
        if st.button("Extend Search", key="extend_face_search"):
            with st.spinner("Fetching more face events..."):
                try:
                    continue_params = {
                        "query_type": "CONTINUE",
                        "token": st.session_state['face_events_token']
                    }
                    continue_resp = logged_request("get", f"{API_URL}/events-search", params=continue_params)
                    continue_resp.raise_for_status()
                    continue_data = continue_resp.json()
                    more_events = continue_data['result'].get('events', [])
                    new_token = continue_data['result'].get('token')
                    if more_events:
                        st.session_state['face_events'].extend(more_events)
                        if new_token and new_token != st.session_state['face_events_token']:
                            st.session_state['face_events_token'] = new_token
                        else:
                            st.session_state['face_events_token'] = None
                        st.rerun()
                    else:
                        st.session_state['face_events_token'] = None
                        st.info("No more face match events found.")
                except Exception as e:
                    st.error(f"Failed to fetch more face events: {e}")
else:
    st.info("Fill in the parameters and click 'Search Face Events' to load data.")

global_page_setup()
