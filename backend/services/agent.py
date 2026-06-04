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
import re
import sys
import os
from pathlib import Path
from typing import Any

from services.providers.base import ToolCall

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
MAX_TOOL_ROUNDS = 6

# ── Planning state tracker ────────────────────────────────────────────────────
# Keeps the agent on the right path regardless of what tool the LLM calls.

_PLANNING_KW = [
    "lên lịch trình", "lên kế hoạch", "kế hoạch chuyến", "itinerary", "plan chuyến",
    "tạo lịch trình", "lập lịch",
    "muốn đi", "tôi muốn đi", "t muốn đi", "mình muốn đi",  # "I want to go to X"
    "đặt tour", "chuyến đi vinpearl", "đi vinpearl", "đến vinpearl",
    "đi du lịch", "đi chơi vinpearl",
]
# Counter-intent keywords: if the MOST RECENT user message contains these,
# we are NOT in a planning flow (user switched topics).
_NON_PLANNING_KW = [
    "ưu đãi", "khuyến mãi", "deal", "promo", "giảm giá",
    "tư vấn phòng", "so sánh phòng", "phòng nào phù hợp", "khu phòng",
    "điểm đến nào", "có những nơi nào", "vinpearl ở đâu",
]
# Booking intent keywords — triggers contact info collection
_BOOKING_KW = [
    "chốt", "đặt lịch", "book", "đăng ký", "liên hệ cskh",
    "liên hệ tôi", "tôi muốn đặt", "xác nhận", "confirm",
]
_DEST_MAP = {
    "phú quốc": (1, "Phú Quốc"), "phu quoc": (1, "Phú Quốc"), "đảo ngọc": (1, "Phú Quốc"),
    "nha trang": (2, "Nha Trang"),
    "hội an": (3, "Nam Hội An"), "hoi an": (3, "Nam Hội An"), "nam hội an": (3, "Nam Hội An"),
    "cửa hội": (4, "Cửa Hội"), "nghệ an": (4, "Cửa Hội"), "vinh": (4, "Cửa Hội"),
    "hải phòng": (5, "Hải Phòng"), "cát bà": (5, "Hải Phòng"),
}


def _get_planning_state(messages: list[dict]) -> dict | None:
    """
    Scan conversation history and return the current planning state.
    Returns None if the conversation is NOT in a planning flow.
    Rules:
    - Only activates if a planning keyword was found in history
    - Deactivates if any message AFTER the last planning keyword contains a counter-intent keyword
    - Only scans from the most recent planning intent onwards
    """
    # Find the LAST planning-intent message index
    last_planning_idx = -1
    for i, m in enumerate(messages):
        if m.get("role") == "user":
            c = m.get("content", "").lower()
            if any(kw in c for kw in _PLANNING_KW):
                last_planning_idx = i

    if last_planning_idx == -1:
        return None  # No planning intent found in this conversation

    # Check if a counter-intent keyword appeared IN OR AFTER the last planning intent
    for m in messages[last_planning_idx:]:
        if m.get("role") == "user":
            c = m.get("content", "").lower()
            if any(kw in c for kw in _NON_PLANNING_KW):
                return None  # User's intent is not planning (or switched topics)

    # ── normalise helper ────────────────────────────────────────────────────
    _TYPO = {
        "nagfy": "ngày", "ngaf": "ngày", "nagay": "ngày", "ngay ": "ngày ",
        "nguoi": "người", "ngưòi": "người",
    }

    def _norm(raw: str) -> str:
        s = raw.lower()
        for wrong, right in _TYPO.items():
            s = s.replace(wrong, right)
        return s

    # Scan from the planning intent point for collected info
    dest = days = who = budget = None
    for m in messages[last_planning_idx:]:
        role = m.get("role")
        content = _norm(m.get("content", ""))

        if role == "user":
            # Destination
            if dest is None:
                for kw, info in _DEST_MAP.items():
                    if kw in content:
                        dest = info
                        break

            # Days — match "X ngày", "X days", or bare integer reply
            if days is None:
                md = re.search(r"(\d+)\s*(?:ngày|days?)", content)
                if md:
                    days = max(1, min(int(md.group(1)), 14))
                else:
                    md2 = re.match(r"^\s*(\d+)\s*$", content)
                    if md2:
                        days = max(1, min(int(md2.group(1)), 14))

            # Who
            if who is None:
                if any(k in content for k in ["một mình", "1 mình", "mình đi", "solo", "di 1 minh", "1 người", "minh di"]):
                    who = "solo"
                elif any(k in content for k in ["gia đình", "có con", "ba mẹ", "cả nhà", "gia dinh", "trẻ nhỏ", "tre nho", "con nhỏ"]):
                    who = "family"
                elif any(k in content for k in ["cặp đôi", "vợ chồng", "người yêu", "bạn trai", "bạn gái", "cap doi", "2 người"]):
                    who = "couple"
                elif any(k in content for k in ["nhóm", "bạn bè", "ban be", "nhom"]):
                    who = "group"
                # Number shortcut (1=couple, 2=family, 3=group, 4=solo)
                elif re.match(r"^\s*1\s*$", content):
                    who = "couple"
                elif re.match(r"^\s*2\s*$", content):
                    who = "family"
                elif re.match(r"^\s*3\s*$", content):
                    who = "group"
                elif re.match(r"^\s*4\s*$", content):
                    who = "solo"

            # Budget — tier keywords OR amount (Xm / X triệu / X million)
            if budget is None:
                if any(k in content for k in ["thấp", "dưới 3", "tiết kiệm", "rẻ", "thap", "budget"]):
                    budget = "thấp"
                elif any(k in content for k in ["trung", "3-6", "3–6", "vừa", "tầm trung", "trung bình"]):
                    budget = "trung"
                elif any(k in content for k in ["cao", "trên 6", "sang", "luxury", "vip", "hạng sang"]):
                    budget = "cao"
                else:
                    # Detect monetary amounts like "20m", "20 triệu", "5tr", "15 million"
                    bm = re.search(r"(\d+(?:\.\d+)?)\s*(?:triệu|trieu|tr\b|m\b|million)", content)
                    if bm:
                        amount = float(bm.group(1))
                        # Interpret as per-night if ≤ 10, else assume total trip / days (estimate)
                        per_night = amount if amount <= 10 else amount / max(days or 3, 1)
                        if per_night <= 3:
                            budget = "thấp"
                        elif per_night <= 6:
                            budget = "trung"
                        else:
                            budget = "cao"
                    # Number shortcut (1=thấp, 2=trung, 3=cao) only as standalone reply
                    elif re.match(r"^\s*1\s*$", content) and who is not None:
                        budget = "thấp"
                    elif re.match(r"^\s*2\s*$", content) and who is not None:
                        budget = "trung"
                    elif re.match(r"^\s*3\s*$", content) and who is not None:
                        budget = "cao"

    # last_planning_idx != -1 guarantees intent was found
    return {"dest": dest, "days": days, "who": who, "budget": budget}


