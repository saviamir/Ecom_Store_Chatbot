from chatbot import chat
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request

app = FastAPI(
    title="Chatbot API",
    description="This is a chatbot API",
    version="0.1",
    docs_url="/",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing GET route (you can keep this if needed)
@app.get("/ask")
def ask(user_id: str, question: str):
    response = chat(user_id, question)
    return JSONResponse(content={"response": response})

# ✅ Add this new POST route to support frontend
@app.post("/")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    # If you want to handle user_id, add it here too
    response = chat("web_user", message)
    return JSONResponse(content={"reply": response})
