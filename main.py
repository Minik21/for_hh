from fastapi import FastAPI
from databeses import database
from fastapi import FastAPI
from users.views import user_router, token_router
from goods.views import goods_router
from category.views import category_router
from managers.views import managers_router
from organizations.views import organization_router
from goods_size.views import goods_size_router
from advertizing_type.views import advertizing_type_router
from advertising.views import advertising_router
from self_buyout.views import self_buyout_router
from netcost.views import netcost_router
from good_manager.views import good_manager_router
from goods_report.views import goods_report_router
from fastapi.middleware.cors import CORSMiddleware
from union_report.views import union_report_router
from good_manager_tabel.views import good_manager_tabel_router
from sales_plan.views import sales_plan_router
from dashboard.views import dashboard_router
from sku_report.views import sku_report_router
import uvicorn

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(sku_report_router)
app.include_router(dashboard_router)
app.include_router(sales_plan_router)
app.include_router(union_report_router)
app.include_router(goods_report_router)
app.include_router(good_manager_router)
app.include_router(good_manager_tabel_router)
app.include_router(netcost_router)
app.include_router(self_buyout_router)
app.include_router(advertising_router)
app.include_router(advertizing_type_router)
app.include_router(goods_size_router)
app.include_router(user_router)
app.include_router(token_router)
app.include_router(organization_router)
app.include_router(goods_router)
app.include_router(category_router)
app.include_router(managers_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
