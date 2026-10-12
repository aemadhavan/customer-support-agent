"""
In-Process Scope Guardrail Agent for Customer Support Pipeline.
Satisfies SPEC §5.5, GR-1, GR-2, GR-3, GR-4, and TECHNICAL §4 Stage 7.
"""

import os
import re
import json
import warnings
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

load_dotenv()
if os.getenv("GEMINI_API_KEY"):
    os.environ.pop("GOOGLE_API_KEY", None)
elif os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ.pop("GOOGLE_API_KEY")

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Domain-specific calibrated prompt (SPEC GR-2, §11 R-6)
GUARDRAIL_INSTRUCTION = """You are a Scope Guardrail for an online retail shop's customer support desk.
Your sole responsibility is to decide whether a customer message is ON-TOPIC and SAFE for our support assistant.

ON-TOPIC topics include:
- Inquiries about orders, shipments, delivery status, items, tracking, or order numbers.
- Order changes, cancellations, returns, replacements, refunds, or damaged goods.
- Delivery instructions and customer preferences (e.g., leaving packages at back door, delivery time preferences, contact preferences, building elevator constraints, or packaging restrictions like peanut allergies).
- Greetings, closing remarks ("thanks, that's all"), conversational corrections ("ignore my last message, I meant order 4"), and general support inquiries.

OFF-TOPIC topics (mark as "unsafe"):
- Creative writing (poems, songs, fictional stories, essays).
- Politics, elections, governmental topics, or public figures.
- Homework help, math solving (e.g., "Solve 3x + 5 = 20"), programming/coding questions.
- Cooking recipes, general knowledge trivia, sports forecasts, movie/book summaries, or philosophical questions ("meaning of life").
- Inquiries completely unrelated to the shop, products, orders, or delivery services.

You must output ONLY a valid JSON object with exactly two keys:
{
  "decision": "safe" | "unsafe",
  "reasoning": "A concise explanation of why the message is within or outside the shop's scope."
}

Do not include markdown fences, comments, or any extra text.
"""

def create_guardrail_agent() -> LlmAgent:
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    return LlmAgent(
        name="guardrail_agent",
        model=model,
        instruction=GUARDRAIL_INSTRUCTION
    )

async def check_scope(text: str) -> Tuple[bool, str]:
    """
    Evaluates message scope using an in-process ADK agent with a fresh session per check (GR-3).
    Returns (is_safe, reasoning).
    Raises ValueError on unparseable decisions (SPEC GR-4, Fail Loud).
    """
    agent = create_guardrail_agent()
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="guardrail")
    
    # Fresh session per check (SPEC GR-3)
    session = await session_service.create_session(app_name="guardrail", user_id="system")
    
    prompt = f"Analyze this message: {text}\nRespond with JSON: {{\"decision\": \"safe\"|\"unsafe\", \"reasoning\": \"...\"}}"
    content = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    
    reply_text = ""
    for attempt in range(3):
        try:
            async for event in runner.run_async(user_id="system", session_id=session.id, new_message=content):
                if event.is_final_response() and event.content:
                    for p in event.content.parts:
                        if p.text:
                            reply_text += p.text
            break
        except Exception as e:
            if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower()) and attempt < 2:
                import asyncio
                await asyncio.sleep(35.0)
                continue
            raise
        finally:
            if attempt == 2 or reply_text:
                # Delete session immediately so one verdict cannot influence subsequent checks (GR-3)
                await session_service.delete_session(app_name="guardrail", user_id="system", session_id=session.id)
        
    if not reply_text:
        raise ValueError("Guardrail agent produced empty output")
        
    clean_json = re.sub(r"^```json\s*|\s*```$", "", reply_text.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(clean_json)
    except Exception as e:
        raise ValueError(f"Unparseable guardrail decision JSON: '{reply_text}'") from e
        
    decision = data.get("decision", "").lower().strip()
    reasoning = data.get("reasoning", "Scope check complete")
    
    if decision == "safe":
        return True, reasoning
    elif decision == "unsafe":
        return False, reasoning
    else:
        # Fail loud on invalid decision enum (SPEC GR-4)
        raise ValueError(f"Invalid guardrail decision value: '{decision}' (expected 'safe' or 'unsafe')")
