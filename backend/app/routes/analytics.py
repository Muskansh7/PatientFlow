from fastapi import APIRouter
from app.services.analytics_service import analytics_service

router = APIRouter()


@router.get("/")
def get_dashboard_stats():
    return analytics_service.get_dashboard_stats()