from users.permissions import PermissionChecker, Permission
from databeses import database, db_goods, db_category, db_organization, db_goods_size
from goods.models import GoodsIn, GoodsUpdate
from users.models import User
from fastapi import HTTPException
from utils.sql_request import create_sql_request, sql_request
import datetime


async def create_good(good : GoodsIn, current_user: User):
    PermissionChecker(required_permissions=[Permission.GOODS_CREATE.value]
                      ).check_permission(current_user.permissions)
    await check_foreign_keys(dict(good))
    await check_unique(good)
    ins = dict(good)
    ins["created_at"] = datetime.datetime.now()
    ins["updated_at"] = ins["created_at"]
    ins["archived"] = False
    query = db_goods.insert().values(ins)
    last_record_id = await database.execute(query)
    return {**ins, "id": last_record_id}


async def read_good_by_id(id, current_user: User):
    PermissionChecker(required_permissions=[Permission.GOODS_READ.value]
                      ).check_permission(current_user.permissions)
    query = db_goods.select().where(db_goods.c.id == id)
    result = await database.fetch_one(query)
    if result == None:
        raise HTTPException(status_code=404, detail="Good not found to read")
    return result


async def read_good_by(current_user: User, all, skip, limit,
                       filter, q, order_by):
    PermissionChecker(required_permissions=[Permission.GOODS_READ.value]
                      ).check_permission(current_user.permissions)
    sql = create_sql_request("goods", all, filter, q, "article_wb",
                            "article_code", "article_options",
                            skip=skip, limit=limit, order_by=order_by)
    result = await sql_request(sql)
    return result


async def read_good_by_with_sizes(current_user: User, all, skip, limit,
                       filter, q, order_by):
    PermissionChecker(required_permissions=[Permission.GOODS_READ.value]
                      ).check_permission(current_user.permissions)
    sql = create_sql_request("goods", all, filter, q, "article_wb",
                            "article_code", "article_options",
                            skip=skip, limit=limit, order_by=order_by)
    result = await sql_request(sql)
    return await goods_expand_goods_size(result)


async def patch_good(id, good: GoodsUpdate, current_user : User):
    PermissionChecker(required_permissions=[Permission.GOODS_CREATE.value]
                      ).check_permission(current_user.permissions)
    db = await database.fetch_one(db_goods.select().where(db_goods.c.id == id))
    if db == None:
        raise HTTPException(status_code=404, detail="Good not found to update")
    db = (dict(db))
    if db.get("article_wb") != good.article_wb:
        await check_unique(good)
    for k, v in good.dict().items():
        if k == "archived" and v != db[k]:
          PermissionChecker(required_permissions=[Permission.GOODS_DELETE.value]
                            ).check_permission(current_user.permissions)
        if v != None:
            db[k] = v
    await check_foreign_keys(db)
    db['updated_at'] = datetime.datetime.now()
    query = db_goods.update().where(db_goods.c.id == db["id"]).values(db)
    await database.execute(query)
    return {**db}


async def archive_good(id : int, current_user : User):
    PermissionChecker(required_permissions=[Permission.GOODS_DELETE.value]
                      ).check_permission(current_user.permissions)
    db = await database.fetch_one(db_goods.select().where(db_goods.c.id == id))
    if db == None:
        raise HTTPException(status_code=404, detail="Good not found to archive")
    db = (dict(db))
    db["archived"] = True
    query = db_goods.update().where(db_goods.c.id == id).values(db)
    await database.execute(query)
    return {**db}


async def check_unique(good : GoodsIn):
    query = db_goods.select().where(db_goods.c.article_wb == good.article_wb)
    res = await database.fetch_one(query)
    if res != None:
        raise HTTPException(status_code=404, detail="Good with that article already exists")
    return res


async def check_foreign_keys(good : dict) -> None:
    query = db_category.select().where(db_category.c.id == good['category_id'])
    res = await database.fetch_one(query)
    if res == None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    query = db_organization.select().where(db_organization.c.id == good['organization_id'])
    res = await database.fetch_one(query)
    if res == None:
        raise HTTPException(status_code=404, detail="Organization not found")


async def goods_expand_goods_size(sql_result):
    temp = []
    temp_dict = {}
    for row in sql_result:
        temp_dict = dict(row)
        req = db_goods_size.select().where(db_goods_size.c.goods_id == row['id'])
        s = await database.fetch_all(req)
        temp_dict['sizes'] = []
        for t in s:
            temp_dict['sizes'].append(dict(t))
        temp.append(temp_dict)
    return temp