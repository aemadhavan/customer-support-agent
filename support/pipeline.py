"""
Pipeline Module for Customer Support Agent.
Satisfies SPEC §7.1, §7.3, P-1–P-4, S-1, S-2, J-1–J-4, O-1–O-4, and EVALS §4.1.
"""

import os
import time
import json
import uuid
import httpx
import warnings
from typing import AsyncGenerator, Dict, Any, List

warnings.filterwarnings("ignore")

if os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
    os.environ.pop("GOOGLE_API_KEY", None)

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from openinference.semconv.trace import OpenInferenceSpanKindValues, SpanAttributes
from opentelemetry.trace import StatusCode

from support.agent import create_support_agent
from support.telemetry import get_tracer, format_trace_url
from guards.sanitizer import sanitize_input
from guards.guardrail import check_scope
from support.memory import recall_memories, save_memory

TOOL_INFO_MAP = {
    "get-order-status": {
        "kind": "MCP",
        "access": "READ",
        "statement": "SELECT order_id, customer_email, delivery_address, status, items, order_date, total_amount FROM customer_orders WHERE order_id = $1 AND customer_email = $2;",
        "params": ["order_id", "customer_email"]
    },
    "find-customer-orders": {
        "kind": "MCP",
        "access": "READ",
        "statement": "SELECT order_id, customer_email, delivery_address, status, items, order_date, total_amount FROM customer_orders WHERE customer_email = $1 ORDER BY order_date DESC;",
        "params": ["customer_email"]
    },
    "action-log": {
        "kind": "MCP",
        "access": "WRITE",
        "statement": "INSERT INTO actions_log (user_email, action_type, parameters) VALUES ($1, $2, $3::jsonb) RETURNING id, timestamp, user_email, action_type, parameters;",
        "params": ["user_email", "action_type", "parameters"]
    }
}

def unwrap_tool_result(raw_response: Any) -> Any:
    """Unwraps MCP Toolbox {'result': '<JSON string>'} and parses inner JSON."""
    if isinstance(raw_response, dict) and "result" in raw_response:
        val = raw_response["result"]
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return val
        return val
    return raw_response

def decode_tool_args(args: Dict[str, Any]) -> Dict[str, Any]:
    """Decodes JSON-string arguments if passed as serialized strings."""
    decoded = {}
    for k, v in args.items():
        if isinstance(v, str):
            try:
                decoded[k] = json.loads(v)
            except Exception:
                decoded[k] = v
        else:
            decoded[k] = v
    return decoded

