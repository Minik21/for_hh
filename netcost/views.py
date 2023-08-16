from typing import Annotated
from fastapi import Depends, Query
from netcost.models import NetcostIn, NetcostOut, NetcostUpdate, NetcostOutList
from users.models import User
from users.services import get_current_active_user
import netcost.services as NetcostService

from fastapi import APIRouter

netcost_router = APIRouter(prefix='/goods_netcost', tags=['goods_netcost'])


@netcost_router.post("", response_model=NetcostOut)
async def create_netcost(netcost: NetcostIn,
                      current_user: Annotated[User, Depends(get_current_active_user)]):
    return await NetcostService.create_netcost(netcost, current_user)


@netcost_router.get("", response_model=NetcostOutList)
async def read_netcost_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="attribute=partial/full entry"),
                        order_by: str | None = "id_desc"):
    obj = await NetcostService.read_netcost_by(current_user, True,
                                         skip, limit, filter, order_by)
    return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}


@netcost_router.patch("/{id}", response_model=NetcostOut)
async def patch_netcost(id : int,
                    netcost: NetcostUpdate,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
    return await NetcostService.patch_netcost(id, netcost, current_user)


@netcost_router.delete("/{id}", response_model={})
async def delete_netcost(id : int,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
    return await NetcostService.delete_netcost(id, current_user)


@netcost_router.get("/{id}", response_model=NetcostOut)
async def read_by_id(id : int,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
    return await NetcostService.read_netcost_by_id(id, current_user)