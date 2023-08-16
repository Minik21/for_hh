from users.permissions import PermissionChecker, Permission
from databeses import database, db_goods_size, db_goods
from goods_size.models import GoodsSizeIn, GoodsSizeUpdate
from users.models import User
from fastapi import HTTPException
from datetime import datetime
from utils.sql_request import create_sql_request, sql_request


async def create_goods_size(goods_size : GoodsSizeIn, current_user: User):
    PermissionChecker(required_permissions=[Permission.GOODS_SIZE_CREATE.value]
                      ).check_permission(current_user.permissions)
    await check_foreign_keys(dict(goods_size))
    await check_unique(goods_size, False)
    ins = dict(goods_size)
    ins["created_at"] = datetime.now()
    ins["updated_at"] = ins["created_at"]
    ins["archived"] = False
    query = db_goods_size.insert().values(ins)
    last_record_id = await database.execute(query)
    return {**ins, "id": last_record_id}


async def read_good_size_by(current_user: User, all, skip, limit,
                       filter, order_by):
    PermissionChecker(required_permissions=[Permission.GOODS_SIZE_READ.value]
                      ).check_permission(current_user.permissions)
    sql = create_sql_request("goods_size", all, filter, q=None,
                            skip=skip, limit=limit, order_by=order_by)
    result = await sql_request(sql)
    return result


async def read_goods_size_by_id(id, current_user: User):
    PermissionChecker(required_permissions=[Permission.GOODS_SIZE_READ.value]
                      ).check_permission(current_user.permissions)
    query = db_goods_size.select().where(db_goods_size.c.id == id)
    result = await database.fetch_one(query)
    if result == None:
        raise HTTPException(status_code=404,
                            detail="goods_size not found to read")
    return result


async def patch_goods_size(id, goods_size: GoodsSizeUpdate, current_user : User):
    PermissionChecker(required_permissions=[Permission.GOODS_SIZE_CREATE.value]
                      ).check_permission(current_user.permissions)
    db = await database.fetch_one(db_goods_size.select().where(db_goods_size.c.id == id))
    if db == None:
      raise HTTPException(status_code=404,
                          detail="goods_size not found to update")
    db = (dict(db))
    await check_unique(goods_size, True)
    # Смотрим все входящие значения, если Nonе оставляем прошлые значения
    for k, v in goods_size.dict().items():
        if k == "archived" and v != db[k]:
            PermissionChecker(required_permissions=[Permission.GOODS_SIZE_DELETE]
                              ).check_permission(current_user.permissions)
        if v != None:
            db[k] = v
    await check_foreign_keys(db)
    db["updated_at"] = datetime.now()
    query = db_goods_size.update().where(db_goods_size.c.id == db["id"]).values(db)
    await database.execute(query)
    return {**db}


async def archive_goods_size(id : int, current_user : User):
  PermissionChecker(required_permissions=[Permission.GOODS_SIZE_DELETE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_goods_size.select().
                                where(db_goods_size.c.id == id))
  if db == None:
      raise HTTPException(status_code=404,
                          detail="goods_size not found to delete")
  db = (dict(db))
  db["archived"] = True
  query = db_goods_size.update().where(db_goods_size.c.id == id).values(db)
  await database.execute(query)
  return {**db}


async def check_unique(goods_size : GoodsSizeIn, putch):
  query = f"SELECT * FROM goods_size WHERE barcode = '{goods_size.barcode}' \
          OR (size = '{goods_size.size}' AND goods_id = '{goods_size.goods_id}')"
  if not putch:
    res = await database.fetch_one(query)
    if res != None:
      raise HTTPException(status_code=404,
                          detail="Barcode must be unique and {size, goods_id} must be unique")
  else:
    res = await database.fetch_all(query)
    if len(res) > 1:
      raise HTTPException(status_code=404,
                          detail="Barcode must be unique and {size, goods_id} must be unique")


async def check_foreign_keys(goods_size : dict) -> None:
  query = db_goods.select().where(db_goods.c.id == goods_size['goods_id'])
  res = await database.fetch_one(query)
  if res == None:
      raise HTTPException(status_code=404,
                          detail="good not found")
