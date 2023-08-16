from typing import List, Annotated
from sku_report.models import SkuReportList
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
import sku_report.services as SkuReportService
from fastapi import APIRouter

sku_report_router = APIRouter(prefix='/sku_report', tags=['sku_report'])


@sku_report_router.get("", response_model=SkuReportList)
async def read_sku_report(current_user: Annotated[User, Depends(get_current_active_user)],
                        year: int ,month: int,
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="goods_id ONLY")):
    obj = await SkuReportService.read_sku_report(current_user,
                                                  skip, limit, year, month, filter)
    return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}

@sku_report_router.post("")
async def post_update_sku_val(current_user: Annotated[User, Depends(get_current_active_user)],
                        date : str,
                        manager_id : int,
                        manager_gypoties : str | None = None,
                        manager_place_for_request : int | None = None):
    await SkuReportService.post_update_sku_val(current_user, date, manager_id,
                                               manager_gypoties, manager_place_for_request)
    return 200

