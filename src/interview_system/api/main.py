# src/interview_system/api/main.py

from fastapi import FastAPI
from interview_system.auth import router as auth_router

# Create the FastAPI app instance
app = FastAPI(
    title="Multi-Agentic RAG Interview System",
    description="An AI-powered system to help users prepare for interviews.",
    version="1.0.0"
)

# Include the authentication router
# All routes defined in auth_router will now be part of your application,
# prefixed with /auth (as defined in router.py).
app.include_router(auth_router.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"status": "API is running"}