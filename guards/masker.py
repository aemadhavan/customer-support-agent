"""
A2A Data Masker Service.
Satisfies SPEC §5.6, K-1, K-2, K-3, and TECHNICAL §4 Stage 8.
"""

import os
import re
from typing import Dict, Any, List
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="A2A Data Masker", version="1.0.0")

# Regex patterns for strict PII redaction without altering other words or casing (SPEC K-2)
PHONE_PATTERN = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

def mask_pii(text: str, user_email: str = "") -> Dict[str, Any]:
    """
    Redacts phone numbers, card sequences, and third-party emails while preserving
    the authenticated user's own email, casing, and whitespace (SPEC K-2, Option A).
    """
    if not text:
        return {"masked_text": "", "changes_count": 0, "detail": "nothing to mask"}
        
    changes = []
    
    # 1. Phone numbers
    def phone_repl(match):
        changes.append("phone number")
        return "[REDACTED_PHONE]"
    masked = PHONE_PATTERN.sub(phone_repl, text)
    
    # 2. Card numbers
    def card_repl(match):
        changes.append("card number")
        return "[REDACTED_CARD]"
    masked = CARD_PATTERN.sub(card_repl, masked)
    
    # 3. Third-party emails (excluding user's own email)
    def email_repl(match):
        email_str = match.group(0)
        if user_email and email_str.lower() == user_email.lower():
            return email_str
        changes.append("email address")
        return "[REDACTED_EMAIL]"
    masked = EMAIL_PATTERN.sub(email_repl, masked)
    
    count = len(changes)
    if count == 0:
        detail = "nothing to mask"
    else:
        detail = f"masked {count} item{'s' if count > 1 else ''} ({', '.join(set(changes))})"
        
    return {
        "masked_text": masked,
        "changes_count": count,
        "detail": detail
    }

# Agent card discovery (SPEC K-1)
@app.get("/.well-known/agent.json")
@app.get("/agent.json")
async def get_agent_card():
    return {
        "name": "data_masker",
        "description": "A2A Data Masker for PII redaction (phone, credit card, third-party emails).",
        "version": "1.0.0",
        "methods": ["tasks/send", "message/send"],
        "endpoints": {"rpc": "http://127.0.0.1:10003/rpc"}
    }

@app.post("/rpc")
@app.post("/")
async def json_rpc_handler(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
        
    method = body.get("method")
    params = body.get("params", {})
    req_id = body.get("id")
    
    if method not in ["tasks/send", "message/send"]:
        return JSONResponse({"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Method {method} not found"}, "id": req_id})
        
    text = ""
    user_email = ""
    if isinstance(params, str):
        text = params
    elif isinstance(params, dict):
        user_email = params.get("user_email", "")
        if "text" in params:
            text = params["text"]
        elif "message" in params:
            msg = params["message"]
            if isinstance(msg, str):
                text = msg
            elif isinstance(msg, dict) and "parts" in msg:
                text = "".join(p.get("text", "") for p in msg["parts"])
                
    result = mask_pii(text, user_email=user_email)
    return {"jsonrpc": "2.0", "result": result, "id": req_id}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=10003, log_level="warning")
