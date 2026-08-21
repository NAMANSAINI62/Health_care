from agents.state import ComplaintAgentState
from agents.llm import call_groq_json
from agents.prompts import LOG_COMPLAINT_SYSTEM, LOG_COMPLAINT_USER  # Import templates
def log_complaint_tool_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Node 2A: Extracts and intelligently infers ALL 12 complaint fields from user complaint text."""
    user_msg = state.get("user_message", "")
    system_prompt = LOG_COMPLAINT_SYSTEM.format()
    prompt = LOG_COMPLAINT_USER.format(user_msg=user_msg)
    
    extracted = call_groq_json(prompt, system_prompt)

    all_keys = [
        "complaint_source", "customer_name", "product_name", "product_strength",
        "batch_lot_number", "manufacturing_date", "expiry_date", "affected_quantity",
        "complaint_category", "complaint_description", "originating_site_block", "impacted_npm"
    ]

    cleaned = {}
    for k in all_keys:
        cleaned[k] = str(extracted.get(k, "") or "")
    state["extracted_fields"] = cleaned
    state["merged_fields"] = cleaned.copy()
    state["tool_used"] = "log_complaint"
    state["changed_fields"] = {k: {"old_value": "", "new_value": v} for k, v in cleaned.items() if v}

    return state