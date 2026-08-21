from fastapi import APIRouter
from backend.services.analytics_service import (
    get_funnel_summary,
    get_department_summary,
    get_role_summary,
    get_reasons_summary,
    get_dropoff_summary
)

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

@router.get("/reasons")
async def get_reasons():
    """Returns aggregated candidate rejection/drop-off reasons."""
    return get_reasons_summary()

@router.get("/dropoff")
async def get_dropoff():
    """Returns drop-off reason cross-tabulation by stage and department."""
    return get_dropoff_summary()

