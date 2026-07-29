import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database.connection import init_db_tables
from routes import complaints, chat, capa

app = FastAPI(
    title="Pharma QMS Complaint API",
    description="Secure Backend API for Customer Complaint Management System in Pharma QMS",
    version="1.0.0"
)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Configure CORS Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db():
    await init_db_tables()

app.include_router(complaints.router)
app.include_router(chat.router)
app.include_router(capa.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "Pharma QMS Complaint System"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
