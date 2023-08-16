from datetime import datetime, timedelta
# from databeses import databases, db_goods_report
import databases
import asyncio
import logging
import sys
from pprint import pprint



log_create_goods_report = logging.getLogger("create_goods_report")
log_create_goods_report.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('reports/logs/logs_create_goods_report.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

log_create_goods_report.addHandler(file_handler)
log_create_goods_report.addHandler(stdout_handler)

async def get_row_data(database : databases.Database,
                      report_date: str):
  await database.connect()
  row_data = []
  today_date_minus_days = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
  query = f'SELECT sales_rate.goods_size_id, sales_rate_7, orders_rate_7,\
          sales_rate.goods_id, free_wb, quantityFull\
          FROM (SELECT goods_size.size, goods_id,\
          goods_size.id as goods_size_id, count(*) as sales_rate_7 FROM goods\
          JOIN sales ON sales."supplierArticle" = goods.article_wb\
          JOIN goods_size ON "techSize" = goods_size.size\
          where "odid" != 0 and\
          "date" BETWEEN TO_DATE(\'{report_date}\', \'YYYYMMDD\') - \
          INTERVAL \'7 days\' AND TO_DATE(\'{report_date}\', \'YYYYMMDD\')\
          and goods_size.size = "techSize"\
          and "incomeID" != 0\
          GROUP BY "techSize", goods_size.size, goods_id, goods_size.id) as sales_rate\
          JOIN (\
          SELECT goods."id" as goods_id, "techSize", goods_size.id as goods_size_id\
          ,count(*) as orders_rate_7 from goods\
          JOIN orders ON orders."supplierArticle" = goods.article_wb\
          JOIN goods_size ON "techSize" = goods_size.size\
          where "date" BETWEEN TO_DATE(\'{report_date}\', \'YYYYMMDD\') -\
          INTERVAL \'7 days\' AND TO_DATE(\'{report_date}\', \'YYYYMMDD\')\
          GROUP BY "techSize", goods."id", goods_size_id) as order_rate\
          ON sales_rate.goods_id = order_rate.goods_id and\
          sales_rate.goods_size_id = order_rate.goods_size_id\
          JOIN (\
          SELECT goods."id" as goods_id, "techSize",goods_size.id as goods_size_id ,\
          sum(quantity) as free_wb, sum("quantityFull") as quantityFull FROM goods\
          JOIN stocks ON stocks."supplierArticle" = goods.article_wb\
          JOIN goods_size ON "techSize" = goods_size.size\
          WHERE stocks.script_at >= TO_DATE(\'{today_date_minus_days}\', \'YYYYMMDD\')\
          GROUP BY stocks.barcode, goods."id", "techSize", goods_size_id) as stocks_quantuty\
          ON stocks_quantuty.goods_id = order_rate.goods_id and\
          stocks_quantuty.goods_size_id = order_rate.goods_size_id'
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


async def create_goods_report(database : databases.Database, db_goods_report):
  for minus_days in range(0, 7):
    report_date = (datetime.now() - timedelta(days=minus_days)).strftime("%Y%m%d")
    row_data = await get_row_data(database, report_date)
    prepared_data = prepare_data(row_data, report_date)
    await push_to_db(prepared_data, database, db_goods_report, report_date)


if __name__ == "__main__":
  pass
  # DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
  # database = databases.Database(DATABASE_URL)
  # row_data = asyncio.run(get_row_data(database))
  # prepared_data = prepare_data(row_data)
  # asyncio.run(push_to_db(prepared_data, database))