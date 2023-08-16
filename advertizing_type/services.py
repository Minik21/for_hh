from users.permissions import PermissionChecker, Permission
from databeses import database, db_advertising_type, db_advertising
from advertizing_type.models import AdvertisingTypeIn, AdvertisingTypeUpdate
from users.models import User
from fastapi import HTTPException
from datetime import datetime
from utils.sql_request import create_sql_request, sql_request


async def create_advertising_type(advertising_type : AdvertisingTypeIn, current_user: User):
    PermissionChecker(required_permissions=[Permission.ADVERTIZING_TYPE_CREATE.value]
                      ).check_permission(current_user.permissions)
    await check_unique(advertising_type)
    ins = dict(advertising_type)
    ins["created_at"] = datetime.now()
    ins["updated_at"] = ins["created_at"]
    query = db_advertising_type.insert().values(ins)
    last_record_id = await database.execute(query)
    return {**ins, "id": last_record_id}

# async def read_advertising_type(current_user: User, skip, limit):
#   PermissionChecker(required_permissions=[11]
#                     ).check_permission(current_user.permissions)
#   query = db_advertising_type.select().limit(limit).offset(skip)
#   return await database.fetch_all(query)

async def read_advertising_type_by(current_user: User, skip, limit,
                       filter, order_by):
    PermissionChecker(required_permissions=[Permission.ADVERTIZING_TYPE_READ.value]
                      ).check_permission(current_user.permissions)
    sql = create_sql_request("advertising_type", all, filter, q=None,
                            skip=skip, limit=limit, order_by=order_by)
    result = await sql_request(sql)
    return result

async def read_advertising_type_by_id(id, current_user: User):
  PermissionChecker(required_permissions=[Permission.ADVERTIZING_TYPE_READ.value]
                    ).check_permission(current_user.permissions)
  query = db_advertising_type.select().where(db_advertising_type.c.id == id)
  result = await database.fetch_one(query)
  if result == None:
    raise HTTPException(status_code=404, detail="advertising_type not found to read")
  return result

async def patch_advertising_type(id, advertising_type: AdvertisingTypeUpdate, current_user : User):
  PermissionChecker(required_permissions=[Permission.ADVERTIZING_TYPE_CREATE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_advertising_type.select().where(db_advertising_type.c.id == id))
  if db == None:
    raise HTTPException(status_code=404, detail="advertising_type not found to update")
  db = (dict(db))
  if db.get("name") != advertising_type.name:
      await check_unique(advertising_type)
  for k, v in advertising_type.dict().items():
      if v != None:
        db[k] = v
  db['updated_at'] = datetime.now()
  query = db_advertising_type.update().where(db_advertising_type.c.id == db["id"]).values(db)
  await database.execute(query)
  return {**db}

async def delete_advertising_type(id : int, current_user : User):
  PermissionChecker(required_permissions=[Permission.ADVERTIZING_TYPE_DELETE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_advertising_type.select().
                                where(db_advertising_type.c.id == id))
  if db == None:
    raise HTTPException(status_code=404, detail="advertising_type not found to delete")
  db = await database.fetch_one(db_advertising_type.select().
                                where(db_advertising.c.type_id == id))
  if db != None:
    raise HTTPException(status_code=403, detail="Cannot delete advertising_type, used in goods")
  query = db_advertising_type.delete().where(db_advertising_type.c.id == id)
  await database.execute(query)
  return {"id": id}

async def check_unique(advertising_type : AdvertisingTypeIn):
  query = db_advertising_type.select().where(db_advertising_type.c.name == advertising_type.name)
  res = await database.fetch_one(query)
  if res != None:
      raise HTTPException(status_code=404, detail="advertising_type already exists")
  return res
