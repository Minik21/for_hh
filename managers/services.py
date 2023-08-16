from users.permissions import PermissionChecker, Permission
from databeses import database, db_manager
from managers.models import ManagesIn, ManagesUpdate
from users.models import User
from fastapi import HTTPException
from datetime import datetime
from utils.sql_request import create_sql_request, sql_request


async def create_manager(manager: ManagesIn, current_user: User):
  PermissionChecker(required_permissions=[Permission.MANAGER_CREATE.value]
                    ).check_permission(current_user.permissions)
  await check_unique(manager)
  ins = dict(manager)
  ins["created_at"] = datetime.now()
  ins["updated_at"] = ins["created_at"]
  ins["archived"] = False
  query = db_manager.insert().values(ins)
  last_record_id = await database.execute(query)
  return {**ins, "id": last_record_id}


async def read_manager_by(current_user: User, all, skip, limit,
                       filter, order_by):
    PermissionChecker(required_permissions=[Permission.MANAGER_READ.value]
                      ).check_permission(current_user.permissions)
    sql = create_sql_request("manager", all, filter, q=None,
                            skip=skip, limit=limit, order_by=order_by)
    result = await sql_request(sql)
    return result


async def archive_manager(id : int, current_user : User):
  PermissionChecker(required_permissions=[Permission.MANAGER_DELETE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_manager.select().where(db_manager.c.id == id))
  if db == None:
    raise HTTPException(status_code=404, detail="manager not found to archive")
  db = (dict(db))
  db["archived"] = True
  query = db_manager.update().where(db_manager.c.id == id).values(db)
  await database.execute(query)
  return {**db}


async def get_manager_by_id(id: int, current_user : User):
  PermissionChecker(required_permissions=[Permission.MANAGER_READ.value]
                    ).check_permission(current_user.permissions)
  query = db_manager.select().where(db_manager.c.id == id)
  res = await database.fetch_one(query)
  if res == None:
      raise HTTPException(status_code=404, detail="manager not found")
  return res


# async def get_manager_by_name(first_name : str, current_user : User):
#   PermissionChecker(required_permissions=[8]).check_permission(current_user.permissions)
#   query = db_manager.select().where(db_manager.c.first_name == first_name)
#   res = await database.fetch_all(query)
#   if res == None:
#       raise HTTPException(status_code=404, detail="manager not found")
#   return res

# async def read_manager(current_user: User, all: bool, skip, limit):
#   PermissionChecker(required_permissions=[8]).check_permission(current_user.permissions)
#   if (all):
#     query = db_manager.select().limit(limit).offset(skip).order_by(db_manager.c.id.desc())
#   else:
#     query = db_manager.select().where(db_manager.c.archived == False
#                                       ).limit(limit).offset(skip).order_by(db_manager.c.id.desc())
#   return await database.fetch_all(query)

async def update_manager(id, manager: ManagesUpdate, current_user : User):
  PermissionChecker(required_permissions=[Permission.MANAGER_CREATE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_manager.select().where(db_manager.c.id == id))
  if db == None:
    raise HTTPException(status_code=404, detail="manager not found to update")
  db = (dict(db))
  if (db.get("first_name") + db.get("last_name") + db.get("patronymic") !=
      manager.first_name + manager.last_name + manager.patronymic):
      await check_unique(manager)
  for k, v in manager.dict().items():
      if k == "archived" and v != db[k]:
         PermissionChecker(required_permissions=[Permission.MANAGER_DELETE.value]
                           ).check_permission(current_user.permissions)
      if v != None:
        db[k] = v
  db['updated_at'] = datetime.now()
  query = db_manager.update().where(db_manager.c.id == db["id"]).values(db)
  await database.execute(query)
  return {**db}


async def check_unique(manager : ManagesIn):
  query = f"SELECT * FROM manager WHERE first_name = '{manager.first_name}' \
          AND last_name = '{manager.last_name}' AND patronymic = '{manager.patronymic}'"
  res = await database.fetch_one(query)
  if res != None:
      raise HTTPException(status_code=404, detail="manager already exists")
  return res
