from users.permissions import PermissionChecker, Permission
from databeses import database, db_goods_report, db_goods
from users.models import User
from fastapi import HTTPException
from utils.sql_request import create_sql_request, sql_request
from pprint import pprint


async def read_union_report_by(current_user: User, skip, limit,
                       filter, year, month):
    PermissionChecker(required_permissions=[Permission.UNION_REPORT_READ.value]
                      ).check_permission(current_user.permissions)
    where = ''
    if month == None:
        date = f'{year}-01-01'
        interval = 'interval \'1 year -1 day\''
        type_date = 'year'
    else:
        date = f'{year}-{month}-01'
        interval = 'interval \'1 month -1 day\''
        type_date = 'month'
    # if filter != None:
    #     attribute, value = filter.split("=")
    #     where = f'WHERE {attribute} = \'{value}\''
    sql = f"select sum(count_ordered) as count_ordered, sum(count_buyed) as count_buyed,\
      sum(count_backordered) as count_backordered,\
      ((sum(count_buyed::float) - sum(count_backordered::float)) * 100\
      / sum(count_ordered::float)) as ransoms,\
      sum(to_transfer_for_product) as to_transfer_for_product,\
      sum(expenses_logy) as expenses_logy, sum(to_pay) as to_pay,\
      sum(netcost) as netcost, sum(advertising) as advertising,\
      sum(expenses_selfbuys) as expenses_selfbuys, sum(sum_in_selfbuys) as sum_in_selfbuys,\
      sum(gross_profit) as gross_profit, sum(gross_profit) /\
      sum(retail_price) * 100 as profitability_gross,\
      (sum(retail_price) / (sum(count_buyed::float) - sum(count_backordered::float)))\
        as retail_price_by_one, sum(retail_price) as sum_retail_price,\
      (sum(gross_profit) / (sum(count_buyed::float) - sum(count_backordered::float)))\
        as gross_profit_by_one, goods_id\
      from union_report where created_at >= \'{date}\' and\
      created_at <= date_trunc('{type_date}', timestamp '{date}') + {interval}\
      group by goods_id\
      ORDER BY goods_id DESC LIMIT {limit} OFFSET {skip}"
    result = await database.fetch_all(sql)
    return await advertizing_expand_goods_goods_size(result, True)


async def advertizing_expand_goods_goods_size(sql_result, isdict):
    temp = []
    temp_dict = {}
    if not isdict:  
        temp_dict = sql_result      
        req = db_goods.select().where(db_goods.c.id == sql_result['goods_id'])
        s = await database.fetch_one(req)
        temp_dict['goods'] = dict(s)
        return temp_dict
    else:
        for row in sql_result:
            temp_dict = dict(row)
            
            req = db_goods.select().where(db_goods.c.id == row['goods_id'])
            s = await database.fetch_one(req)
            temp_dict['goods'] = dict(s)

            temp.append(temp_dict)
        return temp

    # sql_goods_id = ""
    # if goods_id != None:
    #     sql_goods_id = f'AND goods_id = {goods_id}'
    # if month == None:
    #     date = f'{year}-01-01'
    #     interval = 'interval \'1 year -1 day\''
    #     type_date = 'year'
    # else:
    #     date = f'{year}-{month}-01'
    #     interval = 'interval \'1 month -1 day\''
    #     type_date = 'month'
    # query = f"SELECT  SUM(self_buyout.actual_quantity) as sum_quantity, \
    #                  SUM(self_buyout.actual_price * self_buyout.actual_quantity) as sum_price, \
    #                  SUM(self_buyout.actual_cost * self_buyout.actual_quantity) as sum_cost, \
    #                  ROUND(SUM(self_buyout.actual_price * self_buyout.actual_quantity) \
    #                         / SUM(self_buyout.actual_quantity) , 2) as avg_price, \
    #                  goods_id \
    #         FROM self_buyout \
    # JOIN goods_size ON self_buyout.goods_size_id = goods_size.id \
    # JOIN goods ON goods_size.goods_id = goods.id \
    # WHERE self_buyout.created_at BETWEEN '{date}' AND \
    # date_trunc('{type_date}', timestamp '{date}') + {interval} {sql_goods_id}\
    # GROUP BY goods_id"
    # result = await database.fetch_all(query)
    # return await advertizing_expand_self_buyout_report(result)
