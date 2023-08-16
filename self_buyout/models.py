from pydantic import BaseModel
from typing import Optional
from users.models import Meta 
from datetime import datetime
from goods_size.models import GoodsSizeOut
from goods.models import GoodsOut

# class SelfBuyoutOutReport(BaseModel):
#     id : int
#     sum_quantity : int
#     sum_price : float
#     sum_cost : float
#     avg_price : float
#     goods_id : int
#     goods : GoodsOut


class SelfBuyoutOut(BaseModel):
    id : int
    self_datetime : datetime
    goods_size_id : int
    goods_size : GoodsSizeOut
    goods : GoodsOut
    planned_quantity : int
    planned_price : float
    actual_quantity : int
    actual_price : float
    actual_cost : float
    created_at : datetime
    updated_at : datetime

class SelfBuyoutExp(SelfBuyoutOut):
    goods_size : GoodsSizeOut
    goods : GoodsOut

class SelfBuyoutOutList(BaseModel):
    rows : list[SelfBuyoutExp]
    meta : Meta

class SelfBuyoutUpdate(BaseModel):
    self_datetime: Optional[datetime] | None = None
    goods_size_id: Optional[int] | None = None
    planned_quantity: Optional[int] | None = None
    planned_price: Optional[float] | None = None
    actual_quantity: Optional[int] | None = None
    actual_price: Optional[float] | None = None
    actual_cost: Optional[float] | None = None

class SelfBuyoutIn(BaseModel):
    self_datetime: Optional[datetime] | None = None
    goods_size_id: int
    planned_quantity: Optional[int] | None = None
    planned_price: Optional[float] | None = None
    actual_quantity: Optional[int] | None = None
    actual_price: Optional[float] | None = None
    actual_cost: Optional[float] | None = None