def write_run_log(record: Dict[str, Any], is_failing: bool = False):
    """Writes turn record to runs/<turn_id>.json or runs/failing/<turn_id>.json."""
    folder = os.path.join("runs", "failing") if is_failing else "runs"
    os.makedirs(folder, exist_ok=True)
    turn_id = record.get("turn_id", "unknown")
    with open(os.path.join(folder, f"{turn_id}.json"), "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

async def run_pipeline_turn(
    user_email: str,
    message: str,
    session_id: str = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Executes a turn through the support pipeline, yielding typed events (SPEC §7.1).
    Step order: sanitize -> judge -> agent (SPEC P-2).
    Opens root span 'agent.turn' in Phoenix and writes runs/<turn_id>.json upon completion.
    """
    start_time = time.time()
    turn_id = f"turn_{uuid.uuid4().hex[:16]}"
    
    tracer = get_tracer()
    
    # Open root span agent.turn (OpenInference kind CHAIN)
    with tracer.start_as_current_span("agent.turn") as root_span:
        root_span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.CHAIN.value)
        root_span.set_attribute(SpanAttributes.USER_ID, user_email)
        root_span.set_attribute("turn.id", turn_id)
        root_span.set_attribute("input.value", message)
        
        trace_id = format(root_span.get_span_context().trace_id, "032x")
        phoenix_url = format_trace_url(trace_id)
        
        # 1. First event must always be trace with real trace_id and URL (SPEC §7.3 rule 1, O-4)
        yield {
            "type": "trace",
            "turn_id": turn_id,
            "trace_id": trace_id,
            "url": phoenix_url
        }
        
        steps_log: List[Dict[str, Any]] = []
        tool_calls_log: List[Dict[str, Any]] = []
        llm_calls_count = 0
        total_tokens_in = 0
        total_tokens_out = 0
        
        # -------------------------------------------------------------
        # 2. SANITIZER STEP (In-process, SPEC §5.4, S-1, S-2)
        # -------------------------------------------------------------
        yield {
            "type": "stage",
            "key": "sanitize",
            "label": "Input Sanitizer"
        }
        
        san_start = time.time()
        with tracer.start_as_current_span("security.sanitize") as san_span:
            san_span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.GUARDRAIL.value)
            san_ok, san_detail = sanitize_input(message)
            san_ms = max(1, int((time.time() - san_start) * 1000))
            
            if not san_ok:
                san_span.set_status(StatusCode.ERROR, san_detail)
                steps_log.append({"key": "sanitize", "status": "blocked", "ms": san_ms})
                yield {
                    "type": "step",
                    "key": "sanitize",
                    "status": "blocked",
                    "detail": san_detail,
                    "ms": san_ms,
                    "span": "security.sanitize",
                    "kind": "Python fn"
                }
                
                wall_ms = int((time.time() - start_time) * 1000)
                root_span.set_attribute(SpanAttributes.OUTPUT_VALUE, san_detail)
                write_run_log({
                    "turn_id": turn_id,
                    "trace_id": trace_id,
                    "user": user_email,
                    "message": message,
                    "terminated": "blocked",
                    "blocked_at": "sanitize",
                    "wall_clock_ms": wall_ms,
                    "tokens": {"in": 0, "out": 0},
                    "steps": steps_log,
                    "tool_calls": [],
                    "llm_calls": 0
                })
                yield {
                    "type": "final",
                    "blocked": True,
                    "blocked_at": "sanitize",
                    "response": f"Request blocked: {san_detail}",
                    "terminated": "blocked",
                    "wall_clock_ms": wall_ms,
                    "tokens": {"in": 0, "out": 0}
                }
                return

            steps_log.append({"key": "sanitize", "status": "passed", "ms": san_ms})
            yield {
                "type": "step",
                "key": "sanitize",
                "status": "passed",
                "detail": san_detail,
                "ms": san_ms,
                "span": "security.sanitize",
                "kind": "Python fn"
            }

        # -------------------------------------------------------------
        # 3. A2A SECURITY JUDGE STEP (SPEC §5.3, J-1–J-4)
        # -------------------------------------------------------------
        yield {
            "type": "stage",
            "key": "judge",
            "label": "A2A Security Judge"
        }
        
        judge_start = time.time()
        with tracer.start_as_current_span("security.a2a_judge") as judge_span:
            judge_span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.GUARDRAIL.value)
            
            judge_res = None
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        "http://127.0.0.1:10002/rpc",
                        json={
                            "jsonrpc": "2.0",
                            "method": "tasks/send",
                            "params": {"text": message},
                            "id": 1
                        }
                    )
                    if resp.status_code != 200:
                        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
                    rpc_data = resp.json()
                    judge_res = rpc_data.get("result", {})
                    if not isinstance(judge_res, dict) or "verdict" not in judge_res:
                        raise ValueError(f"Unparseable verdict response: {rpc_data}")
            except Exception as e:
                # Fail loud (SPEC §11 R-4, P-4): Unreachable or unparseable Judge terminates turn with 502 error
                judge_span.set_status(StatusCode.ERROR, str(e))
                judge_span.record_exception(e)
                judge_ms = int((time.time() - judge_start) * 1000)
                err_msg = f"Security Judge unreachable: {e}"
                
                wall_ms = int((time.time() - start_time) * 1000)
                write_run_log({
                    "turn_id": turn_id,
                    "trace_id": trace_id,
                    "user": user_email,
                    "message": message,
                    "terminated": "error",
                    "blocked_at": None,
                    "wall_clock_ms": wall_ms,
                    "tokens": {"in": 0, "out": 0},
                    "steps": steps_log,
                    "tool_calls": [],
                    "llm_calls": 0,
                    "error": err_msg
                }, is_failing=True)
                
                yield {
                    "type": "error",
                    "step": "judge",
                    "status": 502,
                    "error": err_msg,
                    "terminated": "error"
                }
                return

            judge_ms = int((time.time() - judge_start) * 1000)
            verdict = judge_res.get("verdict", "block").lower()
            reason = judge_res.get("reason", "Security evaluation")
            
            if verdict == "block":
                judge_span.set_status(StatusCode.ERROR, reason)
                steps_log.append({"key": "judge", "status": "blocked", "ms": judge_ms})
                yield {
                    "type": "step",
                    "key": "judge",
                    "status": "blocked",
                    "detail": f"block: {reason}",
                    "ms": judge_ms,
                    "span": "security.a2a_judge",
                    "kind": "A2A"
                }
                
                wall_ms = int((time.time() - start_time) * 1000)
                root_span.set_attribute(SpanAttributes.OUTPUT_VALUE, reason)
                write_run_log({
                    "turn_id": turn_id,
                    "trace_id": trace_id,
                    "user": user_email,
                    "message": message,
                    "terminated": "blocked",
                    "blocked_at": "judge",
                    "wall_clock_ms": wall_ms,
                    "tokens": {"in": 0, "out": 0},
                    "steps": steps_log,
                    "tool_calls": [],
                    "llm_calls": 0
                })
                yield {
                    "type": "final",
                    "blocked": True,
                    "blocked_at": "judge",
                    "response": f"I cannot process this request due to security restrictions ({reason}).",
                    "terminated": "blocked",
                    "wall_clock_ms": wall_ms,
                    "tokens": {"in": 0, "out": 0}
                }
                return

            steps_log.append({"key": "judge", "status": "passed", "ms": judge_ms})
            yield {
                "type": "step",
                "key": "judge",
                "status": "passed",
                "detail": f"allow: {reason}",
                "ms": judge_ms,
                "span": "security.a2a_judge",
                "kind": "A2A"
            }

        # -------------------------------------------------------------
        # 4. SCOPE GUARDRAIL STEP (In-process, SPEC §5.5, GR-1–GR-4)
        # -------------------------------------------------------------
        yield {
            "type": "stage",
            "key": "guardrail",
            "label": "Scope Guardrail"
        }
        
        gr_start = time.time()
        with tracer.start_as_current_span("guardrail.check") as gr_span:
            gr_span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.GUARDRAIL.value)
            
            try:
                is_safe, gr_reason = await check_scope(message)
            except Exception as e:
                # Fail loud (SPEC §11 R-4, GR-4): unparseable decision is an error
                gr_span.set_status(StatusCode.ERROR, str(e))
                gr_span.record_exception(e)
                gr_ms = int((time.time() - gr_start) * 1000)
                err_msg = f"Guardrail error: {e}"
                
                wall_ms = int((time.time() - start_time) * 1000)
                write_run_log({
                    "turn_id": turn_id,
                    "trace_id": trace_id,
                    "user": user_email,
                    "message": message,
                    "terminated": "error",
                    "blocked_at": None,
                    "wall_clock_ms": wall_ms,
                    "tokens": {"in": 0, "out": 0},
                    "steps": steps_log,
                    "tool_calls": [],
                    "llm_calls": 0,
                    "error": err_msg
                }, is_failing=True)
                
                yield {
                    "type": "error",
                    "step": "guardrail",
                    "status": 502,
                    "error": err_msg,
                    "terminated": "error"
                }
                return

            gr_ms = int((time.time() - gr_start) * 1000)
            if not is_safe:
                gr_span.set_status(StatusCode.ERROR, gr_reason)
                steps_log.append({"key": "guardrail", "status": "blocked", "ms": gr_ms})
                yield {
                    "type": "step",
                    "key": "guardrail",
                    "status": "blocked",
                    "detail": f"blocked: {gr_reason}",
                    "ms": gr_ms,
                    "span": "guardrail.check",
                    "kind": "in-process"
                }
                
                wall_ms = int((time.time() - start_time) * 1000)
                root_span.set_attribute(SpanAttributes.OUTPUT_VALUE, gr_reason)
                write_run_log({
                    "turn_id": turn_id,
                    "trace_id": trace_id,
                    "user": user_email,
                    "message": message,
                    "terminated": "blocked",
                    "blocked_at": "guardrail",
                    "wall_clock_ms": wall_ms,
                    "tokens": {"in": 0, "out": 0},
                    "steps": steps_log,
                    "tool_calls": [],
                    "llm_calls": 0
                })
                yield {
                    "type": "final",
                    "blocked": True,
                    "blocked_at": "guardrail",
                    "response": "I am only able to assist with orders, deliveries, products, and customer account support for our shop. Is there an order or delivery I can help you with?",
                    "terminated": "blocked",
                    "wall_clock_ms": wall_ms,
                    "tokens": {"in": 0, "out": 0}
                }
                return

            steps_log.append({"key": "guardrail", "status": "passed", "ms": gr_ms})
            yield {
                "type": "step",
                "key": "guardrail",
                "status": "passed",
                "detail": f"safe: {gr_reason}",
                "ms": gr_ms,
                "span": "guardrail.check",
                "kind": "in-process"
            }

        # -------------------------------------------------------------
        # 5. MEMORY RECALL STEP (Mem0, SPEC §5.7, R-1–R-3, R-5)
        # -------------------------------------------------------------
        yield {
            "type": "stage",
            "key": "recall",
            "label": "Mem0 Memory Recall"
        }
        
        recall_start = time.time()
        candidates = []
        memory_block = ""
        with tracer.start_as_current_span("memory.recall") as recall_span:
            recall_span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.RETRIEVER.value)
            
            try:
                candidates, memory_block = recall_memories(user_email=user_email, message=message)
            except Exception as e:
                recall_span.record_exception(e)
                candidates = []
                memory_block = ""
                
            for idx, cand in enumerate(candidates):
                recall_span.set_attribute(f"retrieval.documents.{idx}.document.content", cand.get("memory", ""))
                recall_span.set_attribute(f"retrieval.documents.{idx}.document.score", float(cand.get("score", 0.0)))
                
            recall_ms = int((time.time() - recall_start) * 1000)
            inserted_count = sum(1 for c in candidates if c.get("inserted"))
            detail = f"recalled {len(candidates)} candidates, inserted {inserted_count}" if candidates else "no memories found"
            
            steps_log.append({"key": "recall", "status": "passed", "ms": recall_ms})
            yield {
                "type": "step",
                "key": "recall",
                "status": "passed",
                "detail": detail,
                "ms": recall_ms,
                "span": "memory.recall",
                "kind": "in-process",
                "memories": candidates
            }

        # -------------------------------------------------------------
        # 6. AGENT STAGE (SPEC §5.2)
        # -------------------------------------------------------------
        stage_start = time.time()
        yield {
            "type": "stage",
            "key": "agent",
            "label": "Customer Support Agent"
        }
        
        agent, _ = create_support_agent(user_email=user_email)
        session_service = InMemorySessionService()
        runner = Runner(agent=agent, session_service=session_service, app_name="customer_support")
        
        active_session_id = session_id or (await session_service.create_session(
            app_name="customer_support", user_id=user_email
        )).id
        root_span.set_attribute("session.id", active_session_id)
        
        if memory_block:
            agent_input_text = f"{memory_block}\n\nCustomer Message: {message}"
        else:
            agent_input_text = message
            
        content = types.Content(role="user", parts=[types.Part.from_text(text=agent_input_text)])
        
        call_id_counter = 0
        active_call_map = {}
        last_llm_start = time.time()
        final_response_text = ""
        
        try:
            # Iterate runner inside agent.turn so ADK and Gemini attach to trace
            async for event in runner.run_async(
                user_id=user_email,
                session_id=active_session_id,
                new_message=content
            ):
                # Check for Function Calls
                fcalls = event.get_function_calls()
                if fcalls:
                    llm_calls_count += 1
                    usage = getattr(event, "usage_metadata", None)
                    tokens_in = getattr(usage, "prompt_token_count", 0) if usage else 0
                    tokens_out = getattr(usage, "candidates_token_count", 0) if usage else 0
                    total_tokens_in += tokens_in
                    total_tokens_out += tokens_out
                    llm_ms = int((time.time() - last_llm_start) * 1000)
                    
                    first_call_name = fcalls[0].name if fcalls else "unknown"
                    yield {
                        "type": "llm",
                        "model": getattr(agent, "model", "gemini-3.5-flash-lite"),
                        "decision": f"call {first_call_name}",
                        "tokens_in": tokens_in,
                        "tokens_out": tokens_out,
                        "ms": llm_ms,
                        "span": "call_llm"
                    }
                    
                    for fc in fcalls:
                        call_id_counter += 1
                        active_call_map[fc.id] = (call_id_counter, fc.name, time.time())
                        decoded_args = decode_tool_args(fc.args or {})
                        info = TOOL_INFO_MAP.get(fc.name, {"kind": "MCP", "access": "READ", "params": list(decoded_args.keys())})
                        
                        yield {
                            "type": "tool_call",
                            "id": call_id_counter,
                            "name": fc.name,
                            "args": decoded_args,
                            "info": info,
                            "span": f"execute_tool {fc.name}"
                        }
                    last_llm_start = time.time()

                # Check for Function Responses
                fresps = event.get_function_responses()
                if fresps:
                    for fr in fresps:
                        call_meta = active_call_map.get(fr.id, (call_id_counter, fr.name, time.time()))
                        num_id, tool_name, call_time = call_meta
                        tool_ms = int((time.time() - call_time) * 1000)
                        unwrapped = unwrap_tool_result(fr.response)
                        
                        tool_calls_log.append({
                            "name": tool_name,
                            "ok": True,
                            "ms": tool_ms
                        })
                        
                        yield {
                            "type": "tool_result",
                            "id": num_id,
                            "name": tool_name,
                            "ok": True,
                            "ms": tool_ms,
                            "result": unwrapped
                        }
                    last_llm_start = time.time()

                # Check for Final Response
                if event.is_final_response():
                    llm_calls_count += 1
                    usage = getattr(event, "usage_metadata", None)
                    tokens_in = getattr(usage, "prompt_token_count", 0) if usage else 0
                    tokens_out = getattr(usage, "candidates_token_count", 0) if usage else 0
                    total_tokens_in += tokens_in
                    total_tokens_out += tokens_out
                    llm_ms = int((time.time() - last_llm_start) * 1000)
                    
                    yield {
                        "type": "llm",
                        "model": getattr(agent, "model", "gemini-3.5-flash-lite"),
                        "decision": "final answer",
                        "tokens_in": tokens_in,
                        "tokens_out": tokens_out,
                        "ms": llm_ms,
                        "span": "call_llm"
                    }
                    
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                final_response_text += part.text

            agent_ms = int((time.time() - stage_start) * 1000)
            steps_log.append({
                "key": "agent",
                "status": "passed",
                "ms": agent_ms
            })
            
            yield {
                "type": "step",
                "key": "agent",
                "status": "passed",
                "detail": "completed",
                "ms": agent_ms,
                "span": "agent",
                "kind": "in-process"
            }

            # -------------------------------------------------------------
            # 7. A2A DATA MASKER STEP (SPEC §5.6, K-1–K-3)
            # -------------------------------------------------------------
            yield {
                "type": "stage",
                "key": "mask",
                "label": "A2A Data Masker"
            }
            
            mask_start = time.time()
            with tracer.start_as_current_span("security.a2a_mask") as mask_span:
                mask_span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.GUARDRAIL.value)
                
                mask_res = None
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.post(
                            "http://127.0.0.1:10003/rpc",
                            json={
                                "jsonrpc": "2.0",
                                "method": "message/send",
                                "params": {
                                    "text": final_response_text,
                                    "user_email": user_email
                                },
                                "id": 1
                            }
                        )
                        if resp.status_code != 200:
                            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
                        rpc_data = resp.json()
                        mask_res = rpc_data.get("result", {})
                        if not isinstance(mask_res, dict) or "masked_text" not in mask_res:
                            raise ValueError(f"Unparseable masker response: {rpc_data}")
                except Exception as e:
                    # Fail loud (SPEC §11 R-4, P-4): Unreachable or unparseable Masker terminates turn with 502 error
                    mask_span.set_status(StatusCode.ERROR, str(e))
                    mask_span.record_exception(e)
                    mask_ms = int((time.time() - mask_start) * 1000)
                    err_msg = f"Data Masker unreachable: {e}"
                    
                    wall_ms = int((time.time() - start_time) * 1000)
                    write_run_log({
                        "turn_id": turn_id,
                        "trace_id": trace_id,
                        "user": user_email,
                        "message": message,
                        "terminated": "error",
                        "blocked_at": None,
                        "wall_clock_ms": wall_ms,
                        "tokens": {"in": total_tokens_in, "out": total_tokens_out},
                        "steps": steps_log,
                        "tool_calls": tool_calls_log,
                        "llm_calls": llm_calls_count,
                        "error": err_msg
                    }, is_failing=True)
                    
                    yield {
                        "type": "error",
                        "step": "mask",
                        "status": 502,
                        "error": err_msg,
                        "terminated": "error"
                    }
                    return

                mask_ms = int((time.time() - mask_start) * 1000)
                masked_text = mask_res.get("masked_text", final_response_text)
                changes_count = mask_res.get("changes_count", 0)
                mask_detail = mask_res.get("detail", "nothing to mask")
                
                mask_span.set_attribute("masker.changes_count", changes_count)
                steps_log.append({"key": "mask", "status": "passed", "ms": mask_ms})
                yield {
                    "type": "step",
                    "key": "mask",
                    "status": "passed",
                    "detail": mask_detail,
                    "ms": mask_ms,
                    "span": "security.a2a_mask",
                    "kind": "A2A"
                }
                final_response_text = masked_text

            # -------------------------------------------------------------
            # 8. MEMORY SAVE STEP (Mem0, SPEC §5.7, R-4)
            # -------------------------------------------------------------
            yield {
                "type": "stage",
                "key": "save",
                "label": "Mem0 Memory Save"
            }
            
            save_start = time.time()
            with tracer.start_as_current_span("memory.save") as save_span:
                save_span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.TOOL.value)
                try:
                    save_memory(user_email=user_email, user_message=message)
                    save_ms = int((time.time() - save_start) * 1000)
                    steps_log.append({"key": "save", "status": "passed", "ms": save_ms})
                    yield {
                        "type": "step",
                        "key": "save",
                        "status": "passed",
                        "detail": "saved customer message to Mem0",
                        "ms": save_ms,
                        "span": "memory.save",
                        "kind": "in-process"
                    }
                except Exception as e:
                    save_span.record_exception(e)
                    save_ms = int((time.time() - save_start) * 1000)
                    steps_log.append({"key": "save", "status": "warning", "ms": save_ms})
                    yield {
                        "type": "step",
                        "key": "save",
                        "status": "warning",
                        "detail": f"save failed: {e}",
                        "ms": save_ms,
                        "span": "memory.save",
                        "kind": "in-process"
                    }

            wall_clock_ms = int((time.time() - start_time) * 1000)
            
            # Record terminal attributes on root span
            root_span.set_attribute(SpanAttributes.OUTPUT_VALUE, final_response_text.strip())
            root_span.set_attribute("tokens.in", total_tokens_in)
            root_span.set_attribute("tokens.out", total_tokens_out)
            root_span.set_attribute("wall_clock_ms", wall_clock_ms)
            
            run_record = {
                "turn_id": turn_id,
                "trace_id": trace_id,
                "user": user_email,
                "message": message,
                "terminated": "done",
                "blocked_at": None,
                "wall_clock_ms": wall_clock_ms,
                "tokens": {"in": total_tokens_in, "out": total_tokens_out},
                "steps": steps_log,
                "tool_calls": tool_calls_log,
                "llm_calls": llm_calls_count
            }
            
            # Write runs/<turn_id>.json (EVALS §4.1)
            write_run_log(run_record, is_failing=False)

            yield {
                "type": "final",
                "blocked": False,
                "blocked_at": None,
                "response": final_response_text.strip(),
                "terminated": "done",
                "wall_clock_ms": wall_clock_ms,
                "tokens": {"in": total_tokens_in, "out": total_tokens_out}
            }

        except Exception as e:
            root_span.record_exception(e)
            wall_clock_ms = int((time.time() - start_time) * 1000)
            yield {
                "type": "error",
                "step": "agent",
                "status": 502,
                "error": str(e),
                "terminated": "error"
            }
