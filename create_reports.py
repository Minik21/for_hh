from reports.create_goods_report import create_goods_report
from reports.wb_load import load_wb_data
from reports.create_sales_plan_report import create_sales_plan_report
from reports.wb_load_report_by import load_report_detail_by_period
from reports.create_union_report import create_union_report
# from reports.create_goods_sku_report import create_sku_report
from reports.create_dashboard import create_dashbord
import asyncio
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from databeses import databases, db_orders, db_goods_report, db_sales_plan
from databeses import db_report_detail_by_period, db_sales, db_stocks, db_union_report
from databeses import db_report_goods_sku, db_dashboard

if __name__ == "__main__":
  DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
  database = databases.Database(DATABASE_URL)
  asyncio.run(load_wb_data(database, db_sales, db_stocks, db_orders))
  asyncio.run(create_goods_report(database, db_goods_report))
  asyncio.run(load_report_detail_by_period(database, db_report_detail_by_period))
  asyncio.run(create_union_report(database, db_union_report))
  # asyncio.run(create_sku_report(database, db_report_goods_sku))
  asyncio.run(create_sales_plan_report(database, db_sales_plan))
  asyncio.run(create_dashbord(database, db_dashboard))