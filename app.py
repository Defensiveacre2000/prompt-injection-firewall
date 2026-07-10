"""
app.py -- FastAPI wrapper around the rules.py detection engine.

Exposes POST /scan and GET /health per SKILL.md's contract.
"""

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from rules import scan

app = FastAPI(title="Prompt-Injection Firewall")


class ScanRequest(BaseModel):
    content: str
    context: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scan")
def scan_endpoint(req: ScanRequest):
    return scan(req.content).to_dict()
