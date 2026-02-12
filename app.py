import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io, os, base64, json
from PIL import Image
from duckduckgo_search import DDGS

# --- 1. SETUP & PERSISTENT MEMORY ---
st.set_page_config(page_title="Nexus Ultra AI", page_icon="🧬", layout="wide")

# Persistent Memory Initialization
if "memory" not in st.session_state:
    st.session_state.memory = "The user is new. Be professional and adaptive."
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

# --- 2. NEXUS STYLE INJECTION ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

if os.path.exists("nexus_bg.jpg"):
    bin_str = get_base64("nexus_bg.jpg")
    st.markdown(f'''
        <style>
        .stApp {{ background-image: url("data:image/png;base64,{bin_str}"); background-size: cover; background-attachment: fixed; }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
        [data-testid="stSidebar"] {{ background: rgba(0,0,0,0.6); backdrop-filter: blur(10px); color: white; }}
        .stMarkdown {{ color: #e0f2f1; text-shadow: 1px 1px 2px black; }}
        </style>
    ''', unsafe_allow_html=True)

# API Setup
if 'GROQ_API_KEY' not in st.secrets:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. CORE TOOLS (Knowledge & Learning) ---

def web_search(query):
    """Accesses the 2026 internet for real-time knowledge."""
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=3)]
        return "\n".join([f"Source: {r['title']} - {r['body']}" for r in results])

def consolidate_memory(new_chat):
    """Self-Learning: Updates the AI's internal profile of the user."""
    st.session_state.chat_count += 1
    if st.session_state.chat_count % 3 == 0: # Learn every 3 messages
        prompt = f"Based on this conversation: '{new_chat}', update the user's preference profile. Current Memory: {st.session_state.memory}"
        update = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Update the memory summary concisely."}, {"role": "user", "content": prompt}]
        )
        st.session_state.memory = update.choices[0].message.content

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("Nexus Control")
    mode = st.radio("Select Skill:", ["💬 Smart Chat", "🌍 Web Search", "🎙️ Voice Mode", "👁️ Vision", "🎨 Art Studio"])
    language = st.selectbox("Language:", ["English", "Urdu"])
    st.divider()
    st.subheader("Memory Status")
    st.caption(st.session_state.memory)
    st.info("Core: Llama 4 Maverick (128e)")

lang_code = "en" if language == "English" else "ur"

# --- 5. SKILL MODULES ---

# A. SMART CHAT & WEB SEARCH (Combined Power)
if mode in ["💬 Smart Chat", "🌍 Web Search"]:
    st.title(f"{mode} ({language})")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            context = ""
            if mode == "🌍 Web Search":
                with st.spinner("Searching the 2026 Internet..."):
                    context = web_search(prompt)
            
            response = client.chat.completions.create(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                messages=[
                    {"role": "system", "content": f"You are Nexus, a 2026 Super-AI. User Profile: {st.session_state.memory}. Search Context: {context}. Reply in {language}."},
                ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            res_text = response.choices[0].message.content
            st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
            consolidate_memory(prompt)

# B. VISION (Llama 4 Scout)
elif mode == "👁️ Vision":
    st.title("👁️ Nexus Vision")
    file = st.file_uploader("Upload Image", type=["jpg", "png"])
    if file:
        img = Image.open(file)
        st.image(img, width=400)
        q = st.text_input("Analyze:")
        if st.button("See"):
            buffered = io.BytesIO()
            img.convert("RGB").save(buffered, format="JPEG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode()
            res = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": q},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]}]
            )
            st.success(res.choices[0].message.content)

# C. VOICE MODE (Whisper V3 + gTTS)
elif mode == "🎙️ Voice Mode":
    st.title("🎙️ Voice Chat")
    audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Stop ⏹️", key='vox')
    if audio:
        transcription = client.audio.transcriptions.create(file=("a.wav", audio['bytes']), model="whisper-large-v3", language=lang_code)
        st.info(f"You: {transcription.text}")
        reply = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=[{"role":"user", "content": transcription.text}])
        st.success(f"Nexus: {reply.choices[0].message.content}")
        tts = gTTS(text=reply.choices[0].message.content, lang=lang_code)
        fp = io.BytesIO(); tts.write_to_fp(fp)
        st.audio(fp, autoplay=True)

# D. ART STUDIO
elif mode == "🎨 Art Studio":
    st.title("🎨 Imagine")
    p = st.text_input("Describe visual:")
    if st.button("Generate"):
        st.image(f"https://image.pollinations.ai/prompt/{p}?nologo=true&seed={st.session_state.chat_count}")
