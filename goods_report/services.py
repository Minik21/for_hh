from users.permissions import PermissionChecker, Permission
from databeses import database, db_goods, db_goods_size
from users.models import User
from pprint import pprint

async def read_good_report_by(current_user: User, skip, limit,
                       filter, date):
    PermissionChecker(required_permissions=[Permission.GOOD_REPORT_READ.value]
                      ).check_permission(current_user.permissions)
    where, sql_and, body, body_2 = '', '', '', ''
    if date != None:
        where = 'WHERE'
        body = f'goods_report.created_at = \'{date}\''
    if filter != None:
        if where != '':
            sql_and = 'AND'
        where = 'WHERE'
        attribute, value = filter.split("=")
        body_2 = f'{attribute} = \'{value}\''
    sql = f"SELECT * FROM goods_report {where} {body}\
            {sql_and} {body_2} ORDER BY id DESC LIMIT {limit} OFFSET {skip}"
    sql_result = await database.fetch_all(sql)
    return await advertizing_expand_goods_goods_size(sql_result, True)

async def advertizing_expand_goods_goods_size(sql_result, isdict):
    temp = []
    temp_dict = {}
    if not isdict:  
        temp_dict = sql_result      
        req = db_goods.select().where(db_goods.c.id == sql_result['goods_id'])
        s = await database.fetch_one(req)
        temp_dict['goods'] = dict(s)

        req = db_goods_size.select().where(db_goods_size.c.id == sql_result['goods_size_id'])
        s = await database.fetch_one(req)
        temp_dict['goods_size'] = dict(s)
        return temp_dict
    else:
        for row in sql_result:
            temp_dict = dict(row)
            
            req = db_goods.select().where(db_goods.c.id == row['goods_id'])
            s = await database.fetch_one(req)
            temp_dict['goods'] = dict(s)

            req = db_goods_size.select().where(db_goods_size.c.id == row['goods_size_id'])
            s = await database.fetch_one(req)
            temp_dict['goods_size'] = dict(s)

            temp.append(temp_dict)
        return temp
    