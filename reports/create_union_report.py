from datetime import datetime, timedelta
# from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
# from databeses import db_union_report
import databases
import asyncio
import logging
import sys
from pprint import pprint

  # query = f"SELECT * FROM(\
  # SELECT * FROM(\
  # SELECT article_wb, goods.id as goods_id_s, doc_type_name, sum(report_detail_by_period.quantity) as quantity_sale,\
  # sum(ppvz_for_pay) as ppvz_for_pay, sum(delivery_amount) as delivery_amount,\
  # sum(return_amount) as return_amount, sum(delivery_rub) as delivery_rub,\
  # sum(retail_price_withdisc_rub) as retail_price_withdisc_rub, nm_id, sale_dt,\
  # goods.organization_id, avg(netcost.value) as netcost\
  # FROM goods\
  # JOIN report_detail_by_period ON sa_name = article_wb\
  # LEFT JOIN netcost ON goods.id = netcost.goods_id and netcost.date_from <= \'{report_date}\'\
  # and netcost.date_to >= \'{report_date}\'\
  # where sale_dt = \'{report_date}\' and doc_type_name = 'Продажа'\
  # group by article_wb, goods.id, doc_type_name, nm_id, sale_dt, goods.organization_id) as report\
  # LEFT JOIN (\
  # SELECT goods_id, sum(actual_quantity) as quantity_self,\
  # sum(actual_price * actual_quantity) as price, sum(actual_cost) as cost\
  # FROM self_buyout\
  # JOIN goods_size ON goods_size.id = self_buyout.goods_size_id\
  # and self_buyout.self_datetime < \'{plus_one_day}\'\
  # and self_buyout.self_datetime >= \'{report_date}\'\
  # group by goods_id) as self_buy\
  # ON report.goods_id_s = self_buy.goods_id) as t\
  # LEFT JOIN \
  # (SELECT * FROM(\
  # SELECT goods.id as goods_id_r, sum(report_detail_by_period.quantity) as quantity_back_r,\
  # sum(ppvz_for_pay) as ppvz_for_pay_r, sum(delivery_amount) as delivery_amount_r,\
  # sum(return_amount) as return_amount_r, sum(delivery_rub) as delivery_rub_r,\
  # sum(retail_price_withdisc_rub) as retail_price_withdisc_rub_r\
  # FROM goods\
  # JOIN report_detail_by_period ON sa_name = article_wb\
  # where sale_dt = \'{report_date}\' and doc_type_name = 'Возврат'\
  # group by article_wb, goods.id, doc_type_name, nm_id, sale_dt, goods.organization_id) as report\
  # LEFT JOIN (\
  # SELECT goods_id, sum(actual_quantity) as quantity_self,\
  # sum(actual_price * actual_quantity) as price, sum(actual_cost) as cost\
  # FROM self_buyout\
  # JOIN goods_size ON goods_size.id = self_buyout.goods_size_id\
  # and self_buyout.self_datetime < \'{plus_one_day}\'\
  # and self_buyout.self_datetime >= \'{report_date}\'\
  # group by goods_id) as self_buy\
  # ON report.goods_id_r = self_buy.goods_id) as k\
  # ON t.goods_id_s = k.goods_id_r"


