from typing import List, Annotated
from advertising.models import AdvertisingIn, AdvertisingOut, AdvertisingUpdate
from advertising.models import AdvertisingIn, AdvertisingOutSingle, AdvertisingOutList
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
from advertising import services as AdvertisingService

from fastapi import APIRouter

advertising_router = APIRouter(prefix='/advertising', tags=['advertising'])


@advertising_router.post("", response_model=AdvertisingOut)
async def create_advertising(advertising: AdvertisingIn,
                      current_user: Annotated[User, Depends(get_current_active_user)]):
  return await AdvertisingService.create_advertising(advertising, current_user)


@advertising_router.get("", response_model=AdvertisingOutList)
async def read_advertising_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="attribute=partial/full entry"),
                        order_by: str | None = "id_desc"):
    obj = await AdvertisingService.read_advertising_by(current_user, True,
                                         skip, limit, filter, order_by)
    return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}


@advertising_router.patch("/{id}", response_model=AdvertisingOut)
async def patch_advertising(id: int,
                    advertising: AdvertisingUpdate,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
    return await AdvertisingService.patch_advertising(id, advertising, current_user)


@advertising_router.delete("/{id}", response_model={})
async def delete_advertising_type(id: int,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
  return await AdvertisingService.delete_advertising(id, current_user)


@advertising_router.get("/{id}", response_model=AdvertisingOut)
async def read_by_id(id:int,
                     current_user: Annotated[User, Depends(get_current_active_user)]):
  return await AdvertisingService.read_advertising_by_id(id, current_user)

