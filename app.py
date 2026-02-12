import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import os

# --- 1. SETUP ---
st.set_page_config(page_title="Nexus AI Multilingual", page_icon="🎙️", layout="wide")

# Ensure API Key is present
if 'GROQ_API_KEY' not in st.secrets:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("Nexus Control")
    mode = st.radio("Select Mode:", ["🎙️ Voice Chat", "🎨 Art Studio", "💬 Text Chat"])
    language = st.selectbox("Conversation Language:", ["English", "Urdu"])
    st.divider()
    st.info("Verified for 2026: Llama 3.3 + Whisper V3")

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

# --- 4. TEXT CHAT MODE (Updated for Multilingual) ---
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

# --- 5. ART STUDIO (Previously Verified) ---
elif mode == "🎨 Art Studio":
    st.title("🎨 Art Studio")
    prompt = st.text_input("Describe the image:")
    if st.button("Generate"):
        url = f"https://image.pollinations.ai/prompt/{prompt}?nologo=true"
        st.image(url)
