from pydantic import BaseModel
from typing import Optional
from users.models import Meta
from datetime import datetime

class AdvertisingTypeOut(BaseModel):
    id : int
    name: str
    created_at: datetime
    updated_at: datetime

class AdvertisingTypeOutList(BaseModel):
    rows : list[AdvertisingTypeOut]
    meta : Meta

class AdvertisingTypeUpdate(BaseModel):
    name: Optional[str] | None = None

class AdvertisingTypeIn(BaseModel):
    name: str
