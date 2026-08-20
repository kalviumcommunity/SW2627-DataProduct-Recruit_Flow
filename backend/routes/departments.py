from fastapi import APIRouter

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("/")
async def get_departments():
    """Returns department summary placeholder."""
    return {"message": "Department analysis endpoints ready"}
