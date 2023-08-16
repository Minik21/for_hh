from pydantic import BaseModel
from typing import Optional
from users.models import Meta
from datetime import datetime

class ManagersOut(BaseModel):
    id : int
    first_name: str
    last_name: str
    patronymic: str
    created_at: datetime
    updated_at: datetime
    archived: bool

class ManagersOutList(BaseModel):
    rows : list[ManagersOut]
    meta : Meta

class ManagesUpdate(BaseModel):
    first_name: Optional[str] | None = None
    last_name: Optional[str] | None = None
    patronymic: Optional[str] | None = None
    archived: Optional[bool] | None = None

class ManagesIn(BaseModel):
    first_name : str
    last_name : str
    patronymic : str
    # archived : bool | None = False
