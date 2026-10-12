"""
CLI Interface for Customer Support Pipeline.
Satisfies SPEC §7.1, §7.2, C-1, C-2, C-3, and TECHNICAL Stage 4.
"""

import os
import sys
import json
import argparse
import asyncio
import warnings
from getpass import getpass

warnings.filterwarnings("ignore")

from dotenv import load_dotenv

load_dotenv()
if os.getenv("GEMINI_API_KEY"):
    os.environ.pop("GOOGLE_API_KEY", None)
elif os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ.pop("GOOGLE_API_KEY")

from support.db import authenticate_user
from support.pipeline import run_pipeline_turn

def render_event_badge(ev: dict):
    """Renders events using the Option A Icon + Badge style."""
    ev_type = ev.get("type")
    if ev_type == "trace":
        print(f"[🔍] trace: {ev.get('trace_id')} ({ev.get('url')})")
    elif ev_type == "stage":
        print(f"[▶] stage: {ev.get('label')}")
    elif ev_type == "llm":
        decision = ev.get("decision", "")
        tin = ev.get("tokens_in", 0)
        tout = ev.get("tokens_out", 0)
        ms = ev.get("ms", 0)
        print(f"[🤖] llm: {ev.get('model')} -> {decision} ({tin} in / {tout} out, {ms}ms)")
    elif ev_type == "tool_call":
        args_str = json.dumps(ev.get("args", {}))
        print(f"[⚡] tool_call #{ev.get('id')}: {ev.get('name')}({args_str})")
    elif ev_type == "tool_result":
        res_str = json.dumps(ev.get("result"))
        if len(res_str) > 120:
            res_str = res_str[:117] + "..."
        print(f"[📥] tool_result #{ev.get('id')}: {ev.get('name')} -> {res_str} ({ev.get('ms')}ms)")
    elif ev_type == "step":
        status = ev.get("status")
        icon = "[✓]" if status == "passed" else "[🛑]"
        print(f"{icon} step: {ev.get('key')} -> {status} ({ev.get('detail')}, {ev.get('ms')}ms)")
        if ev.get("memories"):
            for m in ev.get("memories", []):
                mark = "[+]" if m.get("inserted") else "[-]"
                print(f"      {mark} memory ({m.get('score')}): {m.get('memory')} ({m.get('reason') or 'inserted'})")
    elif ev_type == "final":
        print(f"\nSupport:\n{ev.get('response')}\n")
    elif ev_type == "error":
        print(f"[❌] error: {ev.get('step')} ({ev.get('error')})")

async def process_turn(user_email: str, message: str, raw_events: bool):
    """Processes a single user message through the pipeline."""
    async for ev in run_pipeline_turn(user_email=user_email, message=message):
        if raw_events:
            print(json.dumps(ev), flush=True)
        else:
            render_event_badge(ev)

async def interactive_session(user_email: str, raw_events: bool):
    """Interactive loop for CLI."""
    if not raw_events:
        print(f"\n--- Logged in as: {user_email} ---")
        print("Type your message, or 'exit' / 'quit' to end.\n")
    
    while True:
        try:
            if not raw_events:
                print("You: ", end="", flush=True)
            line = sys.stdin.readline()
            if not line:
                break
            user_input = line.strip()
        except (EOFError, KeyboardInterrupt):
            break
            
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit"]:
            if not raw_events:
                print("Session ended.")
            break
            
        await process_turn(user_email, user_input, raw_events)

def main():
    parser = argparse.ArgumentParser(description="Customer Support Agent Pipeline CLI")
    parser.add_argument("--user", help="User email to authenticate as")
    parser.add_argument("--password", help="Password for user (demo)")
    parser.add_argument("--events", action="store_true", help="Emit raw NDJSON stream only")
    args = parser.parse_args()
    
    user_email = args.user
    user_pass = args.password
    
    if not user_email:
        user_email = input("Email: ").strip()
        user_pass = getpass("Password: ").strip()
        
    # In --events mode with piped input or demo, allow known default passwords if not supplied
    if not user_pass and user_email:
        user_pass = user_email.split(".")[0]
        
    if not authenticate_user(user_email, user_pass):
        print(f"Authentication failed for user: {user_email}", file=sys.stderr)
        sys.exit(1)
        
    asyncio.run(interactive_session(user_email, args.events))

if __name__ == "__main__":
    main()
