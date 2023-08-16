from datetime import datetime, timedelta
from databeses import db_stocks, databases, db_sales, db_orders
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
import databases
import asyncio
import requests
import json
import time
import logging
import sys
from pprint import pprint


log_wb_load = logging.getLogger("wb_load")
log_wb_load.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('reports/logs/Wb_load.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)


log_wb_load.addHandler(file_handler)
log_wb_load.addHandler(stdout_handler)


async def get_wb_data(operation, key, organization, date) -> dict:
  response_code = 0
  request_url = "https://statistics-api.wildberries.ru/api/v1/supplier"
  while response_code != 200:
    params = {'Authorization': key}
    data = requests.get(f"{request_url}/{operation}?dateFrom={date}", headers=params)
    response_code = data.status_code

    log_wb_load.info(f"{operation} response code: {response_code}")
    if response_code == 401:
       return {}
    if response_code == 200:
        list_of_stocks = json.loads(data.text)
        list_of_stocks = change_date_type(list_of_stocks, organization, operation)
        log_wb_load.info(f"{len(list_of_stocks)} {operation} loaded from {organization}")

        return list_of_stocks
    time.sleep(60)


def change_date_type(list_of_stocks, organization,
                           operation_type) -> dict:
    sales_flag = False
    orders_flag = False
    date_format = "%Y-%m-%dT%H:%M:%S"
    if operation_type == "sales":
       sales_flag = True
    if operation_type == "orders":
       orders_flag = True
    for row in list_of_stocks:
        if orders_flag or sales_flag:
            row['date'] = datetime.strptime(row['date'], date_format)
            if orders_flag:
                row['cancel_dt'] = datetime.strptime(row['cancel_dt'],
                                                     date_format)
        row['organizationId'] = organization
        row['lastChangeDate'] = datetime.strptime(row['lastChangeDate'],
                                                  date_format)
        row['script_at'] = (datetime.now() - timedelta(days=1))
    return list_of_stocks


async def get_organizations(database : databases.Database):
    await database.connect()
    organizations_list = []
    query = "SELECT * FROM organization;"
    db_organizations_list = await database.fetch_all(query)

    for i in db_organizations_list:
        organizations_list.append(dict(i))
    await database.disconnect()

    log_wb_load.info("Organizations loaded")

    return organizations_list


async def collect_full_data(operation, date ,organizations):
    full_data = []
    tasks = []
    for row in organizations:
        tasks.append(asyncio.create_task(get_wb_data(operation, row['standard_token'],
                                                    row['id'], date)))
    full_data = await asyncio.gather(*tasks)
    log_wb_load.info(f"{operation} data prepeared")
    return full_data


async def write_to_db(db_name, data, database : databases.Database,
                      date_to_del, rewrite : bool):
    await database.connect()
    if rewrite:
        date_to_del = datetime.strptime(date_to_del, "%Y-%m-%d")
        query = db_name.delete().where(db_name.c.date >= date_to_del)
        await database.execute(query)
        log_wb_load.info(f"Data deleted from {db_name}")

    for row in data:
      for i in row:
        query = db_name.insert().values(i)
        await database.execute(query)
    log_wb_load.info(f"Data written to {db_name}")
    await database.disconnect()

async def load_wb_data(database : databases.Database, db_sales, db_stocks, db_orders):
    date_for_sales_orders = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
    date_for_stocks = "2000-01-01"
    organizations = await get_organizations(database)
    data = await collect_full_data("sales", date_for_sales_orders, organizations)
    await write_to_db(db_sales, data, database, date_for_sales_orders, True)
    data = await collect_full_data("stocks", date_for_stocks, organizations)
    await write_to_db(db_stocks, data, database, date_for_stocks, False)
    data = await collect_full_data("orders", date_for_sales_orders, organizations)
    await write_to_db(db_orders, data, database, date_for_sales_orders, True)

if __name__ == "__main__":
    pass
#   DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
#   database = databases.Database(DATABASE_URL)
#   date_for_sales_orders = (datetime.now() - timedelta(days=65)).strftime("%Y-%m-%d")
#   date_for_stocks = "2000-01-01"
#   organizations = asyncio.run(get_organizations(database))
#   data = asyncio.run(collect_full_data("sales", date_for_sales_orders, organizations))
#   asyncio.run(write_to_db(db_sales, data, database))
#   data = asyncio.run(collect_full_data("stocks", date_for_stocks, organizations))
#   asyncio.run(write_to_db(db_stocks, data, database))
#   data = asyncio.run(collect_full_data("orders", date_for_sales_orders, organizations))
#   asyncio.run(write_to_db(db_orders, data, database))
  