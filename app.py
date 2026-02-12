import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io, os, base64, sys
from PIL import Image
from duckduckgo_search import DDGS
from io import StringIO

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Nexus Zenith AI", page_icon="⚡", layout="wide")

# Persistent Learning Memory
if "memory" not in st.session_state:
    st.session_state.memory = "User profile: Initializing. Learning mode: ACTIVE."
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Apply "Nexus" Style Background (Style only, no text)
def apply_nexus_style(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{b64}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            [data-testid="stSidebar"] {{
                background: rgba(0, 0, 0, 0.7) !important;
                backdrop-filter: blur(15px);
            }}
            .stMarkdown, h1, h2, h3 {{
                color: #00f2ff !important;
                text-shadow: 2px 2px 4px #000000;
            }}
            </style>
            """, unsafe_allow_html=True)

apply_nexus_style("nexus_bg.jpg")

# API Initialization
if 'GROQ_API_KEY' not in st.secrets:
    st.error("Missing GROQ_API_KEY in Secrets.")
    st.stop()
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. CORE BRAIN FUNCTIONS ---

def update_learning(user_input, ai_output):
    """Self-Learning Module: Updates user profile every interaction."""
    update_prompt = f"System: Update user profile based on: User said '{user_input}', AI replied '{ai_output}'. Current Memory: {st.session_state.memory}"
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a memory-update agent. Summarize user preferences/context."}, 
                      {"role": "user", "content": update_prompt}]
        )
        st.session_state.memory = res.choices[0].message.content
    except: pass

def get_internet_data(query):
    """Real-time Knowledge from the 2026 Internet."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            return "\n".join([f"Info: {r['body']}" for r in results])
    except: return "No live search results available."

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("NEXUS CONTROL")
    mode = st.radio("Skill Selection:", ["💬 Ultra Chat", "💻 Code Lab", "👁️ Vision", "🎙️ Voice", "🎨 Art Studio"])
    language = st.selectbox("Interaction Language:", ["English", "Urdu"])
    st.divider()
    st.write("**AI Memory Status:**")
    st.caption(st.session_state.memory)
    st.info("Version: 2026.02.13-Zenith")

lang_code = "en" if language == "English" else "ur"

# --- 4. SKILLS MODULES ---

# A. ULTRA CHAT (Knowledge + Learning)
if mode == "💬 Ultra Chat":
    st.title("💬 Nexus Ultra Chat")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything (I learn and search)..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            search_context = get_internet_data(prompt)
            # Use Llama 4 Maverick for highest reasoning as of 2026
            response = client.chat.completions.create(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                messages=[{"role": "system", "content": f"You are Nexus Zenith. Memory: {st.session_state.memory}. Internet Context: {search_context}. Reply in {language}."}] + 
                         st.session_state.chat_history
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            update_learning(prompt, ans)

# B. CODE LAB (The New Power Skill)
elif mode == "💻 Code Lab":
    st.title("💻 Neural Code Execution")
    st.write("Ask the AI to write Python code, then execute it below.")
    
    code_input = st.text_area("Python Script:", height=200, placeholder="print('Hello World')")
    
    if st.button("🚀 Execute Code"):
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        try:
            exec(code_input)
            st.code(redirected_output.getvalue(), language="python")
        except Exception as e:
            st.error(f"Execution Error: {e}")
        finally:
            sys.stdout = old_stdout

# C. VISION (Seeing Skill)
elif mode == "👁️ Vision":
    st.title("👁️ Visual Analysis")
    up = st.file_uploader("Upload image", type=["jpg", "png"])
    if up:
        img = Image.open(up)
        st.image(img, width=400)
        task = st.text_input("What should I see?")
        if st.button("Analyze"):
            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="JPEG")
            b64_img = base64.b64encode(buf.getvalue()).decode()
            v_res = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": [{"type": "text", "text": task}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}]}]
            )
            st.success(v_res.choices[0].message.content)

# D. VOICE & ART (Previously Verified)
elif mode == "🎙️ Voice":
    st.title("🎙️ Voice Interface")
    v_audio = mic_recorder(start_prompt="Record 🎤", stop_prompt="Process ⏹️")
    if v_audio:
        trans = client.audio.transcriptions.create(file=("v.wav", v_audio['bytes']), model="whisper-large-v3", language=lang_code)
        st.write(f"**You:** {trans.text}")
        reply = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=[{"role":"user", "content": trans.text}])
        st.write(f"**Nexus:** {reply.choices[0].message.content}")
        tts = gTTS(text=reply.choices[0].message.content, lang=lang_code)
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp, autoplay=True)

elif mode == "🎨 Art Studio":
    st.title("🎨 AI Image Generation")
    art_p = st.text_input("Visual Description:")
    if st.button("Create"):
        st.image(f"https://image.pollinations.ai/prompt/{art_p}?nologo=true&width=1024&height=1024")
