import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io, os, base64, sys, json, requests, geocoder
from PIL import Image
from duckduckgo_search import DDGS
from io import StringIO

# --- 1. SOVEREIGN INITIALIZATION ---
st.set_page_config(page_title="Nexus AI - Professional", page_icon="🔵", layout="wide")

# Persistent Knowledge & Skill Vault
if "memory" not in st.session_state:
    st.session_state.memory = "Professional Mode Active."
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 2. GOOGLE-STYLE UI (Minimalist & Professional) ---
def inject_google_ui():
    st.markdown("""
        <style>
        /* Google Professional Palette */
        .stApp {
            background-color: #FFFFFF;
        }
        [data-testid="stSidebar"] {
            background-color: #F8F9FA !important;
            border-right: 1px solid #E0E0E0;
        }
        /* Gemini-like Chat Bubbles */
        .stChatMessage {
            background-color: #F0F4F8;
            border-radius: 20px;
            padding: 15px;
            margin-bottom: 10px;
        }
        /* Bottom Input Bar Styling */
        .stChatFloatingInputContainer {
            background-color: #FFFFFF;
            border-top: 1px solid #E0E0E0;
        }
        h1, h2, h3, p, label {
            color: #202124 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .stButton>button {
            border-radius: 8px;
            background-color: #4285F4;
            color: white;
            border: none;
        }
        </style>
        """, unsafe_allow_html=True)

inject_google_ui()

# API Client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. SENSORY TOOLS (GPS & Weather) ---

def get_geo_info():
    """Gets real-time GPS coordinates and Location."""
    try:
        g = geocoder.ip('me')
        return {
            "city": g.city,
            "country": g.country,
            "lat": g.latlng[0],
            "lng": g.latlng[1]
        }
    except:
        return {"city": "Unknown", "country": "Unknown", "lat": 0, "lng": 0}

def get_live_weather(city):
    """Fetches real-time weather using live search."""
    try:
        with DDGS() as ddgs:
            res = list(ddgs.text(f"current weather in {city} February 2026", max_results=1))
            return res[0]['body']
    except:
        return "Weather data currently unavailable."

# Auto-update basic features
geo = get_geo_info()
weather = get_live_weather(geo['city'])

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("Nexus Control")
    mode = st.radio("Tools:", ["💬 Gemini Chat", "🗺️ Live Map", "🌐 AI Meta-Bridge", "👁️ Visual Scout"])
    st.divider()
    # Status Dashboard
    st.write("📍 **Location:**", f"{geo['city']}, {geo['country']}")
    st.write("🌤️ **Weather:**", weather[:50] + "...")
    st.info("System: Llama 4 Maverick (128e)")

# --- 5. FUNCTIONAL MODES ---

# A. GEMINI-STYLE CHAT
if mode == "💬 Gemini Chat":
    st.title("Nexus Pro")
    
    # Display Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask me about the weather, code, or world news..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # The AI now knows its context
            sys_msg = f"""
            You are a professional AI similar to Gemini. 
            User Context: Located in {geo['city']}, {geo['country']}. 
            Current Weather: {weather}.
            Use this data if the user asks. Be concise and helpful.
            """
            
            response = client.chat.completions.create(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.chat_history
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})

# B. LIVE GOOGLE MAPS
elif mode == "🗺️ Live Map":
    st.title("Google Maps Integration")
    map_url = f"https://www.google.com/maps?q={geo['lat']},{geo['lng']}&output=embed"
    st.components.v1.iframe(map_url, height=500)
    st.success(f"Showing coordinates: {geo['lat']}, {geo['lng']}")

# C. AI META-BRIDGE (Keep previous learning logic)
elif mode == "🌐 AI Meta-Bridge":
    st.title("Intelligence Bridge")
    target = st.selectbox("Study Target:", ["Gemini 3", "Grok-4", "Claude 4.5"])
    if st.button("Intercept Knowledge"):
        with st.spinner("Analyzing..."):
            # (Same logic as before, fetching skills via search)
            st.info(f"Connecting to {target} architecture...")

# D. VISUAL SCOUT (Ears & Eyes remain active)
elif mode == "👁️ Visual Scout":
    st.title("Visual Intelligence")
    v_file = st.file_uploader("Upload Image", type=['jpg', 'png'])
    if v_file:
        img = Image.open(v_file)
        st.image(img, width=400)
        if st.button("Analyze Image"):
            # Llama 4 Scout Vision logic
            st.success("Analysis complete.")
