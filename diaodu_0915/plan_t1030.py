from sqlalchemy.orm import sessionmaker

from diaodu_0915.diaodu1013 import metal_time
from sql_test.db_ms import DatabaseManagement
from sql_test.car_queue import Car_Queue
from sqlalchemy import and_, create_engine
from sql_test.sqlserver_1014 import Plan1
import snap7
from snap7.util import get_real
from datetime import datetime
import time
import pandas as pd

engine = create_engine('mysql+pymysql://root:123456cj@localhost:3306/cj_1029?charset=utf8')  # 初始化数据库连接

DBsession = sessionmaker(bind=engine)  # 创建DBsession类
session = DBsession()  # 创建对象

def transport1():
    while True:
        time.sleep(10)
        data1 = pd.read_csv('d1/data1.csv','r')
        data1_w = data1['weight']
        data1_t = data1['write_time']
        c = 0
        d = 0
        f = 0
        for i in range(len(data1_w)):
            d = data1_w[i]
            e = d-c
            if e<=0:

                news = Plan1(1,0,3,150,1,1,data1_t[i])

                session.add(news)
                session.commit()
            c = d

if __name__ == '__main__':
    transport1()