log_create_goods_report = logging.getLogger("create_union_report")
log_create_goods_report.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('reports/logs/create_union_report.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

log_create_goods_report.addHandler(file_handler)
log_create_goods_report.addHandler(stdout_handler)

async def get_row_data(database : databases.Database,
                      report_date: str):
  await database.connect()
  plus_one_day = (datetime.strptime(report_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
  row_data = []
  query = f"SELECT * FROM(\
  SELECT * FROM(\
  SELECT article_wb, goods.id as goods_id_s, doc_type_name, sum(report_detail_by_period.quantity) as quantity_sale,\
  sum(ppvz_for_pay) as ppvz_for_pay, sum(delivery_amount) as delivery_amount,\
  sum(return_amount) as return_amount, sum(delivery_rub) as delivery_rub,\
  sum(retail_price_withdisc_rub) as retail_price_withdisc_rub, nm_id, sale_dt,\
  goods.organization_id, avg(netcost.value) as netcost\
  FROM goods\
  JOIN report_detail_by_period ON sa_name = article_wb\
  LEFT JOIN netcost ON goods.id = netcost.goods_id and netcost.date_from <= \'{report_date}\'\
  and netcost.date_to >= \'{report_date}\'\
  where sale_dt = \'{report_date}\' and doc_type_name = 'Продажа'\
  group by article_wb, goods.id, doc_type_name, nm_id, sale_dt, goods.organization_id) as report\
  LEFT JOIN (\
  SELECT goods_id, sum(actual_quantity) as quantity_self,\
  sum(actual_price * actual_quantity) as price, sum(actual_cost) as cost\
  FROM self_buyout\
  JOIN goods_size ON goods_size.id = self_buyout.goods_size_id\
  and self_buyout.self_datetime < \'{plus_one_day}\'\
  and self_buyout.self_datetime >= \'{report_date}\'\
  group by goods_id) as self_buy\
  ON report.goods_id_s = self_buy.goods_id) as t\
  LEFT JOIN \
  (SELECT goods.id as goods_id_r, sum(report_detail_by_period.quantity) as quantity_back_r,\
  sum(ppvz_for_pay) as ppvz_for_pay_r, sum(delivery_amount) as delivery_amount_r,\
  sum(return_amount) as return_amount_r, sum(delivery_rub) as delivery_rub_r,\
  sum(retail_price_withdisc_rub) as retail_price_withdisc_rub_r\
  FROM goods\
  JOIN report_detail_by_period ON sa_name = article_wb\
  where sale_dt = \'{report_date}\' and doc_type_name = 'Возврат'\
  group by article_wb, goods.id, doc_type_name, nm_id, sale_dt, goods.organization_id) as report\
  ON t.goods_id_s = report.goods_id_r\
  LEFT JOIN (SELECT SUM(\"cost\") as ad_cost, goods_id FROM advertising where buy_datetime < \'{plus_one_day}\'\
  and buy_datetime >= \'{report_date}\' group by goods_id)\
  as ad ON t.goods_id_s = ad.goods_id"
  result = await database.fetch_all(query)
  log_create_goods_report.info(f"{len(result)} row data collected")
  await database.disconnect()
  for i in result:
    pprint(dict(i))
    row_data.append(dict(i))
  return row_data


def prepare_data(row_data, report_date):
  result_list = []
  for row in row_data:
      temp_dict = {}
      temp_dict['count_ordered'] = (row['delivery_amount'] - 
                                    int(0 if row['quantity_self'] is None
                                    else row['quantity_self']))
      temp_dict['count_buyed'] = (row['quantity_sale'] - 
                                    int(0 if row['quantity_self'] is None
                                    else row['quantity_self']))
      temp_dict['count_backordered'] = int(0 if row['quantity_back_r'] is None
                                            else row['quantity_back_r'])
      temp_dict['created_at'] = datetime.strptime(report_date, "%Y-%m-%d")
      temp_dict['to_transfer_for_product'] = (row['ppvz_for_pay'] -
                                              int(0 if row['ppvz_for_pay_r'] is None
                                                    else row['ppvz_for_pay_r']))
      temp_dict['expenses_logy'] = row['delivery_rub']
      temp_dict['to_pay'] = temp_dict['to_transfer_for_product'] - temp_dict['expenses_logy']
      temp_dict['netcost'] = ((temp_dict['count_buyed'] -
                                int(0 if temp_dict['count_backordered'] is None
                                    else temp_dict['count_backordered']))
                               * int(0 if row['netcost'] is None
                                    else row['netcost']))
      temp_dict['advertising'] = int(0 if row['ad_cost'] is None else row['ad_cost'])
      temp_dict['expenses_selfbuys'] = int(0 if row['cost'] is None else row['cost'])
      temp_dict['sum_in_selfbuys'] = int(0 if row['price'] is None else row['price'])
      temp_dict['gross_profit'] = (temp_dict['to_pay'] - temp_dict['netcost'] -
                                   temp_dict['advertising'] - temp_dict['expenses_selfbuys'] -
                                   temp_dict['sum_in_selfbuys'])
      temp_dict['retail_price'] = (row['retail_price_withdisc_rub'] - 
                                   int(0 if row['retail_price_withdisc_rub_r'] is None
                                       else row['retail_price_withdisc_rub_r']))              
      temp_dict['sum_retail_price'] = (temp_dict['retail_price'] *
                                       (temp_dict['count_buyed'] - temp_dict['count_backordered']))
      if temp_dict['sum_retail_price'] == 0:
        temp_dict['profitability_gross'] = None
        temp_dict['gross_profit_by_one'] = None
      else:
        temp_dict['profitability_gross'] = round(temp_dict['gross_profit'] /
                                               temp_dict['sum_retail_price'] * 100, 2)
        temp_dict['gross_profit_by_one'] = (temp_dict['gross_profit'] /
                                            (temp_dict['count_buyed'] - temp_dict['count_backordered'] /
                                             temp_dict['sum_retail_price']))
      temp_dict['goods_id'] = row['goods_id_s']
      result_list.append(temp_dict)
  log_create_goods_report.info(f"{len(row_data)} row data prepared")
  return result_list


async def push_to_db(prepared_data, database : databases.Database,
                    report_date, db_union_report):
  await database.connect()
  report_date = (datetime.strptime(report_date, "%Y-%m-%d"))
  query = db_union_report.delete().where(db_union_report.c.created_at == report_date)
  await database.execute(query)
  for row in prepared_data:
      query = db_union_report.insert().values(row)
      await database.execute(query)
  log_create_goods_report.info(f"{len(prepared_data)} data pushed")
  await database.disconnect()


async def create_union_report(database : databases.Database, db_union_report):
  for minus_days in range(0, 21):
    report_date = (datetime.now() - timedelta(days=minus_days)).strftime("%Y-%m-%d")
    row_data = await get_row_data(database, report_date)
    prepared_data = prepare_data(row_data, report_date)
    await push_to_db(prepared_data, database, report_date, db_union_report)


if __name__ == "__main__":
  pass
  # DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
  # database = databases.Database(DATABASE_URL)
  # for minus_days in range(0, 21):
  #   report_date = (datetime.now() - timedelta(days=minus_days)).strftime("%Y-%m-%d")
  #   row_data = asyncio.run(get_row_data(database, report_date))
  #   prepared_data = prepare_data(row_data, report_date)
  #   asyncio.run(push_to_db(prepared_data, database, report_date))
