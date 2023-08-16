from users.permissions import PermissionChecker, Permission
from databeses import database, db_advertising, db_advertising_type, db_goods
from advertising.models import AdvertisingIn, AdvertisingUpdate
from users.models import User
from fastapi import HTTPException
from utils.sql_request import create_sql_request, sql_request
from datetime import datetime
from pprint import pprint


async def create_advertising(advertising : AdvertisingIn, current_user: User):
    PermissionChecker(required_permissions=[Permission.ADVERTIZING_CREATE.value]
                      ).check_permission(current_user.permissions)
    await check_foreign_keys(dict(advertising))
    ins = dict(advertising)
    ins["created_at"] = datetime.now()
    ins["updated_at"] = ins["created_at"]
    query = db_advertising.insert().values(ins)
    last_record_id = await database.execute(query)
    ins = await advertizing_expand_goods_type(ins, False)
    return {**ins, "id": last_record_id}


async def advertizing_expand_goods_type(sql_result, isdict):
    temp = []
    temp_dict = {}
    if not isdict:  
        temp_dict = sql_result      
        req = db_goods.select().where(db_goods.c.id == sql_result['goods_id'])
        s = await database.fetch_one(req)
        temp_dict['goods'] = dict(s)

        req = db_advertising_type.select().where(db_advertising_type.c.id == sql_result['type_id'])
        s = await database.fetch_one(req)
        temp_dict['type'] = dict(s)
        return temp_dict
    else:
        for row in sql_result:
            temp_dict = dict(row)
            
            req = db_goods.select().where(db_goods.c.id == row['goods_id'])
            s = await database.fetch_one(req)
            temp_dict['goods'] = dict(s)

            req = db_advertising_type.select().where(db_advertising_type.c.id == row['type_id'])
            s = await database.fetch_one(req)
            temp_dict['type'] = dict(s)

            temp.append(temp_dict)
        return temp


async def read_advertising_by(current_user: User, all, skip, limit,
                       filter, order_by):
    PermissionChecker(required_permissions=[Permission.ADVERTIZING_READ.value]
                      ).check_permission(current_user.permissions)
    sql = create_sql_request("advertising", all, filter, q=None,
                            skip=skip, limit=limit, order_by=order_by)
    result = await sql_request(sql)
    return await advertizing_expand_goods_type(result, True)


async def patch_advertising(id, advertising: AdvertisingUpdate, current_user : User):
    PermissionChecker(required_permissions=[Permission.ADVERTIZING_CREATE.value]
                      ).check_permission(current_user.permissions)
    db = await database.fetch_one(db_advertising.select().where(db_advertising.c.id == id))
    if db == None:
        raise HTTPException(status_code=404, detail="advertising not found to update")
    db = (dict(db))
    for k, v in advertising.dict().items():
        if v != None:
            db[k] = v
    await check_foreign_keys(db)
    db['updated_at'] = datetime.now()
    query = db_advertising.update().where(db_advertising.c.id == db["id"]).values(db)
    await database.execute(query)
    res = await advertizing_expand_goods_type(db, False)
    return {**res}


async def read_advertising_by_id(id, current_user: User):
    PermissionChecker(required_permissions=[Permission.ADVERTIZING_READ.value]
                      ).check_permission(current_user.permissions)
    query = db_advertising.select().where(db_advertising.c.id == id)
    result = await database.fetch_one(query)
    if result == None:
        raise HTTPException(status_code=404, detail="Advertizing not found to read")
    res = await advertizing_expand_goods_type(dict(result), False)
    return res


async def delete_advertising(id : int, current_user : User):
    PermissionChecker(required_permissions=[Permission.ADVERTIZING_DELETE.value]
                        ).check_permission(current_user.permissions)
    query = db_advertising.delete().where(db_advertising.c.id == id)
    await database.execute(query)
    return {"id": id}


async def check_foreign_keys(advertising : dict) -> None:
    query = db_goods.select().where(db_goods.c.id == advertising['goods_id'])
    res = await database.fetch_one(query)
    if res == None:
        raise HTTPException(status_code=404, detail="Good not found")    
    query = db_advertising_type.select().where(db_advertising_type.c.id == advertising['type_id'])
    res = await database.fetch_one(query)
    if res == None:
        raise HTTPException(status_code=404, detail="Advertizing_type not found")
