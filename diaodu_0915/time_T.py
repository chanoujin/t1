import datetime
from datetime import timedelta
import time

from sqlalchemy import create_engine, Column, INT, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()


class Tank_Queue(Base):
    __tablename__ = 'tank'
    id = Column(INT(),primary_key=True)
    car_num = Column(INT())
    Arrival_time = Column(DateTime())
    position = Column(INT())

def tank_position():
    engine = create_engine('mssql+pymssql://sa:123456cj@LAPTOP-UK384UED\SQLEXPRESS/cjt3')  # IP/dbName?driver=SQL+Server
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建Session:
    session = DBSession()
    # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
    user = session.query(Tank_Queue).filter(Tank_Queue.car_num == '1').first()
    # 打印类型和对象的name属性:

    # 关闭Session:
    session.close()
    return user


user = tank_position()
t1 = user.Arrival_time
t2 = timedelta(hours=2)
t3 = t1+t2
print(t3)
