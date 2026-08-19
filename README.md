# Pharma QMS Complaint Hub — AI-Powered Customer Complaint Management System
**(Pharmaceutical Manufacturing Quality Management System)**

An AI-driven Quality Management System (QMS) application built for pharmaceutical FDF / Sterile / API customer complaint processing and automated triage.

---

## 🌐 Live Production Links

- **Live Frontend Web App**: [https://health-care-five-rosy.vercel.app](https://health-care-five-rosy.vercel.app) *(Vercel CDN)*
- **Live Backend API**: [https://health-care-t51v.onrender.com](https://health-care-t51v.onrender.com) *(Render FastAPI)*
- **Live Cloud Database**: Supabase PostgreSQL Cloud
- **GitHub Repository**: [https://github.com/NAMANSAINI62/Health_care.git](https://github.com/NAMANSAINI62/Health_care.git)

---

### 🌟 Core Paradigm: 100% Agent-Driven Form Population
The left-hand complaint form is **read-only output**. Users never manually type into form inputs. All form entries, partial edits, QMS risk assessments, root cause predictions, and document extractions are orchestrated by the **LangGraph AI Co-Pilot** in the right panel through natural language chat or document uploads (`.pdf`, `.txt`, `.eml`, `.doc`, `.docx`).

---

## 🏗️ Architecture Overview

### LangGraph Agent Orchestration Flow

```
                         [ USER MESSAGE / FILE UPLOAD ]
                                       │
                                       ▼
                              intent_router_node
             (LLM classifies: log / edit / document_extraction)
             ┌─────────────────────────┼────────────────────────┐
             ▼                         ▼                        ▼
    log_complaint_node        edit_complaint_node     document_extraction_node
  (Extracts 12 fields)      (Merges ONLY diff with  (Parses doc text & extracts
                             existing DB complaint)        fresh fields)
             └─────────────────────────┬────────────────────────┘
                                       ▼
                             risk_assessment_node
                 (LLM computes: Severity, Suggested Action,
                 Risk Narrative, & Likely Root Cause [Bonus])
                                       │
                                       ▼
                           response_formatter_node
                  (Generates natural confirmation reply)
                                       │
                                       ▼
                                 persist_node
                 (Saves complaint, audit log & chat history)
                                       │
                                       ▼
                                [ FRONTEND API ]
```

---

## ✨ Features & Key Capabilities

1. **12-Field Data Extraction & Inference**: Automatically extracts/infers: `Complaint Source`, `Customer Name`, `Product Name`, `Dosage/Strength`, `Batch/Lot Number`, `Manufacturing Date`, `Expiry Date`, `Affected Quantity`, `Complaint Category`, `Manufacturing Site/Block`, `Impacted Non-Product Material`, and `Detailed Description`.
2. **Partial Field Editing & State Preservation**: Updates *only* explicitly requested fields while strictly preserving untouched fields.
3. **QMS Risk Assessment Engine & Root Cause Recommendation (Bonus Feature)**: Computes Severity (`Minor`, `Major`, `Critical`), Suggested QMS Action, Risk Narrative, and **Predicted Root Cause**.
4. **QMS Field Audit Trail Modal**: Tracks field mutations (`old_value` $\rightarrow$ `new_value`, `changed_by`, `timestamp`) with timestamps formatted in **Indian Standard Time (Asia/Kolkata)** without seconds.
5. **Zero-Data-Loss Refresh Persistence (F5)**: Stores active `complaint_id` in `localStorage` and auto-hydrates state and full chat history on reload.
6. **Dynamic Draggable Splitter**: Left and Right panels are separated by a resizable divider handle with smooth vertical scrolling for the form.
7. **Soft Light Sky-Blue Theme & Pill Action Buttons**: Clean enterprise light theme with pill-shaped action buttons and 10 ready-to-click quick prompts.

---

## 🛡️ Security Hardening

1. **Prompt Injection Guardrails**: User inputs and document text are enclosed in `<user_input>...</user_input>` XML tags with strict system instructions treating enclosed content purely as data.
2. **File Upload Security**: Enforces 5MB maximum file size limit and strict extension whitelisting (`.pdf`, `.txt`, `.eml`, `.doc`, `.docx`).
3. **API Rate Limiting**: In-memory IP rate limiter restricting API calls to **5 requests per minute per IP** (HTTP 429 on limit breach).
4. **HTTP Security Headers & CORS**: Injects `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, and `Referrer-Policy` security headers.

---

## 🛠️ Tech Stack

- **Frontend:** React 18 + Redux Toolkit + Lucide Icons + Google Inter Font
- **Backend:** Python 3.11 + FastAPI + SQLAlchemy (Async) + Uvicorn
- **AI Agent:** LangGraph (`StateGraph`) + Groq API (`llama-3.3-70b-versatile`)
- **Database:** PostgreSQL / SQLite Dual-Fallback Engine (`complaints`, `complaint_chat_messages`, `complaint_field_audit`)

---

## 🚀 Quick Local Setup

### 1. Environment Configuration
Create `backend/.env`:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL_PRIMARY=llama-3.3-70b-versatile
DATABASE_URL=postgresql+asyncpg://postgres:postgrespassword@localhost:5400/aivoa_complaints
```

Create `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 2. Run Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 3. Run Frontend (React Vite)
```bash
cd frontend
npm install
npm run dev
```
Access the application at `http://localhost:5173`.

---

## 🌐 Cloud Deployment Architecture

| Component | Host | Live Production URL | Build Command / Config |
| :--- | :--- | :--- | :--- |
| **Frontend (React)** | **Vercel** | [https://health-care-five-rosy.vercel.app](https://health-care-five-rosy.vercel.app) | Framework: `Vite`, Root: `frontend`, Build: `npm run build` |
| **Backend (FastAPI)** | **Render** | [https://health-care-t51v.onrender.com](https://health-care-t51v.onrender.com) | Root: `backend`, Build: `pip install -r requirements.txt`, Start: `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Database (PostgreSQL)** | **Supabase** | `aws-1-ap-south-1.pooler.supabase.com:6543` | PostgreSQL Connection URI (`postgresql+asyncpg://...`) |

---

## 📋 Database Schema

```sql
CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    complaint_source VARCHAR(50),
    customer_name VARCHAR(255),
    product_name VARCHAR(255),
    product_strength VARCHAR(100),
    batch_lot_number VARCHAR(100),
    manufacturing_date VARCHAR(50),
    expiry_date VARCHAR(50),
    affected_quantity VARCHAR(100),
    complaint_category VARCHAR(150),
    complaint_description TEXT,
    originating_site_block VARCHAR(150),
    impacted_npm VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Pending Triage',
    severity VARCHAR(50),
    suggested_next_action VARCHAR(255),
    initial_risk_assessment TEXT,
    likely_root_cause TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE complaint_chat_messages (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES complaints(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE complaint_field_audit (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES complaints(id) ON DELETE CASCADE,
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(20) DEFAULT 'ai_agent',
    changed_at TIMESTAMP DEFAULT NOW()
);
```
