from agents.state import ComplaintAgentState
from agents.llm import call_llm_json

def response_formatter_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Node 4: Generates the natural confirmation message describing what fields were extracted/updated."""
    tool_used = state.get("tool_used", "log_complaint")
    changed = state.get("changed_fields", {}) or {}
    merged = state.get("merged_fields", {}) or {}
    risk = state.get("risk_assessment", {}) or {}

    if tool_used == "edit_complaint":
        if changed:
            items_str = ", ".join([f"'{k}' to '{v.get('new_value')}'" for k, v in changed.items()])
            msg = f"Got it. I have updated the {items_str} in the form while keeping all other fields unchanged. I've also updated the Risk Assessment to reflect these changes."
        else:
            msg = "Got it. I checked the complaint record. No changes were necessary based on your input."
    elif tool_used == "document_extraction":
        product = merged.get("product_name", "the product")
        batch = merged.get("batch_lot_number", "N/A")
        msg = f"I've extracted the complaint details from the document for {product} (Batch: {batch}). The complaint form and AI risk assessment have been auto-filled."
    else:
        product = merged.get("product_name", "the product")
        severity = risk.get("severity", "Major")
        msg = f"Got it! I have logged the complaint for {product} into the system. Risk severity evaluated as {severity}. You can review the details on the left form."

    state["assistant_message"] = msg
    return state
