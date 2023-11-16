#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import datetime

from sqlalchemy import orm
import sqlalchemy
from data.database import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Device(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 't_device'

    id = sqlalchemy.Column(sqlalchemy.String(50), primary_key=True, doc="id")
    deviceName = sqlalchemy.Column("device_name", sqlalchemy.String(50), doc="设备名称")
    ip = sqlalchemy.Column(sqlalchemy.String(255), doc="IP地址")
    controlPort = sqlalchemy.Column("control_port", sqlalchemy.Integer, doc="控制端口")
    videoPort = sqlalchemy.Column("video_port", sqlalchemy.Integer, doc="视频端口")
    createTime = sqlalchemy.Column("create_time", sqlalchemy.DateTime, default=datetime.datetime.now, doc="创建时间")
    subCodeStream = sqlalchemy.Column("sub_code_stream", sqlalchemy.String(2083), doc="子码流")
    mainCodeStream = sqlalchemy.Column("mainCodeStream", sqlalchemy.String(2083), doc="主码流")
    userName = sqlalchemy.Column("user_name", sqlalchemy.String(255), doc="用户名")
    password = sqlalchemy.Column(sqlalchemy.String(255), doc="用户密码")
    agreement = sqlalchemy.Column(sqlalchemy.String(255), doc="协议")
    manufactor = sqlalchemy.Column(sqlalchemy.String(25), doc="厂家")
    runningState = sqlalchemy.Column("running_state", sqlalchemy.Integer, default=1, doc="运行状态，1为未运行，2为运行中，3为运行异常")

    monitoring_area = orm.relationship("DeviceMonitoringArea", cascade="save-update, merge, delete")
    engine_device_areas_to_device = orm.relationship("EngineDeviceArea", uselist=True,
                                                     backref="device_to_engine_device_area", lazy='dynamic')
