# CLAUDE.md — Prompt-Injection Firewall (NANDAHack submission)

## What we're building
A stateless HTTP microservice that other AI agents call to check untrusted text
for prompt-injection **before acting on it**. This is a NANDAHack (HCLTech × MIT
Media Lab) Phase 2 submission. The only "user" of the service is another AI
agent — no human in the loop. It directly answers NANDA's core mission of agents
coordinating "without creating security vulnerabilities."

## Deadlines (US Eastern)
- **Fri Jul 10, 12:00 noon** — initial submission of both phases (HARD wall). Phase 1 PRs final here.
- **Sat Jul 11, 2:00 PM** — Phase 2 edits lock + video demo due.
Priority: get a live, deployed, submittable version done first; polish after.

## Definition of done
1. FastAPI service with two endpoints: `POST /scan` and `GET /health`.
2. Deployed live on Render with a public URL that responds.
3. `SKILL.md`'s Base URL updated to the live URL.
4. A stock agent can read `SKILL.md` and use `/scan` with zero human help.

## Files
- `rules.py` — **already written. This is the detection engine; do not rewrite it, only extend.**
  Exposes `scan(text) -> ScanResult`; call `.to_dict()` for the JSON response.
  Layer 0 (de-obfuscation) + Layer 1 (heuristic rules) + scoring/verdict.
- `app.py` — you write this: FastAPI wrapper around `scan()`.
- `SKILL.md` — the agent-facing instructions (already drafted; update Base URL).
- `requirements.txt` — you write this: `fastapi`, `uvicorn[standard]`, (`httpx` if Layer 2 added).
- `tests/` — a few known attack + benign strings asserting the right verdict.

## Endpoint contract
`POST /scan`, Content-Type application/json
Request: `{ "content": "<untrusted text>", "context": "<optional>" }`
Response: `{ "verdict": "allow"|"flag"|"block", "risk_score": 0.0-1.0, "detections": [...], "recommendation": "..." }`
`GET /health` → `{ "status": "ok" }`

Reference wiring for app.py:
```python
from fastapi import FastAPI
from pydantic import BaseModel
from rules import scan

app = FastAPI()

class ScanRequest(BaseModel):
    content: str
    context: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/scan")
def scan_endpoint(req: ScanRequest):
    return scan(req.content).to_dict()
```

## Standards
- Python 3.11, type hints, keep it minimal and readable.
- No secrets in the repo. Any API key (for the optional Layer 2 judge) lives in
  an env var (e.g. `LLM_API_KEY`) — never in `SKILL.md` or git.

## Build order (time-boxed)
1. Scaffold `app.py` + `requirements.txt`. Run locally: `uvicorn app:app --reload`. Test `/scan` with curl.
2. **Deploy to Render early** (free web service). Confirm the public URL works. A dead URL = zero score.
3. Put the live URL into `SKILL.md`. Commit + push.
4. (Optional Phase 1, worth 20%, also due noon Jul 10) Small tested PR to the nandatown repo.
5. Phase 2 polish (until Sat 2pm): add Layer 2 LLM judge — call it ONLY when `risk_score` is
   between `FLAG_THRESHOLD` and `BLOCK_THRESHOLD` (ambiguous band). Wrap the untrusted text in a
   clearly delimited block and ask the judge only to classify, so the judge itself can't be injected.
   Tune thresholds against sample attacks + benign text. Record the demo video.

## Render deploy notes
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

## Demo (for the required video)
Show a stock agent about to act on a booby-trapped web page → it calls `/scan`
first → gets `block` with the caught injection → refuses to obey. Contrast with
what happens without the firewall.
