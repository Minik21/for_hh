from typing import List, Annotated
from dashboard.models import DashboardOutList
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
import dashboard.services as DashboardService
from fastapi import APIRouter

dashboard_router = APIRouter(prefix='/dashboard', tags=['dashboard'])


@dashboard_router.get("", response_model=DashboardOutList)
async def read_dashboard(current_user: Annotated[User, Depends(get_current_active_user)],
                        year: int ,month: int,
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="organization_id ONLY"),
                        q: str | None = Query(default=None, max_length=100,
                                              description="search by goods name")):
    obj = await DashboardService.read_dashboard(current_user,
                                                  skip, limit, year, month, filter, q)
    return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}

