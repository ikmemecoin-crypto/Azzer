import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import os
import base64
from PIL import Image

# --- 1. SETUP ---
st.set_page_config(page_title="Nexus AI Multilingual", page_icon="🧠", layout="wide")

# Ensure API Key is present
if 'GROQ_API_KEY' not in st.secrets:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("Nexus Control")
    # Added Vision Chat to the list below
    mode = st.radio("Select Mode:", ["🎙️ Voice Chat", "💬 Text Chat", "👁️ Vision Chat", "🎨 Art Studio"])
    language = st.selectbox("Conversation Language (Voice/Text only):", ["English", "Urdu"])
    st.divider()
    st.info("Verified for 2026: Llama 3.3, Whisper V3 & Llama 3.2 Vision")

lang_code = "en" if language == "English" else "ur"

# --- 3. VOICE CHAT ENGINE ---
if mode == "🎙️ Voice Chat":
    st.title(f"🎙️ Voice Chat ({language})")
    st.write(f"Speak in {language}, and I will reply with voice.")

    # Record Audio
    audio = mic_recorder(
        start_prompt="Click to Speak 🎤",
        stop_prompt="Stop & Process ⏹️",
        key='recorder'
    )

    if audio:
        # A. Speech to Text (STT) via Groq Whisper
        with st.spinner("Listening..."):
            try:
                # Convert bytes to file-like object for Groq
                audio_file = ("audio.wav", audio['bytes'], "audio/wav")
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    language=lang_code,
                    response_format="text",
                )
                user_text = transcription
                st.info(f"You said: {user_text}")

                # B. Brain (LLM) - Llama 3.3
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"You are a helpful assistant. Please reply in {language} only."},
                        {"role": "user", "content": user_text}
                    ]
                )
                ai_response = completion.choices[0].message.content
                st.success(f"AI: {ai_response}")

                # C. Text to Speech (TTS) via gTTS
                with st.spinner("Generating Voice Response..."):
                    tts = gTTS(text=ai_response, lang=lang_code)
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format="audio/mp3", autoplay=True)

            except Exception as e:
                st.error(f"Voice Error: {str(e)}")

# --- 4. TEXT CHAT MODE ---
elif mode == "💬 Text Chat":
    st.title(f"💬 Text Chat ({language})")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Type here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": f"Reply in {language}"}] + 
                         [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            full_res = response.choices[0].message.content
            st.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

# --- 5. NEW VISION CHAT MODE ---
elif mode == "👁️ Vision Chat":
    st.title("👁️ Vision Chat")
    st.write("Upload an image, and I will analyze it for you.")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption='Ready for analysis', width=400)

        user_question = st.text_input("What do you want to know about this image?", placeholder="e.g., Describe this image in detail.")

        if st.button("🔍 Analyze Image"):
            if user_question:
                with st.spinner("AI Eyes are looking..."):
                    try:
                        # 1. Prepare Image for API (Base64 Encoding)
                        buffered = io.BytesIO()
                        # Convert RGBA to RGB if necessary before saving as JPEG
                        if image.mode in ("RGBA", "P"): image = image.convert("RGB")
                        image.save(buffered, format="JPEG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        img_data_url = f"data:image/jpeg;base64,{img_str}"

                        # 2. Call Groq Vision Model
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": user_question},
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": img_data_url},
                                        },
                                    ],
                                }
                            ],
                            # Using the free-tier eligible vision model
                            model="llama-3.2-11b-vision-preview",
                        )

                        # 3. Display Response
                        st.markdown("### AI Analysis:")
                        st.success(chat_completion.choices[0].message.content)

                    except Exception as e:
                        st.error(f"Vision API Error: {e}")
            else:
                st.warning("Please enter a question about the image first.")

# --- 6. ART STUDIO ---
elif mode == "🎨 Art Studio":
    st.title("🎨 Art Studio")
    prompt = st.text_input("Describe the image:")
    if st.button("Generate"):
        with st.spinner("Painting..."):
            url = f"https://image.pollinations.ai/prompt/{prompt}?nologo=true"
            st.image(url)
