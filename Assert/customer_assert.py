# -*- coding: utf-8 -*-
import datetime
from time import sleep

from common.get_config_data import GetConfig
from common.log import Log
from common.request_api import RequestApi

GC = GetConfig()

log = Log(__file__)


class Customer(RequestApi):
    """
    客资断言
    1.判断最新的一条客资有没有生成，以时间为条件，启动落地页的时候会生成一个开始时间
    2.判断生成的click_id是不是在客资的的url上面
    3，是否上报成功
    """

    def __init__(self):
        super().__init__()

        self.customer_li = ""

    def get_data(self):
        get_data_params = {
            "uri": "/api/v1/customer/customers/pmp",
            "method": "get",
            "data": {"page": 1,
                     "size": 20,
                     "order": "desc",
                     "sort": "createdAt",
                     "advertiserAccountId": int(GC.get_config_data("PMP")["PMP_ID"]),
                     "filtering": [{"field": "advertiser_account_group_id", "operator": "EQ",
                                    "values": [int(GC.get_config_data("PMP")["PMP_ID"])]}],
                     "startTime": str(datetime.date.today()),
                     "endTime": str(datetime.date.today())
                     },
            "id": 18
        }
        # 取客资最近的一条客资
        self.customer_li = self.request(get_data_params)["records"][0]

    @staticmethod
    def compare_time(start_time, create_customer_time):
        """
        时间比较，打开的落地页时间小于生成客资的时间结果返回为Ture
        """
        d_start = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')

        d_end = datetime.datetime.strptime(create_customer_time, '%Y-%m-%d %H:%M:%S')

        result = d_start <= d_end
        return result

    def assert_customer(self, start_time):
        """
        客资断言
        1.判断最新的一条客资有没有生成，以时间为条件，启动落地页的时候会生成一个开始时间
        """

        self.get_data()

        # 查到客资生成的时间
        create_customer_time = self.customer_li["createdAt"].replace("T", " ")[:-5]
        # 把strTime转化为时间格式
        startTime = datetime.datetime.strptime(create_customer_time, '%Y-%m-%d %H:%M:%S')
        # 将客资转化成+8的时间
        create_customer_time = (startTime + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        # 是否生成客资
        is_customer = self.compare_time(start_time, str(create_customer_time))

        log.warning(f"断言判断客资是否生成{start_time}< 生成客资时间{create_customer_time}")
        return is_customer

    def assert_click_id(self, click_id):
        """
        2.判断生成的click_id是不是在客资的的url上面
        click_id 在最新的客资上则这个客资为当前客资
        """
        # 访问URL(成功添加企业微信)
        wechatAppletLandingPageViewUrl = self.customer_li["wechatAppletLandingPageViewUrl"]
        log.warning(f"断言判断客资是否有clickid{wechatAppletLandingPageViewUrl}生成的click_id {click_id}")
        return True if click_id in wechatAppletLandingPageViewUrl else False

    def assert_customer_upload(self):
        """
        3，是否上报成功
        如果有一个上报条件是False断言失败
        """
        uploadRecordReturnMessageDtos = self.customer_li["uploadRecordReturnMessageDtos"]
        # 获取上报是否成功
        upload_status = [i["isSuccess"] for i in uploadRecordReturnMessageDtos]
        log.warning(f"断言判断客资是否上报成功{upload_status}")
        return False if False in upload_status else True

    def applet_add_friends_assert(self, start_time, click_id):
        """
        断言小程序添加好友链路合并起来的方法
        """
        customer_wait_time = 0

        while customer_wait_time < int(GC.get_config_data("WAIT")["CUSTOMER_WAIT_TIME"]):
            assert_data = [self.assert_customer(start_time), self.assert_customer_upload(),
                           self.assert_click_id(click_id)]
            is_true = True if False not in assert_data else False
            if is_true:
                return True
            else:
                sleep(5)
                log.error(f"等待客资生成{customer_wait_time}秒")
            customer_wait_time += 5


    def assert_customer_value(self):
        pass


if __name__ == '__main__':
    aaa = Customer()
    clickid = "EIfQmZ-Dq4cDGKaZ3PXcAiDt77C3qvXHBzAMOMG4AkIiMjAyMjAxMDUxOTM5MDQwMTAxNTAxNjExNjIwMEM3NDQ2MkjBuAKQAAC"
    aaa.assert_customer(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(aaa.assert_customer_upload())
