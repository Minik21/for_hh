from databeses import databases
from pprint import pprint
from datetime import datetime, timedelta
from sqlalchemy import text
import asyncio
import databases
import asyncio
import requests
import json
import time
import logging
import sys


log_wb_load = logging.getLogger("report_detaild_by_period")
log_wb_load.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('reports/logs/report_detaild_by_period.log')
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
       log_wb_load.info("Invalid token")
       return {}
    if response_code == 200:
        list_of_stocks = json.loads(data.text)
        list_of_stocks = change_date_type(list_of_stocks, organization)
        log_wb_load.info(f"{len(list_of_stocks)} {operation} loaded from {organization}")

        return list_of_stocks
    time.sleep(60)


def change_date_type(list_of_stocks, organization):
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    for row in list_of_stocks:
        if row['sale_dt'] is not None:
            row['sale_dt'] = datetime.strptime(row['sale_dt'], date_format)
        if row['create_dt'] is not None:
            row['create_dt'] = datetime.strptime(row['create_dt'], date_format)
        if row['order_dt'] is not None:
            row['order_dt'] = datetime.strptime(row['order_dt'], date_format)
        if row['rr_dt'] is not None:
            row['rr_dt'] = datetime.strptime(row['rr_dt'], date_format)
        if row['date_to'] is not None:
            row['date_to'] = datetime.strptime(row['date_to'], date_format)
        if row['date_from'] is not None:
            row['date_from'] = datetime.strptime(row['date_from'], date_format)
        row['organization_id'] = organization
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


async def write_to_db(data, database : databases.Database, db_report_detail_by_period):
    await database.connect()
    for row in data:
        query = db_report_detail_by_period.insert().values(row)
        await database.execute(query)
    log_wb_load.info("Data written to db_report_detail_by_period")
    await database.disconnect()


def get_wb_report(key, organization, date_from, date_to) -> dict:
  response_code = 0
  request_url = "https://statistics-api.wildberries.ru/api/v1/supplier"
  while response_code != 200:
    params = {'Authorization': key}
    data = requests.get(f"{request_url}/reportDetailByPeriod?dateFrom={date_from}&dateTo={date_to}",
                        headers=params, stream=True)
    response_code = data.status_code
    log_wb_load.info(f"reportDetailByPeriod response code: {response_code}")
    if response_code == 401:
       return {}
    if response_code == 200:
        list_of_stocks = json.loads(data.text)
        list_of_stocks = change_date_type(list_of_stocks, organization)
        log_wb_load.info(f"{len(list_of_stocks)} reportDetailByPeriod loaded from {organization}")

        return list_of_stocks
    time.sleep(60)


async def clean_db(database : databases.Database, date_from, date_to):
    await database.connect()
    query = f'DELETE FROM report_detail_by_period where create_dt >=\
        DATE(\'{date_from}\') and create_dt <= DATE(\'{date_to}\')'
    await database.execute(text(query))
    await database.disconnect()

async def load_report_detail_by_period(database : databases.Database, db_report_detail_by_period):
    s = await get_organizations(database)
    date_from = (datetime.now() - timedelta(days=21)).strftime("%Y-%m-%d")
    date_to = datetime.now().strftime("%Y-%m-%d")
    await clean_db(database, date_from, date_to)
    for row in s:
        t = get_wb_report(row['standard_token'], row['id'], date_from, date_to)
        await write_to_db(t, database, db_report_detail_by_period)
    return True

if __name__ == "__main__":
    pass
    # DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    # database = databases.Database(DATABASE_URL)
    # s = asyncio.run(get_organizations(database))
    # date_from = (datetime.now() - timedelta(days=21)).strftime("%Y-%m-%d")
    # date_to = datetime.now().strftime("%Y-%m-%d")
    # asyncio.run(clean_db(database, date_from, date_to))
    # for row in s:
    #     t = get_wb_report(row['standard_token'], row['id'], date_from, date_to)
    #     asyncio.run(write_to_db(db_report_detail_by_period, t, database))
