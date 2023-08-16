from users.permissions import PermissionChecker, Permission
from databeses import database, db_netcost, db_goods
from netcost.models import NetcostIn, NetcostUpdate
from users.models import User
from fastapi import HTTPException
from datetime import datetime
from utils.sql_request import create_sql_request, sql_request


async def create_netcost(netcost : NetcostIn, current_user: User):
    PermissionChecker(required_permissions=[Permission.NETCOST_CREATE.value]
                      ).check_permission(current_user.permissions)
    await check_foreign_keys(dict(netcost))
    ins = dict(netcost)
    ins["created_at"] = datetime.now()
    ins["updated_at"] = ins["created_at"]
    query = db_netcost.insert().values(ins)
    last_record_id = await database.execute(query)
    return {**ins, "id": last_record_id}


async def read_netcost_by(current_user: User, all, skip, limit,
                       filter, order_by):
    PermissionChecker(required_permissions=[Permission.NETCOST_READ.value]
                      ).check_permission(current_user.permissions)
    sql = create_sql_request("netcost", all, filter, q=None,
                            skip=skip, limit=limit, order_by=order_by)
    result = await sql_request(sql)
    return result


async def read_netcost_by_id(id, current_user: User):
    PermissionChecker(required_permissions=[Permission.NETCOST_READ.value]
                      ).check_permission(current_user.permissions)
    query = db_netcost.select().where(db_netcost.c.id == id)
    result = await database.fetch_one(query)
    if result == None:
        raise HTTPException(status_code=404,
                            detail="netcost not found to read")
    return result


async def patch_netcost(id, netcost: NetcostUpdate, current_user : User):
    PermissionChecker(required_permissions=[Permission.NETCOST_CREATE.value]
                      ).check_permission(current_user.permissions)
    db = await database.fetch_one(db_netcost.select().where(db_netcost.c.id == id))
    if db == None:
      raise HTTPException(status_code=404,
                          detail="netcost not found to update")
    db = (dict(db))
    for k, v in netcost.dict().items():
        if v != None:
            db[k] = v
    db["updated_at"] = datetime.now()
    await check_foreign_keys(db)
    query = db_netcost.update().where(db_netcost.c.id == db["id"]).values(db)
    await database.execute(query)
    return {**db}


async def delete_netcost(id : int, current_user : User):
  PermissionChecker(required_permissions=[Permission.NETCOST_DELETE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_netcost.select().
                                where(db_netcost.c.id == id))
  if db == None:
      raise HTTPException(status_code=404,
                          detail="netcost not found to delete")
  query = db_netcost.delete().where(db_netcost.c.id == id)
  await database.execute(query)
  return {"id": id}


async def check_foreign_keys(netcost : dict) -> None:
  query = db_goods.select().where(db_goods.c.id == netcost['goods_id'])
  res = await database.fetch_one(query)
  if res == None:
      raise HTTPException(status_code=404,
                          detail="goods_size not found")
