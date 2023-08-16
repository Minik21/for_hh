from users.permissions import PermissionChecker, Permission
from databeses import database, db_self_buyout, db_goods_size, db_goods
from self_buyout.models import SelfBuyoutIn, SelfBuyoutUpdate
from users.models import User
from fastapi import HTTPException
from datetime import datetime
from utils.sql_request import create_sql_request, sql_request
from pprint import pprint


async def create_self_buyout(self_buyout : SelfBuyoutIn, current_user: User):
    PermissionChecker(required_permissions=[Permission.SELF_BUYOUT_CREATE.value]
                      ).check_permission(current_user.permissions)
    await check_foreign_keys(dict(self_buyout))
    ins = dict(self_buyout)
    ins["created_at"] = datetime.now()
    ins["updated_at"] = ins["created_at"]
    query = db_self_buyout.insert().values(ins)
    last_record_id = await database.execute(query)
    ins = await advertizing_expand_self_buyout(ins, False)
    return {**ins, "id": last_record_id}


async def advertizing_expand_self_buyout(sql_result, isdict):
    temp = []
    temp_dict = {}
    if not isdict:  
        temp_dict = sql_result      
        req = db_goods_size.select().where(db_goods_size.c.id == temp_dict['goods_size_id'])
        s = await database.fetch_one(req)
        temp_dict['goods_size'] = dict(s)

        req = db_goods.select().where(db_goods.c.id == temp_dict['goods_size']['goods_id'])
        s = await database.fetch_one(req)
        temp_dict['goods'] = dict(s)
        return temp_dict
    else:
        for row in sql_result:
            temp_dict = dict(row)
            
            req = db_goods_size.select().where(db_goods_size.c.id == row['goods_size_id'])
            s = await database.fetch_one(req)
            temp_dict['goods_size'] = dict(s)

            req = db_goods.select().where(db_goods.c.id == temp_dict['goods_size']['goods_id'])
            s = await database.fetch_one(req)
            temp_dict['goods'] = dict(s)

            temp.append(temp_dict)
        return temp


async def read_self_buyout_by(current_user: User, all, skip, limit,
                       filter, order_by):
    PermissionChecker(required_permissions=[Permission.SELF_BUYOUT_READ.value]
                      ).check_permission(current_user.permissions)
    sql = create_sql_request("self_buyout", all, filter, q=None,
                            skip=skip, limit=limit, order_by=order_by)
    result = await sql_request(sql)
    return await advertizing_expand_self_buyout(result, True)


async def read_self_buyout_by_id(id, current_user: User):
    PermissionChecker(required_permissions=[Permission.SELF_BUYOUT_READ.value]
                      ).check_permission(current_user.permissions)
    query = db_self_buyout.select().where(db_self_buyout.c.id == id)
    result = await database.fetch_one(query)
    if result == None:
        raise HTTPException(status_code=404,
                            detail="self_buyout not found to read")
    result = await advertizing_expand_self_buyout(dict(result), False)
    return result


async def patch_self_buyout(id, self_buyout: SelfBuyoutUpdate, current_user : User):
    PermissionChecker(required_permissions=[Permission.SELF_BUYOUT_CREATE.value]
                      ).check_permission(current_user.permissions)
    db = await database.fetch_one(db_self_buyout.select(
                        ).where(db_self_buyout.c.id == id))
    if db == None:
      raise HTTPException(status_code=404,
                          detail="self_buyout not found to update")
    db = (dict(db))
    # await check_unique(self_buyout, True)
    # Смотрим все входящие значения, если Nonе оставляем прошлые значения
    for k, v in self_buyout.dict().items():
        if v != None:
            db[k] = v
    db["updated_at"] = datetime.now()
    await check_foreign_keys(db)
    query = db_self_buyout.update().where(db_self_buyout.c.id == db["id"]).values(db)
    await database.execute(query)
    db = await advertizing_expand_self_buyout(db, False)
    return {**db}


async def delete_self_buyout(id : int, current_user : User):
  PermissionChecker(required_permissions=[Permission.SELF_BUYOUT_DELETE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_self_buyout.select().
                                where(db_self_buyout.c.id == id))
  if db == None:
      raise HTTPException(status_code=404,
                          detail="self_buyout not found to delete")
  query = db_self_buyout.delete().where(db_self_buyout.c.id == id)
  await database.execute(query)
  return {"id": id}


async def check_foreign_keys(self_buyout : dict) -> None:
  query = db_goods_size.select().where(db_goods_size.c.id == self_buyout['goods_size_id'])
  res = await database.fetch_one(query)
  if res == None:
      raise HTTPException(status_code=404,
                          detail="goods_size not found")
  

async def get_self_buyout_report(current_user : User, year, month, goods_id):
    PermissionChecker(required_permissions=[Permission.SELF_BUYOUT_REPORT.value]
                      ).check_permission(current_user.permissions)
    sql_goods_id = ""
    if goods_id != None:
        sql_goods_id = f'AND goods_id = {goods_id}'
    if month == None:
        date = f'{year}-01-01'
        interval = 'interval \'1 year -1 day\''
        type_date = 'year'
    else:
        date = f'{year}-{month}-01'
        interval = 'interval \'1 month -1 day\''
        type_date = 'month'
    query = f"SELECT  SUM(self_buyout.actual_quantity) as sum_quantity, \
                     SUM(self_buyout.actual_price * self_buyout.actual_quantity) as sum_price, \
                     SUM(self_buyout.actual_cost * self_buyout.actual_quantity) as sum_cost, \
                     ROUND(SUM(self_buyout.actual_price * self_buyout.actual_quantity) \
                            / SUM(self_buyout.actual_quantity) , 2) as avg_price, \
                     goods_id \
            FROM self_buyout \
    JOIN goods_size ON self_buyout.goods_size_id = goods_size.id \
    JOIN goods ON goods_size.goods_id = goods.id \
    WHERE self_buyout.created_at BETWEEN '{date}' AND \
    date_trunc('{type_date}', timestamp '{date}') + {interval} {sql_goods_id}\
    GROUP BY goods_id"
    result = await database.fetch_all(query)
    return await advertizing_expand_self_buyout_report(result)


async def advertizing_expand_self_buyout_report(sql_result):
    temp = []
    temp_dict = {}
    for row in sql_result:
        temp_dict = dict(row)
        
        req = db_goods.select().where(db_goods.c.id == temp_dict['goods_id'])
        s = await database.fetch_one(req)
        temp_dict['goods'] = dict(s)

        temp.append(temp_dict)
    return temp


#  SUM(self_buyout.actual_quantity), \
#      SUM(self_buyout.actual_price), SUM(self_buyout.actual_cost)