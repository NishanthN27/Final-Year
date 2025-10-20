from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from interview_system.auth.dependencies import get_current_user
from interview_system.schemas.session import ResumeUploadResponse # We'll update this schema next
from interview_system.services.cloudinary_service import upload_resume_file

router = APIRouter(
    prefix="/session",
    tags=["Session Management"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/upload_resume",
    response_model=ResumeUploadResponse,
    summary="Upload a Resume File to Cloudinary"
)
async def upload_resume(
    file: UploadFile = File(..., description="The candidate's resume (PDF or DOCX)."),
    current_user: dict = Depends(get_current_user),
):
    """
    Handles the upload of a user's resume to Cloudinary.

    - **Authenticates** the user.
    - **Validates** file type and size.
    - **Uploads** the file to a secure, user-specific folder.
    - **Returns** a confirmation message and the secure URL of the file.
    """
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Please upload a PDF or DOCX file."
        )

    file_contents = await file.read()
    
    if len(file_contents) > 5 * 1024 * 1024: # 5 MB limit
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 5MB limit."
        )

    # Call the simplified service
    file_url = await upload_resume_file(
        file_contents=file_contents,
        file_name=file.filename,
        user_id=str(current_user["user_id"]) # Assumes the fix for 'sub' key is in place
    )

    return ResumeUploadResponse(
        message="Resume uploaded successfully.",
        file_url=file_url
    )