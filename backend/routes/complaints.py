from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta

from database.connection import get_db
from database.models import Complaint, ComplaintChatMessage, ComplaintFieldAudit, CAPA, CAPAActionItem
from schemas.complaint_schema import ComplaintRead, AuditLogRead, ChatMessageRead
from routes.capa import generate_capa_number

router = APIRouter(prefix="/api/complaints", tags=["complaints"])

@router.get("", response_model=List[ComplaintRead])
async def list_complaints(db: AsyncSession = Depends(get_db)):
    stmt = select(Complaint).options(
        selectinload(Complaint.chat_messages),
        selectinload(Complaint.audit_logs),
        selectinload(Complaint.capas).selectinload(CAPA.action_items)
    ).order_by(Complaint.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{complaint_id}", response_model=ComplaintRead)
async def get_complaint(complaint_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Complaint).options(
        selectinload(Complaint.chat_messages),
        selectinload(Complaint.audit_logs),
        selectinload(Complaint.capas).selectinload(CAPA.action_items)
    ).filter(Complaint.id == complaint_id)
    result = await db.execute(stmt)
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

@router.get("/{complaint_id}/audit", response_model=List[AuditLogRead])
async def get_complaint_audit(complaint_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(ComplaintFieldAudit).filter(ComplaintFieldAudit.complaint_id == complaint_id).order_by(ComplaintFieldAudit.changed_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/{complaint_id}/status")
async def update_complaint_status(complaint_id: int, status: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Complaint).filter(Complaint.id == complaint_id)
    result = await db.execute(stmt)
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    complaint.status = status
    await db.commit()
    await db.refresh(complaint)
    return {"id": complaint.id, "status": complaint.status}

