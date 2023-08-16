from users.permissions import PermissionChecker, Permission
from databeses import database, db_good_manager_tabel, db_goods, db_manager
from good_manager.models import GoodManagerIn, GoodManagerUpdate
from users.models import User
from fastapi import HTTPException
from datetime import datetime
from utils.sql_request import create_sql_request, sql_request
from pprint import pprint



async def create_good_manager_tabel(good_manager : GoodManagerIn, current_user: User):
    PermissionChecker(required_permissions=[Permission.GOOD_MANAGER_TABEL_CREATE.value]
                      ).check_permission(current_user.permissions)
    await check_foreign_keys(dict(good_manager))
    ins = dict(good_manager)
    ins["created_at"] = datetime.now()
    ins["updated_at"] = ins["created_at"]
    query = db_good_manager_tabel.insert().values(ins)
    last_record_id = await database.execute(query)
    ins = await good_manager_tabel_expand_good(ins, isdict=False)
    return {**ins, "id": last_record_id}


async def read_good_manager_tabel_by(current_user: User, all, skip, limit,
                       filter, order_by):
    PermissionChecker(required_permissions=[Permission.GOOD_MANAGER_TABEL_READ.value]
                      ).check_permission(current_user.permissions)
    sql = create_sql_request("good_manager_tabel", all, filter, q=None,
                            skip=skip, limit=limit, order_by=order_by)
    result = await sql_request(sql)
    return await good_manager_tabel_expand_good(result, True)

# async def read_good_manager_tabel_by_id(id, current_user: User):
#     PermissionChecker(required_permissions=[Permission.GOOD_MANAGER_TABEL_READ.value]
#                       ).check_permission(current_user.permissions)
#     query = db_good_manager.select().where(db_good_manager.c.id == id)
#     result = await database.fetch_one(query)
#     if result == None:
#         raise HTTPException(status_code=404,
#                             detail="good_manager not found to read")
#     return result

async def patch_good_manager_tabel(id, good_manager: GoodManagerUpdate,
                                   current_user : User):
    PermissionChecker(required_permissions=[Permission.GOOD_MANAGER_TABEL_CREATE.value]
                      ).check_permission(current_user.permissions)
    db = await database.fetch_one(db_good_manager_tabel.select(
                        ).where(db_good_manager_tabel.c.id == id))
    if db == None:
      raise HTTPException(status_code=404,
                          detail="good_manager_table not found to update")
    db = (dict(db))
    for k, v in good_manager.dict().items():
        if v != None:
            db[k] = v
    db["updated_at"] = datetime.now()
    await check_foreign_keys(db)
    query = db_good_manager_tabel.update(
            ).where(db_good_manager_tabel.c.id == db["id"]).values(db)
    await database.execute(query)
    return await good_manager_tabel_expand_good(db, False)

async def delete_good_manager_tabel(id : int, current_user : User):
  PermissionChecker(required_permissions=[Permission.GOOD_MANAGER_TABEL_DELETE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_good_manager_tabel.select().
                                where(db_good_manager_tabel.c.id == id))
  if db == None:
      raise HTTPException(status_code=404,
                          detail="good_manager not found to delete")
  query = db_good_manager_tabel.delete().where(db_good_manager_tabel.c.id == id)
  await database.execute(query)
  return {"id": id}


async def check_foreign_keys(good_manager : dict) -> None:
  query = db_goods.select().where(db_goods.c.id == good_manager['goods_id'])
  res = await database.fetch_one(query)
  if res == None:
      raise HTTPException(status_code=404,
                          detail="good not found")
  query = db_manager.select().where(db_manager.c.id == good_manager['manager_id'])
  res = await database.fetch_one(query)
  if res == None:
      raise HTTPException(status_code=404,
                          detail="manager not found")
  

async def good_manager_tabel_expand_good(sql_result, isdict):
    temp = []
    temp_dict = {}
    if not isdict:  
        temp_dict = sql_result      
        req = db_goods.select().where(db_goods.c.id == sql_result['goods_id'])
        s = await database.fetch_one(req)
        temp_dict['goods'] = dict(s)

        req = db_manager.select().where(db_manager.c.id == sql_result['manager_id'])
        s = await database.fetch_one(req)
        temp_dict['manager'] = dict(s)
        return temp_dict
    else:
        for row in sql_result:
            temp_dict = dict(row)
            
            req = db_goods.select().where(db_goods.c.id == row['goods_id'])
            s = await database.fetch_one(req)
            temp_dict['goods'] = dict(s)

            req = db_manager.select().where(db_manager.c.id == row['manager_id'])
            s = await database.fetch_one(req)
            temp_dict['manager'] = dict(s)

            temp.append(temp_dict)
        return temp
