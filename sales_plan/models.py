from pydantic import BaseModel
from typing import Optional
from users.models import Meta
from goods.models import GoodsOut
from goods_size.models import GoodsSizeOut
from datetime import datetime


class SalesPlan(BaseModel):
    # id : int
    goods_size: GoodsSizeOut | None
    goods : GoodsOut | None
    plan_at_month: int | None
    fact_at_month: int | None
    plan_completion_perc_month: float | None
    plan_today: int | None
    plan_completion_perc_today: float | None
    plan_month_ago: int | None
    fact_month_ago: int | None
    plan_2month_ago: int | None
    fact_2month_ago: int | None
    growth_percentage: float | None

class SalesPlanList(BaseModel):
    rows : list[SalesPlan]
    meta : Meta
