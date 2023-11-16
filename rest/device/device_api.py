#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import flask
from auth.auth import login_required
from data import database
from data.model.device import Device
from data.request.device.device_add_form import DeviceAddForm
from loguru import logger

from rest.ApiResult import ApiResult, error_message
from device import screenshot, network, websocket_server
from flask import request
import uuid

from rest.enum.running_state_enum import RunningStateEnum

blueprint = flask.Blueprint(
    'device_api',
    __name__
)


# 获取设备列表
@login_required
@blueprint.route('/api/device/list', methods=['GET'])
def device_list():
    db_sess = database.create_session()
    device_lists = db_sess.query(Device).order_by(Device.createTime.desc()).all()
    db_sess.close()
    # V1.1加入设备运行状态
    for device in device_lists:
        # 判断相机是否绑定引擎
        db_sess_new = database.create_session()
        # 根据相机id并用引擎id分组来查询引擎相机区域列表
        engine_device_area_list = db_sess_new.query(EngineDeviceArea).filter(
            EngineDeviceArea.deviceId == device.id).group_by(EngineDeviceArea.engineId).all()
        if engine_device_area_list:
            # 该相机已绑定引擎
            # 判断相机状态是否异常  只有布控的相机才可以显示异常，运行中以及未运行
            if device.runningState is not RunningStateEnum.RUNNINGABNORMALLY.value:
                # 相机运行状态未异常：
                # 存放引擎的数组
                engine_device_ids = []
                for engine_device_area in engine_device_area_list:
                    # 把引擎id放入数组中
                    engine_device_ids.append(engine_device_area.engineId)
                # 根据引擎ids以及引擎启动状态为运行的 查询引擎列表
                business_engine = db_sess_new.query(BusinessEngine).filter(BusinessEngine.id.in_(engine_device_ids),
                                                                           BusinessEngine.status == 1).first()
                # 判断是否存在以上条件引擎
                if business_engine:
                    # 存在 则将设备运行状态改成运行中
                    device.runningState = RunningStateEnum.RUNNING.value
                else:
                    # 不存在 则将设备运行改为未运行
                    device.runningState = RunningStateEnum.NOTRUNNING.value
        # 相机未布控一律显示未运行
        else:
            device.runningState = RunningStateEnum.NOTRUNNING.value

    return ApiResult(
        [item.to_dict(
            only=('id', 'deviceName', 'ip', 'controlPort', 'videoPort', 'createTime', 'manufactor', 'runningState'))
            for item in device_lists]).to_json()


# 设备重新运行
@login_required
@blueprint.route('/api/device/rerun/<device_id>', methods=['GET'])
def rerun_device(device_id):
    db_sess = database.create_session()
    # 判断设备是否存在
    device = is_exist_device(db_sess, device_id)

    # 判断设备状态是否是异常的状态 如果是异常则可以重新运行 反之不可
    if device.runningState is not RunningStateEnum.RUNNINGABNORMALLY.value:
        raise Exception("该设备状态无异常无需重新运行")

    device.runningState = RunningStateEnum.RUNNING.value
    db_sess.commit()

    # 更新
    do_write_protocol_json()
    return ApiResult(None).to_json()


# 设备是否布控
@login_required
@blueprint.route('/api/device/isDeploy/<device_id>', methods=['GET'])
def is_deploy_device(device_id):
    db_sess = database.create_session()
    # 判断设备是否存在
    is_exist_device(db_sess, device_id)

    engine_device_area = db_sess.query(EngineDeviceArea.deviceId).filter(EngineDeviceArea.deviceId == device_id).first()
    if not engine_device_area:
        return ApiResult(False).to_json()

    return ApiResult(True).to_json()


# 设备详情
@login_required
@blueprint.route('/api/device/<device_id>', methods=['GET'])
def get_one_device(device_id):
    db_sess = database.create_session()
    # 判断设备是否存在
    device = is_exist_device(db_sess, device_id)
    return ApiResult(
        device.to_dict(
            only=('id', 'manufactor', 'deviceName',
                  'ip', 'agreement', 'controlPort',
                  'videoPort', 'userName', 'password',
                  'subCodeStream', 'mainCodeStream'))).to_json()


# 修改设备信息
@login_required
@blueprint.route('/api/device', methods=['PUT'])
def update_device():
    try:
        form = DeviceAddForm().validate_for_api()
    except Exception as err:
        return error_message(str(err))
    device_json = request.json
    db_sess = database.create_session()
    # 判断设备是否存在
    is_exist_device(db_sess, form.id.data)

    try:
        db_sess.query(Device).filter(
            Device.id == device_json['id']).update(device_json)
        db_sess.commit()
    except Exception as e:
        db_sess.rollback()
        logger.error(str(e))
        return error_message("修改失败:{}".format(e)).to_json()
    return ApiResult(None).to_json()


