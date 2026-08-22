from agents.state import ComplaintAgentState
from agents.llm import call_llm_json
from agents.prompts import EDIT_COMPLAINT_SYSTEM, EDIT_COMPLAINT_USER  # Import templates
from typing import Dict, Any

def edit_complaint_tool_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Node 2B: Extracts partial updates from prompt, diffs against existing DB fields, and merges while PRESERVING untouched fields."""
    user_msg = state.get("user_message", "")
    existing = state.get("existing_fields", {}) or {}

    system_prompt = EDIT_COMPLAINT_SYSTEM.format()
    prompt = EDIT_COMPLAINT_USER.format(existing=existing, user_msg=user_msg)
    
    res = call_llm_json(prompt, system_prompt)
    updates: Dict[str, Any] = res.get("updated_fields", {})

    merged = existing.copy()
    changed: Dict[str, Dict[str, Any]] = {}

    for field, new_val in updates.items():
        old_val = merged.get(field, "")
        new_val_str = str(new_val)
        if old_val != new_val_str:
            changed[field] = {"old_value": old_val, "new_value": new_val_str}
            merged[field] = new_val_str

    state["extracted_fields"] = updates
    state["merged_fields"] = merged
    state["changed_fields"] = changed
    state["tool_used"] = "edit_complaint"
    return state
