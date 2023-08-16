from pydantic import BaseModel
from users.models import Meta
from goods.models import GoodsOut
from category.models import CategoryOut
from managers.models import ManagersOut
from datetime import datetime


class SkuReport(BaseModel):
    date: datetime | None
    sales_plan: int | None
    sales_fact: int | None
    sales_plan_sub_fact: int | None
    stock_quantity : int | None
    selfbuys_actual_quantity : int | None
    selfbuys_sum_actual_price : float | None
    selfbuys_mean_actual_price : float | None
    selfbuys_per_orders : float | None
    manager_place_for_request : int | None
    manager_selfbuys_actual_quantity : int | None
    manager_selfbuys_sum_actual_cost : float | None
    manager_adv_cost : float | None
    manager_comments_adv : list | None
    manager_gypoties : str | None
    goods_id : int | None

    goods : GoodsOut | None
    # category : CategoryOut | None
    manager : ManagersOut | None


class SkuReportList(BaseModel):
    rows : list[SkuReport]
    meta : Meta
