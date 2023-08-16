from typing import List, Annotated
from managers.models import ManagesIn, ManagersOut, ManagesUpdate, ManagersOutList
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
import managers.services as ManagerServicies

from fastapi import APIRouter

managers_router = APIRouter(prefix='/managers', tags=['managers'])


@managers_router.post("", response_model=ManagersOut)
async def create_manager(manager: ManagesIn,
                              current_user: Annotated[User, Depends(get_current_active_user)]):
    return await ManagerServicies.create_manager(manager, current_user)

@managers_router.get("", response_model=ManagersOutList)
async def read_manager_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="attribute=partial/full entry"),
                        show_archived: bool | None = False,
                        order_by: str | None = "id_desc"):
  obj = await ManagerServicies.read_manager_by(current_user, show_archived,
                                         skip, limit, filter, order_by)
  return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}

@managers_router.patch("", response_model=ManagersOut)
async def update_manager(id: int,
                              manager: ManagesUpdate,
                              current_user: Annotated[User, Depends(get_current_active_user)]):
    return await ManagerServicies.update_manager(id, manager, current_user)

# @managers_router.get("", response_model=ManagersOutList)
# async def read_manager(current_user: Annotated[User, Depends(get_current_active_user)],
#                     skip: int = 0, limit: int | None = 100):
#     obj = await ManagerServicies.read_manager(current_user, 0, skip, limit)
#     return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}

# @managers_router.get("/all", response_model=ManagersOutList)
# async def read_manager(current_user: Annotated[User, Depends(get_current_active_user)],
#                     skip: int = 0, limit: int | None = 100):
#     obj = await ManagerServicies.read_manager(current_user, 1, skip, limit)
#     return {"rows" : obj, "meta" : {"skip" : skip,
#                                     "limit" : limit,
#                                     "count" : len(obj)}}

# @managers_router.get("/name/{first_name} {second_name} {patronym}", response_model=ManagersOutList)
# async def read_user_by_name(first_name: str, current_user: Annotated[User, Depends(get_current_active_user)],
#                             skip: int = 0, limit: int | None = 100):
#     obj = await ManagerServicies.read_manager_by_name(first_name, current_user)
#     return {"rows" : obj, "meta" : {"skip" : skip,
#                                     "limit" : limit,
#                                     "count" : len(obj)}}

@managers_router.get("/{id}", response_model=ManagersOut)
async def read_by_id(id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    return await ManagerServicies.get_manager_by_id(id, current_user)

@managers_router.patch("/archive/{id}", response_model=ManagersOut)
async def archive_good(id: int,
                       current_user: Annotated[User, Depends(get_current_active_user)]):
  return await ManagerServicies.archive_manager(id, current_user)