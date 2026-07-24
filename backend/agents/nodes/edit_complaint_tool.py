from agents.state import ComplaintAgentState
from agents.llm import call_groq_json
from typing import Dict, Any

def edit_complaint_tool_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Node 2B: Extracts partial updates from prompt, diffs against existing DB fields, and merges while PRESERVING untouched fields."""
    user_msg = state.get("user_message", "")
    existing = state.get("existing_fields", {}) or {}

    system_prompt = (
        "You are an expert pharmaceutical QMS AI Assistant performing a PARTIAL EDIT on an existing complaint.\n"
        "Analyze the user's edit input and extract ONLY the fields explicitly mentioned or requested to be changed.\n"
        "Do NOT include or invent fields that were NOT mentioned in the update request.\n\n"
        "Allowed target keys:\n"
        "complaint_source, customer_name, product_name, product_strength, batch_lot_number, "
        "manufacturing_date, expiry_date, affected_quantity, complaint_category, "
        "complaint_description, originating_site_block, impacted_npm.\n\n"
        "Return a JSON object with a single key 'updated_fields' containing ONLY the mentioned keys and their new values.\n"
        "Example output: {\"updated_fields\": {\"batch_lot_number\": \"BMX-240602\", \"affected_quantity\": \"48 capsules\"}}"
    )

    prompt = f"Existing Complaint Fields:\n{existing}\n\nUser Edit Request:\n'{user_msg}'"
    res = call_groq_json(prompt, system_prompt)
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
