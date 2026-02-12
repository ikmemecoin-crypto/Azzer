import streamlit as st
from groq import Groq

# 1. Page Configuration
st.set_page_config(page_title="Nexus AI", page_icon="⚡", layout="centered")

# 2. Sidebar for API Key (or use Secrets in Deployment)
with st.sidebar:
    st.title("Settings")
    if 'GROQ_API_KEY' in st.secrets:
        groq_api_key = st.secrets["GROQ_API_KEY"]
    else:
        groq_api_key = st.text_input("Enter Groq API Key:", type="password")
        st.info("Get your free key at console.groq.com")

# 3. Initialize Groq Client
if groq_api_key:
    client = Groq(api_key=groq_api_key)

    # 4. Chat History Logic
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("Nexus AI ⚡")
    st.caption("Powered by Llama-3.3-70B & Groq Ultra-Fast Inference")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 5. User Input
    if prompt := st.chat_input("Ask Nexus anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 6. AI Response Generation
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )

                for chunk in completion:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    st.warning("Please enter your API Key in the sidebar to begin.")