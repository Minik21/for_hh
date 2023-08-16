from typing import List, Annotated
from sales_plan.models import SalesPlanList, SalesPlan
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
import sales_plan.services as SalesPlanService
from fastapi import APIRouter

sales_plan_router = APIRouter(prefix='/sales_plan', tags=['sales_plan'])


@sales_plan_router.get("", response_model=SalesPlanList)
async def read_sales_plan_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        year: int ,month: int,
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="goods_id ONLY"),
                        q: str | None = Query(default=None, max_length=100,
                                              description="search by goods name")):
    obj = await SalesPlanService.read_sales_plan_by(current_user,
                                                  skip, limit, filter, year, month, q)
    return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}

@sales_plan_router.patch("", response_model=SalesPlan)
async def create_sales_plan_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        year: int ,month: int,
                        goods_size_id: int, plan_at_month: int):
    obj = await SalesPlanService.put_in_sales_plan(current_user, year,
                                                      month, goods_size_id,
                                                      plan_at_month)
    return obj
