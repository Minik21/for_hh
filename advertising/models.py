from pydantic import BaseModel
from typing import Optional
from users.models import Meta
from datetime import datetime
from goods.models import GoodsOut
from advertizing_type.models import AdvertisingTypeOut


class AdvertisingOutSingle(BaseModel):
    id : int
    buy_datetime: datetime
    goods_id: int
    type_id: int
    cost: float
    comment: str
    views: int
    frequency: float
    clicks: int
    ctr: float
    cpc: float
    add_to_cart: int
    orders: int
    amount: float
    created_at: datetime
    updated_at: datetime

class AdvertisingOut(BaseModel):
    id : int
    buy_datetime: datetime
    goods_id: int
    goods: GoodsOut
    type_id: int
    type: AdvertisingTypeOut
    cost: float
    comment: str
    views: int
    frequency: float
    clicks: int
    ctr: float
    cpc: float
    add_to_cart: int
    orders: int
    amount: float
    created_at: datetime
    updated_at: datetime

class AdvertisingOutList(BaseModel):
    rows : list[AdvertisingOut]
    meta : Meta

class AdvertisingUpdate(BaseModel):
    buy_datetime: Optional[datetime] | None = None
    goods_id: Optional[int] | None = None
    type_id: Optional[int] | None = None
    cost: Optional[float] | None = None
    comment: Optional[str] | None = None
    views: Optional[int] | None = None
    frequency: Optional[float] | None = None
    clicks: Optional[int] | None = None
    ctr: Optional[float] | None = None
    cpc: Optional[float] | None = None
    add_to_cart: Optional[int] | None = None
    orders: Optional[int] | None = None
    amount: Optional[float] | None = None

class AdvertisingIn(BaseModel):
    buy_datetime: Optional[datetime] | None = None
    goods_id: int
    type_id: int
    cost: Optional[float] | None = None
    comment: Optional[str] | None = None
    views: Optional[int] | None = None
    frequency: Optional[float] | None = None
    clicks: Optional[int] | None = None
    ctr: Optional[float] | None = None
    cpc: Optional[float] | None = None
    add_to_cart: Optional[int] | None = None
    orders: Optional[int] | None = None
    amount: Optional[float] | None = None