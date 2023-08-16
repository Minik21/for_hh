from pydantic import BaseModel
from users.models import Meta 
from datetime import datetime
from goods.models import GoodsOut


class UnionReportOut(BaseModel):
    # id : int
    goods_id : int
    goods: GoodsOut
    count_ordered: int
    count_buyed: int
    count_backordered: int
    ransoms: int
    to_transfer_for_product: float
    expenses_logy: float
    to_pay: float
    # total_logy_sum: float
    costs_fines: float | None
    costs_additional_payments: float | None
    costs_others: float | None
    fact_transfer: float | None
    netcost: float
    expenses_selfbuys: float
    sum_in_selfbuys: float
    # expenses: float
    advertising: float
    gross_profit: float
    profitability_gross: float | None
    sum_retail_price: float
    retail_price_by_one : float
    gross_profit_by_one : float | None
    # created_at: datetime

class UnionReportOutList(BaseModel):
    rows : list[UnionReportOut]
    meta : Meta
