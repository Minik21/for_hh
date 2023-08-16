from pydantic import BaseModel
from typing import Optional
from users.models import Meta
from datetime import datetime
from goods_size.models import GoodsSizeOut

class GoodsOut(BaseModel):
    id : int
    article_wb: str
    zero_cost: float
    average_price: float
    optimal_price: float
    article_code: str
    article_options: str
    organization_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    archived: bool

class GoodsOutWithSizes(BaseModel):
    id : int
    sizes : list[GoodsSizeOut]
    article_wb: str
    zero_cost: float
    average_price: float
    optimal_price: float
    article_code: str
    article_options: str
    organization_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    archived: bool

class GoodsOutListWithSizes(BaseModel):
    rows : list[GoodsOutWithSizes]
    meta : Meta

class GoodsOut2(BaseModel):
    rows : list[GoodsOut]
    meta : Meta

class GoodsUpdate(BaseModel):
    article_wb: Optional[str] | None = None
    zero_cost: Optional[float] | None = None
    average_price: Optional[float] | None = None
    optimal_price: Optional[float] | None = None
    article_code: Optional[str] | None = None
    article_options: Optional[str] | None = None
    organization_id: Optional[int] | None = None
    category_id: Optional[int] | None = None
    archived: Optional[bool] | None = None

class GoodsIn(BaseModel):
    article_wb: str
    zero_cost: Optional[float] | None = 0
    average_price: Optional[float] | None = 0
    optimal_price: Optional[float] | None = 0
    article_code: Optional[str] | None = None
    article_options: Optional[str] | None = None
    organization_id: int
    category_id: int
    # archived: Optional[bool] | None = False