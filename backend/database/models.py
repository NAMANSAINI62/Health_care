from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func
from datetime import datetime
from database.connection import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_source = Column(String(50), nullable=True)
    customer_name = Column(String(255), nullable=True)
    product_name = Column(String(255), nullable=True)
    product_strength = Column(String(100), nullable=True)
    batch_lot_number = Column(String(100), nullable=True)
    manufacturing_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    affected_quantity = Column(String(100), nullable=True)
    complaint_category = Column(String(150), nullable=True)
    complaint_description = Column(Text, nullable=True)
    originating_site_block = Column(String(150), nullable=True)
    impacted_npm = Column(String(255), nullable=True)
    status = Column(String(50), default="Pending Triage")
    severity = Column(String(50), nullable=True)
    suggested_next_action = Column(String(255), nullable=True)
    initial_risk_assessment = Column(Text, nullable=True)
    likely_root_cause = Column(Text, nullable=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CAPA(Base):
    __tablename__ = "capas"

    id = Column(Integer, primary_key=True, index=True)
    capa_number = Column(String(100), unique=True, index=True, nullable=False)
    complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    severity = Column(String(50), nullable=False, default="Major")  # Critical, Major, Minor
    owner_department = Column(String(150), nullable=False, default="Quality Assurance")  # e.g., Packaging, Sterile Block B, QC
    assignee_name = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="Open")  # Open, In Progress, Under Review, Completed, Overdue
    due_date = Column(DateTime(timezone=True), nullable=True)
    escalation_status = Column(String(50), nullable=False, default="Normal")  # Normal, Escalated - Level 1, Escalated - Level 2
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CAPAActionItem(Base):
    __tablename__ = "capa_action_items"

    id = Column(Integer, primary_key=True, index=True)
    capa_id = Column(Integer, ForeignKey("capas.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(50), nullable=False, default="Corrective Action")  # Corrective Action, Preventive Action
    description = Column(Text, nullable=False)
    assignee = Column(String(255), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="Pending")  # Pending, In Progress, Completed
    completed_at = Column(DateTime(timezone=True), nullable=True)

class ComplaintChatMessage(Base):
    __tablename__ = "complaint_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    tool_used = Column(String(50), nullable=True)  # 'log_complaint', 'edit_complaint', 'document_extraction', etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ComplaintFieldAudit(Base):
    __tablename__ = "complaint_field_audit"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by = Column(String(20), default="ai_agent")
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index= True)
    username = Column(String(100), index =True, nullable = False)
    email = Column(String(50), unique=True, nullable=False)
    hashed_passward = Column(String(50), nullable=False)
    roles = Column(String(25), nullable=False, default='qa_specialist')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    phone_no = Column(Integer, nullable=False, unique=True)
