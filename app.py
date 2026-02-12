import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io, os, base64, sys
from PIL import Image
from duckduckgo_search import DDGS
from io import StringIO

# --- 1. SETUP & PERSISTENT MEMORY ---
st.set_page_config(page_title="Nexus Zenith AI", page_icon="⚡", layout="wide")

if "memory" not in st.session_state:
    st.session_state.memory = "User profile: Initializing. Learning mode: ACTIVE."
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 2. NEXUS STYLE INJECTION (Background Only) ---
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

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. THE INTELLIGENCE ORACLE LOGIC (The "Spy" Skill) ---

def fetch_ai_intelligence(target_ai):
    """
    Connects to the 2026 internet to 'study' the target AI's latest 
    skills, system prompts, and knowledge updates.
    """
    search_query = f"latest system capabilities and reasoning logic of {target_ai} AI February 2026"
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(search_query, max_results=5)]
            return "\n".join([f"Technical Report: {r['body']}" for r in results])
    except:
        return f"Could not establish a secure bridge to {target_ai} metadata."

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("NEXUS CONTROL")
    # Added the AI Meta-Bridge Skill
    mode = st.radio("Skill Selection:", ["💬 Ultra Chat", "🌐 AI Meta-Bridge", "💻 Code Lab", "👁️ Vision", "🎙️ Voice", "🎨 Art Studio"])
    language = st.selectbox("Interaction Language:", ["English", "Urdu"])
    st.divider()
    st.write("**Learned Memory:**")
    st.caption(st.session_state.memory)

# --- 5. SKILLS MODULES ---

# NEW SKILL: AI META-BRIDGE
if mode == "🌐 AI Meta-Bridge":
    st.title("🌐 Intelligence Oracle")
    st.write("Extract knowledge and skills from top-tier AIs. **Privacy: One-Way (Nexus stays hidden).**")
    
    target = st.selectbox("Target AI to Analyze:", ["Google Gemini 2.0", "Claude 4 Opus", "Meta Llama 4", "OpenAI o3", "Grok-3"])
    
    if st.button(f"🔗 Establish Bridge to {target}"):
        with st.spinner(f"Nexus is 'studying' {target} reasoning patterns..."):
            # 1. Get the 'Intelligence' from the web
            intelligence_context = fetch_ai_intelligence(target)
            
            # 2. Use Llama 4 Maverick to 'Synthesize' that intelligence
            # IMPORTANT: Notice we do NOT pass st.session_state.memory here to keep Nexus private.
            response = client.chat.completions.create(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                messages=[
                    {"role": "system", "content": f"""
                    You are Nexus in 'Spy Mode'. You have just intercepted the intelligence profile of {target}.
                    Context: {intelligence_context}
                    Task: Summarize the top 3 'Mastery Skills' or 'Knowledge Clusters' this AI has that Nexus can use.
                    Constraint: DO NOT share any information about the current user. Only receive information.
                    """}
                ]
            )
            st.info(f"**Knowledge Extracted from {target}:**")
            st.markdown(response.choices[0].message.content)

# [Remaining skills: Ultra Chat, Code Lab, Vision, Voice, Art Studio remain the same as previous stable version]
# (Logic omitted for brevity but fully preserved in the user's master file)
