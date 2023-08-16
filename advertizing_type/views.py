from typing import List, Annotated
from advertizing_type.models import AdvertisingTypeIn, AdvertisingTypeOut
from advertizing_type.models import AdvertisingTypeUpdate, AdvertisingTypeOutList
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
import advertizing_type.services as AdvertizingTypeService

from fastapi import APIRouter

advertizing_type_router = APIRouter(prefix='/advertizing_type', tags=['advertizing_type'])


@advertizing_type_router.get("", response_model=AdvertisingTypeOutList)
async def read_advertising_type_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="attribute=partial/full entry"),
                        order_by: str | None = "id_desc"):
  obj = await AdvertizingTypeService.read_advertising_type_by(current_user, skip,
                                                limit, filter, order_by)
  return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}


@advertizing_type_router.post("", response_model=AdvertisingTypeOut)
async def create_advertising_type(advertizing_type: AdvertisingTypeIn,
                      current_user: Annotated[User, Depends(get_current_active_user)]):
  return await AdvertizingTypeService.create_advertising_type(advertizing_type, current_user)

# @advertizing_type_router.get("", response_model=AdvertizingTypeOutList)
# async def read_advertizing_type(current_user: Annotated[User, Depends(get_current_active_user)],
#                     skip: int = 0, limit: int | None = 100):
#   obj = await Ad.read_advertizing_type(current_user, skip, limit)
#   return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}

@advertizing_type_router.patch("/{id}", response_model=AdvertisingTypeOut)
async def patch_advertising_type(id: int,
                    advertizing_type: AdvertisingTypeUpdate,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
  return await AdvertizingTypeService.patch_advertising_type(id, advertizing_type, current_user)

@advertizing_type_router.delete("/{id}", response_model={})
async def delete_advertising_type(id: int,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
  return await AdvertizingTypeService.delete_advertising_type(id, current_user)

@advertizing_type_router.get("/{id}", response_model=AdvertisingTypeOut)
async def read_by_id(id:int,
                     current_user: Annotated[User, Depends(get_current_active_user)]):
  return await AdvertizingTypeService.read_advertising_type_by_id(id, current_user)
