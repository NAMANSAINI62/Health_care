from agents.state import ComplaintAgentState
from agents.llm import call_groq_json

def intent_router_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Node 1: Classifies the user message into log_complaint, edit_complaint, or document_extraction."""
    user_msg = state.get("user_message", "")
    doc_text = state.get("document_text", "")
    complaint_id = state.get("complaint_id")

    if doc_text and doc_text.strip():
        state["intent"] = "document_extraction"
        return state

    system_prompt = (
        "You are an AI intent classifier for a pharmaceutical Quality Management System (QMS).\n"
        "Classify the user input into ONE of these 3 intent categories:\n"
        "1. 'log_complaint': The user is logging a new customer complaint from scratch.\n"
        "2. 'edit_complaint': The user is correcting, updating, or editing an existing complaint (e.g. changing batch number, quantity, strength, product, etc.).\n"
        "3. 'document_extraction': The user has uploaded a file or is referencing an attached document.\n\n"
        "Respond strictly with JSON format: {\"intent\": \"log_complaint\" | \"edit_complaint\" | \"document_extraction\"}"
    )

    prompt = f"Existing Complaint ID: {complaint_id}\nUser Input: '{user_msg}'"
    result = call_groq_json(prompt, system_prompt)
    intent = result.get("intent", "log_complaint")

    # If user provided complaint_id and intent returned log_complaint, but the message sounds like an update, flip to edit_complaint
    if complaint_id and intent == "log_complaint":
        update_keywords = ["update", "change", "correct", "sorry", "instead", "is actually", "should be", "wrong", "fix"]
        if any(k in user_msg.lower() for k in update_keywords):
            intent = "edit_complaint"


    state["intent"] = intent
    return state
