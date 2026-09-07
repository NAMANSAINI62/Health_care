from agents.state import ComplaintAgentState
from agents.llm import create_lcel_json_chain
from agents.prompts import DOC_EXTRACTION_SYSTEM

# Chain for Document Extraction
document_extraction_chain = create_lcel_json_chain(
    system_prompt_str=DOC_EXTRACTION_SYSTEM.template,
    user_prompt_str="Document Extracted Text:\n'{doc_text}'"
)

def document_extraction_tool_node(state: ComplaintAgentState) -> ComplaintAgentState:
    doc_text = state.get("document_text", "")
    extracted = document_extraction_chain.invoke({"doc_text": doc_text})

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

