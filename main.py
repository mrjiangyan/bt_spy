#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from flask import make_response, jsonify
from gevent import pywsgi
import traceback

import config
import monitor

from auth import auth
from flask import Flask
from data import database
from rest.ApiResult import error_message
from rest.index import index
from flask_cors import CORS
from loguru import logger
import os
import faulthandler

faulthandler.enable()


def create_app():
    app = Flask(__name__)

    # 必须要通过app上下文去启动数据库
    database.global_init("edge.db")

    # 添加api接口到
    register_api(app)

    app.config['JSON_AS_ASCII'] = False
    app.after_request(auth.after_request)
    app.before_request(auth.jwt_authentication)
  
    app.config.from_object(config)

    # 注册日志
    config_logging()
    # 添加定时任务
    monitor.start_monitor()
    # add_task()
    # 解决跨域问题
    CORS(app)
    return app


# def add_task():
    # 配置线程池 ，支持最多10个线程同时执行
    executors = {
        'default': ThreadPoolExecutor(10)
    }
    # 开启定时任务
    scheduler = BackgroundScheduler(executors=executors, timezone='Asia/Shanghai', daemon=True)

    #定时清理定时任务
    scheduler.add_job(func= monitor.start_monitor, id='start_monitor', trigger="cron",  hour='*', minute='*', second='0', max_instances=1, coalesce=True)
    # 心跳机制定时任务 30秒执行一次
    # scheduler.add_job(func=get_health, id='get_health_job', trigger="interval", seconds=30)
    # 更新同步盒子版本的信息 同步盒子版本信息 3分钟执行一次
    # scheduler.add_job(func=sync_box_version, id='sync_box_version_job', trigger="interval", minutes=3)
    # 获取是否同步数据信息  3分钟执行一次
    # scheduler.add_job(func=get_sync_status, id='get_sync_status_job', trigger="interval", minutes=3)
    # 补偿机制同步数据定时任务 10分钟执行一次
    # scheduler.add_job(func=compensate_data, id='compensate_data_job', trigger="interval", minutes=10)
    # 获取minio信息 3分钟执行一次
    # scheduler.add_job(func=get_minio_config, id='get_minio_config_job', trigger="interval", minutes=3)
    scheduler.start()


def register_api(app):
    # 添加api接口到
    app.register_blueprint(index.blueprint)
    # app.register_blueprint(system_api.blueprint)


def config_logging():
    os.chdir("./")  # 日志写入地址
    logger.add("./logs/log_{time}.log", rotation="1 day", retention="7 days")
    logger.add("./logs/error/log_{time}.log", rotation="1 day", level='ERROR',retention="7 days")


app = create_app()

@app.errorhandler(404)
def not_found(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Not found'}), 404)


# 定义错误的处理方法
@app.errorhandler(Exception)
def error_handler(e):
    logger.error(traceback.format_exc())
    return error_message(str(e))


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 90), app)
    server.serve_forever()
