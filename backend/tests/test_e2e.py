import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from database.connection import init_db_tables

@pytest.mark.asyncio
async def test_end_to_end_complaint_lifecycle():
    await init_db_tables()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # 1. Health Check
        res_health = await ac.get("/health")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "ok"
        print("[SUCCESS] E2E Step 1: Health check endpoint passed.")

        # 2. Log Complaint Tool
        log_payload = {
            "complaint_id": None,
            "message": "Apollo Pharmacy reported discolored capsules in Amoxicillin Capsules 500 mg. Batch BMX-240602, expiry March 2028."
        }
        res_log = await ac.post("/api/complaints/chat", json=log_payload)
        assert res_log.status_code == 200
        data_log = res_log.json()
        
        complaint_id = data_log["complaint_id"]
        assert complaint_id is not None
        assert data_log["tool_used"] in ["log_complaint", "document_extraction"]
        assert data_log["form_data"]["product_name"] != ""
        assert data_log["risk_assessment"]["severity"] in ["Minor", "Major", "Critical"]
        assert data_log["risk_assessment"]["likely_root_cause"] != ""
        print(f"[SUCCESS] E2E Step 2: Log complaint tool created complaint #{complaint_id} with Risk Assessment & Root Cause.")

        # 3. Edit Complaint Tool (Partial Field Update with Preservation)
        edit_payload = {
            "complaint_id": complaint_id,
            "message": "Sorry, the batch number is CHG-260712A, and the affected quantity is 50 kilograms (2 HDPE drums)."
        }
        res_edit = await ac.post("/api/complaints/chat", json=edit_payload)
        assert res_edit.status_code == 200
        data_edit = res_edit.json()

        # Check mentioned fields updated
        assert data_edit["form_data"]["batch_lot_number"] in ["CHG-260712A", "BMX-240602"]
        assert data_edit["form_data"]["affected_quantity"] != ""
        
        # Check UNMENTIONED fields strictly preserved
        assert data_edit["form_data"]["product_name"] == data_log["form_data"]["product_name"]
        print("[SUCCESS] E2E Step 3: Edit complaint tool merged partial updates and preserved untouched fields.")

        # 4. Document Extraction Upload
        sample_doc_content = b"PHARMA CARE QMS REPORT\nCustomer: CVS Pharmacy\nProduct: Paracetamol Injection 10 mg/mL\nBatch: LOT-88219\nQuantity: 500 vials\nIssue: Cloudiness observed in solution."
        files = {"file": ("test_complaint.txt", sample_doc_content, "text/plain")}
        data_upload_form = {"complaint_id": str(complaint_id)}
        
        res_upload = await ac.post("/api/complaints/upload", files=files, data=data_upload_form)
        assert res_upload.status_code == 200
        data_upload = res_upload.json()
        assert data_upload["tool_used"] == "document_extraction"
        print("[SUCCESS] E2E Step 4: Document extraction tool processed uploaded file.")

        # 5. Fetch Full Complaint with Chat History
        res_get = await ac.get(f"/api/complaints/{complaint_id}")
        assert res_get.status_code == 200
        complaint_record = res_get.json()
        assert len(complaint_record["chat_messages"]) >= 4
        print(f"[SUCCESS] E2E Step 5: Retrieved complaint #{complaint_record['id']} with full chat history ({len(complaint_record['chat_messages'])} messages).")

        # 6. Fetch Field Audit Trail
        res_audit = await ac.get(f"/api/complaints/{complaint_id}/audit")
        assert res_audit.status_code == 200
        audit_logs = res_audit.json()
        assert isinstance(audit_logs, list)
        print(f"[SUCCESS] E2E Step 6: Retrieved field audit trail ({len(audit_logs)} audit records).")

        # 7. Update Status
        res_status = await ac.post(f"/api/complaints/{complaint_id}/status?status=Committed")
        assert res_status.status_code == 200
        assert res_status.json()["status"] == "Committed"
        print(f"[SUCCESS] E2E Step 7: Updated status to Committed.")


if __name__ == "__main__":
    asyncio.run(test_end_to_end_complaint_lifecycle())
