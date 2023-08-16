from typing import List, Annotated
# from union_report.models import unionreportIn, unionreportOut, unionreportUpdate, UnionReportOutList
from union_report.models import UnionReportOutList
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
import union_report.services as UnionReportService

from fastapi import APIRouter

union_report_router = APIRouter(prefix='/union_report', tags=['union_report'])


@union_report_router.get("", response_model=UnionReportOutList)
async def read_union_report_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        year: int ,month: int | None = None,
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="union_report.created_at, goods.id ONLY")):
  obj = await UnionReportService.read_union_report_by(current_user,
                                                    skip, limit, filter, year, month)
  return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}