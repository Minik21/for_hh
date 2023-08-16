import requests
import json
from pprint import pprint


# def remove_doubles(x):
#     x = [json.dumps(i) for i in x]
#     x = list(set(x))
#     return [json.loads(i) for i in x]


# def verify(x):
#     y = {}
#     for i in x:
#         for j in i:
#             y[j] = 1 if j not in y else y[j] + 1
#     y = set(y.values())
#     l = y.pop()
#     return len(y) == 0 and l == len(x)


def getWB(key, operation, dateFrom="2000-01-01", nameCompany=""):
    # url = "https://statistics-api.wildberries.ru/api/v1/supplier/{}?flag=0&dateFrom={}"
    url = "https://statistics-api.wildberries.ru/api/v1/supplier/reportDetailByPeriod?dateFrom=2023-03-01&dateTo=2023-05-30"
    params = {'Authorization': key}
    done = False
    data = []
    # while not done:
    pprint(url.format(operation, dateFrom))
    pprint(params)
    res = requests.get(url.format(operation, dateFrom), headers=params)
    add_data = json.loads(res.text)
    pprint(add_data)
        # data += add_data
        # done = True
        # if len(add_data)==0: done=True
        # else: dateFrom = data[-1]["lastChangeDate"]
    # pprint(data[0])
    # res = sum([d['quantity']
    #           for d in data if d['sa_name'] == '1730/бордовый/сетка/горох' and d['doc_type_name'] == 'Продажа'])
    # res = sum([d['ppvz_for_pay'] for d in data if
    #            d['sa_name'] == '1730/Синий/сетка/горох' and
    #            d['doc_type_name'] == 'Возврат' and
    #            d['sale_dt'] >= '2023-04-01' and
    #            d['sale_dt'] <= '2023-04-30'])



if __name__ == "__main__":
    op = ["stocks", "orders", "sales"]
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjBlN2UyMWVjLWEzZmUtNGFjMC1iNmZkLWM2MGFhZWVlYjlmMyJ9.7JZtWfvEnb-ikUql3jvLWRa4Wu8bl73c2twn2Ss5oJM"
    data = getWB(key, "incomes", dateFrom="2023-06-06")
    pprint(data)
    # with open("data2.json","r") as f:
    #     x = json.load(f)
    # pprint(x[0])
