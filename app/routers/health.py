"""Endpoint definition for health"""

from fastapi import APIRouter


router = APIRouter(
    prefix="/health",
)


@router.get("", tags=["Health Check"])
def health_endpoint():
    """Health Endpoint"""
    return {"status": "OK"}
