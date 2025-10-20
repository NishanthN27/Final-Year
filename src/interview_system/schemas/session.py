from pydantic import BaseModel, HttpUrl

class ResumeUploadResponse(BaseModel):
    """
    Defines the response structure after a resume is successfully uploaded.
    """
    message: str
    file_url: HttpUrl

class StartInterviewTextRequest(BaseModel):
    """
    Defines the request for starting an interview with pasted text.
    """
    resume_text: str