from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ComplaintFormData(BaseModel):
    complaint_source: Optional[str] = ""
    customer_name: Optional[str] = ""
    product_name: Optional[str] = ""
    product_strength: Optional[str] = ""
    batch_lot_number: Optional[str] = ""
    manufacturing_date: Optional[str] = ""
    expiry_date: Optional[str] = ""
    affected_quantity: Optional[str] = ""
    complaint_category: Optional[str] = ""
    complaint_description: Optional[str] = ""
    originating_site_block: Optional[str] = ""
    impacted_npm: Optional[str] = ""

class RiskAssessmentData(BaseModel):
    severity: Optional[str] = "Minor"
    suggested_next_action: Optional[str] = ""
    initial_risk_assessment: Optional[str] = ""
    likely_root_cause: Optional[str] = ""  # Bonus feature

class ChatRequest(BaseModel):
    complaint_id: Optional[int] = None
    message: str

class ChatResponse(BaseModel):
    complaint_id: int
    form_data: ComplaintFormData
    risk_assessment: RiskAssessmentData
    status: str = "Pending Triage"
    assistant_message: str
    tool_used: str

class ChatMessageRead(BaseModel):
    id: int
    complaint_id: int
    role: str
    content: str
    tool_used: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogRead(BaseModel):
    id: int
    complaint_id: int
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: str
    changed_at: datetime

    class Config:
        from_attributes = True

class ComplaintRead(BaseModel):
    id: int
    complaint_source: Optional[str] = ""
    customer_name: Optional[str] = ""
    product_name: Optional[str] = ""
    product_strength: Optional[str] = ""
    batch_lot_number: Optional[str] = ""
    manufacturing_date: Optional[str] = ""
    expiry_date: Optional[str] = ""
    affected_quantity: Optional[str] = ""
    complaint_category: Optional[str] = ""
    complaint_description: Optional[str] = ""
    originating_site_block: Optional[str] = ""
    impacted_npm: Optional[str] = ""
    status: str
    severity: Optional[str] = ""
    suggested_next_action: Optional[str] = ""
    initial_risk_assessment: Optional[str] = ""
    likely_root_cause: Optional[str] = ""
    created_at: datetime
    updated_at: datetime
    chat_messages: List[ChatMessageRead] = []
    audit_logs: List[AuditLogRead] = []

    class Config:
        from_attributes = True
