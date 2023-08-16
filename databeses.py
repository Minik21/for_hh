"""Создание таблиц и подключение базы данных + создание суперпользователя"""
import datetime
import databases
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, DateTime, TEXT, null
from sqlalchemy import String, Boolean, VARCHAR, NUMERIC, UniqueConstraint, ForeignKey, BIGINT
from sqlalchemy.dialects.postgresql import JSONB
from users.hash import Hash
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

database = databases.Database(DATABASE_URL)

metadata = MetaData()

db_users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("username", String, nullable=False),
    Column("email", String, nullable=False, default=None, unique=True),
    Column("hashed_password", String, default=None),
    Column("disabled", Boolean, default=False),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("archived", Boolean, default=False),
    Column("permissions", JSONB),
)

db_organization = Table(
    "organization",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("name", VARCHAR(255), nullable=False),
    Column("inn", VARCHAR(255), nullable=False, unique=True),
    Column("standard_token", String, default=None),
    Column("statistics_token", String, default=None),
    Column("advertizing_token", String, default=None),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("archived", Boolean, default=False),
)

db_manager = Table(
    "manager",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("first_name", VARCHAR(255), nullable=False),
    Column("last_name", VARCHAR(255), nullable=False),
    Column("patronymic", VARCHAR(255), default=None),
    Column("archived", Boolean, default=False),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
)

db_good_manager = Table(
    "good_manager",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("manager_id", Integer, ForeignKey("manager.id"), nullable=False),
    Column("goods_id", Integer, ForeignKey("goods.id"), nullable=False),
    Column("date_from", DateTime, nullable=False),
    Column("date_to", DateTime),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
)


db_good_manager_tabel = Table(
    "good_manager_tabel",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("manager_id", Integer, ForeignKey("manager.id"), nullable=False),
    Column("goods_id", Integer, ForeignKey("goods.id"), nullable=False),
    Column("date_from", DateTime, nullable=False),
    Column("date_to", DateTime),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
)


db_category = Table(
    "category",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("name", VARCHAR(255), nullable=False, unique=True),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
)

db_goods = Table(
    "goods",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("article_wb", VARCHAR(255), nullable=False, unique = True),
    Column("zero_cost", NUMERIC),
    Column("average_price", NUMERIC),
    Column("optimal_price", NUMERIC),
    Column("article_code", VARCHAR(255), nullable=False),
    Column("article_options", VARCHAR(255), nullable=False),
    Column("organization_id", Integer, ForeignKey("organization.id")),
    Column("category_id", Integer, ForeignKey("category.id"), nullable=False),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("archived", Boolean, default=False)
)

db_netcost = Table(
    "netcost",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("goods_id", Integer, ForeignKey("goods.id"), nullable=False),
    Column("value", NUMERIC, nullable=False),
    Column("date_from", DateTime, nullable=False),
    Column("date_to", DateTime),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
)

db_goods_size = Table(
    "goods_size",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("goods_id", Integer, ForeignKey("goods.id"), nullable=False),
    Column("size", VARCHAR(255), nullable=False),
    Column("barcode", VARCHAR(255), nullable=False, unique=True),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("archived", Boolean, default=False),
    UniqueConstraint("goods_id", "size")
)

db_self_buyout = Table(
    "self_buyout",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("self_datetime", DateTime),
    Column("goods_size_id", Integer, ForeignKey("goods_size.id"), nullable=False),
    Column("planned_quantity", Integer),
    Column("planned_price", NUMERIC),
    Column("actual_quantity", Integer),
    Column("actual_price", NUMERIC),
    Column("actual_cost", NUMERIC),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
)

db_advertising_type = Table(
    "advertising_type",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("name", VARCHAR(255), nullable=False, unique=True),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
)

db_advertising = Table(
    "advertising",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("buy_datetime", DateTime),
    Column("goods_id", Integer, ForeignKey("goods.id"), nullable=False),
    Column("type_id", Integer, ForeignKey("advertising_type.id"), nullable=False),
    Column("cost", NUMERIC),
    Column("comment", TEXT),
    Column("views", Integer),
    Column("frequency", NUMERIC),
    Column("clicks", Integer),
    Column("ctr", NUMERIC),
    Column("cpc", NUMERIC),
    Column("add_to_cart", Integer),
    Column("orders", Integer),
    Column("amount", NUMERIC),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("updated_at", DateTime, nullable=False, default=datetime.datetime.now()),
)

