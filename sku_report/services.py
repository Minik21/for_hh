from users.permissions import PermissionChecker, Permission
from databeses import database, db_manager, db_goods
from users.models import User
from datetime import datetime
from pprint import pprint

async def read_sku_report(current_user: User, skip, limit,
                        year, month, filter):
    PermissionChecker(required_permissions=[Permission.SKU_REPORT_READ.value]
                      ).check_permission(current_user.permissions)
    res = []
    zero_date = datetime(year, month, 1).strftime("%Y-%m-%d")
    sql_filter = ''
    if filter != None:
        sql_filter = f'WHERE goods_id_s = \'{filter}\''

    sql = f'SELECT article_wb,\
       goods_id_s as goods_id,\
       gs AS date,\
       temp_fact - COALESCE(selfbuys_actual_quantity, 0) AS sales_fact,\
       ceil(temp_plan / DATE_PART(\'days\', DATE(\'{zero_date}\') +\
       INTERVAL \'1 month\' - INTERVAL \'1 day\')) AS sales_plan,\
       stock_quantity,\
       selfbuys_actual_quantity,\
       selfbuys_sum_actual_price,\
       selfbuys_mean_actual_price,\
       selfbuys_actual_quantity::float / temp_fact::float * 100 AS selfbuys_per_orders,\
       temp_fact - COALESCE(selfbuys_actual_quantity, 0) -\
       ceil(temp_plan / DATE_PART(\'days\', DATE(\'{zero_date}\') +\
                                 INTERVAL \'1 month\' - INTERVAL \'1 day\')) AS sales_plan_sub_fact,\
       stock_quantity / (temp_fact - COALESCE(selfbuys_actual_quantity, 0)) AS turnover,\
       adv_cost as manager_adv_cost,\
	     adv_comments as manager_comments_adv,\
       good_manager.manager_id, \
       help_sku.manager_gypoties,\
	     help_sku.manager_place_for_request \
FROM\
  (SELECT gs,\
          article_wb,\
          article_code,\
          goods.id as goods_id_s\
   FROM generate_series(\'{zero_date}\', (DATE(\'{zero_date}\') + INTERVAL \'1 month\' -\
                                       INTERVAL \'1 day\'), interval \'1 day\') AS gs,\
        goods) AS ma \
LEFT JOIN\
  (SELECT sum(actual_quantity) AS selfbuys_actual_quantity,\
          DATE(self_datetime),\
          goods_size_id,\
          goods_id,\
          sum(actual_quantity * actual_price) AS selfbuys_sum_actual_price,\
          sum(actual_quantity * actual_price) / sum(actual_quantity) AS selfbuys_mean_actual_price\
   FROM self_buyout\
   LEFT JOIN goods_size ON goods_size.id = self_buyout.goods_size_id\
   GROUP BY goods_size_id, goods_id,\
            DATE(self_datetime)) AS d ON d.date = gs and d.goods_id = goods_id_s \
LEFT JOIN\
  (SELECT count(*) AS temp_fact,\
          DATE(date) AS orders_date,\
          "supplierArticle"\
   FROM orders\
   GROUP BY \"supplierArticle\",\
            DATE(date)) AS fct ON fct.orders_date = ma.gs \
AND fct.\"supplierArticle\" = ma.article_wb \
LEFT JOIN\
  (SELECT goods_id,\
          sum(plan_at_month) AS temp_plan,\
          DATE(created_at)\
   FROM sales_plan\
   WHERE created_at = \'{zero_date}\'\
   GROUP BY goods_id,\
            DATE(created_at)) AS sp ON ma.goods_id_s = sp.goods_id \
LEFT JOIN\
  (SELECT sum(quantity) AS stock_quantity,\
          \"supplierArticle\",\
          DATE(script_at) AS stock_time\
   FROM stocks\
   GROUP BY \"supplierArticle\",\
            DATE(script_at))AS stocks ON stocks.stock_time = gs \
AND stocks.\"supplierArticle\" = article_wb \
LEFT JOIN good_manager ON ma.goods_id_s = good_manager.goods_id and DATE(good_manager.date_from) <= ma.gs \
						and DATE(good_manager.date_to) >= ma.gs \
LEFT JOIN (select sum("cost") as adv_cost, goods_id, DATE(buy_datetime),\
           ARRAY_AGG("comment") as adv_comments from advertising\
			group by goods_id, DATE(buy_datetime)) as adv\
			ON ma.goods_id_s = adv.goods_id and DATE(adv.date) = ma.gs \
LEFT JOIN help_sku ON help_sku.date_at = ma.gs AND help_sku.manager_id = good_manager.manager_id \
{sql_filter}\
  ORDER BY gs, goods_id DESC LIMIT {limit} OFFSET {skip}'
    sql_result = await database.fetch_all(sql)
    t = await sku_expand_goods_manager(sql_result)
    # for row in sql_result:
    #     row = dict(row)
    #     pprint(row)
    #     res.append(row)
    return t

async def post_update_sku_val(current_user: User, date : str,
                             manager_id : int,
                             manager_gypoties : str | None,
                             manager_place_for_request : int | None):
    PermissionChecker(required_permissions=[Permission.SKU_REPORT_UPDATE.value]
                      ).check_permission(current_user.permissions)
    sql = f"SELECT * FROM help_sku WHERE date_at = DATE(\'{date}\') AND manager_id = {manager_id}"
    sql_result = await database.fetch_one(sql)
    if sql_result != None:
        if manager_gypoties == None:
            manager_gypoties = dict(sql_result)['manager_gypoties']
        if manager_place_for_request == None:
            manager_place_for_request = dict(sql_result)['manager_place_for_request']
        sql = f"UPDATE help_sku SET manager_gypoties = \'{manager_gypoties}\',\
          manager_place_for_request = {manager_place_for_request}\
          WHERE date_at = DATE(\'{date}\') AND manager_id = {manager_id}"
        await database.execute(sql)
    else:
        manager_gypoties = "" if manager_gypoties == None else manager_gypoties
        manager_place_for_request = 0 if manager_place_for_request == None else manager_place_for_request
        sql = f"INSERT INTO help_sku (date_at, manager_id, manager_gypoties, manager_place_for_request)\
              VALUES (DATE(\'{date}\'), {manager_id}, \'{manager_gypoties}\', {manager_place_for_request})"
        await database.execute(sql)


async def sku_expand_goods_manager(sql_result):
    temp = []
    temp_dict = {}
    for row in sql_result:
        temp_dict = dict(row)
        req = db_manager.select().where(db_manager.c.id == row['manager_id'])
        s = await database.fetch_one(req)
        temp_dict['manager'] = dict(s) if s != None else None
        req = db_goods.select().where(db_goods.c.id == row['goods_id'])
        s = await database.fetch_one(req)
        temp_dict['goods'] = dict(s) if s != None else None

        temp.append(temp_dict)
    return temp
    