def _is_booking_intent(messages: list[dict]) -> bool:
    """True if the most recent user message contains a booking intent keyword."""
    for m in reversed(messages):
        if m.get("role") == "user":
            c = m.get("content", "").lower()
            return any(kw in c for kw in _BOOKING_KW)
    return False


def _get_booking_contact(messages: list[dict]) -> dict:
    """Extract name/phone/email from conversation history."""
    import re
    contact: dict = {"name": None, "phone": None, "email": None}
    for m in messages:
        if m.get("role") != "user":
            continue
        c = m.get("content", "")
        cl = c.lower()
        # Email
        if contact["email"] is None:
            em = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", c)
            if em:
                contact["email"] = em.group(0)
        # Phone
        if contact["phone"] is None:
            ph = re.search(r"(?<!\d)(0[0-9]{9,10}|\+84[0-9]{9,10})(?!\d)", c)
            if ph:
                contact["phone"] = ph.group(0)
        # Name — look for "tên ... là" or long Vietnamese words that look like a name
        if contact["name"] is None:
            nm = re.search(r"(?:tên(?:\s+là)?|họ tên(?:\s+là)?)\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+){1,3})", c)
            if nm:
                contact["name"] = nm.group(1).strip()
            elif re.match(r"^[A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+){1,4}$", c.strip()):
                contact["name"] = c.strip()
    return contact


