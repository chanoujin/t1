from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sql_test.sqlserver_1014 import Plan1,DatabaseManagement
# , encoding='utf-8', echo=True
import datetime
'''a = datetime.datetime(2020,10,18)
b = datetime.datetime(2020,2,11)
c = a-b
print(c)
>> 250 days, 0:00:00'''
a = DatabaseManagement()
news = Plan1(1,0,1,175,3,2)# 轨道号、出铁口状态、当前任务类型、计划铁水重量、罐次、车号、写入时间
a.add_obj(news)