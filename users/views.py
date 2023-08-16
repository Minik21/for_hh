from typing import List, Annotated
from users.models import User, UserOut, Token, UserIn, UserUpdate, UserOut2
from users.services import get_current_active_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, Query
from users.services import UserServices

from fastapi import APIRouter


user_router = APIRouter(prefix='/user', tags=['users'])
token_router = APIRouter(prefix='/token', tags=['token'])


@user_router.post("", response_model=UserOut)
async def create_user(user: UserIn,
                      current_user: Annotated[User, Depends(get_current_active_user)]):
    return await UserServices().create_user(user, current_user)


@user_router.get("", response_model=UserOut2)
async def read_user_by(current_user: Annotated[User, Depends(get_current_active_user)],
                        skip: int = 0, limit: int | None = 100,
                        filter: str | None = Query(default=None, max_length=100,
                                              description="attribute=partial/full entry"),
                        show_archived: bool | None = False,
                        order_by: str | None = "id_desc"):
    obj = await UserServices().read_good_by(current_user, show_archived,
                                         skip, limit, filter, order_by)
    return {"rows" : obj, "meta" : {"skip" : skip, "limit" : limit, "count" : len(obj)}}


@user_router.patch("/{id}", response_model=UserOut)
async def update_user(id: int,
                      user: UserUpdate,
                      current_user: Annotated[User, Depends(get_current_active_user)]):
    return await UserServices().update_user(id, user, current_user)


@user_router.get("/me", response_model=UserOut)
async def read_users_me(current_user: Annotated[UserOut, Depends(get_current_active_user)]):
    return await UserServices().read_users_me(current_user)


@user_router.delete("/{id}", response_model=UserOut)
async def delete_user_dy_id(id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    return await UserServices().delete_user_by_id(id, current_user)


@user_router.get("/{id}", response_model=UserOut)
async def read_by_id(id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    return await UserServices().read_user_by_id(id, current_user)


@token_router.post("", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return await UserServices().login_for_access_token(form_data)
