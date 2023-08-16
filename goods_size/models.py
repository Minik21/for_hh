from pydantic import BaseModel
from typing import Optional
from users.models import Meta 
from datetime import datetime

class GoodsSizeOut(BaseModel):
    id : int
    goods_id: int
    size : str
    barcode : str
    archived : bool
    created_at: datetime
    updated_at: datetime

class GoodsSizeOutList(BaseModel):
    rows : list[GoodsSizeOut]
    meta : Meta

class GoodsSizeUpdate(BaseModel):
    goods_id: Optional[int] | None = None
    size: Optional[str] | None = None
    barcode: Optional[str] | None = None
    archived: Optional[bool] | None = None

class GoodsSizeIn(BaseModel):
    goods_id: int
    size: str
    barcode: str
    # archived: Optional[bool] | None = False
