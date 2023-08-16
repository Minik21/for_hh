from pydantic import BaseModel
from typing import Optional
from users.models import Meta
from goods.models import GoodsOut
from goods_size.models import GoodsSizeOut
from datetime import datetime


class GoodsReportOut(BaseModel):
    id : int
    # goods_size_id: int
    goods_size: GoodsSizeOut
    # goods_id: int
    goods: GoodsOut
    orders_rate_7: float
    sales_rate_7: float
    free_wb: int
    on_way_wb: int
    in_stock_1c: int
    in_tailoring: int
    in_stock_ff: int
    on_way_ff: int
    in_production: int
    total: float
    days_remain: int
    created_at: datetime

class GoodsReportOutList(BaseModel):
    rows : list[GoodsReportOut]
    meta : Meta

# class GoodsReportUpdate(BaseModel):
#     goods_id: Optional[int] | None = None
#     size: Optional[str] | None = None
#     barcode: Optional[str] | None = None
#     archived: Optional[bool] | None = None

# class GoodsReportIn(BaseModel):
#     goods_id: int
#     size: str
#     barcode: str
    # archived: Optional[bool] | None = False
