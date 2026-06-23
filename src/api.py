import os
from pathlib import Path

from typing import Any, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bot import ask
from storage import list_reports, save_report

app = FastAPI()

allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    report_fields: Optional[dict[str, Any]] = None


class ChatResponse(BaseModel):
    reply: str


class ReportResponse(BaseModel):
    id: int
    submitted_at: str
    fields: dict[str, Any]
    reply: str


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    messages = [m.model_dump() for m in request.messages]
    reply = ask(messages)
    if request.report_fields is not None:
        save_report(request.report_fields, reply)
    return ChatResponse(reply=reply)


@app.get("/api/reports", response_model=list[ReportResponse])
def get_reports() -> list[dict[str, Any]]:
    return list_reports()


if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