# 新增设备
@login_required
@blueprint.route('/api/device', methods=['POST'])
def add_device():
    try:
        form = DeviceAddForm().validate_for_api()
    except Exception as err:
        return error_message(str(err))
    device = Device()
    device.controlPort = form.controlPort.data
    device.deviceName = form.deviceName.data
    device.ip = form.ip.data
    device.videoPort = form.videoPort.data
    device.subCodeStream = form.subCodeStream.data
    device.mainCodeStream = form.mainCodeStream.data
    device.userName = form.userName.data
    device.password = form.password.data
    device.agreement = form.agreement.data
    device.manufactor = form.manufactor.data
    device.id = str(uuid.uuid1())

    device.monitoring_area = [creat_pull_monitoring_area()]
    db_sess = database.create_session()
    try:
        # 添加设备并添加全屏区域
        db_sess.add(device)
        db_sess.commit()
    except Exception as e:
        db_sess.rollback()
        logger.error(str(e))
        return error_message(str(e))
    return ApiResult("添加成功").to_json()


# 根据设备id删除设备
@login_required
@blueprint.route('/api/device/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    db_sess = database.create_session()
    # 判断设备是否存在
    device = is_exist_device(db_sess, device_id)

    try:
        # 获取绑定设备的业务引擎
        engine_device_areas = db_sess.query(EngineDeviceArea).filter(
            EngineDeviceArea.deviceId == device_id).group_by(
            EngineDeviceArea.engineId).all()
        # 删除引擎设备区域
        db_sess.query(EngineDeviceArea).filter(EngineDeviceArea.deviceId == device_id).delete()
        # 删除设备记录 并删除设备下的区域˚
        db_sess.delete(device)

        for engine_device_area in engine_device_areas:
            business_engine = db_sess.query(BusinessEngine).get(engine_device_area.engineId)
            # 业务引擎为基础模型
            if business_engine.templateType == 1:
                count = db_sess.query(EngineDeviceArea).filter(EngineDeviceArea.engineId == business_engine.id).count()
                if count == 0:
                    change_engine_status(db_sess, business_engine.id)

            # sop流程
            else:
                change_engine_status(db_sess, business_engine.id)

        db_sess.commit()
    except Exception as e:
        db_sess.rollback()
        logger.error("删除设备异常: {}".format(e))
        return error_message("删除设备异常: {}".format(str(e)))
    do_write_protocol_json()
    return ApiResult(None).to_json()


def change_engine_status(db_sess, engineId):
    db_sess.query(BusinessEngine).filter(BusinessEngine.id == engineId).update({"status": False})
    db_sess.commit()


@login_required
@blueprint.route('/api/device/preview/<device_id>', methods=['GET'])
def get_screenshot(device_id):
    db_sess = database.create_session()
    device = is_exist_device(db_sess, device_id)
    if not screenshot.device_status(device.subCodeStream):
        return error_message("该相机设备离线!")
    try:
        # 主码流截图
        base64_str = screenshot.screenshot(device.mainCodeStream)
    except Exception as err_main:
        logger.error('main stream screenshot error: {}'.format(str(err_main)))
        try:
            # 主码流异常，子码流截图
            base64_str = screenshot.screenshot(device.subCodeStream)
        except Exception as err_sub:
            logger.error('sub stream screenshot error: {}'.format(str(err_sub)))
            return error_message("截图异常，请稍后重试!")
    return ApiResult('data:image/jpeg;base64,' + base64_str).to_json()


@login_required
@blueprint.route('/api/device/isOnline/<device_id>', methods=['GET'])
def is_online(device_id):
    db_sess = database.create_session()
    device = is_exist_device(db_sess, device_id)
    try:
        return ApiResult(screenshot.device_status(device.mainCodeStream)).to_json()
    except Exception:
        return error_message("该相机设备状态查询失败!")


@login_required
@blueprint.route('/api/device/websocket/start/<device_id>', methods=['GET'])
def websocket_start(device_id):
    db_sess = database.create_session()
    device = is_exist_device(db_sess, device_id)
    if not screenshot.device_status(device.subCodeStream):
        return error_message("该相机设备离线!")
    try:
        # 使用子码流播放，降低CPU消耗
        websocket_server.start(device_id, device.subCodeStream)
    except Exception as err:
        logger.error(str(err))
        return error_message('该相机设备视频播放失败，请稍后重试!')
    ip = network.get_ip()
    response = {"websocketUrl": "ws://{}:8765/{}".format(ip, device_id), "uuid": uuid.uuid4()}
    return ApiResult(response).to_json()


@login_required
@blueprint.route('/api/device/websocket/stop/<uuid>', methods=['GET'])
def websocket_stop(uuid):
    return ApiResult(websocket_server.rm_start_list(uuid)).to_json()


# 判断设备是否存在
def is_exist_device(db_sess, device_id):
    device = db_sess.query(Device).get(device_id)
    if not device:
        raise Exception("该设备不存在!")
    return device


# 创建全屏区域
def creat_pull_monitoring_area():
    monitoring_area = DeviceMonitoringArea()
    monitoring_area.id = str(uuid.uuid1())
    monitoring_area.areaName = '全屏区域'
    monitoring_area.effectiveArea = '-1'
    return monitoring_area
