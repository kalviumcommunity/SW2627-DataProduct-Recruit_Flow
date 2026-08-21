from fastapi import APIRouter
from backend.services.analytics_service import get_funnel_summary, get_department_summary, get_role_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/funnel")
async def get_funnel():
    """Returns aggregated recruitment funnel metrics."""
    return get_funnel_summary()

@router.get("/department")
async def get_department():
    """Returns department-wise drop-off rates and comparison against company averages."""
    return get_department_summary()

@router.get("/role")
async def get_role():
    """Drills down into specific roles within departments."""
    return get_role_summary()
