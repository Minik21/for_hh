from typing import List, Annotated
from goods_size.models import GoodsSizeIn, GoodsSizeOut, GoodsSizeUpdate, GoodsSizeOutList
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
import goods_size.services as GoodsSizeService

from fastapi import APIRouter

goods_size_router = APIRouter(prefix='/goods_size', tags=['goods_size'])


@goods_size_router.post("", response_model=GoodsSizeOut)
async def create_goods_size(goods_size: GoodsSizeIn,
                      current_user: Annotated[User, Depends(get_current_active_user)]):
  return await GoodsSizeService.create_goods_size(goods_size, current_user)

# @goods_size_router.get("", response_model=GoodsSizeOutList)
# async def read_goods_size(current_user: Annotated[User, Depends(get_current_active_user)],
#                     skip: int = 0, limit: int | None = 100):
#   obj = await GoodsSizeService.read_goods_size(current_user, skip, limit)
#   return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}

@goods_size_router.get("", response_model=GoodsSizeOutList)
async def read_good_size_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="attribute=partial/full entry"),
                        show_archived: bool | None = False,
                        order_by: str | None = "id_desc"):
  obj = await GoodsSizeService.read_good_size_by(current_user, show_archived,
                                         skip, limit, filter, order_by)
  return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}

@goods_size_router.patch("/{id}", response_model=GoodsSizeOut)
async def patch_goods_size(id: int,
                    goods_size: GoodsSizeUpdate,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
  return await GoodsSizeService.patch_goods_size(id, goods_size, current_user)

@goods_size_router.patch("/archive/{id}", response_model=GoodsSizeOut)
async def archive_goods_size(id: int,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
  return await GoodsSizeService.archive_goods_size(id, current_user)

@goods_size_router.get("/{id}", response_model=GoodsSizeOut)
async def read_by_id(id:int,
                          current_user: Annotated[User, Depends(get_current_active_user)]):
  return await GoodsSizeService.read_goods_size_by_id(id, current_user)