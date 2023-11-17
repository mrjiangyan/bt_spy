#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from loguru import logger

def global_init(db_file):
    global __factory
    global __db_file

    if __factory:
        return


    if not db_file or not db_file.strip():
        raise Exception("db_file is not found")

    __db_file = db_file
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    logger.info(f"Connection String {conn_str}")

    engine = sa.create_engine(conn_str, echo=True)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()



def create_readonly_ssession() -> Session:

    conn_str = f'sqlite:///{__db_file.strip()}?check_same_thread=False'
    engine = sa.create_engine(conn_str, echo=True)
    # 创建会话工厂
    Session = orm.sessionmaker(bind=engine)

    # 创建只读会话
    session = Session(readonly=True)
    # session = scoped_session(Session)
    return session



SqlAlchemyBase = dec.declarative_base()

__factory = None