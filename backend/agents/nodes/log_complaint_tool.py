from agents.state import ComplaintAgentState
from agents.llm import create_lcel_json_chain
from agents.prompts import LOG_COMPLAINT_SYSTEM, LOG_COMPLAINT_USER

# Chain for Log Complaint Extraction
log_complaint_chain = create_lcel_json_chain(
    system_prompt_str=LOG_COMPLAINT_SYSTEM.template,
    user_prompt_str="Customer Complaint Message: {user_msg}"
)

def log_complaint_tool_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Node 2A: Extracts and intelligently infers ALL 12 complaint fields from user complaint text."""
    user_msg = state.get("user_message", "")
    extracted = log_complaint_chain.invoke({"user_msg": user_msg})

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

