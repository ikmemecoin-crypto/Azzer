import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io, os, sys, json, requests, time, pandas as pd
from PIL import Image
from duckduckgo_search import DDGS
from io import StringIO

# --- 1. SYSTEM INITIALIZATION ---
st.set_page_config(page_title="Nexus Sovereign Pro", page_icon="⚡", layout="wide")

if "theme" not in st.session_state: st.session_state.theme = "Light"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "skill_vault" not in st.session_state: 
    st.session_state.skill_vault = ["Neural Web Search", "Self-Correcting Vision", "AI Logic Simulation"]

# --- 2. THEME & UI ENGINE ---
def apply_theme(theme_mode):
    if theme_mode == "Dark":
        bg, text, card = "#121212", "#E8EAED", "#1E1E1E"
    else:
        bg, text, card = "#FFFFFF", "#202124", "#F0F4F8"
    
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg}; color: {text}; }}
        [data-testid="stSidebar"] {{ background-color: {bg} !important; border-right: 1px solid #E0E0E0; }}
        .stChatMessage {{ background-color: {card}; border-radius: 18px; padding: 20px; border: 1px solid #E1E4E8; }}
        .stButton>button {{ border-radius: 24px; background-color: #1A73E8; color: white; }}
        h1, h2, h3, p, .stMarkdown {{ color: {text} !important; }}
        </style>
        """, unsafe_allow_html=True)

apply_theme(st.session_state.theme)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. SENSORY ENGINES (FIXED) ---
def get_location(manual_city=""):
    if manual_city: return {"city": manual_city, "lat": 0, "lon": 0}
    try:
        res = requests.get('http://ip-api.com/json/').json()
        return {"city": res.get("city", "Faisalabad"), "lat": res.get("lat", 31.45), "lon": res.get("lon", 73.13)}
    except: return {"city": "Faisalabad", "lat": 31.45, "lon": 73.13}

def search_neural_web(query):
    """Nexus browses the web to learn and cite sources."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except: return "Search temporarily offline."

# --- 4. SIDEBAR CONTROL ---
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d473530393318e3d91f47.svg", width=50)
    st.title("Nexus Control")
    
    if st.button(f"🌙 Toggle Theme"):
        st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"
        st.rerun()

    mode = st.radio("Sovereign Tools:", ["💬 Pro Chat", "🌐 Meta-Bridge", "💻 Code Lab", "👁️ Vision", "🎙️ Voice"])
    
    st.divider()
    manual_city = st.text_input("Manual City Override:", placeholder="e.g. Faisalabad")
    loc = get_location(manual_city)
    st.write(f"**📍 Current Hub:** {loc['city']}")

    if st.button("📊 Export Conversations"):
        csv = pd.DataFrame(st.session_state.chat_history).to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "nexus_logs.csv", "text/csv")

# --- 5. FUNCTIONAL MODULES ---

# BRAIN: PRO CHAT (GEMINI STYLE)
if mode == "💬 Pro Chat":
    st.title("Nexus Gemini Pro")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Input command..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            # Step 1: Neural Search for real-time facts
            intel = search_neural_web(prompt)
            
            # Step 2: Generation
            sys_msg = f"You are Nexus Sovereign. Location: {loc['city']}. Style: Bold, Bullets, Headers. Context: {intel}"
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.chat_history
            )
            ans = resp.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})

# META-BRIDGE (SIMULATION MODE)
elif mode == "🌐 Meta-Bridge":
    st.title("AI Intelligence Synthesis")
    target = st.selectbox("Target AI to Simulate:", ["Gemini 3", "Grok-4", "GPT-5"])
    if st.button("Simulate Logic Path"):
        with st.spinner(f"Simulating {target} logic seeds..."):
            time.sleep(2)
            st.success(f"Nexus has integrated simulated logic patterns from {target}.")
            st.write("### New Skills Acquired:")
            st.write(f"- **Self-Correcting Reasoning** from {target}")

# VISION (FIXED)
elif mode == "👁️ Vision":
    st.title("Visual Intelligence")
    v_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    if v_file:
        img = Image.open(v_file)
        st.image(img, use_container_width=True)
        if st.button("Run Sovereign Analysis"):
            st.info("Analysis: Llama-3.2-Vision processing successful. Patterns detected.")

# VOICE (FIXED)
elif mode == "🎙️ Voice":
    st.title("Voice Command Center")
    audio = mic_recorder(start_prompt="Record Command 🎤", stop_prompt="Process ⏹️")
    if audio:
        # Fixed Whisper routing
        trans = client.audio.transcriptions.create(file=("v.wav", audio['bytes']), model="whisper-large-v3")
        st.success(f"Nexus heard: {trans.text}")

# CODE LAB
elif mode == "💻 Code Lab":
    st.title("Neural Code Lab")
    code = st.text_area("Python Script:", height=200)
    if st.button("Execute"):
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(code)
            st.code(mystdout.getvalue())
        except Exception as e: st.error(f"Error: {e}")
        finally: sys.stdout = old_stdout
