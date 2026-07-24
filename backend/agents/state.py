from typing import TypedDict, Optional, Dict, Any, List

class ComplaintAgentState(TypedDict):
    complaint_id: Optional[int]
    user_message: str
    document_text: Optional[str]
    intent: Optional[str]
    existing_fields: Dict[str, Any]
    extracted_fields: Dict[str, Any]
    merged_fields: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    changed_fields: Dict[str, Dict[str, Any]]  # field_name -> {old_value, new_value}
    assistant_message: str
    tool_used: str
    status: str
