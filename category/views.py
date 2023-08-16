from typing import List, Annotated
from category.models import CategoryIn, CategoryOut, CategoryUpdate, CategoryOutList
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
import category.services as CategoryServices
from typing import List

from fastapi import APIRouter

category_router = APIRouter(prefix='/category', tags=['category'])


@category_router.get("", response_model=CategoryOutList)
async def read_category_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="attribute=partial/full entry"),
                        # show_archived: bool | None = False,
                        order_by: str | None = "id_desc"):
  obj = await CategoryServices.read_category_by(current_user, skip,
                                                limit, filter, order_by)
  return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}


@category_router.post("", response_model=CategoryOut)
async def create_category(category: CategoryIn,
                      current_user: Annotated[User, Depends(get_current_active_user)]):
  return await CategoryServices.create_category(category, current_user)

# @category_router.get("", response_model=CategoryOutList)
# async def read_category(current_user: Annotated[User, Depends(get_current_active_user)],
#                     skip: int = 0, limit: int | None = 100):
#   obj = await CategoryServices.read_category(current_user, skip, limit)
#   return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}

@category_router.patch("/{id}", response_model=CategoryOut)
async def patch_category(id: int,
                    category: CategoryUpdate,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
  return await CategoryServices.patch_category(id, category, current_user)

@category_router.delete("/{id}", response_model={})
async def delete_category(id: int,
                    current_user: Annotated[User, Depends(get_current_active_user)]):
  return await CategoryServices.delete_category(id, current_user)

@category_router.get("/{id}", response_model=CategoryOut)
async def read_by_id(id:int,
                     current_user: Annotated[User, Depends(get_current_active_user)]):
  return await CategoryServices.read_category_by_id(id, current_user)