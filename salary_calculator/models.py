from pydantic import BaseModel
from typing import Optional
from users.models import Meta
from goods.models import GoodsOut
from datetime import datetime


class SalaryCalculator(BaseModel):
    id : int
    goods : GoodsOut | None
    good_created_at: datetime | None
    count_days_on_manager: int | None
    sum_salary_on_manager: float | None
    plan: int | None
    fact: int | None
    plan_progres: int | None
    sum_premium_on_manager: int | None
    sum_full_salary_on_manager: int | None
    
class SalaryCalculatorList(BaseModel):
    rows : list[SalaryCalculator]
    meta : Meta
