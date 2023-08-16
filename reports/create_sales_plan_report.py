from datetime import datetime, timedelta
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
# from databeses import db_goods_report, db_sales_plan
from sqlalchemy import text
import databases
import asyncio
import logging
import sys
from pprint import pprint


log_create_goods_report = logging.getLogger("create_sales_plan_report")
log_create_goods_report.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('reports/logs/create_sales_plan_report.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

log_create_goods_report.addHandler(file_handler)
log_create_goods_report.addHandler(stdout_handler)

async def get_row_data(database : databases.Database,
                      report_date: str):
  await database.connect()
  zero_date = report_date[0:-2] + "01"
  query = f"SELECT * ,fact_month_ago / fact_2month_ago AS growth_percentage FROM( \
SELECT goods_size.id as goods_size_id,\
		goods_id,\
		goods.article_wb,\
		fact as fact_at_month\
	FROM goods_size \
LEFT JOIN goods ON goods.id = goods_size.goods_id \
LEFT JOIN \
(SELECT count(*) AS fact,\
             \"supplierArticle\",\
 			\"techSize\"\
      FROM orders\
      WHERE orders.date >= '{zero_date}'\
        AND DATE('{zero_date}') + INTERVAL '1 month' > orders.date\
      GROUP BY \"supplierArticle\", \"techSize\" order by \"supplierArticle\") as ord \
ON ord.\"supplierArticle\" = goods.article_wb and \"techSize\" = goods_size.size) as main \
LEFT JOIN (SELECT\
			   plan_at_month as plan_month_ago,\
			   goods_size_id as tr,\
		   	   fact_at_month as fact_month_ago\
		   FROM sales_plan where created_at = DATE('{zero_date}') - INTERVAL '1 month') as m1 \
ON m1.tr = main.goods_size_id \
LEFT JOIN (SELECT\
		   		plan_at_month as plan_2month_ago,\
		   		goods_size_id as tr_2,\
		   		fact_at_month as fact_2month_ago\
		   FROM sales_plan where created_at = DATE('{zero_date}') - INTERVAL '2 month') as m2 \
ON m2.tr_2 = main.goods_size_id"
  result = await database.fetch_all(query)
  log_create_goods_report.info(f"{len(result)} row data collected sales_plan")
  await database.disconnect()
  return result


def prepare_data(row_data, report_date):
  zero_date = datetime.strptime(report_date[0:-2] + "01", "%Y-%m-%d")
  result_list = []
  for i in row_data:
    i = dict(i)
    i.pop('tr')
    i.pop('tr_2')
    i.pop('article_wb')
    i.update({'created_at': zero_date})
    result_list.append(i)
  log_create_goods_report.info(f"{len(row_data)} row data prepared")
  return result_list


async def push_to_db(prepared_data, database : databases.Database,
                    report_date, db_sales_plan):
  await database.connect()
  zero_date = report_date[0:-2] + "01"
  for row in prepared_data:
      temp = f'goods_size_id = {row["goods_size_id"]} and created_at = DATE(\'{zero_date}\')'
      query = db_sales_plan.select(
      ).where(text(temp))
      t = await database.fetch_one(query)
      if t == None:
          query = db_sales_plan.insert().values(row)
      else:
          query = db_sales_plan.update().where(text(temp)).values(row)
      await database.execute(query)
  log_create_goods_report.info(f"{len(prepared_data)} data pushed sales_plan")
  await database.disconnect()


async def create_sales_plan_report(database : databases.Database, db_sales_plan):
    report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    # report_date = '2023-08-01'
    row_data = await get_row_data(database, report_date)
    to_push_data = prepare_data(row_data, report_date)
    await push_to_db(to_push_data, database, report_date, db_sales_plan)


if __name__ == "__main__":
  DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
  database = databases.Database(DATABASE_URL)
  # for minus_days in range(14, 0):
  report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
  row_data = asyncio.run(get_row_data(database, report_date))
    # prepared_data = prepare_data(row_data, report_date)
    # asyncio.run(push_to_db(prepared_data, database, report_date))