def _next_planning_question(ps: dict, all_events: list[dict]) -> str | None:
    """
    Return the next clarify question text, or None if all info is collected.
    Also auto-builds the itinerary call if everything is ready.
    """
    if ps["dest"] is None:
        # Check if get_destinations was already called — auto-show the list
        for ev in all_events:
            if ev.get("tool") == "get_destinations" and isinstance(ev.get("result"), str):
                return ev["result"]   # already includes "Bạn muốn đến điểm nào?"
        return None  # LLM hasn't called get_destinations yet → let it proceed

    dest_name = ps["dest"][1]

    if ps["days"] is None:
        return (
            f"📅 **Chuyến đi bao nhiêu ngày?** *(Vinpearl {dest_name})*\n\n"
            "Ví dụ: 2 ngày, 3 ngày, 5 ngày... *(tối đa 14 ngày)*"
        )

    if ps["who"] is None:
        return (
            f"🤝 **Bạn đi với ai?** *(Vinpearl {dest_name} · {ps['days']} ngày)*\n\n"
            "1. 👫 Cặp đôi\n"
            "2. 👨‍👩‍👧 Gia đình (có con nhỏ)\n"
            "3. 👥 Nhóm bạn\n"
            "4. 🧍 Một mình\n\n"
            "*(Gõ số hoặc mô tả)*"
        )

    if ps["budget"] is None:
        who_labels = {"solo": "Một mình", "couple": "Cặp đôi", "family": "Gia đình", "group": "Nhóm bạn"}
        who_label = who_labels.get(ps["who"], ps["who"])
        return (
            f"💰 **Ngân sách** mỗi đêm tại **{dest_name}**? "
            f"👤*(đi với: {who_label})*\n\n"
            "1. 💚 Thấp — dưới 3 triệu/đêm\n"
            "2. 💛 Trung bình — 3–6 triệu/đêm\n"
            "3. 🔴 Cao — trên 6 triệu/đêm\n\n"
            "*(Gõ số hoặc mô tả)*"
        )

    return None  # All info collected → LLM should call build_itinerary


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
            "Dùng kết quả tool ở trên để trả lời user bằng markdown đẹp.\n"
            "⚠️ Nếu đang lập lịch trình: PHẢI tiếp tục hỏi thông tin còn thiếu qua clarify "
            "theo đúng thứ tự (điểm đến → số ngày → who → budget_tier). "
            "TUYỆT ĐỐI KHÔNG gọi build_itinerary khi chưa user xác nhận đủ 4 thông tin."
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

    # ── Booking intent fast-path ──────────────────────────────────────────────
    # Detect "chốt / đặt lịch / book" BEFORE calling the LLM.
    # If contact info is missing, ask for it directly without going through LLM.
    if _is_booking_intent(messages):
        contact = _get_booking_contact(messages)
        missing = []
        if not contact["name"]:
            missing.append("**họ và tên đầy đủ**")
        if not contact["phone"]:
            missing.append("**số điện thoại**")
        if not contact["email"]:
            missing.append("**địa chỉ email**")
        if missing:
            q = (
                "📞 **Đăng ký liên hệ CSKH Vinpearl**\n\n"
                "Để nhân viên chăm sóc khách hàng liên hệ xác nhận lịch trình, "
                "vui lòng cung cấp:\n"
                + "".join(f"- {f}\n" for f in missing)
                + "\n*(Gõ theo định dạng: Họ Tên, 0912345678, email@gmail.com)*"
            )
            return {
                "status":         "waiting_for_user",
                "assistant_text": q,
                "rounds":         rounds,
                "tool_events":    all_events,
                "usage":          total_usage,
                "provider":       provider_name,
                "model":          used_model,
            }
        # All contact info available — let LLM call submit_booking
    # ─────────────────────────────────────────────────────────────────────────

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
                    # If other tools (e.g. get_destinations) ran before clarify,
                    # combine their text output with the question so nothing is lost.
                    prefix_parts: list[str] = []
                    for ev in non_clarify:
                        r = ev.get("result")
                        if isinstance(r, str) and r.strip():
                            prefix_parts.append(r.strip())
                    if prefix_parts:
                        combined_text = "\n\n".join(prefix_parts) + "\n\n" + question
                    else:
                        combined_text = question

                    rounds.append(round_record)
                    return {
                        "status":         "waiting_for_user",
                        "assistant_text": combined_text,
                        "rounds":         rounds,
                        "tool_events":    all_events,
                        "usage":          total_usage,
                        "provider":       provider_name,
                        "model":          used_model,
                    }

                non_clarify.append(event)

            rounds.append(round_record)

            # ── Planning state guard ──────────────────────────────────────────
            # After each tool round, check if we're in a planning flow and
            # need to ask for missing info — regardless of what tool the LLM chose.
            ps = _get_planning_state(messages)
            if ps is not None:
                next_q = _next_planning_question(ps, all_events)
                if next_q is not None:
                    # Missing info → stop and ask user
                    return {
                        "status":         "waiting_for_user",
                        "assistant_text": next_q,
                        "rounds":         rounds,
                        "tool_events":    all_events,
                        "usage":          total_usage,
                        "provider":       provider_name,
                        "model":          used_model,
                    }
                # All 4 fields collected — check if build_itinerary was already called
                already_built = any(ev.get("tool") == "build_itinerary" for ev in all_events)
                if not already_built:
                    # Force build_itinerary call directly
                    from services.tools import TOOL_FUNCTIONS
                    build_fn = TOOL_FUNCTIONS.get("build_itinerary")
                    if build_fn:
                        dest_id, dest_name = ps["dest"]
                        days = ps["days"]
                        who = ps["who"]
                        budget = ps["budget"]
                        print(f"🔧 [agent-guard] build_itinerary(dest={dest_name}, days={days}, who={who}, budget={budget})")
                        itinerary_result = build_fn(
                            destination_id=dest_id,
                            destination_name=dest_name,
                            days=days,
                            who=who,
                            budget_tier=budget,
                        )
                        return {
                            "status":         "answered",
                            "assistant_text": itinerary_result,
                            "rounds":         rounds,
                            "tool_events":    all_events,
                            "usage":          total_usage,
                            "provider":       provider_name,
                            "model":          used_model,
                        }
            # ─────────────────────────────────────────────────────────────────

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