db_goods_report = Table(
    "goods_report",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("goods_size_id", Integer, ForeignKey("goods_size.id"), nullable=False),
    Column("goods_id", Integer, ForeignKey("goods.id"), nullable=False),
    Column("orders_rate_7", NUMERIC),
    Column("sales_rate_7", NUMERIC),
    Column("free_wb", Integer),
    Column("on_way_wb", Integer),
    Column("in_stock_1c", Integer),
    Column("in_tailoring", Integer),
    Column("in_stock_ff", Integer),
    Column("on_way_ff", Integer),
    Column("in_production", Integer),
    Column("total", NUMERIC),
    Column("days_remain", Integer),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
)

db_union_report = Table(
    "union_report",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("goods_id", Integer),
    Column("count_ordered", Integer),
    Column("count_buyed", Integer),
    Column("count_backordered", Integer),
    Column("ransoms", Integer),
    Column("to_transfer_for_product", NUMERIC),
    Column("expenses_logy", NUMERIC),
    Column("to_pay", NUMERIC),
    Column("total_logy_sum", NUMERIC),
    Column("fines", NUMERIC),
    Column("additional_payments", NUMERIC),
    Column("others", NUMERIC),
    Column("fact_transfer", NUMERIC),
    Column("netcost", NUMERIC),
    Column("expenses_selfbuys", NUMERIC),
    Column("sum_in_selfbuys", NUMERIC),
    Column("expenses", NUMERIC),
    Column("advertising", NUMERIC),
    Column("gross_profit", NUMERIC),
    Column("profitability_gross", NUMERIC),
    Column("sum_retail_price", NUMERIC),
    Column("retail_price", NUMERIC),
    Column("gross_profit_by_one", NUMERIC),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
)


db_report_detail_by_period = Table(
    "report_detail_by_period",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("sa_name", String),
    Column("doc_type_name", VARCHAR(21)),
    Column("sale_dt", DateTime),
    Column("quantity", Integer),
    Column("ppvz_for_pay", NUMERIC),
    Column("delivery_amount", Integer),
    Column("return_amount", Integer),
    Column("delivery_rub", NUMERIC),
    Column("retail_price_withdisc_rub", NUMERIC),
    Column("barcode", VARCHAR(31)),
    Column("nm_id", Integer),
    Column("organization_id", Integer),
    Column("create_dt", DateTime),
    Column("rrd_id", BIGINT),
    Column("gi_id", Integer),
    Column("subject_name", VARCHAR(51)),
    Column("nm_id", Integer),
    Column("brand_name", VARCHAR(51)),
    Column("ts_name", VARCHAR(51)),
    Column("retail_price", NUMERIC),
    Column("retail_amount", NUMERIC),
    Column("sale_percent", Integer),
    Column("commission_percent", NUMERIC),
    Column("office_name", String),
    Column("supplier_oper_name", String),
    Column("order_dt", DateTime),
    Column("rr_dt", DateTime),
    Column("shk_id", BIGINT),
    Column("gi_box_type_name", String),
    Column("product_discount_for_report", NUMERIC),
    Column("supplier_promo", NUMERIC),
    Column("rid", BIGINT),
    Column("ppvz_spp_prc", NUMERIC),
    Column("ppvz_kvw_prc", NUMERIC),
    Column("ppvz_kvw_prc_base", NUMERIC),
    Column("ppvz_ratign_prc_up", NUMERIC),
    Column("is_kgvp_v2", NUMERIC),
    Column("ppvz_sales_commission", NUMERIC),
    Column("ppvz_reward", NUMERIC),
    Column("acquiring_fee", NUMERIC),
    Column("acquiring_bank", String),
    Column("ppvz_vw", NUMERIC),
    Column("ppvz_vw_nds", NUMERIC),
    Column("ppvz_office_id", Integer),
    Column("ppvz_office_name", String),
    Column("ppvz_inn", VARCHAR(51)),
    Column("ppvz_supplier_id", Integer),
    Column("ppvz_supplier_name", String),
    Column("date_to", DateTime),
    Column("realization_id", Integer),
    Column("site_country", VARCHAR(51)),
    Column("sticker_id", VARCHAR(51)),
    Column("sup_rating_prc_up", NUMERIC),
    Column("additional_payment", NUMERIC),
    Column("bonus_type_name", String),
    Column("declaration_number", VARCHAR(51)),
    Column("suppliercontract_code", VARCHAR(51)),
    Column("penalty", NUMERIC),
    Column("date_from", DateTime),
    Column("srid", VARCHAR(51)),
    Column("currency_name", VARCHAR(21)),
    Column("realizationreport_id", Integer),
    Column("rebill_logistic_cost", NUMERIC),
    Column("rebill_logistic_org", String),
    Column("created_at", DateTime),
)

