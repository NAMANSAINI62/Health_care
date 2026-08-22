from agents.state import ComplaintAgentState
from agents.llm import call_llm_json
from agents.prompts import DOC_EXTRACTION_SYSTEM, DOC_EXTRACTION_USER  # Import templates

def document_extraction_tool_node(state: ComplaintAgentState) -> ComplaintAgentState:
    doc_text = state.get("document_text", "")

    system_prompt = DOC_EXTRACTION_SYSTEM.format()
    prompt = DOC_EXTRACTION_USER.format(doc_text=doc_text)
    
    extracted = call_llm_json(prompt, system_prompt)

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
    state["tool_used"] = "document_extraction"
    state["changed_fields"] = {k: {"old_value": "", "new_value": v} for k, v in cleaned.items() if v}
    return state
