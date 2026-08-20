from fastapi import APIRouter
from backend.services.analytics_service import get_funnel_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/funnel")
async def get_funnel():
    """Returns aggregated recruitment funnel metrics."""
    return get_funnel_summary()
