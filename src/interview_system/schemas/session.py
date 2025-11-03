# src/interview_system/schemas/session.py

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
import uuid

# --- ADD THIS NEW CLASS ---
class ResumeUploadResponse(BaseModel):
    """
    Pydantic model for the response after uploading a resume PDF.
    """
    file_url: HttpUrl = Field(..., description="The public URL of the uploaded resume.")
    file_id: str = Field(..., description="The unique ID for the uploaded file.")
    message: str = "Resume uploaded successfully"

    class Config:
        from_attributes = True
# --- END NEW CLASS ---


class StartInterviewRequest(BaseModel):
    """
    Pydantic model for the request to start a new interview.
    """
    # We use HttpUrl to get Pydantic validation
    file_url: Optional[HttpUrl] = Field(
        None, 
        description="A URL to a PDF resume (e.g., from Cloudinary)."
    )
    resume_text: Optional[str] = Field(
        None, 
        description="Plain text of the resume."
    )
    job_description: Optional[str] = Field(
        None, 
        description="The job description to tailor the interview."
    )

    class Config:
        # This allows the model to work with ORM objects
        from_attributes = True


class StartInterviewResponse(BaseModel):
    """
    Pydantic model for the response after starting an interview.
    """
    session_id: str = Field(..., description="The unique ID for the new session.")
    first_question: str = Field(..., description="The first question for the user.")

    class Config:
        from_attributes = True


class SubmitAnswerRequest(BaseModel):
    """
    Pydantic model for the request to submit an answer.
    """
    answer_text: str = Field(..., description="The user's text answer.")
    # audio_ref: Optional[str] = Field(None, description="Reference to a stored audio file.")

    class Config:
        from_attributes = True


class SubmitAnswerResponse(BaseModel):
    """
    Pydantic model for the response after submitting an answer.
    """
    feedback: str = Field(..., description="Immediate feedback on the answer.")
    next_question: Optional[str] = Field(
        None, 
        description="The next question in the interview."
    )
    follow_up_question: Optional[str] = Field(
        None, 
        description="A follow-up question, if needed."
    )

    class Config:
        from_attributes = True