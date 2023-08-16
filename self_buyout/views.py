from typing import List, Annotated
from self_buyout.models import SelfBuyoutIn, SelfBuyoutOut, SelfBuyoutUpdate
from self_buyout.models import SelfBuyoutOutList, SelfBuyoutExp
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
import self_buyout.services as SelfBuyoutService

from fastapi import APIRouter

self_buyout_router = APIRouter(prefix='/self_buyout', tags=['self_buyout'])


@self_buyout_router.post("", response_model=SelfBuyoutOut)
async def create_self_buyout(self_buyout: SelfBuyoutIn,
                      current_user: Annotated[User, Depends(get_current_active_user)]):
  return await SelfBuyoutService.create_self_buyout(self_buyout, current_user)


@self_buyout_router.get("", response_model=SelfBuyoutOutList)
async def read_self_buyout_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="attribute=partial/full entry"),
                        order_by: str | None = "id_desc"):
    obj = await SelfBuyoutService.read_self_buyout_by(current_user, True,
                                          skip, limit, filter, order_by)
    return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}


@self_buyout_router.get("/report")
async def get_report(current_user: Annotated[User,
                                             Depends(get_current_active_user)]
                     ,year: int, month: int | None = None,
                     goods_id: int | None = None):
    return await SelfBuyoutService.get_self_buyout_report(current_user,
                                                          year, month, goods_id)


@self_buyout_router.patch("/{id}", response_model=SelfBuyoutOut)
async def patch_self_buyout(id: int,
                    self_buyout: SelfBuyoutUpdate,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
    return await SelfBuyoutService.patch_self_buyout(id, self_buyout, current_user)


@self_buyout_router.delete("/{id}", response_model={})
async def delete_self_buyout(id: int,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
  return await SelfBuyoutService.delete_self_buyout(id, current_user)


@self_buyout_router.get("/{id}", response_model=SelfBuyoutOut)
async def read_by_id(id:int,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
  return await SelfBuyoutService.read_self_buyout_by_id(id, current_user)