from typing import Annotated
from fastapi import Depends, Query
from good_manager_tabel.models import (GoodManagerTabelIn, GoodManagerTabelOut,
GoodManagerTabelUpdate, GoodManagerOutTabelList)
from users.models import User
from users.services import get_current_active_user
import good_manager_tabel.services as GoodManagerService

from fastapi import APIRouter

good_manager_tabel_router = APIRouter(prefix='/good_manager_tabel',
                                tags=['good_manager_tabel'])


@good_manager_tabel_router.post("", response_model=GoodManagerTabelOut)
async def create_good_manager(good_manager: GoodManagerTabelIn,
                      current_user: Annotated[User, Depends(get_current_active_user)]):
    return await GoodManagerService.create_good_manager_tabel(good_manager, current_user)


@good_manager_tabel_router.get("", response_model=GoodManagerOutTabelList)
async def read_good_manager_tabel_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="attribute=partial/full entry"),
                        order_by: str | None = "id_desc"):
    obj = await GoodManagerService.read_good_manager_tabel_by(current_user, True,
                                         skip, limit, filter, order_by)
    return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}


@good_manager_tabel_router.patch("/{id}", response_model=GoodManagerTabelOut)
async def patch_good_manager(id : int,
                    good_manager: GoodManagerTabelUpdate,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
    return await GoodManagerService.patch_good_manager_tabel(id, good_manager, current_user)


@good_manager_tabel_router.delete("/{id}", response_model={})
async def delete_good_manager(id : int,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
    return await GoodManagerService.delete_good_manager_tabel(id, current_user)


# @good_manager_tabel_router.get("/{id}", response_model=GoodManagerTabelOut)
# async def read_by_id(id : int,
#                     current_user: Annotated[User, Depends(get_current_active_user)]):
#     return await GoodManagerService.read_good_manager_by_id(id, current_user)
