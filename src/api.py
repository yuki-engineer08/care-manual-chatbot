from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bot import ask

app = FastAPI()

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    reply: str


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    messages = [m.model_dump() for m in request.messages]
    reply = ask(messages)
    return ChatResponse(reply=reply)


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
