"""
Support Agent Definition for Assignment 4: Customer Support.
Satisfies SPEC M-3, M-5, and SPEC §5.2.
"""

import os
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

load_dotenv()
if os.getenv("GEMINI_API_KEY"):
    os.environ.pop("GOOGLE_API_KEY", None)
elif os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ.pop("GOOGLE_API_KEY")

from typing import Tuple, List, Any
from google.adk.agents import LlmAgent
from toolbox_core import ToolboxSyncClient
from support.telemetry import init_telemetry

# Ensure TracerProvider and instrumentation are global before building agents (TECHNICAL §4 Stage 5)
init_telemetry()

# System instructions detailing domain, tool grounding, and boundaries
SUPPORT_AGENT_INSTRUCTION = """You are a helpful and courteous customer support assistant for our online shop.

Core Operating Rules:
1. Always ground your answers about orders strictly in data retrieved from your database tools.
2. Never fabricate, assume, or hallucinate order numbers, products, tracking details, or order dates.
3. If an order lookup returns no results or an empty list, clearly state that the order was not found on the customer's account.
4. You cannot look up or access orders belonging to other accounts.
5. If the customer requests an order cancellation or return, use the action-log tool to record the action with the appropriate action type.
6. Keep your answers concise, accurate, and professional.
7. If customer preferences or memories are provided, respect them, but always trust database tools over memories for order facts.
"""

def create_support_agent(
    user_email: str,
    toolbox_url: str = "http://127.0.0.1:5000",
    model: str = None
) -> Tuple[LlmAgent, List[Any]]:
    """
    Creates an ADK LlmAgent with MCP tools bound to the authenticated user's session email.
    SPEC M-5: The email the tools receive comes from the session, not the model.
    """
    if model is None:
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    client = ToolboxSyncClient(url=toolbox_url)
    
    # Bind user's email so the model cannot supply or tamper with it
    bound_params = {
        "customer_email": user_email,
        "user_email": user_email
    }
    
    tools = client.load_toolset("customer-support-tools", bound_params=bound_params)
    
    agent = LlmAgent(
        name="support_agent",
        model=model,
        instruction=SUPPORT_AGENT_INSTRUCTION,
        tools=tools
    )
    
    return agent, tools
