from typing import List, Annotated
from organizations.models import OrganizationIn, OrganizationOut, OrganizationUpdate, OrganizationOut2
from users.models import User
from users.services import get_current_active_user
from fastapi import Depends, Query
import organizations.services as OrganizationServices

from fastapi import APIRouter

organization_router = APIRouter(prefix='/organization', tags=['organizations'])


@organization_router.get("", response_model=OrganizationOut2)
async def read_organization_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="attribute=partial/full entry"),
                        show_archived: bool | None = False,
                        order_by: str | None = "id_desc"):
  obj = await OrganizationServices.read_organization_by(current_user, show_archived,
                                         skip, limit, filter, order_by)
  return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}


@organization_router.post("", response_model=OrganizationOut)
async def create_organization(organization: OrganizationIn,
                              current_user: Annotated[User, Depends(get_current_active_user)]):
    return await OrganizationServices.create_organization(organization, current_user)

@organization_router.patch("", response_model=OrganizationOut)
async def update_organization(id: int,
                              organization: OrganizationUpdate,
                              current_user: Annotated[User, Depends(get_current_active_user)]):
    return await OrganizationServices.update_organization(id, organization, current_user)

# @organization_router.get("", response_model=OrganizationOut2)
# async def read_organization(current_user: Annotated[User, Depends(get_current_active_user)],
#                     skip: int = 0, limit: int | None = 100):
#     obj = await OrganizationServices.read_organization(current_user, 0, skip, limit)
#     return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}

# @organization_router.get("/all", response_model=OrganizationOut2)
# async def read_organization(current_user: Annotated[User, Depends(get_current_active_user)],
#                     skip: int = 0, limit: int | None = 100):
#     obj = await OrganizationServices.read_organization(current_user, 1, skip, limit)
#     return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}

@organization_router.get("/{id}", response_model=OrganizationOut)
async def read_by_id(id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    return await OrganizationServices.get_organization_by_id(id, current_user)

@organization_router.patch("/archive/{id}", response_model=OrganizationOut)
async def archive_good(id: int,
                       current_user: Annotated[User, Depends(get_current_active_user)]):
  return await OrganizationServices.archive_organization(id, current_user)