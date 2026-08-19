from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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
    detected_defects: Optional[List[str]] = []

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

class QASignatureCreate(BaseModel):
    signer_name: str
    signer_role: str = "QA Manager"
    signature_meaning: str = "Approval of Complaint Classification, Root Cause & Risk Assessment"
    checksum_hash: str
    comments: Optional[str] = ""
    auto_spawn_capa: Optional[bool] = True

class QASignatureRead(BaseModel):
    id: int
    complaint_id: int
    signer_name: str
    signer_role: str
    signature_meaning: str
    checksum_hash: str
    comments: Optional[str] = None
    signed_at: datetime

    class Config:
        from_attributes = True

class CAPAActionItemCreate(BaseModel):
    action_type: str = "Corrective Action"
    description: str
    assignee: Optional[str] = ""
    due_date: Optional[datetime] = None

class CAPAActionItemRead(BaseModel):
    id: int
    capa_id: int
    action_type: str
    description: str
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CAPACreate(BaseModel):
    complaint_id: Optional[int] = None
    title: str
    description: Optional[str] = ""
    root_cause: Optional[str] = ""
    severity: str = "Major"
    owner_department: str = "Quality Assurance"
    assignee_name: Optional[str] = ""
    due_days: Optional[int] = 30
    action_items: Optional[List[CAPAActionItemCreate]] = []

class CAPAUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    root_cause: Optional[str] = None
    severity: Optional[str] = None
    owner_department: Optional[str] = None
    assignee_name: Optional[str] = None
    status: Optional[str] = None
    escalation_status: Optional[str] = None

class CAPARead(BaseModel):
    id: int
    capa_number: str
    complaint_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    root_cause: Optional[str] = None
    severity: str
    owner_department: str
    assignee_name: Optional[str] = None
    status: str
    due_date: Optional[datetime] = None
    escalation_status: str
    created_at: datetime
    updated_at: datetime
    action_items: List[CAPAActionItemRead] = []

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
    qa_signatures: List[QASignatureRead] = []
    capas: List[CAPARead] = []

    class Config:
        from_attributes = True

