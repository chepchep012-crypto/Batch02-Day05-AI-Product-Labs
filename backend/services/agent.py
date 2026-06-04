"""
VinBot Agent
============
Async multi-round tool-calling loop — follows the Day04 lab pattern.

Architecture (mirrors starter_v0/chat.py):
  1. Load system_prompt.md + tools.yaml
  2. Provider.complete(messages, tools) → ModelResponse(text, tool_calls)
  3. Execute each tool via TOOL_FUNCTIONS registry
  4. If tool returns awaiting_user=True → stop, return question to user
  5. Else append TOOL_RESULTS_JSON and loop (max 6 rounds)
"""
from __future__ import annotations

import json
import sys
import os
from pathlib import Path
from typing import Any

from services.providers.base import ToolCall

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
MAX_TOOL_ROUNDS = 6


# ── Helpers (same as chat.py) ─────────────────────────────────────────────────

def _json_text(value: Any, *, max_chars: int | None = 24000) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if max_chars and len(text) > max_chars:
        return text[:max_chars] + "\n...<truncated>"
    return text


def _assistant_tool_message(response_text: str | None, calls: list[ToolCall]) -> dict:
    summary = [{"name": c.name, "args": c.args} for c in calls]
    content = response_text or "Tôi sẽ gọi tool phù hợp."
    return {
        "role": "assistant",
        "content": f"{content}\n\nTOOL_CALLS_JSON:\n{_json_text(summary)}",
    }


def _tool_results_message(events: list[dict[str, Any]]) -> dict:
    return {
        "role": "user",
        "content": (
            "TOOL_RESULTS_JSON:\n"
            f"{_json_text(events)}\n\n"
            "Dùng kết quả tool ở trên để trả lời user. "
            "Nếu cần thêm thông tin, hỏi qua clarify. "
            "Nếu đã đủ, trả lời trực tiếp bằng markdown đẹp."
        ),
    }


def _execute_tool(call: ToolCall) -> dict[str, Any]:
    from services.tools import TOOL_FUNCTIONS
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {
            "tool": call.name,
            "args": call.args,
            "result": {"error": "unknown_tool", "message": f"No implementation for '{call.name}'"},
        }
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


# ── Main agent loop ───────────────────────────────────────────────────────────

async def run_vinbot_agent(
    history: list[dict[str, str]],
    provider_name: str,
    model: str | None = None,
    *,
    system_prompt_path: Path | None = None,
    tools_yaml_path: Path | None = None,
    max_tool_rounds: int = MAX_TOOL_ROUNDS,
) -> dict[str, Any]:
    """
    Run the VinBot agent for one user turn.

    Returns a dict:
      {
        "status":         "answered" | "waiting_for_user" | "max_tool_rounds" | "error",
        "assistant_text": str,
        "rounds":         [...],
        "tool_events":    [...],
        "usage":          {prompt_tokens, completion_tokens, total_tokens},
        "provider":       str,
        "model":          str,
      }
    """
    from services.providers import make_provider
    from services.tools import load_tool_declarations, to_openai_tools

    # Load artifacts
    sp_path = system_prompt_path or ARTIFACTS_DIR / "system_prompt.md"
    tl_path = tools_yaml_path    or ARTIFACTS_DIR / "tools.yaml"
    system_prompt    = sp_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tl_path)
    openai_tools      = to_openai_tools(tool_declarations)

    provider   = make_provider(provider_name)
    used_model = model or getattr(provider, "default_model", "unknown")

    # Build messages: system + conversation history
    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})

    rounds: list[dict]     = []
    all_events: list[dict] = []
    total_usage            = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    try:
        for round_idx in range(1, max_tool_rounds + 1):
            response = await provider.complete(
                messages, openai_tools, model=used_model, temperature=0.0
            )

            # Accumulate token usage
            if response.usage:
                for k in total_usage:
                    total_usage[k] += response.usage.get(k, 0)

            calls = response.tool_calls
            round_record: dict[str, Any] = {
                "round":         round_idx,
                "assistant_text": response.text,
                "tool_calls":    [{"name": c.name, "args": c.args} for c in calls],
                "tool_results":  [],
            }

            if not calls:
                rounds.append(round_record)
                return {
                    "status":         "answered",
                    "assistant_text": response.text or "",
                    "rounds":         rounds,
                    "tool_events":    all_events,
                    "usage":          total_usage,
                    "provider":       provider_name,
                    "model":          used_model,
                }

            messages.append(_assistant_tool_message(response.text, calls))
            non_clarify: list[dict] = []

            for call in calls:
                print(f"🔧 [{provider_name}] {call.name}({json.dumps(call.args, ensure_ascii=False)})")
                event = _execute_tool(call)
                round_record["tool_results"].append(event)
                all_events.append(event)

                result = event.get("result", {})
                if isinstance(result, dict) and result.get("awaiting_user"):
                    question = (
                        result.get("question")
                        or call.args.get("question")
                        or "Bạn bổ sung thêm thông tin nhé."
                    )
                    rounds.append(round_record)
                    return {
                        "status":         "waiting_for_user",
                        "assistant_text": question,
                        "rounds":         rounds,
                        "tool_events":    all_events,
                        "usage":          total_usage,
                        "provider":       provider_name,
                        "model":          used_model,
                    }

                non_clarify.append(event)

            rounds.append(round_record)
            messages.append(_tool_results_message(non_clarify))

    except Exception as exc:
        import traceback
        print(f"[agent] EXCEPTION: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return {
            "status":         "error",
            "assistant_text": f"Xin lỗi, đã xảy ra lỗi: {exc}",
            "rounds":         rounds,
            "tool_events":    all_events,
            "usage":          total_usage,
            "provider":       provider_name,
            "model":          used_model,
        }

    return {
        "status":         "max_tool_rounds",
        "assistant_text": "Đã xử lý tối đa vòng lặp tool, vui lòng thử lại.",
        "rounds":         rounds,
        "tool_events":    all_events,
        "usage":          total_usage,
        "provider":       provider_name,
        "model":          used_model,
    }
