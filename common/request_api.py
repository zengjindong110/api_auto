# coding=utf-8
import requests

from common.connectdb import ConnectDb
from common.log import Log
from config.get_config_data import GetConfig

logger = Log(__file__)
GC = GetConfig()
gateway = GC.get_config_data("USER")["HOST"]
header = GC.get_header()
execution_sql = ConnectDb()


def deal_with_data(request_data):
    _data = {}
    if "id" in request_data.keys():
        _id = request_data["id"]
    else:
        _id = 999

    data = request_data["data"]
    uri = request_data["uri"]
    method = request_data["method"].lower()
    if "advertiserGroupId" in data.keys():
        advertiser_group_id = GC.get_pmp_id()
        data["advertiserGroupId"] = advertiser_group_id
    if "http" in uri:
        url = uri
    else:
        url = gateway + uri

    _data["uri"] = url
    _data["method"] = method
    _data["data"] = data
    _data["id"] = _id
    return _data


class RequestApi(object):

    def request(self, request_data):
        """
        data ={'id':1,'uri': '/api/v1/landing-page/landing-pages/pmp', 'method': 'post', 'data': {'aa': 'bb'}, 'assert': {'aa': 'bb'}, 'describe': '这是模板'}

        respond = self.request(data)
        """
        logger.info("未处理之前的参数所有请求参数：{}".format(str(request_data)))
        res = ""
        _data = deal_with_data(request_data)
        try:

            if _data["method"] in ["post", "put"]:

                res = requests.request(method=_data["method"], url=_data["uri"],
                                       headers=header, json=_data["data"],
                                       timeout=30)

            elif _data["method"] in ["get", "delete"]:
                res = requests.request(method=_data["method"], url=_data["uri"],
                                       headers=header, params=_data["data"], timeout=30)
        except Exception:
            logger.error("请求的时候出错了出错了:{}".format(str(request_data)))

        logger.info(
            "请求方式：{}  请求头：{} 请求地址：{} 请求参数：{}  返回参数：{}".format(_data["method"], header, _data["uri"],
                                                              _data["data"],
                                                              res.text))

        if request_data["id"] != 999:
            execution_sql.update_data(
                """UPDATE asp_saas_zjd.api_test SET respond = '{}' WHERE id = {}""".format(res.text,
                                                                                           request_data["id"]))

        return res


if __name__ == '__main__':
    r = RequestApi()
    a = {'id': 26, 'uri': '/api/v1/marketing/advertiser-accounts/collect/filtering/from/management', 'method': 'get',
         'data': {'page': 1, 'size': 20, 'sort': 'id',
                  'filtering': [{"field": "system_status", "operator": "IN", "values": [None]},
                                {"field": "account_name", "operator": "LIKE", "values": ["1642912301664260"],
                                 "logic": "OR"},
                                {"field": "corporation_name", "operator": "LIKE", "values": ["1642912301664260"],
                                 "logic": "OR"}, {"field": "cast(account_id as varchar)", "operator": "LIKE",
                                                  "values": ["1642912301664260"], "logic": "OR"}]}, 'assert': 1,
         'describe': '查询投放庄户的id'}
    r.request(a)

