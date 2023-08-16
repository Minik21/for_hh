from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from users.models import Meta


class NetcostOut(BaseModel):
    id : int
    goods_id : int
    value : float
    date_from : datetime
    date_to : datetime | None
    created_at : datetime
    updated_at : datetime


class NetcostOutList(BaseModel):
    rows : list[NetcostOut]
    meta : Meta


class NetcostUpdate(BaseModel):
    goods_id: Optional[int] | None = None
    value: Optional[float] | None = None
    date_from: Optional[datetime] | None = None
    date_to: Optional[datetime] | None = None


class NetcostIn(BaseModel):
    goods_id : int
    value : float
    date_from : datetime
    date_to : Optional[datetime] | None
