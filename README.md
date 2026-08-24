# 🏥 Pharma QMS Complaint Hub — AI-Powered Quality Management System

**Pharmaceutical Manufacturing Quality Management System (FDA 21 CFR Part 11 Compliant)**

An end-to-end AI-driven Quality Management System (QMS) for pharmaceutical FDF / Sterile / API customer complaint processing, automated triage, and CAPA management powered by a **LangGraph AI Agent**.

---

## 🌐 Live Production Links

| Service | URL |
| :--- | :--- |
| **Frontend (React + Vite)** | [https://health-care-five-rosy.vercel.app](https://health-care-five-rosy.vercel.app) *(Vercel CDN)* |
| **Backend API (FastAPI)** | [https://health-care-t51v.onrender.com](https://health-care-t51v.onrender.com) *(Render)* |
| **Cloud Database** | Supabase PostgreSQL Cloud |
| **GitHub Repository** | [https://github.com/NAMANSAINI62/Health_care](https://github.com/NAMANSAINI62/Health_care) |

---

## 🌟 Core Paradigm: 100% Agent-Driven Form Population

The left-hand complaint form is **read-only output**. Users **never manually type** into form fields. All form entries, partial edits, QMS risk assessments, root cause predictions, and document extractions are fully orchestrated by the **LangGraph AI Co-Pilot** in the right chat panel via natural language conversation or document uploads (`.pdf`, `.txt`, `.eml`, `.doc`, `.docx`).

---

## ✨ Features & Key Capabilities

### 🤖 AI Agent (LangGraph)
1. **12-Field Intelligent Extraction & Inference** — Automatically extracts/infers: `Complaint Source`, `Customer Name`, `Product Name`, `Dosage/Strength`, `Batch/Lot Number`, `Manufacturing Date`, `Expiry Date`, `Affected Quantity`, `Complaint Category`, `Manufacturing Site/Block`, `Impacted NPM`, and `Detailed Description`.
2. **Partial Field Editing & State Preservation** — Updates *only* explicitly requested fields while strictly preserving all untouched data.
3. **QMS Risk Assessment Engine** — Computes Severity (`Minor`, `Major`, `Critical`), Suggested QMS Action, Risk Narrative, and **Predicted Root Cause**.
4. **Document Extraction Mode** — Parses uploaded PDF/TXT/EML/DOC/DOCX files and auto-populates complaint form fields.

### 📋 CAPA Management
8. **Automated CAPA Generation** — Auto-spawns structured CAPA records with corrective & preventive action items for Critical/Major severity complaints.
9. **CAPA Lifecycle Tracking** — Full CAPA workflow: `Open -> In Progress -> Completed`, with individual action item completion tracking.
10. **CAPA Escalation Engine** — Escalate overdue CAPAs to `Escalated - Level 1/2/3` with automated audit trail entries.

### 🛡️ Compliance & Audit (FDA 21 CFR Part 11)
11. **Immutable Field Audit Trail** — Tracks every field mutation (`old_value -> new_value`, `changed_by`, `timestamp`) formatted in **Indian Standard Time (IST)**.
12. **Zero-Data-Loss F5 Refresh** — Persists active `complaint_id` in `localStorage` and auto-hydrates full state and chat history on page reload.

### 🎨 UI/UX
14. **Dynamic Draggable Splitter** — Left/right panels separated by a resizable divider with smooth scrolling.
15. **Soft Sky-Blue Enterprise Theme** — Clean light theme with pill-shaped action buttons and 10 ready-to-click quick-prompt chips.

---

## 🏗️ Architecture Overview

### LangGraph Agent Orchestration Flow

```
                     [ USER MESSAGE / FILE UPLOAD ]
                                    |
                                    v
                           intent_router_node
          (LLM classifies: log_complaint / edit_complaint / document_extraction)
          +-------------------------+-----------------------+
          v                         v                       v
 log_complaint_node       edit_complaint_node    document_extraction_node
 (Extracts 12 fields)   (Merges ONLY diff with  (Parses doc text & extracts
                         existing DB complaint)        fresh fields)
          +-------------------------+-----------------------+
                                    v
                          risk_assessment_node
              (LLM computes: Severity, Suggested Action,
              Risk Narrative, & Likely Root Cause)
                                    |
                                    v
                        response_formatter_node
               (Generates natural confirmation reply)
                                    |
                                    v
                              [DB Persist]
             (Saves complaint, audit log, and chat history)
                                    |
                                    v
                             [ FRONTEND API ]
```

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 18, Redux Toolkit, Vite, Lucide Icons, Google Inter Font |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy (Async), Uvicorn |
| **AI Agent** | LangGraph `StateGraph`, HuggingFace Inference API (`Qwen/Qwen2.5-Coder-32B-Instruct`) |
| **LLM Integration** | LangChain Core, `JsonOutputParser` |
| **Database** | PostgreSQL (Supabase Cloud) / SQLite dual-fallback engine |
| **Document Parsing** | PyPDF (`pypdf`), plain-text / EML fallback |
| **PDF Generation** | FPDF2 + Pillow |
| **Deployment** | Vercel (Frontend), Render (Backend), Supabase (PostgreSQL) |

---

## 📁 Project Structure

```
Health_care/
├── backend/
│   ├── main.py                    # FastAPI app entry point, CORS, security headers
│   ├── config.py                  # Settings (HF_API_KEY, DATABASE_URL, model names)
│   ├── requirements.txt           # Python dependencies
│   ├── agents/
│   │   ├── graph.py               # LangGraph StateGraph definition
│   │   ├── llm.py                 # HuggingFace LLM caller with prompt injection guard
│   │   ├── prompts.py             # All LLM system & user prompt templates
│   │   ├── state.py               # ComplaintAgentState TypedDict
│   │   └── nodes/
│   │       ├── intent_router.py           # Classifies user intent
│   │       ├── log_complaint_tool.py      # Extracts 12 fields from user message
│   │       ├── edit_complaint_tool.py     # Merges partial field edits
│   │       ├── document_extraction_tool.py # Parses uploaded document text
│   │       ├── risk_assessment_node.py    # Computes severity & root cause
│   │       └── response_formatter.py     # Formats natural language reply
│   ├── routes/
│   │   ├── complaints.py          # CRUD, QA sign-off, audit trail
│   │   ├── chat.py                # AI chat & document upload endpoints
│   │   └── capa.py                # CAPA lifecycle & escalation endpoints
│   ├── database/
│   │   ├── connection.py          # Async SQLAlchemy engine & session
│   │   └── models.py              # ORM models (Complaint, CAPA, Audit, Chat, QASignature)
│   └── schemas/
│       └── complaint_schema.py    # Pydantic request/response schemas
└── frontend/
    ├── src/
    │   ├── App.jsx                # Root app with draggable splitter layout
    │   ├── main.jsx               # React entry point
    │   ├── index.css              # Global styles (sky-blue enterprise theme)
    │   ├── api/                   # Axios API service layer
    │   ├── redux/                 # Redux Toolkit store & slices
    │   └── components/
    │       ├── Header/            # App header with nav
    │       ├── ComplaintForm/     # Read-only AI-populated form
    │       ├── CopilotChat/       # AI chat panel with file upload
    │       ├── RiskAssessmentPanel/  # Severity, root cause, actions
    │       ├── CapaDashboard/     # CAPA list with filters
    │       ├── CapaDetailModal/   # CAPA detail & action items
    │       ├── AuditLogModal/     # Field mutation history
    │       ├── DigitalSignatureModal/ # FDA 21 CFR Part 11 QA sign-off
    │       └── StatusPill/        # Complaint status badge
    ├── package.json
    └── vite.config.js
```

---

## 🛡️ Security Hardening

| # | Security Control | Implementation |
| :--- | :--- | :--- |
| 1 | **Prompt Injection Guardrails** | User inputs wrapped in `<user_input>...</user_input>` XML tags with strict system instructions to treat enclosed content purely as data |
| 2 | **File Upload Validation** | 5 MB max file size + strict extension whitelist (`.pdf`, `.txt`, `.eml`, `.doc`, `.docx`) |
| 3 | **API Rate Limiting** | In-memory IP rate limiter — **5 requests/minute/IP** → HTTP 429 on breach |
| 4 | **HTTP Security Headers** | `X-Content-Type-Options`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Referrer-Policy` injected on every response |
| 5 | **Input Length Cap** | Chat messages capped at **5,000 characters** → HTTP 400 on breach |
| 6 | **CORS Policy** | Restricted to approved frontend origins only |

---

## 🚀 Quick Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or use the built-in SQLite fallback)

### 1. Clone the Repository
```bash
git clone https://github.com/NAMANSAINI62/Health_care.git
cd Health_care
```

### 2. Configure Environment Variables

**`backend/.env`**
```env
HF_API_KEY=hf_your_huggingface_api_key_here
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/aivoa_complaints
HF_MODEL_PRIMARY=Qwen/Qwen2.5-Coder-32B-Instruct
```

> **Note:** Get a free HuggingFace API key at [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

**`frontend/.env`**
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Run Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python main.py
# or: uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Run Frontend (React Vite)
```bash
cd frontend
npm install
npm run dev
```
Access the app at **`http://localhost:5173`**

---

## 🌐 Cloud Deployment Architecture

| Component | Host | URL | Config |
| :--- | :--- | :--- | :--- |
| **Frontend (React)** | Vercel | [health-care-five-rosy.vercel.app](https://health-care-five-rosy.vercel.app) | Framework: `Vite`, Root: `frontend/`, Build: `npm run build` |
| **Backend (FastAPI)** | Render | [health-care-t51v.onrender.com](https://health-care-t51v.onrender.com) | Root: `backend/`, Build: `pip install -r requirements.txt`, Start: `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Database** | Supabase | PostgreSQL Cloud | Connection via `postgresql+asyncpg://...` URI |

---

## 📡 API Endpoints Reference

### Complaints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/complaints` | List all complaints (ordered by updated_at desc) |
| `GET` | `/api/complaints/{id}` | Get single complaint with full relations |
| `GET` | `/api/complaints/{id}/audit` | Get field-level audit trail |
| `POST` | `/api/complaints/{id}/status` | Update complaint status |

### AI Chat & Document Upload
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/complaints/chat` | Send message to LangGraph AI Co-Pilot |
| `POST` | `/api/complaints/upload` | Upload document for AI extraction |

### CAPA Management
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/capas` | List CAPAs (filter by dept/status/severity) |
| `GET` | `/api/capas/{id}` | Get CAPA detail with action items |
| `POST` | `/api/capas` | Create new CAPA |
| `PUT` | `/api/capas/{id}` | Update CAPA fields |
| `POST` | `/api/capas/{id}/action-items` | Add action item to CAPA |
| `PUT` | `/api/capas/action-items/{id}` | Toggle action item status |
| `POST` | `/api/capas/{id}/escalate` | Escalate overdue CAPA |

### Health
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | API health check |

---

## 📦 Python Dependencies

```
fastapi>=0.100.0
uvicorn[standard]>=0.22.0
pydantic>=2.0
sqlalchemy>=2.0.0
asyncpg>=0.28.0
aiosqlite>=0.19.0
psycopg2-binary>=2.9.6
python-dotenv>=1.0.0
langgraph>=0.1.0
langchain-core>=0.2.0
langchain-huggingface
python-multipart>=0.0.6
pypdf>=3.10.0
fpdf2>=2.7.0
Pillow>=10.0.0
```

---

*Built with love for pharmaceutical quality management compliance.*
