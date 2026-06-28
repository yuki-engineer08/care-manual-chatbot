import os
from pathlib import Path

from typing import Any, Literal, Optional

from fastapi import FastAPI, HTTPException
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


FacilityType = Literal[
    "グループホーム",
    "特別養護老人ホーム",
    "介護老人保健施設",
    "デイサービス",
    "自宅",
]

FallRisk = Literal["小", "中", "高"]


class ChatRequest(BaseModel):
    messages: list[Message]
    report_fields: Optional[dict[str, Any]] = None
    facility_type: Optional[FacilityType] = None
    fall_risk: Optional[FallRisk] = None


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
    reply = ask(messages, facility_type=request.facility_type, fall_risk=request.fall_risk)
    if request.report_fields is not None:
        save_report(request.report_fields, reply)
    return ChatResponse(reply=reply)


@app.get("/api/reports", response_model=list[ReportResponse])
def get_reports() -> list[dict[str, Any]]:
    return list_reports()


@app.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
def api_not_found(path: str) -> None:
    raise HTTPException(status_code=404, detail="Not Found")


if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
