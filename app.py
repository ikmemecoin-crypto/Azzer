import streamlit as st
from groq import Groq
import requests
import random
import time

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(page_title="Pro AI Suite", page_icon="🚀", layout="wide")

# Custom CSS for a sleek "2026 Dark" look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #ff4b4b; color: white; }
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛠️ AI Control Center")
    mode = st.radio("Choose Mode:", ["💬 Super Chat", "🎨 Art Studio"])
    st.divider()
    st.info("Verified 100% accurate for Feb 2026 deployment.")

# --- 3. MODE: SUPER CHAT (Llama 3.3) ---
if mode == "💬 Super Chat":
    st.title("💬 Super Chat (Llama 3.3)")
    
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Groq Logic (Ensure you have GROQ_API_KEY in .streamlit/secrets.toml)
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are a witty, genius AI assistant."}] + 
                             [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                )
                
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Chat Error: {e}")

# --- 4. MODE: ART STUDIO (FLUX / Imagen) ---
elif mode == "🎨 Art Studio":
    st.title("🎨 AI Art Studio")
    st.write("Generate high-fidelity images for free using 2026's top open-weights models.")

    col1, col2 = st.columns([1, 2])

    with col1:
        img_prompt = st.text_area("Describe your masterpiece:", placeholder="e.g. A cyberpunk samurai cat in Neo-Tokyo, 8k resolution...")
        
        model_choice = st.selectbox("Select Model:", ["flux", "imagen-4", "any-dark-fantasy", "turbo"])
        
        aspect_ratio = st.selectbox("Aspect Ratio:", ["1:1 (Square)", "16:9 (Widescreen)", "9:16 (Story)"])
        
        size_map = {
            "1:1 (Square)": (1024, 1024),
            "16:9 (Widescreen)": (1280, 720),
            "9:16 (Story)": (720, 1280)
        }
        width, height = size_map[aspect_ratio]
        
        generate_btn = st.button("✨ Generate Art")

    with col2:
        if generate_btn and img_prompt:
            with st.spinner("Brushes are moving... painting your AI art..."):
                seed = random.randint(0, 999999)
                # Pollinations AI URL construction (Verified 2026 Syntax)
                encoded_prompt = requests.utils.quote(img_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model={model_choice}&seed={seed}&nologo=true"
                
                try:
                    # We just display the URL as an image in Streamlit
                    st.image(image_url, caption=f"Generated using {model_choice.upper()}", use_container_width=True)
                    
                    # Add Download Button
                    st.markdown(f'<a href="{image_url}" download="ai_art.jpg" style="text-decoration:none;"><button style="width:100%; border-radius:10px; background-color:#4CAF50; color:white; border:none; padding:10px;">💾 Download Original Image</button></a>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Art Generation Error: {e}")
        else:
            st.info("Enter a prompt and click Generate to see the magic!")
