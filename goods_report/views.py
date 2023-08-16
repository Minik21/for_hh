from typing import List, Annotated
# from goods_report.models import GoodsreportIn, GoodsreportOut, GoodsreportUpdate, GoodsreportOutList
from goods_report.models import GoodsReportOut, GoodsReportOutList
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
import goods_report.services as GoodsReportService
from datetime import datetime, timedelta
from fastapi import APIRouter

goods_report_router = APIRouter(prefix='/goods_report', tags=['goods_report'])


@goods_report_router.get("", response_model=GoodsReportOutList)
async def read_good_report_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        skip: int = 0, limit: int | None = 100,
                        date: str | None = Query(default=None,
                                                max_length=10,
                                                description="YYYY-MM-DD format only"),
                        filter: str | None = Query(default=None, max_length=100,
                                              description="goods_id ONLY")):
  obj = await GoodsReportService.read_good_report_by(current_user,
                                                    skip, limit, filter, date)
  return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}
