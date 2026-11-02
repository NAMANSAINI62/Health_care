# 🏥 Pharma QMS Complaint Hub — AI-Powered Quality Management System

**Pharmaceutical Manufacturing Quality Management System (FDA 21 CFR Part 11 Compliant)**

An end-to-end, AI-driven Quality Management System (QMS) for Active Pharmaceutical Ingredient (API) customer complaint processing, automated triage and risk assessment.

---

## 🌐 Live Production Links

| Service | Platform | URL |
| :--- | :--- | :--- |
| **Frontend UI** | Vercel (React 18 + Vite) | [https://health-care-five-rosy.vercel.app](https://health-care-five-rosy.vercel.app) |
| **Backend API** | Render (FastAPI + SlowAPI) | [https://health-care-t51v.onrender.com](https://health-care-t51v.onrender.com) |
| **Cloud Database** | Supabase Cloud | Managed PostgreSQL (Async via `asyncpg`) |
| **Source Code** | GitHub | [https://github.com/NAMANSAINI62/Health_care](https://github.com/NAMANSAINI62/Health_care) |

---

## 🌟 Core Paradigm: 100% Agent-Driven Form Population

The left-hand complaint form is a **read-only reactive display**. Regulatory operators and QA specialists **never manually type** into form fields. All form entries, partial edits, QMS risk assessments, root cause determinations, and document extractions are orchestrated by the **LangGraph AI Co-Pilot** in the right-hand chat panel via natural language conversation or direct document uploads (`.pdf`, `.txt`, `.eml`, `.doc`, `.docx`).

---

## ✨ Features & Capabilities

### 🤖 AI Agent Workflow (LangGraph & LangChain)
1. **12-Field Intelligent Extraction & Inference** — Extracts and normalizes:
   - `Complaint Source`, `Customer Name`, `Product Name`, `Dosage/Strength`
   - `Batch/Lot Number`, `Manufacturing Date`, `Expiry Date`, `Affected Quantity`
   - `Complaint Category`, `Originating Site/Block`, `Impacted NPM`, `Detailed Description`
2. **Partial Field Editing with State Preservation** — Allows operators to request changes to specific fields (e.g., *"Update batch to B-8821 and quantity to 150 vials"*). The agent merges only the requested differences while strictly maintaining all existing complaint data.
3. **In-Memory Document Extraction (Zero-RAG)** — Directly parses uploaded regulatory documents in RAM with `pypdf`, feeding structured text chunks into the LangGraph extraction pipeline without needing vector databases or embedding indexing.
4. **Resilient Multi-LLM Fallback** — Employs Groq (`qwen/qwen3.8-27b`) as the ultra-fast primary inference engine with automated fallback to Google Gemini (`gemini-flash-lite-latest`) using `ChatModel.with_fallbacks()`.
5. **QMS Risk & Prevention Engine** — Predicts root causes and suggests corrective/preventive actions (CAPA-aligned guidance) based on pharmaceutical quality standards.

### 🛡️ Enterprise Security & Authentication
1. **HttpOnly Cookie-Based JWT Auth** — Authentication tokens are stored in `HttpOnly`, `SameSite=Lax` cookies rather than `localStorage`. This completely eliminates token theft risks via Cross-Site Scripting (XSS).
2. **SlowAPI Rate Limiting** — Dedicated brute-force defense throttling:
   - `/api/auth/login`: **5 requests/minute/IP**
   - `/api/auth/register`: **5 requests/minute/IP**
   - `/api/complaints/chat`: **5 requests/minute/IP**
3. **Anti-Injection & Input Sanitization** — Username inputs enforce strict regex filters (`^[a-zA-Z0-9_.\-]+$`), email strings are validated via RFC-compliant `EmailStr`, and SQL injection characters are blocked before reaching database queries.
4. **Anti-Enumeration Safeguards** — Generic authentication responses prevent attackers from discovering registered user emails or usernames.
5. **Prompt Injection Guardrails** — User inputs are wrapped in strict XML data boundaries (`<user_input>...</user_input>`) with system instructions to treat content purely as literal data.
6. **HTTP Security Headers** — Injected on every response: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, and `Referrer-Policy: strict-origin-when-cross-origin`.

### 📋 Compliance & Regulatory Audit (FDA 21 CFR Part 11)
1. **Immutable Field-Level Audit Trail** — Automatically captures every mutation (`field_name`, `old_value`, `new_value`, `changed_by`, `timestamp`) formatted in **Indian Standard Time (IST)**.
2. **Zero-Data-Loss Hydration** — Active complaint context is retained across browser reloads via automated state hydration.
3. **Session Verification** — Automatic `/api/auth/me` background verification on application load with user profile badge and logout controls.

### 🎨 Enterprise UI/UX
1. **Interactive Draggable Split Pane** — Left form and right chat separated by a draggable splitter with smooth scrolling.
2. **Dedicated Authentication Gate** — Modern tabbed login and registration interface with error handling and validation.
3. **Quick-Prompt Suggestions** — One-click buttons to accelerate standard complaint ingestion.

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
 (Extracts 12 fields)   (Merges ONLY diff with  (Parses in-memory doc text &
                         existing DB complaint)    extracts fresh fields)
          +-------------------------+-----------------------+
                                    v
                          risk_assessment_node
              (LLM predicts: Prevention & Corrective Action,
               Likely Root Cause, & Risk Narrative)
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

## 🛡️ Security Hardening Matrix

| # | Security Control | Threat Mitigated | Technical Implementation |
| :--- | :--- | :--- | :--- |
| 1 | **HttpOnly Cookies** | XSS Token Theft | JWT stored in `HttpOnly`, `SameSite=Lax`, `Secure` cookies (`path="/"`) |
| 2 | **SlowAPI Rate Limiting** | Brute Force & Credential Stuffing | IP-based limits: 5 req/min on `/login` and `/register` |
| 3 | **Input Validation & Regex** | SQL Injection & Payload Injections | Pydantic v2 schemas + regex pattern `^[a-zA-Z0-9_.\-]+$` |
| 4 | **Anti-Enumeration** | User Harvesting / Enumeration | Uniform error details on failed auth attempts |
| 5 | **Prompt Injection Guardrails** | LLM Jailbreak & Instruction Hijacking | Enclosed in `<user_input>` XML tags with strict system delimiters |
| 6 | **In-Memory File Parsing** | Shell Execution & Disk Tampering | Direct RAM extraction via `pypdf` with 5 MB cap & extension whitelist |
| 7 | **HTTP Security Headers** | MIME Sniffing, Clickjacking, XSS | `X-Content-Type-Options`, `X-Frame-Options: DENY`, `X-XSS-Protection` |
| 8 | **Strict CORS Policy** | Unauthorized Cross-Origin Requests | Whitelisted origins with `allow_credentials=True` |

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 18, Vite, Redux Toolkit, Lucide React
| **Backend** | Python 3.11+, FastAPI (Modern `lifespan` handler), SQLAlchemy (Async)
| **Rate Limiter** | SlowAPI (IP-keyed rate limiting with automated 429 handlers) |
| **AI Orchestration** | LangGraph `StateGraph`, LangChain Core |
| **Inference Engines** | Groq (`qwen/qwen3.8-27b`) primary + Google Gemini (`gemini-flash-lite-latest`) fallback |
| **Database** | PostgreSQL on Supabase Cloud (async connection via `asyncpg` + `greenlet`) |
| **Auth & Security** | Passlib (Bcrypt password hashing), Python-Jose (JWT), HttpOnly Cookies |
| **Document Parsing** | In-Memory PyPDF (`pypdf`), Plain-Text, EML |
| **Deployment** | Vercel (Frontend), Render (Backend), Supabase (PostgreSQL) |

---

## 📁 Project Structure

```
Health_care/
├── backend/
│   ├── main.py                     # FastAPI entrypoint, lifespan startup, CORS, SlowAPI & security headers
│   ├── config.py                   # Environment settings (GROQ, GEMINI, DATABASE_URL)
│   ├── limiter.py                  # SlowAPI centralized rate limiter instance
│   ├── requirements.txt            # Backend Python dependencies
│   ├── agents/
│   │   ├── graph.py                # LangGraph StateGraph workflow definition
│   │   ├── llm.py                  # Groq + Gemini LLM fallback chain
│   │   ├── prompts.py              # System prompts & XML data boundaries
│   │   ├── state.py                # ComplaintAgentState TypedDict
│   │   └── nodes/
│   │       ├── intent_router.py            # Intent classification node
│   │       ├── log_complaint_tool.py       # 12-field extraction node
│   │       ├── edit_complaint_tool.py      # Partial edit & diff merge node
│   │       ├── document_extraction_tool.py  # In-memory document parser node
│   │       ├── risk_assessment_node.py     # QMS risk & root cause analysis
│   │       └── response_formatter.py      # Natural language confirmation builder
│   ├── auth/
│   │   ├── security.py             # Bcrypt hashing & JWT token generation
│   │   └── dependencies.py         # Cookie-based current user extraction dependency
│   ├── routes/
│   │   ├── auth_routes.py          # /register, /login (rate-limited), /me, /logout
│   │   ├── complaints.py           # Complaint CRUD and field audit logs
│   │   └── chat.py                 # AI copilot chat & in-memory document upload
│   ├── database/
│   │   ├── connection.py           # Async SQLAlchemy engine & session maker
│   │   └── models.py               # ORM Models (User, Complaint, ChatMessage, AuditLog)
│   └── schemas/
│       └── complaint_schema.py     # Pydantic validation & response models
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Application layout, auth gating, draggable divider
│   │   ├── main.jsx                # React DOM entrypoint
│   │   ├── index.css               # Sky-blue enterprise theme styling
│   │   ├── api/
│   │   │   └── complaintsApi.js    # Axios client with credentials (cookies) enabled
│   │   ├── redux/
│   │   │   ├── store.js            # Redux Toolkit store configuration
│   │   │   ├── authSlice.js        # Auth state, user profile & session management
│   │   │   ├── complaintSlice.js   # 12-field form data & risk state
│   │   │   └── chatSlice.js        # Chat messages, streaming & upload state
│   │   └── components/
│   │       ├── Header/             # Brand header, user profile badge, logout & audit trigger
│   │       ├── AuthScreen/         # Sign In / Create Account modal
│   │       ├── ComplaintForm/      # 12-field AI-populated read-only QMS form
│   │       ├── CopilotChat/        # AI Copilot chat panel with document upload
│   │       ├── RiskAssessmentPanel/# Root cause analysis & preventive solutions
│   │       └── AuditLogModal/      # timestamped history
│   ├── package.json
│   └── vite.config.js
├── pyrightconfig.json              # IDE Pyright type-checker configuration
└── requirements.txt                # Root production dependencies
```

---

## 📡 API Reference

### 🔐 Authentication (`/api/auth`)
| Method | Endpoint | Rate Limit | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | 5 / min | Register new user with username, email, and password |
| `POST` | `/api/auth/login` | 5 / min | Authenticate user and issue secure `HttpOnly` cookie |
| `GET` | `/api/auth/me` | — | Retrieve current authenticated user session |
| `POST` | `/api/auth/logout` | — | Invalidate and clear the `HttpOnly` session cookie |

### 📋 Complaints Management (`/api/complaints`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/complaints` | Retrieve all complaints (ordered by latest update) |
| `GET` | `/api/complaints/{id}` | Retrieve specific complaint with chat history and audit logs |
| `GET` | `/api/complaints/{id}/audit` | Retrieve field-level audit trail |

### 🤖 AI Copilot & Document Upload
| Method | Endpoint | Rate Limit | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/complaints/chat` | 5 / min | Send conversation message to the LangGraph AI Co-Pilot |
| `POST` | `/api/complaints/upload` | 5 / min | Upload PDF/document for direct in-memory AI extraction |

### 🩺 System Health
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Check API server status and connection health |

---

## 🚀 Quick Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL database (e.g., Supabase Cloud)

### 1. Clone the Repository
```bash
git clone https://github.com/NAMANSAINI62/Health_care.git
cd Health_care
```

### 2. Configure Environment Variables

**`backend/.env`**
```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@your-supabase-host:5432/postgres
JWT_SECRET_KEY=your-super-secret-jwt-key
ENV=development
```

> **API Key Tips:** Get a free Groq key at [console.groq.com](https://console.groq.com) and a Gemini key at [aistudio.google.com](https://aistudio.google.com).

**`frontend/.env`**
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Run Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python main.py
# Server starts at http://127.0.0.1:8000
```

### 4. Run Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
# App opens at http://localhost:5173
```