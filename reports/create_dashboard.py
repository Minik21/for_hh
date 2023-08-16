from datetime import datetime, timedelta
import databases
import asyncio
import logging
import sys
from pprint import pprint



log_create_goods_report = logging.getLogger("create_dashbord")
log_create_goods_report.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('reports/logs/logs_create_dashbord.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

log_create_goods_report.addHandler(file_handler)
log_create_goods_report.addHandler(stdout_handler)

async def get_row_data(database : databases.Database,
                      report_date: str, zero_date: str):
  await database.connect()
  row_data = []
  query = f"SELECT SUM(fact) as fact,\
       article_wb,\
       category_id,\
       id AS good_id,\
       manager_id,\
       PLAN,\
       actual_quantity,\
       sum_actual_cost,\
       adv_cost,\
       sum(fact) / (PLAN / DATE_PART(\'days\', DATE(\'{zero_date}\') + \
       INTERVAL \'1 month\' - INTERVAL \'1 day\') *\
       DATE_PART(\'days\', DATE(\'{report_date}\'))) AS plan_for_today,\
       COALESCE((sum(fact) / PLAN), 0) * 100 AS per_plane_done,\
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
   WHERE script_at >= \'{report_date}\'\
     AND script_at < DATE(\'{report_date}\') + INTERVAL \'1 day\'\
   GROUP BY \"supplierArticle\")AS stocks ON stocks.\"supplierArticle\" = article_wb \
GROUP BY article_wb,\
         category_id,\
         id,\
         manager_id,\
         PLAN,\
         actual_quantity,\
         adv_cost,\
         sum_actual_cost,\
         stock_quantity,\
         organization_id"
  result = await database.fetch_all(query)
  log_create_goods_report.info(f"{len(result)} row data collected")
  await database.disconnect()
  for i in result:
    row_data.append(dict(i))
  return row_data


def prepare_data(row_data, zero_date):
  for row in row_data:
    row['created_at'] = datetime.strptime(zero_date, "%Y-%m-%d")
    row['sum_salary'] = 0
    row['sum_prmium'] = 0
    row['sum_premium_salary'] = row['sum_salary'] + row['sum_prmium']
  log_create_goods_report.info(f"{len(row_data)} row data prepared")
  return row_data


async def push_to_db(prepared_data, database : databases.Database,
                     db_dashboard, zero_date):
  await database.connect()
  zero_date = datetime.strptime(zero_date, "%Y-%m-%d")
  query = db_dashboard.delete().where(db_dashboard.c.created_at == zero_date)
  await database.execute(query)
  for row in prepared_data:
      query = db_dashboard.insert().values(row)
      await database.execute(query)
  log_create_goods_report.info(f"{len(prepared_data)} data pushed")
  await database.disconnect()


async def create_dashbord(database : databases.Database, db_dashboard):
    report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    zero_date = report_date[0:-2] + "01"
    row_data = await get_row_data(database, report_date, zero_date)
    prepared_data = prepare_data(row_data, zero_date)
    await push_to_db(prepared_data, database, db_dashboard, zero_date)


if __name__ == "__main__":
  pass
  # DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
  # database = databases.Database(DATABASE_URL)
  # report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
  # zero_date = report_date[0:-2] + "01"
  # row_data = asyncio.run(get_row_data(database, report_date, zero_date))
  # pprint(row_data)
  # prepared_data = prepare_data(row_data, report_date)
  # await push_to_db(prepared_data, database, db_goods_report, report_date)