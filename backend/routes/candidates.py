from fastapi import APIRouter, HTTPException
from backend.services.candidate_service import get_candidate_journey

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.get("/{candidate_id}")
async def get_candidate(candidate_id: str):
    """Returns candidate journey timeline by candidate_id."""
    journey = get_candidate_journey(candidate_id)
    if not journey:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return journey
