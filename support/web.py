"""
FastAPI Web Server for Customer Support Agent.
Satisfies SPEC §7.2, W-1, W-2, and TECHNICAL §4 Stage 9.
"""

import os
import json
import httpx
import uvicorn
from typing import Dict, Any
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from support.db import authenticate_user, get_user_info, get_db_connection
from support.pipeline import run_pipeline_turn
from support.memory import get_memory_client

app = FastAPI(title="Customer Support Agent Web API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active session management: user_id -> user_data
active_sessions: Dict[str, Dict[str, Any]] = {}
logged_out_users: set = set()

class LoginRequest(BaseModel):
    email: str
    password: str

class LogoutRequest(BaseModel):
    user_id: str

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/api/login")
async def login(req: LoginRequest):
    """
    POST /api/login body: { "email": "…", "password": "…" }
    -> 200 { "user_id": "alice.jones@example.com", "full_name": "Alice Jones", "is_premium": false }
    -> 401 { "error": "Invalid email or password." }
    """
    if not authenticate_user(req.email, req.password):
        return JSONResponse(status_code=401, content={"error": "Invalid email or password."})
    
    info = get_user_info(req.email)
    if not info:
        return JSONResponse(status_code=401, content={"error": "Invalid email or password."})
    
    logged_out_users.discard(req.email)
    active_sessions[req.email] = info
    return JSONResponse(status_code=200, content=info)

@app.post("/api/logout")
async def logout(req: LogoutRequest):
    """
    POST /api/logout body: { "user_id": "…" } -> 200 { "ok": true }
    """
    active_sessions.pop(req.user_id, None)
    logged_out_users.add(req.user_id)
    return JSONResponse(status_code=200, content={"ok": True})

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    POST /api/chat body: { "user_id": "…", "message": "…" }
    -> 200 application/x-ndjson (the §7.1 stream)
    -> 400 { "error": "message is empty" }
    -> 401 { "error": "Not logged in." }
    -> 413 { "error": "message too long" }
    """
    msg = req.message
    if not msg or not msg.strip():
        return JSONResponse(status_code=400, content={"error": "message is empty"})
    
    if len(msg) > 1000:
        return JSONResponse(status_code=413, content={"error": "message too long"})
    
    # Check session: if explicitly logged out, reject with 401
    if req.user_id in logged_out_users:
        return JSONResponse(status_code=401, content={"error": "Not logged in."})
        
    # Check session: active or valid registered user
    if req.user_id not in active_sessions:
        info = get_user_info(req.user_id)
        if not info:
            return JSONResponse(status_code=401, content={"error": "Not logged in."})
        active_sessions[req.user_id] = info

    async def stream_events():
        async for ev in run_pipeline_turn(user_email=req.user_id, message=msg):
            yield json.dumps(ev) + "\n"

    return StreamingResponse(
        stream_events(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/health")
async def health():
    """
    GET /health -> 200 { "status": "ok", "model": "gemini-3.5-flash-lite", "db": "ok", ... }
    -> 503 same shape, with failing dependency's value set to its error string
    """
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    results = {
        "status": "ok",
        "model": model_name,
        "db": "ok",
        "toolbox": "ok",
        "judge": "ok",
        "masker": "ok",
        "mem0": "ok",
        "phoenix": "ok"
    }
    is_healthy = True

    # 1. DB Check
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        conn.close()
    except Exception as e:
        results["db"] = str(e)
        is_healthy = False

    # 2. Toolbox Check (:5000)
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get("http://127.0.0.1:5000/")
            if resp.status_code != 200:
                results["toolbox"] = f"HTTP {resp.status_code}"
                is_healthy = False
    except Exception as e:
        results["toolbox"] = str(e)
        is_healthy = False

    # 3. Judge Check (:10002)
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get("http://127.0.0.1:10002/.well-known/agent.json")
            if resp.status_code != 200:
                results["judge"] = f"HTTP {resp.status_code}"
                is_healthy = False
    except Exception as e:
        results["judge"] = str(e)
        is_healthy = False

    # 4. Masker Check (:10003)
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get("http://127.0.0.1:10003/.well-known/agent.json")
            if resp.status_code != 200:
                results["masker"] = f"HTTP {resp.status_code}"
                is_healthy = False
    except Exception as e:
        results["masker"] = str(e)
        is_healthy = False

    # 5. Mem0 Check
    try:
        get_memory_client()
    except Exception as e:
        results["mem0"] = str(e)
        is_healthy = False

    # 6. Phoenix Check (:6006)
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get("http://127.0.0.1:6006/")
            if resp.status_code not in [200, 302, 307]:
                results["phoenix"] = f"HTTP {resp.status_code}"
                is_healthy = False
    except Exception as e:
        results["phoenix"] = str(e)
        is_healthy = False

    status_code = 200 if is_healthy else 503
    if not is_healthy:
        results["status"] = "error"

    return JSONResponse(status_code=status_code, content=results)

@app.get("/")
async def root():
    """Serves the single page dashboard UI."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "web", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return JSONResponse({"status": "ok", "message": "Customer Support Web Server is running."})

if __name__ == "__main__":
    uvicorn.run("support.web:app", host="127.0.0.1", port=8000, reload=False, log_level="warning")
