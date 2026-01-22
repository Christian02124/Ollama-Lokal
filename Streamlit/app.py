import streamlit as st
import requests
import json
import os
from pypdf import PdfReader

# ================= CONFIG =================
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma3:4b"
HISTORY_FILE = "chat_history.json"
MAX_CONTEXT = 4  # biar ringan
PDF_CONTEXT_LIMIT = 2500  # batasi teks PDF
# =========================================

st.set_page_config(page_title="Chatbot Ollama", layout="centered")
st.title("🤖 Chatbot (Lokal)")

# ---------- Load history ----------
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ---------- Save history ----------
def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

# ---------- Extract PDF ----------
def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# ---------- Upload PDF ----------
uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Membaca PDF..."):
        st.session_state.pdf_text = extract_pdf_text(uploaded_file)

    if st.session_state.pdf_text:
        st.success("PDF berhasil dibaca ✅")
        st.caption(f"Panjang teks PDF: {len(st.session_state.pdf_text)} karakter")
    else:
        st.warning("PDF kosong atau tidak bisa diekstrak.")

# ---------- Tampilkan Chat ----------
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# ---------- Input ----------
user_input = st.chat_input("Tanya apapun...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # ---------- SYSTEM CONTEXT dari PDF ----------
    system_message = {
        "role": "system",
        "content": (
            "Kamu adalah asisten AI yang menjawab pertanyaan "
            "BERDASARKAN isi PDF berikut. "
            "Jika jawabannya tidak ada di PDF, katakan dengan jujur.\n\n"
            f"{st.session_state.pdf_text[:PDF_CONTEXT_LIMIT]}"
        )
    }

    # ---------- Context dibatasi ----------
    context = [system_message] + st.session_state.messages[-MAX_CONTEXT:]

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": context,
                "stream": False
            },
            timeout=300
        )

        data = response.json()

        # ---------- Parsing AMAN ----------
        if "message" in data and "content" in data["message"]:
            reply = data["message"]["content"]
        else:
            reply = (
                "⚠️ Response Ollama tidak sesuai format.\n\n"
                f"{json.dumps(data, indent=2)}"
            )

    except requests.exceptions.ConnectionError:
        reply = "❌ Ollama tidak dapat dihubungi. Pastikan `ollama serve` sudah berjalan."
    except Exception as e:
        reply = f"⚠️ Terjadi error:\n{e}"

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    save_history(st.session_state.messages)
    st.chat_message("assistant").write(reply)

# ---------- Clear ----------
if st.button("🧹 Hapus Riwayat Chat"):
    st.session_state.messages = []
    save_history([])
    st.rerun()