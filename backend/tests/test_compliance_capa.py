import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database.connection as db_conn
from database.models import Complaint, QASignature, CAPA, CAPAActionItem
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

async def run_compliance_test():
    # Initialize DB (triggers fallback to SQLite if postgres isn't running)
    await db_conn.init_db_tables()
    
    async with db_conn.AsyncSessionLocal() as db:
        # 1. Create a test complaint requiring HITL approval
        test_complaint = Complaint(
            customer_name="St. Jude Hospital",
            product_name="Ciprofloxacin 500mg IV",
            batch_lot_number="CIP-88301",
            complaint_description="Particulate matter observed in IV solution bottle.",
            originating_site_block="Sterile Block B",
            severity="Critical",
            status="Pending QA Signoff",
            likely_root_cause="Sterile filter rupture during filling."
        )
        db.add(test_complaint)
        await db.commit()
        await db.refresh(test_complaint)
        print(f"[TEST] Created Complaint #{test_complaint.id} with status '{test_complaint.status}'")

        # 2. Simulate QA Digital Signature Sign-Off (FDA 21 CFR Part 11)
        sig = QASignature(
            complaint_id=test_complaint.id,
            signer_name="Dr. Sarah Jenkins",
            signer_role="QA Manager",
            signature_meaning="Approval of Complaint Classification, Root Cause & Risk Assessment",
            checksum_hash="b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
            comments="Verified sterile block logs. CAPA initiated."
        )
        db.add(sig)
        test_complaint.status = "QA Approved"
        await db.commit()
        print(f"[TEST] Digital Signature recorded with hash: {sig.checksum_hash[:12]}...")

        # 3. Simulate CAPA Auto-Spawning
        new_capa = CAPA(
            capa_number=f"CAPA-2026-TEST-{test_complaint.id}",
            complaint_id=test_complaint.id,
            title=f"CAPA for Complaint #{test_complaint.id}: Ciprofloxacin 500mg IV",
            description="Particulate matter investigation in Sterile Block B.",
            root_cause="Sterile filter rupture during filling.",
            severity="Critical",
            owner_department="Sterile Block B",
            assignee_name="Dr. Sarah Jenkins",
            status="Open",
            escalation_status="Normal"
        )
        db.add(new_capa)
        await db.flush()

        ai = CAPAActionItem(
            capa_id=new_capa.id,
            action_type="Corrective Action",
            description="Quarantine batch CIP-88301 and inspect filter Integrity.",
            assignee="Sterile Line Supervisor",
            status="Pending"
        )
        db.add(ai)
        await db.commit()
        print(f"[TEST] CAPA task '{new_capa.capa_number}' spawned for department '{new_capa.owner_department}'")

        # 4. Verify Relationships & Queries
        stmt = select(Complaint).options(
            selectinload(Complaint.qa_signatures),
            selectinload(Complaint.capas).selectinload(CAPA.action_items)
        ).filter(Complaint.id == test_complaint.id)

        res = await db.execute(stmt)
        queried = res.scalar_one()

        assert len(queried.qa_signatures) == 1
        assert queried.qa_signatures[0].signer_name == "Dr. Sarah Jenkins"
        assert len(queried.capas) == 1
        assert queried.capas[0].owner_department == "Sterile Block B"
        assert len(queried.capas[0].action_items) == 1
        print("[SUCCESS] All Compliance & CAPA integration assertions passed!")

if __name__ == "__main__":
    asyncio.run(run_compliance_test())