# db_plan_sales = Table(
#     "plan_sales",
#     metadata,
#     Column("id", Integer, primary_key=True, unique=True),

# )

db_stocks = Table(
    "stocks",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("Discount", NUMERIC),
    Column("Price", NUMERIC),
    Column("SCCode", VARCHAR(51)),
    Column("barcode", VARCHAR(31)),
    Column("brand", VARCHAR(51)),
    Column("category", VARCHAR(51)),
    Column("daysOnSite", Integer),
    Column("inWayFromClient", Integer),
    Column("inWayToClient", Integer),
    Column("isRealization", Boolean),
    Column("isSupply", Boolean),
    Column("lastChangeDate", DateTime),
    Column("nmId", Integer),
    Column("quantity", Integer),
    Column("quantityFull", Integer),
    Column("subject", VARCHAR(51)),
    Column("supplierArticle", VARCHAR(76)),
    Column("techSize", VARCHAR(31)),
    Column("warehouseName", VARCHAR(51)),
    Column("organizationId", Integer),
    Column("script_at", DateTime),
)

db_sales = Table(
    "sales",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("IsStorno", Boolean),
    Column("barcode", VARCHAR(31)),
    Column("brand", VARCHAR(51)),
    Column("category", VARCHAR(51)),
    Column("countryName", VARCHAR(201)),
    Column("date", DateTime),
    Column("discountPercent", Integer),
    Column("finishedPrice", NUMERIC),
    Column("forPay", NUMERIC),
    Column("gNumber", VARCHAR(51)),
    Column("incomeID", Integer),
    Column("isRealization", Boolean),
    Column("isSupply", Boolean),
    Column("lastChangeDate", DateTime),
    Column("nmId", Integer),
    Column("organizationId", Integer),
    Column("oblastOkrugName", VARCHAR(200)),
    Column("odid", BIGINT),
    Column("priceWithDisc", NUMERIC),
    Column("promoCodeDiscount", NUMERIC),
    Column("regionName", VARCHAR(200)),
    Column("saleID", VARCHAR(16)),
    Column("spp", NUMERIC),
    Column("srid", String),
    Column("sticker", String),
    Column("subject", VARCHAR(51)),
    Column("supplierArticle", VARCHAR(76)),
    Column("techSize", VARCHAR(31)),
    Column("totalPrice", NUMERIC),
    Column("warehouseName", VARCHAR(51)),
    Column("script_at", DateTime),
)

db_orders = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("barcode", VARCHAR(31)),
    Column("brand", VARCHAR(51)),
    Column("cancel_dt", DateTime),
    Column("category", VARCHAR(51)),
    Column("date", DateTime),
    Column("discountPercent", Integer),
    Column("gNumber", VARCHAR(51)),
    Column("incomeID", Integer),
    Column("isCancel", Boolean),
    Column("lastChangeDate", DateTime),
    Column("nmId", Integer),
    Column("oblast", VARCHAR(201)),
    Column("odid", BIGINT),
    Column("orderType", String),
    Column("srid", String),
    Column("sticker", String),
    Column("subject", VARCHAR(51)),
    Column("supplierArticle", VARCHAR(76)),
    Column("techSize", VARCHAR(31)),
    Column("totalPrice", NUMERIC),
    Column("warehouseName", VARCHAR(51)),
    Column("organizationId", Integer),
    Column("script_at", DateTime),
)


db_incomes = Table(
    "incomes",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("barcode", VARCHAR(31)),
    Column("date", DateTime),
    Column("dateClose", DateTime),
    Column("incomeId", Integer),
    Column("lastChangeDate", DateTime),
    Column("nmId", Integer),
    Column("number", VARCHAR(41)),
    Column("quantity", Integer),
    Column("status", VARCHAR(51)),
    Column("supplierArticle", VARCHAR(76)),
    Column("techSize", VARCHAR(31)),
    Column("totalPrice", NUMERIC),
    Column("warehouseName", VARCHAR(51)),
)


db_sales_plan = Table(
    "sales_plan",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("goods_size_id", Integer),
    Column("goods_id", Integer),
    Column("plan_at_month", Integer),
    Column("fact_at_month", Integer, default=0),
    Column("plan_completion_perc_month", NUMERIC, default=0),
    Column("plan_today", Integer, default=0),
    Column("plan_completion_perc_today", NUMERIC, default=0),
    Column("plan_month_ago", Integer, default=0),
    Column("fact_month_ago", Integer, default=0),
    Column("plan_2month_ago", Integer, default=0),
    Column("fact_2month_ago", Integer, default=0),
    Column("growth_percentage", NUMERIC, default=0),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
)


