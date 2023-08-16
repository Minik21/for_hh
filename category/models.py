from pydantic import BaseModel
from typing import Optional
from users.models import Meta
from datetime import datetime

class CategoryOut(BaseModel):
    id : int
    name: str
    created_at: datetime
    updated_at: datetime

class CategoryOutList(BaseModel):
    rows : list[CategoryOut]
    meta : Meta

class CategoryUpdate(BaseModel):
    name: Optional[str] | None = None

class CategoryIn(BaseModel):
    name: str
