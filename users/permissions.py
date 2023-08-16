from fastapi import HTTPException, status
from enum import Enum

class Permission(Enum):
    ADMIN = 1
    GOODS_READ = 2
    GOODS_CREATE = 3
    GOODS_DELETE = 4
    ORGANIZATIONS_READ = 5
    ORGANIZATIONS_CREATE = 6
    ORGANIZATIONS_DELETE = 7
    MANAGER_READ = 8
    MANAGER_CREATE = 9
    MANAGER_DELETE = 10
    CATEGORY_READ = 11
    CATEGORY_CREATE = 12
    CATEGORY_DELETE = 13
    GOODS_SIZE_READ = 14
    GOODS_SIZE_CREATE = 15
    GOODS_SIZE_DELETE = 16
    ADVERTIZING_TYPE_READ = 17
    ADVERTIZING_TYPE_CREATE = 18
    ADVERTIZING_TYPE_DELETE = 19
    ADVERTIZING_READ = 20
    ADVERTIZING_CREATE = 21
    ADVERTIZING_DELETE = 22
    SELF_BUYOUT_READ = 23
    SELF_BUYOUT_CREATE = 24
    SELF_BUYOUT_DELETE = 25
    NETCOST_READ = 26
    NETCOST_CREATE = 27
    NETCOST_DELETE = 28
    GOOD_MANAGER_READ = 29
    GOOD_MANAGER_CREATE = 30
    GOOD_MANAGER_DELETE = 31
    GOOD_REPORT_READ = 32
    SELF_BUYOUT_REPORT = 33
    UNION_REPORT_READ = 34
    GOOD_MANAGER_TABEL_READ = 35
    GOOD_MANAGER_TABEL_CREATE = 36
    GOOD_MANAGER_TABEL_DELETE = 37
    SALES_PLAN_READ = 38
    SALES_PLAN_CREATE = 39
    DASHBOARD_READ = 40
    SKU_REPORT_READ = 41
    SKU_REPORT_UPDATE = 42

class PermissionChecker:
    def __init__(self, required_permissions: list[int]) -> None:
        self.required_permissions = required_permissions
        self.required_permissions.append(Permission.ADMIN.value)

    def check_permission(self, permissions: list[int]):
        if permissions == None:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f'Wrong Permissions, required: {self.required_permissions}')
        for r_perm in permissions:
            if r_perm in self.required_permissions:
                return True
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Wrong Permissions, required: {self.required_permissions}')
            

def validate_permissions(permissions: list[int]):
    if permissions == []:
        return
    for r_perm in permissions:
        for all_perm in Permission:
            if r_perm == all_perm.value:
                return
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Incorrect type of permissions'
    )
    