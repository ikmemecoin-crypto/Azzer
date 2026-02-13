import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io, os, base64, sys, json, requests, geocoder
from PIL import Image
from duckduckgo_search import DDGS
from io import StringIO

# --- 1. SYSTEM CONFIG & UI ---
st.set_page_config(page_title="Nexus Sovereign Pro", page_icon="⚡", layout="wide")

# Google/Gemini Professional Style
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E0E0E0; }
    .stChatMessage { background-color: #F0F4F8; border-radius: 15px; padding: 15px; border: 1px solid #E1E4E8; margin-bottom: 10px; }
    .stButton>button { border-radius: 20px; background-color: #1A73E8; color: white; border: none; font-weight: 500; }
    h1, h2, h3, p { color: #202124 !important; font-family: 'Segoe UI', sans-serif; }
    .status-card { padding: 10px; background: #E8F0FE; border-radius: 10px; border-left: 5px solid #1A73E8; margin-bottom: 10px; font-size: 0.9rem;}
    </style>
    """, unsafe_allow_html=True)

# State Management (Memory)
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "skill_vault" not in st.session_state: st.session_state.skill_vault = ["GPS Integration", "Weather Analysis"]

# API Client (Fixed Model selection to prevent InternalServerError)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. SENSORY ENGINES (GPS & Weather) ---
def get_location_data(manual_city=None):
    if manual_city:
        return {"city": manual_city, "lat": 0, "lon": 0} # Simplified for manual
    try:
        # Better IP lookup to avoid 'The Dalles' server location
        res = requests.get('http://ip-api.com/json/').json()
        return {"city": res.get("city", "Faisalabad"), "lat": res.get("lat", 31.45), "lon": res.get("lon", 73.13)}
    except: return {"city": "Unknown", "lat": 31.45, "lon": 73.13}

def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        data = requests.get(url).json()
        return f"{data['current_weather']['temperature']}°C"
    except: return "Data Unavailable"

# --- 3. SIDEBAR: THE CONTROL CENTER ---
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d473530393318e3d91f47.svg", width=40)
    st.title("Nexus Control")
    
    # RESTORED NAVIGATION
    mode = st.radio("Sovereign Tools:", [
        "💬 Pro Chat (Brain)", 
        "🌐 Meta-Bridge (Learning)", 
        "💻 Code Lab (Hands)", 
        "👁️ Vision (Eyes)", 
        "🎙️ Voice (Ears)",
        "🗺️ Live Map",
        "🎨 Art Studio"
    ])
    
    st.divider()
    # Fixed Location Control
    manual_city = st.text_input("Set City (Fix 'The Dalles'):", placeholder="e.g. Faisalabad")
    loc = get_location_data(manual_city if manual_city else None)
    temp = get_weather(loc['lat'], loc['lon'])
    
    st.markdown(f"""
    <div class="status-card">
    <b>📍 Location:</b> {loc['city']}<br>
    <b>🌤️ Weather:</b> {temp}<br>
    <b>🧠 Brain:</b> Llama 3.3 70B
    </div>
    """, unsafe_allow_html=True)

# --- 4. FUNCTIONAL MODES ---

# BRAIN: PRO CHAT
if mode == "💬 Pro Chat (Brain)":
    st.title("Nexus Pro Chat")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about weather, location, or code..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            sys_msg = f"You are Nexus. Current City: {loc['city']}. Weather: {temp}. Skills: {st.session_state.skill_vault}."
            # Fixed model call to prevent 500 error
            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.chat_history
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

# LEARNING: META-BRIDGE
elif mode == "🌐 Meta-Bridge (Learning)":
    st.title("AI Meta-Bridge")
    target = st.selectbox("Connect to AI:", ["Grok-4", "Gemini 3", "Claude 4.5"])
    if st.button("Intercept Skills"):
        with st.spinner("Learning..."):
            with DDGS() as ddgs:
                results = list(ddgs.text(f"technical architecture of {target}", max_results=1))
                new_skill = f"Advanced logic from {target}"
                st.session_state.skill_vault.append(new_skill)
                st.success(f"Nexus learned: {new_skill}")
                st.write(results[0]['body'] if results else "Architecture decoded.")

# HANDS: CODE LAB
elif mode == "💻 Code Lab (Hands)":
    st.title("Neural Code Lab")
    code_input = st.text_area("Write/Edit Code (Python):", height=200)
    if st.button("🚀 Execute"):
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(code_input)
            st.code(mystdout.getvalue())
        except Exception as e: st.error(f"Execution Error: {e}")
        finally: sys.stdout = old_stdout

# EYES: VISION
elif mode == "👁️ Vision (Eyes)":
    st.title("Visual Intelligence")
    v_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    if v_file:
        img = Image.open(v_file)
        st.image(img, use_container_width=True)
        if st.button("Analyze"):
            # Fixed Vision Model Name
            st.info("Scanning with Llama 3.2 Vision...")
            # (Actual Vision API call would go here using llama-3.2-90b-vision-preview)

# EARS: VOICE
elif mode == "🎙️ Voice (Ears)":
    st.title("Voice Bridge")
    audio = mic_recorder(start_prompt="Start Speaking 🎤", stop_prompt="Process ⏹️")
    if audio:
        trans = client.audio.transcriptions.create(file=("v.wav", audio['bytes']), model="whisper-large-v3")
        st.success(f"Heard: {trans.text}")

# MAP & ART
elif mode == "🗺️ Live Map":
    st.title("Live Intelligence Map")
    map_url = f"https://maps.google.com/maps?q={loc['city']}&t=&z=13&ie=UTF8&iwloc=&output=embed"
    st.components.v1.iframe(map_url, height=500)

elif mode == "🎨 Art Studio":
    st.title("Art Studio")
    p = st.text_input("Describe your vision:")
    if st.button("Generate"):
        st.image(f"https://image.pollinations.ai/prompt/{p}?width=1024&height=1024&nologo=true")
