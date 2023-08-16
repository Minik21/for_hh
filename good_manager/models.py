from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from users.models import Meta

# Column("id", Integer, primary_key=True, unique=True),
# Column("manager_id", Integer, ForeignKey("manager.id"), nullable=False),
# Column("goods_id", Integer, ForeignKey("goods.id"), nullable=False),
# Column("date_from", DateTime, nullable=False),
# Column("date_to", DateTime),
# Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
# Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),


class GoodManagerOut(BaseModel):
    id : int
    manager_id: int
    goods_id : int
    date_from : datetime
    date_to : datetime | None
    created_at : datetime
    updated_at : datetime


class GoodManagerOutList(BaseModel):
    rows : list[GoodManagerOut]
    meta : Meta


class GoodManagerUpdate(BaseModel):
    manager_id: Optional[int] | None = None
    goods_id: Optional[int] | None = None
    date_from: Optional[datetime] | None = None
    date_to: Optional[datetime] | None = None


class GoodManagerIn(BaseModel):
    manager_id: int
    goods_id : int
    date_from : datetime
    date_to : Optional[datetime] | None
