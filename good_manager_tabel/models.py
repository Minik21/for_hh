from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from users.models import Meta
from goods.models import GoodsOut
from managers.models import ManagersOut


class GoodManagerTabelOut(BaseModel):
    id : int
    manager_id: int
    manager : ManagersOut
    goods_id : int
    goods : GoodsOut
    date_from : datetime
    date_to : datetime
    created_at : datetime
    updated_at : datetime


class GoodManagerOutTabelList(BaseModel):
    rows : list[GoodManagerTabelOut]
    meta : Meta


class GoodManagerTabelUpdate(BaseModel):
    manager_id: Optional[int] | None = None
    goods_id: Optional[int] | None = None
    date_from: Optional[datetime] | None = None
    date_to: Optional[datetime] | None = None


class GoodManagerTabelIn(BaseModel):
    manager_id: int
    goods_id : int
    date_from : datetime
    date_to : datetime
