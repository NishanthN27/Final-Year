from fastapi import APIRouter

# This is the line that creates the 'router' object that main.py needs.
router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

# Add an example route so the router does something
@router.get("/")
def get_admin_panel():
    return {"message": "Welcome to the admin router!"}