from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ComplaintAgentState(BaseModel):
    complaint_id: Optional[int] = None
    user_message: str = ""
    document_text: Optional[str] = None
    intent: Optional[str] = None
    existing_fields: Dict[str, Any] = Field(default_factory=dict)
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    merged_fields: Dict[str, Any] = Field(default_factory=dict)
    changed_fields: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)
    assistant_message: str = ""
    tool_used: str = "log_complaint"
    status: str = "Pending Triage"

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)


