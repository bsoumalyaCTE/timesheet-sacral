from fastapi import APIRouter

project_router = APIRouter(prefix="/projects", tags=["Projects"])

@project_router.get("/timesheet")
async def get_timesheet():
    return {"timesheet": "This is a timesheet"}