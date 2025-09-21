from fastapi import APIRouter

# This is the line that creates the 'router' object that main.py needs.
router = APIRouter(
    prefix="/interview",
    tags=["Interview"],
)

# Add an example route so the router does something
@router.get("/")
def get_interview_details():
    return {"message": "Welcome to the interview router!"}