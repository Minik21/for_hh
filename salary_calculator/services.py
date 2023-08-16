from users.permissions import PermissionChecker, Permission
from databeses import database, db_goods, db_goods_size, db_sales_plan
from users.models import User
from pprint import pprint
from sqlalchemy import text
from datetime import datetime
import calendar

async def read_sales_plan_by(current_user: User, skip, limit,
                       filter, year, month, q):
    PermissionChecker(required_permissions=[Permission.SALES_PLAN_READ.value]
                      ).check_permission(current_user.permissions)
    result_list = []
    zero_date = datetime(year, month, 1)
    sql_q = '' if q == None else f"and goods.article_wb LIKE '%{q}%'"
    if filter == None:
        sql_filter = ''
    else:
        sql_filter = f'and sales_plan.{filter}'
    sql = f"SELECT * FROM sales_plan JOIN goods ON sales_plan.goods_id = goods.id\
            where sales_plan.created_at = \'{zero_date}\' {sql_filter} {sql_q}\
            ORDER BY goods_id DESC LIMIT {limit} OFFSET {skip}"
    sql_result = await database.fetch_all(sql)
    t = await sales_plan_expand_goods_size(sql_result, True)
    for i in t:
        if i['plan_at_month'] == None or i['plan_at_month'] == 0:
            i['plan_completion_perc_month'] = 0
        else:
            i['plan_completion_perc_month'] = (i['fact_at_month'] / i['plan_at_month']
                                            * 100)
        i['plan_today'] = ((calendar.monthrange(year, month)[1] / datetime.now().day)
                           * i['plan_at_month'] if i['plan_at_month'] != None else 0)
        if i['plan_today'] == 0:
            i['plan_completion_perc_today'] = 0
        else:
            i['plan_completion_perc_today'] = i['fact_at_month'] / i['plan_today'] * 100
        if i['fact_2month_ago'] != 0:
            i['growth_percentage'] = i['fact_month_ago'] / i['fact_2month_ago']
        else:
            i['growth_percentage'] = 0
        result_list.append(i)
    return result_list


async def put_in_sales_plan(current_user, year, month, goods_size_id,
                            plan_at_month):
        PermissionChecker(required_permissions=[Permission.SALES_PLAN_CREATE.value]
                      ).check_permission(current_user.permissions)
        zero_date = datetime(year, month, 1)
        query = db_sales_plan.select().where(text(f"created_at = \'{zero_date}\' and\
                             goods_size_id = {goods_size_id}"))
        is_exists = await database.execute(query)
        if is_exists == None:
            query = db_sales_plan.insert().values(plan_at_month=plan_at_month,
                                                  created_at=zero_date,
                                                  goods_size_id=goods_size_id)
        else:
            query = db_sales_plan.update().values(plan_at_month=plan_at_month
                    ).where(text(f"created_at = \'{zero_date}\' and\
                                goods_size_id = {goods_size_id}"))
        await database.execute(query)

        query = db_sales_plan.select().where(text(f"created_at = \'{zero_date}\' and\
                        goods_size_id = {goods_size_id}"))
        result = await database.fetch_one(query)
        if is_exists == None:
            return result
        return await sales_plan_expand_goods_size(dict(result), False)
        


async def sales_plan_expand_goods_size(sql_result, isdict):
    temp = []
    temp_dict = {}
    if not isdict:  
        temp_dict = sql_result
        req = db_goods_size.select().where(db_goods_size.c.id == sql_result['goods_size_id'])
        s = await database.fetch_one(req)
        temp_dict['goods_size'] = dict(s)

        req = db_goods.select().where(db_goods.c.id == dict(s)['goods_id'])
        s = await database.fetch_one(req)
        temp_dict['goods'] = dict(s)
        return temp_dict
    else:
        for row in sql_result:
            temp_dict = dict(row)
            
            req = db_goods_size.select().where(db_goods_size.c.id == row['goods_size_id'])
            s = await database.fetch_one(req)
            temp_dict['goods_size'] = dict(s)

            req = db_goods.select().where(db_goods.c.id == dict(s)['goods_id'])
            s = await database.fetch_one(req)
            temp_dict['goods'] = dict(s)

            temp.append(temp_dict)
        return temp
    