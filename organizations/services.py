from users.permissions import PermissionChecker, Permission
from databeses import database, db_organization
from organizations.models import OrganizationIn, OrganizationUpdate
from users.models import User
from fastapi import HTTPException
from datetime import datetime
from utils.sql_request import create_sql_request, sql_request
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjBlN2UyMWVjLWEzZmUtNGFjMC1iNmZkLWM2MGFhZWVlYjlmMyJ9.7JZtWfvEnb-ikUql3jvLWRa4Wu8bl73c2twn2Ss5oJM"
async def create_organization(organization: OrganizationIn, current_user: User):
  PermissionChecker(required_permissions=[Permission.ORGANIZATIONS_CREATE.value]
                    ).check_permission(current_user.permissions)
  await check_unique(organization)
  ins = dict(organization)
  ins["created_at"] = datetime.now()
  ins["updated_at"] = ins["created_at"]
  ins["archived"] = False
  query = db_organization.insert().values(ins)
  last_record_id = await database.execute(query)
  return {**ins, "id": last_record_id}

async def archive_organization(id : int, current_user : User):
  PermissionChecker(required_permissions=[Permission.ORGANIZATIONS_DELETE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_organization.select(
                      ).where(db_organization.c.id == id))
  if db == None:
    raise HTTPException(status_code=404, detail="Organization not found to archive")
  db = (dict(db))
  db["archived"] = True
  query = db_organization.update().where(db_organization.c.id == id).values(db)
  await database.execute(query)
  return {**db}

async def get_organization_by_id(id: int, current_user : User):
  PermissionChecker(required_permissions=[Permission.ORGANIZATIONS_READ.value]
                    ).check_permission(current_user.permissions)
  query = db_organization.select().where(db_organization.c.id == id)
  res = await database.fetch_one(query)
  if res == None:
      raise HTTPException(status_code=404, detail="Organization not found")
  return res


async def read_organization_by(current_user: User, all, skip, limit,
                       filter, order_by):
    PermissionChecker(required_permissions=[Permission.ORGANIZATIONS_READ.value]
                      ).check_permission(current_user.permissions)
    sql = create_sql_request("organization", all, filter, q=None,
                            skip=skip, limit=limit, order_by=order_by)
    result = await sql_request(sql)
    return result


async def update_organization(id, organization: OrganizationUpdate, current_user : User):
  PermissionChecker(required_permissions=[Permission.ORGANIZATIONS_CREATE.value]
                    ).check_permission(current_user.permissions)
  db = await database.fetch_one(db_organization.select(
                    ).where(db_organization.c.id == id))
  if db == None:
    raise HTTPException(status_code=404, detail="Organization not found to update")
  db = (dict(db))
  if db.get("inn") != organization.inn:
      await check_unique(organization)
  for k, v in organization.dict().items():
      if k == "archived" and v != db[k]:
         PermissionChecker(required_permissions=[Permission.ORGANIZATIONS_DELETE.value]
                           ).check_permission(current_user.permissions)
      if v != None:
        db[k] = v
  query = db_organization.update().where(db_organization.c.id == db["id"]).values(db)
  await database.execute(query)
  return {**db}

async def check_unique(organization : OrganizationIn):
  query = db_organization.select().where(db_organization.c.inn == organization.inn)
  res = await database.fetch_one(query)
  if res != None:
      raise HTTPException(status_code=404,
                          detail="Organization with that inn already exists")
  return res
 