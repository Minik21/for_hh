from users.permissions import PermissionChecker, Permission
from databeses import database, db_goods, db_manager, db_category
from users.models import User
from datetime import datetime

async def read_dashboard(current_user: User, skip, limit,
                        year, month, filter, q):
    PermissionChecker(required_permissions=[Permission.DASHBOARD_READ.value]
                      ).check_permission(current_user.permissions)
    zero_date = datetime(year, month, 1)
    report_date = datetime.now().strftime("%Y-%m-%d")
    sql_q, sql_filter, sql_where, sql_and = '', '', '', ''
    if q != None:
        sql_q = f"article_wb LIKE '%{q}%'"
        sql_where = 'WHERE'
    if filter != None:
        if q != None:
            sql_and = 'AND'
        sql_filter = f'organization_id = {filter}'
        sql_where = 'WHERE'

    sql = f'SELECT SUM(fact) as fact,\
       article_wb,\
       category_id,\
       id AS good_id,\
       manager_id,\
       PLAN,\
       actual_quantity as selfbuys_actual_quantity,\
       sum_actual_cost as selfbuys_sum_actual_cost,\
       adv_cost as advertising_cost,\
       sum(fact) / (PLAN / DATE_PART(\'days\', DATE(\'{zero_date}\') + \
       INTERVAL \'1 month\' - INTERVAL \'1 day\') *\
       DATE_PART(\'days\', DATE(\'{report_date}\'))) AS implementation_plan_for_today,\
       COALESCE((sum(fact) / PLAN), 0) * 100 AS implementation_plan_for_month,\
       stock_quantity,\
       organization_id as organisation_id \
FROM\
  (SELECT article_wb,\
          goods.id,\
          category_id,\
          manager_id,\
          fact,\
          organization_id\
   FROM goods\
   LEFT JOIN good_manager ON good_manager.goods_id = goods.id\
   LEFT JOIN\
     (SELECT count(*) AS fact,\
             \"supplierArticle\"\
      FROM orders\
      WHERE orders.date >= \'{zero_date}\'\
        AND DATE(\'{zero_date}\') + INTERVAL \'1 month\' > orders.date\
      GROUP BY \"supplierArticle\") \
        AS fct ON \"supplierArticle\" = article_wb) AS k \
LEFT JOIN\
  (SELECT sum(plan_at_month) AS PLAN,\
          goods_id\
   FROM sales_plan\
   WHERE created_at = \'{zero_date}\'\
   GROUP BY goods_id) AS pln ON pln.goods_id = id \
LEFT JOIN\
  (SELECT goods_id,\
          SUM(actual_quantity) AS actual_quantity,\
          SUM(sum_actual_cost) AS sum_actual_cost\
   FROM(\
          (SELECT goods_id,\
                  id AS goods_size_id\
           FROM goods_size) AS self_1\
        LEFT JOIN\
          (SELECT SUM(actual_quantity) AS actual_quantity,\
                  SUM(actual_quantity * actual_cost) AS sum_actual_cost,\
                  goods_size_id\
           FROM self_buyout\
           WHERE self_datetime >= \'{zero_date}\'\
             AND self_datetime < DATE(\'{zero_date}\') + INTERVAL \'1 month\' - INTERVAL \'1 day\'\
           GROUP BY goods_size_id) AS self_2 ON self_1.goods_size_id = self_2.goods_size_id)\
   GROUP BY goods_id) AS self_0 ON self_0.goods_id = id \
LEFT JOIN\
  (SELECT sum(\"cost\") AS adv_cost,\
          goods_id\
   FROM advertising\
   WHERE buy_datetime >= \'{zero_date}\'\
     AND buy_datetime < DATE(\'{zero_date}\') + INTERVAL \'1 month\' - INTERVAL \'1 day\'\
   GROUP BY goods_id) AS ad ON ad.goods_id = id \
LEFT JOIN\
  (SELECT sum(\"quantity\") AS stock_quantity,\
          \"supplierArticle\"\
   FROM stocks\
   WHERE script_at >= (select DATE(MAX(script_at)) as min_stock_date from stocks\
			  where script_at >= \'{zero_date}\'\
                    and script_at < DATE(\'{zero_date}\') + INTERVAL \'1 month\') and\
        script_at < (select DATE(MAX(script_at)) as max_stock_date from stocks\
			where script_at >= \'{zero_date}\' and script_at < DATE(\'{zero_date}\') +\
                                INTERVAL \'1 month\') + INTERVAL \'1 day\'\
   GROUP BY \"supplierArticle\")AS stocks ON stocks.\"supplierArticle\" = article_wb \
{sql_where} {sql_q} {sql_and} {sql_filter} \
GROUP BY article_wb,\
         category_id,\
         id,\
         manager_id,\
         PLAN,\
         actual_quantity,\
         adv_cost,\
         sum_actual_cost,\
         stock_quantity,\
         organization_id \
ORDER BY id DESC LIMIT {limit} OFFSET {skip}'
    # sql = f"SELECT * FROM dashboard\
    #         where dashboard.created_at = \'{zero_date}\' {sql_q} {sql_filter}\
    #         ORDER BY id DESC LIMIT {limit} OFFSET {skip}"
#    WHERE script_at >= DATE(\'{report_date}\') - INTERVAL \'1 day\'\
#      AND script_at < DATE(\'{report_date}\')\
    sql_result = await database.fetch_all(sql)
    t = await dashboard_expand_goods_manager_category(sql_result)
    return t


async def dashboard_expand_goods_manager_category(sql_result):
    temp = []
    temp_dict = {}
    for row in sql_result:
        temp_dict = dict(row)
        req = db_manager.select().where(db_manager.c.id == row['manager_id'])
        s = await database.fetch_one(req)
        temp_dict['manager'] = dict(s) if s != None else None
        req = db_goods.select().where(db_goods.c.id == row['good_id'])
        s = await database.fetch_one(req)
        temp_dict['goods'] = dict(s) if s != None else None

        req = db_category.select().where(db_category.c.id == row['category_id'])
        s = await database.fetch_one(req)
        temp_dict['category'] = dict(s) if s != None else None

        temp.append(temp_dict)
    return temp
    