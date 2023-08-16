from datetime import datetime, timedelta
# from databeses import databases, db_goods_report
import databases
import asyncio
import logging
import sys
from pprint import pprint


log_create_goods_report = logging.getLogger("create_goods_sku_report")
log_create_goods_report.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('reports/logs/logs_create_goods_sku_report.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

log_create_goods_report.addHandler(file_handler)
log_create_goods_report.addHandler(stdout_handler)

async def get_row_data(database : databases.Database,
                      report_date: str):
  await database.connect()
  row_data = []
  today_date_minus_days = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
  query = f'SELECT * from goods'
  result = await database.fetch_all(query)
  log_create_goods_report.info(f"{len(result)} row data collected")
  await database.disconnect()
  for i in result:
    row_data.append(dict(i))
  return row_data


def prepare_data(row_data, report_date):
  for row in row_data:
    row['sales_rate_7'] = round(row['sales_rate_7'] / 7, 2)
    row['orders_rate_7'] = round(row['orders_rate_7'] / 7, 2)
    row['on_way_wb'] = row['quantityfull'] - row['free_wb']
    row['days_remain'] = row['orders_rate_7'] * (row['free_wb'] +
                                                 (row['on_way_wb'] * 0.7))
    if row['days_remain'] < 0:
        row['days_remain'] = 0
    del row['quantityfull']
    row['in_stock_1c'] = 0
    row['in_tailoring'] = 0
    row['in_stock_ff'] = 0
    row['on_way_ff'] = 0
    row['in_production'] = 0
    row['total'] = round(row['free_wb'] + (row['on_way_wb'] * 0.7) + row['in_stock_1c'] +
                    row['in_tailoring'] + row['in_stock_ff'] + row['on_way_ff'] +
                    row['in_production'])
    row['created_at'] = (datetime.strptime(report_date, "%Y%m%d") - timedelta(days=1))
  log_create_goods_report.info(f"{len(row_data)} row data prepared")
  return row_data


async def push_to_db(prepared_data, database : databases.Database,
                     db_goods_report, report_date):
  await database.connect()
  report_date = (datetime.strptime(report_date, "%Y%m%d") - timedelta(days=1))
  query = db_goods_report.delete().where(db_goods_report.c.created_at == report_date)
  await database.execute(query)
  for row in prepared_data:
      query = db_goods_report.insert().values(row)
      await database.execute(query)
  log_create_goods_report.info(f"{len(prepared_data)} data pushed")
  await database.disconnect()


async def create_sku_report(database : databases.Database, db_sku_report):
  for minus_days in range(0, 14):
    report_date = (datetime.now() - timedelta(days=minus_days)).strftime("%Y%m%d")
    row_data = await get_row_data(database, report_date)
    # prepared_data = prepare_data(row_data, report_date)
    # await push_to_db(prepared_data, database, db_sku_report, report_date)


if __name__ == "__main__":
  pass
  # DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
  # database = databases.Database(DATABASE_URL)
  # row_data = asyncio.run(get_row_data(database))
  # prepared_data = prepare_data(row_data)
  # asyncio.run(push_to_db(prepared_data, database))

# select gs, article_wb, article_code, plan_at_month /
# DATE_PART('days', DATE('2023-06-01') + INTERVAL '1 month' - INTERVAL '1 day') as plan_on_orders,
# sum(actual_quantity) as actual_quantity, sum(actual_price) as sum_actual_price, avg(actual_price) as avg_actual_price,
# COALESCE(fact, 0) - COALESCE(sum(actual_quantity), 0) as fact, (sum(actual_quantity::float) / fact::float) * 100 as percent_self,
# COALESCE(stock_quantity, 0) as stock_quantity, COALESCE(stock_quantity, 0)/ NULLIF(COALESCE(stock_quantity, 0), 0) as turnover
# from(
# select gs, article_wb, article_code, sum(sales_plan.plan_at_month) as plan_at_month, goods_size.id as goods_size_id
# from generate_series('2023-06-01', (DATE('2023-06-01') + INTERVAL '1 month' - INTERVAL '1 day'), interval '1 day') as gs, goods
# LEFT JOIN sales_plan ON goods.id = sales_plan.goods_id
# JOIN goods_size ON goods_size.goods_id = goods.id
# group by article_wb, article_code, gs, goods_size.id) as t
# LEFT JOIN
# (SELECT actual_quantity, actual_price, self_datetime, goods_size_id from self_buyout) as d
# ON DATE(self_datetime) = gs and d.goods_size_id = t.goods_size_id
# LEFT JOIN
# (SELECT count(*) as fact, DATE(date), "supplierArticle" from orders group by "supplierArticle", DATE(date)) as fct
# ON fct.date = t.gs and fct."supplierArticle" = t.article_wb
# LEFT JOIN
# (SELECT sum("quantityFull") as stock_quantity, "supplierArticle", DATE(script_at) as time_at
#  from stocks group by "supplierArticle", DATE(script_at))as stocks
# ON stocks.time_at = fct.date and stocks."supplierArticle" = article_wb
# GROUP BY article_wb, gs, article_code, plan_at_month, fact, stock_quantity
