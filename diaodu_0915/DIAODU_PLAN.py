import threading
import time
from datetime import timedelta
from queue import Queue

import requests
import snap7
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sql_test.car_queue import Car_Queue, Tank_Queue


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


# 判断是否使用备用车
def car_b():
    T1 = 30
    Ts = tank_position(Tank_Queue.Arrival_time, Tank_Queue)
    T2 = timedelta(minutes=30)
    if (T2 - Ts) >= T1:
        plc_w()


# 出铁完成信号
def chutie(track_num):
    return track_num # 车号


# 空罐装载信号
def emptyTank_break(track_num):
    return track_num


# 加废钢信号
def scrap_steel(track_num):
    return True


# 轨道判断
def track_state(sd):
    if (sd % 2) == 0:
        return sd - 1
    else:
        return sd + 1


# plc写
def plc_w():
    plc = snap7.client.Client()
    plc.connect('172.0.0.1', 0, 1)
    plc.db_write(m1, 0, '123236546')


# 二级通讯模块
def send_msg(msg):
    response = requests.post(url='https://api.weixin.qq.com/cgi-bin/token', params=msg)
    # response.content返回的是Unicode格式，通常需要转换为utf-8格式，否则就是乱码。
    response_body = response.content.decode('utf-8')


# 重罐线程
def heavy_tank():
    while True:
        if chutie(1) is not None:
            a = chutie(1)  # 轨道
            user = tank_position((Car_Queue.track == a, Car_Queue.position == 1), Car_Queue)
            b = user.car_number
            plc_w(b + 1)


# 空罐线程


def empty_Tank(t):
    a = emptyTank_break(1)

    # 空罐装载完成
    if a is not None:

        user = tank_position((Car_Queue.track == a, Car_Queue.position == 2), Car_Queue)
        b = user.car_number
        user1 = tank_position((Car_Queue.track == a, Car_Queue.car_number == b + 1), Car_Queue)
        c = user1.position
        car_sql = tank_position((Tank_Queue.car_num == b), Tank_Queue)
        d = car_sql.Arrival_time

        if c == 0:  # 备用车在初始位置

            plc_w(2)


# 半罐处理机制
def half_tank():
    weight = int(input('>>>>'))
    if weight < 6:
        user = tank_position(Car_Queue.position == 2, Car_Queue)
        a, b = user.car_number, user.track
        if a and b is None:
            return True


if __name__ == '__main__':

    a = chutie(1)
    if a > 0:  # 出铁完成
        # 向plc发送指令
        plc_w()
        # 记录时间
        t1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())






    '''    q = Queue()
    th1 = MyThread(1, heavy_tank, args=(q,))
    th1.start()
    th2 = MyThread(2, empty_Tank, args=(q,))
    th2.start()
    # 读取出铁计划    
    
    T = 30  # 时长
        q = []  # 线程池
        M = []  # 信号池
        i = 3
        while True:
            # 开启信号接收线程
            th1 = MyThread(1, chutie, (1,))
            th2 = MyThread(2, emptyTank_break, (1,))
            th1.start()
            th2.start()
            q.append(th1)
            q.append(th2)
            for th in q:
                msg = th.get_result()
                M.append(msg)
                i = i + 1
            msg1 = M[-1][-2]  # 轨道号 动作
            # 出铁完成信号
            if msg1 == 1:
                # 获取车号
                tank_position = tank_position(msg1, 2)
                m_value = tank_position.car_number + msg1
                # 运重罐
                plc_w()
            空罐装载完成信号,相邻轨道接铁完成时间预测，尽量避免接铁等待时间
            t1 一轨道接铁完成时间
            t2 二轨道接铁完成时间
            T = t2-t1
            
            
    
            if msg1 == 2:
                # 查询对应轨道上是否有在接铁
                m1 = tank_position()
                if scrap_steel(1) is None:
                    MyThread(i, send_msg, (M[-1],)).start()
                else:
                    msgs = M[-1][:4] + '3'
                    MyThread(i, send_msg, (msgs,)).start()'''
