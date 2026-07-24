from agents.state import ComplaintAgentState
from agents.llm import call_groq_json

def document_extraction_tool_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Node 2C: Extracts complaint details from document/file uploads, filling all 12 fields."""
    doc_text = state.get("document_text", "")

    system_prompt = (
        "You are an expert pharmaceutical Quality Assurance AI Assistant.\n"
        "Extract and infer ALL 12 fields from the uploaded complaint document into a JSON object:\n"
        "- complaint_source (e.g. Pharmacy, Hospital, Email, Distributor, Patient)\n"
        "- customer_name (e.g. Apollo Pharmacy, CVS, MedPlus)\n"
        "- product_name (e.g. Amoxicillin Capsules, Paracetamol Injection)\n"
        "- product_strength (e.g. 500mg, 10 mg/mL)\n"
        "- batch_lot_number (e.g. BMX-240602, CHG-260712A)\n"
        "- manufacturing_date (e.g. Jan 2026 — infer standard Mfg date if missing)\n"
        "- expiry_date (e.g. Jan 2028 — infer standard 2-year Expiry date if missing)\n"
        "- affected_quantity (e.g. 48 capsules, 100 vials)\n"
        "- complaint_category (e.g. Discoloration, Packaging Defect, Contamination)\n"
        "- complaint_description (Detailed summary of document complaint)\n"
        "- originating_site_block (e.g. Block A - Sterile Injectables, Block B - Solid Oral Dosage)\n"
        "- impacted_npm (Non-Product Materials e.g. PVC Blister Foil, Glass Vial, Rubber Stopper)\n\n"
        "IMPORTANT: Infer realistic defaults for any missing fields so that ALL 12 FIELDS are populated."
    )

    prompt = f"Document Extracted Text:\n'{doc_text}'"
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
    state["tool_used"] = "document_extraction"
    state["changed_fields"] = {k: {"old_value": "", "new_value": v} for k, v in cleaned.items() if v}
    return state
