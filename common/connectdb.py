import json
# import pymysql
import threading

import psycopg2

from config.get_config_data import GetConfig


class ConnectDb(object):
    def __init__(self):
        self.gc = GetConfig()
        self.config = self.gc.get_config_data("PG")
        # self.connect = pymysql.connect(host=self.config["HOST"],
        #                                port=3306,
        #                                user=self.config["USER"],
        #                                passwd=self.config["PASSWORD"],
        #                                db=self.config["DB"],
        # print(self.config["HOST"], self.config["USER"], self.config["PASSWORD"], self.config["DB"])
        self.connect = psycopg2.connect(host=self.config["HOST"],
                                        port=5432,
                                        user=self.config["USER"],
                                        password=self.config["PASSWORD"],
                                        database=self.config["DB"]
                                        )
        self.cursor = self.connect.cursor()
        self.lock = threading.Lock()

    def __del__(self):

        # self.connect.close()
        # self.cursor.close()
        pass

    def execute_sql(self, sql):
        """
        执行sql
        :param sql:
        :return:
        """
        self.cursor.execute(sql)

        return self.cursor.execute(sql)

    def insert_data(self, sql):

        """
        执行insert语句插入数据到数据库
        :param sql:
        :return:
        """
        try:
            result = self.execute_sql(sql)
            self.connect.commit()
            return result
        # 错误回滚
        except Exception as E:
            print('\033[1;31;31m err-sql  "{}" {} \033[0m!'.format(sql, E))
            self.connect.rollback()

    def select_data(self, sql):
        """
        执行select语句查询输入,返回所有数据
        :param sql:
        :return:
        """

        try:
            self.execute_sql(sql)
            all_data = self.cursor.fetchall()

            return all_data
        except Exception as E:
            print('\033[1;31;31m err-sql  "{}" {} \033[0m!'.format(sql, E))
            self.connect.rollback()

    def update_data(self, sql):
        try:
            result = self.execute_sql(sql)
            self.connect.commit()
            return result
        # 错误回滚
        except Exception as E:
            print('\033[1;31;31m err-sql  "{}" {} \033[0m!'.format(sql, E))
            self.connect.rollback()

    def get_pmp_id(self):
        pmp_id = json.loads(self.select_data(
            """SELECT respond FROM api_test WHERE uri = '/api/v1/marketing/advertiser-account-groups/collect/list' """)[
                                0][0])["records"][0]["id"]

        return pmp_id


if __name__ == '__main__':
    c = ConnectDb()
    x = c.select_data(
        """SELECT respond FROM api_test WHERE uri = '/api/v1/marketing/advertiser-account-groups/collect/list' """)
    print(x)
    print(c.get_pmp_id())