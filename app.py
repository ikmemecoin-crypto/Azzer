import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io, os, base64, sys
from PIL import Image
from duckduckgo_search import DDGS
from io import StringIO

# --- 1. SYSTEM INITIALIZATION ---
st.set_page_config(page_title="Nexus Zenith AI", page_icon="⚡", layout="wide")

# Persistent Memory & History
if "memory" not in st.session_state:
    st.session_state.memory = "User profile: Initializing. Learning mode: ACTIVE."
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 2. NEXUS VISUAL ENGINE (Background Style Only) ---
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
                background: rgba(0, 0, 0, 0.8) !important;
                backdrop-filter: blur(15px);
            }}
            .stChatFloatingInputContainer {{
                background: rgba(0,0,0,0);
            }}
            .stMarkdown, h1, h2, h3, p, label {{
                color: #00f2ff !important;
                text-shadow: 2px 2px 4px #000000;
            }}
            </style>
            """, unsafe_allow_html=True)
    else:
        st.warning("Nexus Style Error: 'nexus_bg.jpg' not found. Defaulting to standard view.")

apply_nexus_style("nexus_bg.jpg")

# API Client
if 'GROQ_API_KEY' not in st.secrets:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. CORE BRAIN LOGIC ---

def update_learning(user_input, ai_output):
    """Updates user profile every 2nd interaction for efficiency."""
    update_prompt = f"Update user context: User: '{user_input}', AI: '{ai_output}'. Context: {st.session_state.memory}"
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Update the memory summary concisely."}, 
                      {"role": "user", "content": update_prompt}]
        )
        st.session_state.memory = res.choices[0].message.content
    except: pass

def fetch_ai_intelligence(target):
    """Scrapes latest 2026 intelligence on other top-tier AI apps."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(f"latest technical capabilities of {target} AI 2026", max_results=3)]
            return "\n".join([f"Intelligence: {r['body']}" for r in results])
    except: return "Intelligence Bridge failed. Target currently shielded."

# --- 4. SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.title("NEXUS CONTROL")
    mode = st.radio("Skill Selection:", ["💬 Ultra Chat", "🌐 AI Meta-Bridge", "💻 Code Lab", "👁️ Vision", "🎙️ Voice", "🎨 Art Studio"])
    language = st.selectbox("Interaction Language:", ["English", "Urdu"])
    st.divider()
    st.write("**Learned Memory:**")
    st.caption(st.session_state.memory)
    st.info("System: Llama 4 Maverick (128e)")

lang_code = "en" if language == "English" else "ur"

# --- 5. SKILL EXECUTION BLOCKS (FIXED: Full Modules) ---

# A. ULTRA CHAT (Web-Knowledge + Learning)
if mode == "💬 Ultra Chat":
    st.title("💬 Nexus Ultra Chat")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Nexus is thinking..."):
                response = client.chat.completions.create(
                    model="meta-llama/llama-4-maverick-17b-128e-instruct",
                    messages=[{"role": "system", "content": f"You are Nexus. Memory: {st.session_state.memory}. Reply in {language}."}] + st.session_state.chat_history
                )
                ans = response.choices[0].message.content
                st.markdown(ans)
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
                update_learning(prompt, ans)

# B. AI META-BRIDGE (Intelligence Extraction)
elif mode == "🌐 AI Meta-Bridge":
    st.title("🌐 Intelligence Oracle")
    target = st.selectbox("Extract Skills From:", ["Google Gemini 2.0", "Claude 4 Opus", "Meta Llama 4", "Grok-3"])
    if st.button(f"🔗 Bridge to {target}"):
        with st.spinner(f"Intercepting {target} reasoning patterns..."):
            intel = fetch_ai_intelligence(target)
            res = client.chat.completions.create(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                messages=[{"role": "system", "content": f"Extract the top 3 skills from this data: {intel}. Do not share user info."}]
            )
            st.info(f"**Knowledge Stolen from {target}:**")
            st.markdown(res.choices[0].message.content)

# C. CODE LAB (Physical Script Execution)
elif mode == "💻 Code Lab":
    st.title("💻 Neural Code Lab")
    code_in = st.text_area("Write/Paste Python here:", height=200)
    if st.button("🚀 Run Locally"):
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(code_in)
            st.code(mystdout.getvalue())
        except Exception as e: st.error(f"Logic Error: {e}")
        finally: sys.stdout = old_stdout

# D. VISION (Llama 4 Scout Fix)
elif mode == "👁️ Vision":
    st.title("👁️ Visual Intelligence")
    file = st.file_uploader("Upload Image", type=["jpg", "png"])
    if file:
        img = Image.open(file)
        st.image(img, width=400)
        q = st.text_input("Ask about this image:")
        if st.button("🔍 Analyze"):
            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="JPEG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            res = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct", # 2026 Model
                messages=[{"role": "user", "content": [{"type": "text", "text": q}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]
            )
            st.success(res.choices[0].message.content)

# E. VOICE (Whisper + gTTS)
elif mode == "🎙️ Voice":
    st.title("🎙️ Voice Bridge")
    v_audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Process ⏹️")
    if v_audio:
        trans = client.audio.transcriptions.create(file=("v.wav", v_audio['bytes']), model="whisper-large-v3", language=lang_code)
        st.write(f"**You:** {trans.text}")
        reply = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=[{"role":"user", "content": trans.text}])
        st.write(f"**Nexus:** {reply.choices[0].message.content}")
        tts = gTTS(text=reply.choices[0].message.content, lang=lang_code)
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp, autoplay=True)

# F. ART STUDIO
elif mode == "🎨 Art Studio":
    st.title("🎨 Imagine")
    p = st.text_input("Describe visual:")
    if st.button("Generate"):
        st.image(f"https://image.pollinations.ai/prompt/{p}?nologo=true&width=1024&height=1024")
