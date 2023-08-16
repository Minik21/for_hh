from fastapi import HTTPException
from databeses import database
from asyncpg import exceptions


def create_sql_filter_request(on_db, archived, filter, skip, limit, order_by):
    sql_filter, sql_archived, sql_connector, sql_where = "", "", "", ""
    if filter != None:
        try:
            column, value = filter.split("=")
        except ValueError:
            raise HTTPException(status_code=404, detail="Bad filter")
        sql_filter = f'{column}::text ILIKE \'%{value}%\''
    order_name ,order = order_by.split("_")
    if not (archived):
        sql_archived = "archived = False"

    if sql_filter != "" and sql_archived != "":
        sql_connector = " AND "

    if sql_filter != "" or sql_archived != "":
        sql_where = " WHERE "

    sql = f'SELECT * FROM {on_db}{sql_where}{sql_archived}{sql_connector}{sql_filter}\
        ORDER BY {order_name} {order} LIMIT {limit} OFFSET {skip}'
    return sql
    

def create_sql_q_request(on_db, archived, q, *args, skip, limit, order_by):
    sql_archived = ""
    if not (archived):
        sql_archived = "archived = False AND"
    generate_comparasion = ""
    for i in args:
        if generate_comparasion != "":
            generate_comparasion += " OR "
        generate_comparasion += f'{i}::text ILIKE \'%{q}%\''
    order_name ,order = order_by.split("_")
    sql = f"SELECT * FROM {on_db} WHERE {sql_archived} ({generate_comparasion}) \
        ORDER BY {order_name} {order} LIMIT {limit} OFFSET {skip}"
    return sql

def create_sql_request(on_db, archived, filter, q, *args, skip, limit, order_by):
    sql, sql_q, sql_filter = "", "", ""
    if q != None:
        sql_q = create_sql_q_request(on_db, archived, q, *args, skip=skip,
                                     limit=limit, order_by=order_by)
    if filter != None:
        sql_filter = create_sql_filter_request(on_db, archived, filter, skip, limit, order_by)
    
    if sql_q != "" and sql_filter != "":
        sql = f"({sql_q}) INTERSECT ALL ({sql_filter})"
    else:
        if sql_q != "":
            sql = sql_q
        else :
            sql = create_sql_filter_request(on_db, archived, filter, skip, limit, order_by)
    return sql

async def sql_request(body):
    response = None
    try:
        response = await database.fetch_all(body)
    except exceptions.UndefinedColumnError:
        raise HTTPException(status_code=422, detail="Bad Column")
    except exceptions.PostgresSyntaxError:
        raise HTTPException(status_code=422, detail="Bad SQL")
    return response

    