from pydantic import BaseModel
from users.models import Meta
from goods.models import GoodsOut
from category.models import CategoryOut
from managers.models import ManagersOut
from datetime import datetime


class DashboardOut(BaseModel):
    plan: int | None
    fact: int | None
    advertising_cost : float | None
    article_wb : str | None
    implementation_plan_for_month : float | None
    implementation_plan_for_today : float | None
    stock_quantity : int | None
    selfbuys_actual_quantity : int | None
    selfbuys_sum_actual_cost : float | None
    salary_sum : float | None
    salary_premium_sum : float | None
    salary_premium_salary_sum : float | None
    goods : GoodsOut | None
    category : CategoryOut | None
    manager : ManagersOut | None


class DashboardOutList(BaseModel):
    rows : list[DashboardOut]
    meta : Meta
