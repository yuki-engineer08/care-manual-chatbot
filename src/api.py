import os
from pathlib import Path

from typing import Any, Optional

from fastapi import Cookie, Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from auth import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS,
    create_session_token,
    logout_session,
    require_auth,
    verify_password,
)
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


class LoginRequest(BaseModel):
    password: str


@app.post("/api/login")
def login(request: LoginRequest, response: Response) -> dict[str, bool]:
    if not verify_password(request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    token = create_session_token()
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
    )
    return {"ok": True}


@app.post("/api/logout")
def logout(response: Response, staff_session: str | None = Cookie(default=None)) -> dict[str, bool]:
    if staff_session:
        logout_session(staff_session)
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    return {"ok": True}


@app.get("/api/session", dependencies=[Depends(require_auth)])
def session_check() -> dict[str, bool]:
    return {"authenticated": True}


@app.post("/api/chat", response_model=ChatResponse, dependencies=[Depends(require_auth)])
def chat(request: ChatRequest) -> ChatResponse:
    messages = [m.model_dump() for m in request.messages]
    reply = ask(messages)
    if request.report_fields is not None:
        save_report(request.report_fields, reply)
    return ChatResponse(reply=reply)


@app.get("/api/reports", response_model=list[ReportResponse], dependencies=[Depends(require_auth)])
def get_reports() -> list[dict[str, Any]]:
    return list_reports()


if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
