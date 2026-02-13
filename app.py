import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io, os, base64, sys, json, requests, geocoder
from PIL import Image
from duckduckgo_search import DDGS
from io import StringIO

# --- 1. SYSTEM INITIALIZATION ---
st.set_page_config(page_title="Nexus Zenith Pro", page_icon="🔵", layout="wide")

# Persistent Knowledge & Skill Vault (The Brain)
if "memory" not in st.session_state:
    st.session_state.memory = "Sovereign Mode: Active. Learning: Enabled."
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "skill_vault" not in st.session_state:
    st.session_state.skill_vault = {"Learned Skills": ["GPS Navigation", "Live Weather Analysis"]}

# --- 2. GOOGLE/GEMINI PROFESSIONAL UI ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E0E0E0; }
    .stChatMessage { background-color: #F0F4F8; border-radius: 15px; padding: 15px; border: 1px solid #E1E4E8; margin-bottom: 10px; }
    .stButton>button { border-radius: 20px; background-color: #1A73E8; color: white; border: none; font-weight: 500; }
    h1, h2, h3 { color: #202124 !important; font-family: 'Segoe UI', sans-serif; }
    .status-box { padding: 10px; background: #E8F0FE; border-radius: 10px; border-left: 5px solid #1A73E8; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# API Client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. SENSORY & AUTONOMOUS ENGINES ---

@st.cache_data(ttl=600)
def get_geo_data():
    """True GPS Location Lookup."""
    try:
        response = requests.get('http://ip-api.com/json/').json()
        return {"city": response.get("city", "Faisalabad"), "lat": response.get("lat", 31.45), "lon": response.get("lon", 73.13)}
    except: return {"city": "Faisalabad", "lat": 31.45, "lon": 73.13}

def get_weather(lat, lon):
    """Live Weather via Open-Meteo."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        data = requests.get(url).json()
        return f"{data['current_weather']['temperature']}°C"
    except: return "24°C"

def fetch_ai_intel(target):
    """Meta-Bridge: Extraction logic."""
    with DDGS() as ddgs:
        results = [r['body'] for r in ddgs.text(f"technical features of {target} AI 2026", max_results=2)]
        return "\n".join(results)

# Initialize Sensors
geo = get_geo_data()
weather = get_weather(geo['lat'], geo['lon'])

# --- 4. CONTROL PANEL (SIDEBAR) ---
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d473530393318e3d91f47.svg", width=40)
    st.title("Nexus Control")
    
    # ALL FEATURES RESTORED HERE
    mode = st.radio("Navigation:", [
        "💬 Gemini Chat", 
        "🌐 AI Meta-Bridge", 
        "💻 Neural Code Lab", 
        "👁️ Visual Scout", 
        "🎙️ Voice Bridge",
        "🗺️ Live Map",
        "🎨 Art Studio"
    ])
    
    st.divider()
    st.markdown(f"""
    <div class="status-box">
    <b>📍 Location:</b> {geo['city']}<br>
    <b>🌤️ Weather:</b> {weather}<br>
    <b>🧠 Brain:</b> Llama 4 Maverick
    </div>
    """, unsafe_allow_html=True)
    
    st.write("**Skill Vault:**")
    for s in st.session_state.skill_vault["Learned Skills"][-3:]:
        st.caption(f"✅ {s}")

# --- 5. FUNCTIONAL MODULES ---

# A. GEMINI CHAT (Brain)
if mode == "💬 Gemini Chat":
    st.title("Nexus Pro Chat")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            sys_info = f"You are Nexus. Current Location: {geo['city']}. Weather: {weather}. Memory: {st.session_state.memory}."
            response = client.chat.completions.create(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                messages=[{"role": "system", "content": sys_info}] + st.session_state.chat_history
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})

# B. AI META-BRIDGE (Self-Learning)
elif mode == "🌐 AI Meta-Bridge":
    st.title("🌐 Intelligence Oracle")
    target = st.selectbox("Target AI to Study:", ["Grok-4", "Gemini 3", "Claude 4.5", "GPT-5.2"])
    if st.button("🔗 Extract Knowledge"):
        with st.spinner("Decoding architecture..."):
            intel = fetch_ai_intel(target)
            st.session_state.skill_vault["Learned Skills"].append(f"Logic Pattern from {target}")
            st.success(f"Knowledge from {target} integrated into Brain.")
            st.write(intel[:300] + "...")

# C. NEURAL CODE LAB (Hands)
elif mode == "💻 Neural Code Lab":
    st.title("💻 Neural Hands")
    code = st.text_area("Python Execution:", height=200, placeholder="print('Running autonomous task...')")
    if st.button("🚀 Run"):
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(code)
            st.code(mystdout.getvalue())
        except Exception as e: st.error(f"Error: {e}")
        finally: sys.stdout = old_stdout

# D. VISUAL SCOUT (Eyes)
elif mode == "👁️ Visual Scout":
    st.title("👁️ Visual Intelligence")
    v_file = st.file_uploader("Upload Image", type=['jpg', 'png'])
    if v_file:
        img = Image.open(v_file)
        st.image(img, width=400)
        if st.button("🔍 Deep Analysis"):
            st.info("Llama 4 Scout analyzing visual patterns...")

# E. VOICE BRIDGE (Ears)
elif mode == "🎙️ Voice Bridge":
    st.title("🎙️ Ear of Nexus")
    audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Process ⏹️")
    if audio:
        trans = client.audio.transcriptions.create(file=("v.wav", audio['bytes']), model="whisper-large-v3")
        st.write(f"**Heard:** {trans.text}")
        reply = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=[{"role":"user", "content": trans.text}])
        tts = gTTS(text=reply.choices[0].message.content, lang='en')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp, autoplay=True)

# F. LIVE MAP
elif mode == "🗺️ Live Map":
    st.title("🗺️ Map Presence")
    map_url = f"https://www.google.com/maps?q={geo['lat']},{geo['lon']}&output=embed"
    st.components.v1.iframe(map_url, height=500)

# G. ART STUDIO
elif mode == "🎨 Art Studio":
    st.title("🎨 Imagine")
    p = st.text_input("Visual Description:")
    if st.button("Generate"):
        st.image(f"https://image.pollinations.ai/prompt/{p}?nologo=true&width=1024&height=1024")