db_report_goods_sku = Table(
    "help_sku",
    metadata,
    Column("date_at", DateTime, nullable=False, default=datetime.datetime.now()),
    Column("manager_gypoties", String),
    Column("manager_place_for_request", Integer),
    Column("manager_id", Integer),
)


db_dashboard = Table(
    "dashboard",
    metadata,
    Column("id", Integer, primary_key=True, unique=True),
    Column("actual_quantity", Integer),
    Column("adv_cost", NUMERIC),
    Column("article_wb", VARCHAR(100)),
    Column("category_id", Integer),
    Column("fact", Integer),
    Column("good_id", Integer),
    Column("manager_id", Integer),
    Column("per_plane_done", NUMERIC),
    Column("plan", Integer),
    Column("plan_for_today", NUMERIC),
    Column("stock_quantity", Integer),
    Column("sum_actual_cost", NUMERIC),
    Column("sum_salary", NUMERIC),
    Column("sum_prmium", NUMERIC),
    Column("sum_premium_salary", NUMERIC),
    Column("organisation_id", Integer),
    Column("created_at", DateTime, nullable=False, default=datetime.datetime.now()),
)

# db_salarys_calculation = Table(
#     "salarys_calculation",
#     metadata,
#     Column("id", Integer, primary_key=True, unique=True),
#     Column('goods_id', Integer),
#     Column('salary', NUMERIC),
#     Column('premium', NUMERIC),
#     Column('premium_multiplier', NUMERIC),
#     Column('is_new', Boolean),
#     Column('good_created_at', DateTime),
#     Column('fact_at_month', Integer),
#     Column("plan_at_month", Integer),
#     Column("created_at", DateTime),
# )

metadata.create_all(engine)
# создание суперпользователя
s = db_users.select().where(db_users.c.email == "2")
conn = engine.connect()
result = conn.execute(s).fetchall()
if len(result) == 0:
    ins = db_users.insert().values(username="2", hashed_password=Hash().get_password_hash("2"),
                                disabled=False, permissions = [1], email="2")
    print(ins)
    conn = engine.connect()
    result = conn.execute(ins)
# создание тестовых данных (все что ниже - удалить)
s = db_category.select().where(db_category.c.name == "Платья")
conn = engine.connect()
result = conn.execute(s).fetchall()
if len(result) == 0:
    ins = db_category.insert().values(name="Платья")
    conn = engine.connect()
    result = conn.execute(ins)

s = db_manager.select().where(db_manager.c.first_name == "Иван",
                              db_manager.c.last_name == "Иванов",
                              db_manager.c.patronymic == "Иванович")
conn = engine.connect()
result = conn.execute(s).fetchall()
if len(result) == 0:
    ins = db_manager.insert().values(first_name="Иван", last_name="Иванов", patronymic="Иванович")
    conn = engine.connect()
    result = conn.execute(ins)

s = db_organization.select().where(db_organization.c.inn == "123")
conn = engine.connect()
result = conn.execute(s).fetchall()
if len(result) == 0:
    ins = db_organization.insert().values(name="elcora", inn="123",
                                          standard_token = "standart_token",
                                          statistics_token = "statistic_token",
                                          advertizing_token = "advertizing_token",
                                          archived = False)
    conn = engine.connect()
    result = conn.execute(ins)

# select * from goods_report
# insert into goods_report (goods_size_id, datetime_in, orders_rate_7, sales_rate_7, free_wb, on_way_wb, in_stock_1c,
# 						 in_tailoring, in_stock_ff, on_way_ff, in_production, created_at, updated_at)
# 	values (3, '2023-07-17', 2.4, 2.4, 15, 31, 3, 2, 6, 1, 15, '2023-07-17', '2023-07-17')
	
# select * from union_report
# insert into union_report (count_ordered, count_buyed, count_backordered, ransoms, to_transfer_for_product, expenses_logy,
#     					to_pay, total_logy_sum, fines, additional_payments, others, fact_transfer, net_cost,
#     					expenses, gross_profit, profitability_gross, retail_price, gross_profit_by_one, created_at)
# 	values (3, 2, 3, 4, 5, 31.4, 32.1, 11.2, 36.3, 41.2, 15, 22.2, 11.2, 32.1, 55.6, 9, 8, 9, '2023-07-19')