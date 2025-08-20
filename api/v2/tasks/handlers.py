from fastapi import APIRouter

v2_tasks_router = APIRouter(tags=["tasks"], prefix="/tasks")
