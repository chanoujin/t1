import struct

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql_test.sqlserver_1014 import Plan1,DatabaseManagement
from sql_test.sqlserver_1014 import Plan1,Car_Queue
import snap7
from snap7.util import get_int,get_string
plc=snap7.client.Client()
plc.connect('192.168.6.102',0,1)
print('connect success')
area   = 0x84
start  = 0
length = 1
bit    = 0
c = [0,0,0,0,0,0,0,0]
d = []
# 读取出铁口状态
byte1= plc.db_read(1,0,10)
byte2= plc.db_read(2,0,10)
byte3= plc.db_read(3,0,10)
byte4= plc.db_read(4,0,10)
byte5= plc.db_read(5,0,10)
byte6= plc.db_read(6,0,10)
byte7= plc.db_read(7,0,10)
byte8= plc.db_read(8,0,10)
c[0] = byte1
c[1] = byte2
c[2] = byte3
c[3] = byte4
c[4] = byte5
c[5] = byte6
c[6] = byte7
c[7] = byte8
s = DatabaseManagement()
for i in range(len(c)):
    news = s.query_all(Plan1,Plan1.truck_num==c[i])
    Mytruck_state = news.truck_state
    if Mytruck_state is 0:
        plc.write_area()
        news1 = Plan1(news.truck_num,0,4,0,1,news.car_num)
        s.add_obj(news1)
