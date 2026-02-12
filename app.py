import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import os
import base64
from PIL import Image

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Nexus AI Multilingual", page_icon="🧠", layout="wide")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# APPLYING YOUR ATTACHED STYLE (Background only)
# Make sure your image file is named 'nexus_bg.jpg' in your project folder
if os.path.exists("nexus_bg.jpg"):
    bin_str = get_base64("nexus_bg.jpg")
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}
    [data-testid="stSidebar"] {{
        background: rgba(0,0,0,0.5);
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Ensure API Key is present
if 'GROQ_API_KEY' not in st.secrets:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("Nexus Control")
    mode = st.radio("Select Mode:", ["🎙️ Voice Chat", "💬 Text Chat", "👁️ Vision Chat", "🎨 Art Studio"])
    language = st.selectbox("Conversation Language:", ["English", "Urdu"])
    st.divider()
    # Updated verification info for 2026
    st.info("Verified: Llama 3.3 (Text) + Llama 4 Scout (Vision)")

lang_code = "en" if language == "English" else "ur"

# --- 3. VOICE CHAT ENGINE ---
if mode == "🎙️ Voice Chat":
    st.title(f"🎙️ Voice Chat ({language})")
    audio = mic_recorder(start_prompt="Click to Speak 🎤", stop_prompt="Stop & Process ⏹️", key='recorder')
    if audio:
        with st.spinner("Listening..."):
            try:
                audio_file = ("audio.wav", audio['bytes'], "audio/wav")
                transcription = client.audio.transcriptions.create(
                    file=audio_file, model="whisper-large-v3", language=lang_code, response_format="text"
                )
                user_text = transcription
                st.info(f"You said: {user_text}")

                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"Reply in {language} only."},
                        {"role": "user", "content": user_text}
                    ]
                )
                ai_response = completion.choices[0].message.content
                st.success(f"AI: {ai_response}")

                with st.spinner("Generating Voice..."):
                    tts = gTTS(text=ai_response, lang=lang_code)
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format="audio/mp3", autoplay=True)
            except Exception as e:
                st.error(f"Voice Error: {str(e)}")

# --- 4. TEXT CHAT MODE ---
elif mode == "💬 Text Chat":
    st.title(f"💬 Text Chat ({language})")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Type here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": f"Reply in {language}"}] + 
                         [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            full_res = response.choices[0].message.content
            st.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

# --- 5. VISION CHAT (FIXED MODEL) ---
elif mode == "👁️ Vision Chat":
    st.title("👁️ Nexus Vision")
    uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=400)
        user_question = st.text_input("Ask about this image:")
        if st.button("🔍 Analyze Image"):
            with st.spinner("Processing with Llama 4 Scout..."):
                try:
                    buffered = io.BytesIO()
                    if image.mode != "RGB": image = image.convert("RGB")
                    image.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # UPDATED TO LLAMA 4 SCOUT (LATEST 2026 VISION MODEL)
                    chat_completion = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_question},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                            ]
                        }]
                    )
                    st.success(chat_completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"API Error: {e}")

# --- 6. ART STUDIO ---
elif mode == "🎨 Art Studio":
    st.title("🎨 Art Studio")
    prompt = st.text_input("Describe the image:")
    if st.button("Generate"):
        url = f"https://image.pollinations.ai/prompt/{prompt}?nologo=true"
        st.image(url)
