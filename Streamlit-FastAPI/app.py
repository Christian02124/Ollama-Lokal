import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="Streamlit → FastAPI → Ollama")
st.title("🤖 Test Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# tampilkan chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ketik pesan...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    try:
        res = requests.post(
            API_URL,
            json={"message": user_input},
            timeout=120
        )
        reply = res.json()["reply"]
    except Exception as e:
        reply = f"⚠️ Backend error: {e}"

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    st.chat_message("assistant").write(reply)