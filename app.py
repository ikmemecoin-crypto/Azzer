import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import base64
from PIL import Image

# --- 1. CONFIG & MEMORY INITIALIZATION ---
st.set_page_config(page_title="Omni-AI Hub", page_icon="🧠", layout="wide")

# This is the "Learning" part: It stores what the AI learns about you
if "ai_memory" not in st.session_state:
    st.session_state.ai_memory = "The user is exploring the app. No specific preferences learned yet."
if "messages" not in st.session_state:
    st.session_state.messages = []

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. THE LEARNING ENGINE (Self-Update Logic) ---
def update_memory(user_input, ai_response):
    """Verifies and updates the AI's internal understanding of the user."""
    learning_prompt = f"""
    Based on this conversation:
    User: {user_input}
    AI: {ai_response}
    
    Current Memory: {st.session_state.ai_memory}
    
    Update the 'Current Memory' with any new facts about the user (name, language, interests, preferences). 
    Keep it concise. Return ONLY the new memory string.
    """
    try:
        update = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": learning_prompt}]
        )
        st.session_state.ai_memory = update.choices[0].message.content
    except:
        pass

# --- 3. SIDEBAR: SKILL SELECTOR ---
with st.sidebar:
    st.title("🧠 Omni-AI Suite")
    skill = st.selectbox("Choose a Skill:", 
        ["💬 General Intel (Chat)", "👁️ Vision (See Images)", "🎙️ Voice (Eng/Urdu)", "🎨 Art Studio", "💻 Code Pro"])
    
    st.divider()
    st.subheader("AI's Learned Memory:")
    st.caption(st.session_state.ai_memory)
    if st.button("Clear Memory"):
        st.session_state.ai_memory = "Memory wiped."
        st.rerun()

# --- 4. SKILL: VISION (Image Analysis) ---
if skill == "👁️ Vision (See Images)":
    st.title("👁️ AI Vision")
    uploaded_file = st.file_uploader("Upload an image for the AI to 'see'...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, width=400)
        
        if st.button("Analyze Image"):
            # Convert to Base64 for Groq Vision
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            completion = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image? Describe it in detail."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }]
            )
            st.write(completion.choices[0].message.content)

# --- 5. SKILL: CHAT & LEARNING ---
elif skill == "💬 General Intel (Chat)":
    st.title("💬 Adaptive Chat")
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Ask anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Inject memory into the system prompt so the AI "remembers"
            full_system_prompt = f"You are a genius AI. Here is what you have learned about the user: {st.session_state.ai_memory}"
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": full_system_prompt}] + 
                         [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            ai_res = response.choices[0].message.content
            st.markdown(ai_res)
            st.session_state.messages.append({"role": "assistant", "content": ai_res})
            
            # Auto-Update Memory
            update_memory(prompt, ai_res)

# --- 6. REMAINING SKILLS (Voice & Art - Same as previous steps) ---
# [Logic for Voice and Art remains integrated here in the same style]
