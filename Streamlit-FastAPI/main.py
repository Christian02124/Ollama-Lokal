from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma3:4b"

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": req.message}
        ],
        "stream": False
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=180)
        data = r.json()

        # 🔍 DEBUG kalau error lagi
        print("OLLAMA RESPONSE:", data)

        # ✅ ambil dengan aman
        if "message" in data:
            reply = data["message"].get("content", "")
        elif "response" in data:
            reply = data["response"]
        elif "error" in data:
            reply = f"Ollama error: {data['error']}"
        else:
            reply = f"Unknown response: {data}"

        return {"reply": reply}

    except Exception as e:
        return {"reply": f"Backend error: {e}"}