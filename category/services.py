from users.permissions import PermissionChecker, Permission
from databeses import database, db_category, db_goods
from category.models import CategoryIn, CategoryUpdate
from users.models import User
from fastapi import HTTPException
from datetime import datetime
from utils.sql_request import create_sql_request, sql_request


async def create_category(category : CategoryIn, current_user: User):
  PermissionChecker(required_permissions=[Permission.CATEGORY_CREATE.value]
                    ).check_permission(current_user.permissions)
  await check_unique(category)
  ins = dict(category)
  ins["created_at"] = datetime.now()
  ins["updated_at"] = ins["created_at"]
  query = db_category.insert().values(ins)
  last_record_id = await database.execute(query)
  return {**ins, "id": last_record_id}

# async def read_category(current_user: User, skip, limit):
#   PermissionChecker(required_permissions=[11]
#                     ).check_permission(current_user.permissions)
#   query = db_category.select().limit(limit).offset(skip)
#   return await database.fetch_all(query)

async def read_category_by(current_user: User, skip, limit,
                       filter, order_by):
    PermissionChecker(required_permissions=[Permission.CATEGORY_READ.value]
                      ).check_permission(current_user.permissions)
    sql = create_sql_request("category", all, filter, q=None,
                            skip=skip, limit=limit, order_by=order_by)
    result = await sql_request(sql)
    return result

async def read_category_by_id(id, current_user: User):
  PermissionChecker(required_permissions=[Permission.CATEGORY_READ.value]
                    ).check_permission(current_user.permissions)
  query = db_category.select().where(db_category.c.id == id)
  result = await database.fetch_one(query)
  if result == None:
    raise HTTPException(status_code=404, detail="category not found to read")
  return result

async def patch_category(id, category: CategoryUpdate, current_user : User):
  PermissionChecker(required_permissions=[Permission.CATEGORY_CREATE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_category.select().where(db_category.c.id == id))
  if db == None:
    raise HTTPException(status_code=404, detail="category not found to update")
  db = (dict(db))
  if db.get("name") != category.name:
      await check_unique(category)
  for k, v in category.dict().items():
      if v != None:
        db[k] = v
  db['updated_at'] = datetime.now()
  query = db_category.update().where(db_category.c.id == db["id"]).values(db)
  await database.execute(query)
  return {**db}

async def delete_category(id : int, current_user : User):
  PermissionChecker(required_permissions=[Permission.CATEGORY_DELETE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_category.select().
                                where(db_category.c.id == id))
  if db == None:
    raise HTTPException(status_code=404, detail="category not found to delete")
  db = await database.fetch_one(db_category.select().
                                where(db_goods.c.category_id == id))
  if db != None:
    raise HTTPException(status_code=403, detail="Cannot delete category, used in goods")
  query = db_category.delete().where(db_category.c.id == id)
  await database.execute(query)
  return {"id": id}

async def check_unique(category : CategoryIn):
  query = db_category.select().where(db_category.c.name == category.name)
  res = await database.fetch_one(query)
  if res != None:
      raise HTTPException(status_code=404, detail="category already exists")
  return res
