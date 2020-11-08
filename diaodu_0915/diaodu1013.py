import threading
import time
from datetime import timedelta
import datetime
from queue import Queue
import struct
import requests
import snap7
from snap7.util import get_real, get_int, get_dword, get_bool, get_string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sql_test.car_queue import Car_Queue, Tank_Queue
from sql_test.sqlserver_1014 import DatabaseManagement, Person, Plan1, car_Position


# 多线程
class MyThread(threading.Thread):
    def __init__(self, threadID, func, args):
        super(MyThread, self).__init__()
        self.threadID = threadID

        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None


# 读取罐车实时位置
def tank_position(track, db):
    engine = create_engine('mssql+pymssql://sa:123456cj@LAPTOP-UK384UED\SQLEXPRESS/cjt3')  # IP/dbName?driver=SQL+Server
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建Session:
    session = DBSession()
    # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
    user = session.query(db).filter(track).first()
    # 打印类型和对象的name属性:
    print(user.id, user.track, user.car_number, user.time_one, user.time_two, user.time_three, user.position,
          user.direction)
    # 关闭Session:
    session.close()
    return user


# 轨道判断
def track_state(sd):
    if (sd % 2) == 0:
        return sd - 1
    else:
        return sd + 1


# plc写
def plc_w(start, my_Data):
    try:
        plc = snap7.client.Client()
        plc.connect('192.168.6.101', 0, 1)
        plc.write_area(0x84, 100, start, my_Data)
    except:
        print('plc connect error')


# plc读
def plc_r(db_number, start, size):
    try:
        plc = snap7.client.Client()
        plc.connect('192.168.6.101', 0, 1)
        print('connect success')
        area = 0x84
        news = plc.read_area(area, db_number, start, size)
        return news

    except:
        print('can not connect plc')


# 出铁完成时间预测
def metal_time():
    while True:
        metal_weight = 150
        t1 = metal_weight / 5  # 出铁时间预测

        t2 = datetime.datetime.now()
        t = t2 + timedelta(minutes=int(t1))  # 出铁完成时间
        return t


# 返回
def tank_back():
    while True:
        for i in range(8):
            start_t = 22 + i * 36
            start_w = 578 + i * 4
            start_s = 576 + i * 4

            tank_state = plc_r(100, start_t, 6)
            truck_state = get_bool(tank_state, 1, 0)
            # 空罐装载完成
            if truck_state:
                mysql_2 = DatabaseManagement()
                truck_s = get_bool(plc_r(100, start_s, 2), 0, 0)
                # 出铁口未出铁
                if truck_s is False:
                    truck = i + 1
                    # 原点、接铁、炼钢、废钢---1、2、3、4
                    # 查询炼钢区域指定轨道车辆
                    data = mysql_2.query_all(car_Position,
                                             car_Position.truck_num == truck and car_Position.position == 3)
                    # 如果后车在炼钢
                    if data.car_num % 2 == 0:
                        plc_w(start_t, struct.pack('B', 2))
                        news_b = Plan1(data.car_num, 0, 2, 0, None)

                    # 如果前车在炼钢
                    else:
                        data2 = mysql_2.query_all(car_Position, car_Position.car_num == data.car_num + 1)
                        if data2.position > 0:
                            plc_w(start_t, struct.pack('B', 2))
                            news_b = Plan1(data.car_num, 0, 2, 0, None)


# 重罐运输
def transport1():
    while True:
        tr = False
        # 读取出铁口状态
        for i in range(8):
            db = 576 + i * 4
            start_w = 578 + i * 4
            start_s = 607 + i
            truck_state = plc_r(100, db, 2)  # 出铁口状态
            truck_state = get_bool(truck_state, 0, 0)
            # 铁水接满0-1
            if truck_state - tr == -1:

                mysql_2 = DatabaseManagement()
                weight = get_int(plc_r(100, start_w, 4), 0)
                weight = get_int(weight, 0)
                steel_scrap_w = get_int(plc_r(100, start_s, 4), 0)
                real_w = weight + steel_scrap_w
                if weight >= 150:
                    print('接铁完成')
                    truck = i + 1

                    data = mysql_2.query_all(car_Position, car_Position.truck_num == truck)
                    car_num = data.car_num

                    start = 22 + (car_num - 1) * 36
                    plc_w(start, True)
                    print(str(car_num) + '号车运走')
                    news = Plan1(truck, 0, 3, weight, i, car_num)
                    mysql_2.add_obj(news)
            tr = truck_state


# 过跨车实时位置
def car_position_1():
    p_old = 0
    b = 0
    while True:
        time.sleep(5)
        mysql_1 = DatabaseManagement()
        for i in range(16):
            start = 2 + 36 * i
            # 向plc读取过跨车位置
            position_1 = plc_r(100, start, 4)
            position_1 = get_real(position_1, 0)
            a = position_1 - p_old
            p_old = position_1
            if a != 0:

                truck_num = i % 8+1

                news = car_Position(truck_num, i + 1, position_1)
                mysql_1.add_obj(news)

            else:
                b += 1
                if b % 4 == 0:
                    truck_num = i % 8+1

                    news = car_Position(truck_num, i + 1, position_1)
                    mysql_1.add_obj(news)


def my_Plan():
    # 等待接铁、接铁中、运输、炼钢等待、返回
    data_p = DatabaseManagement()
    data = data_p.query_all(Plan1,Plan1.car_num)


# 流量稳定值为  5.45
if __name__ == '__main__':
    th_run = MyThread(1320, transport1, args=())
    th_back = MyThread(1321, tank_back, args=())
    th_position = threading.Thread(target=car_position_1, args=())
    th_position.start()
    th_back.start()
    th_run.start()
    '''    th_break = MyThread(123, plc_r, args=())

    th_break.start()
    a = 0
    b = 0
    c = 0
    while True:
        # 接铁完成-->车走
        state1 = plc_r('192.168.0.2')

        if state1 is not None:
            a += 1
            th1 = MyThread(a, plc_w(), args=(a,))
            th1.start()
        # 接铁预计完成时间写入数据库
        if state1 is None:
            b += 1
            th2 = MyThread(b, metal_time(), args=())
            th2.start()
        # 返回
        if emptyTank_break() is None:

            c += 1
            th3 = MyThread(c, emptyTank_break(), args=())
            th3.start()'''
