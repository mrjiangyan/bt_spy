#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import threading
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from monitor.spy_4khdr import spy


def start_monitor():
    print('start_monitor')
    executors = {
        'default': ThreadPoolExecutor(10)
    }
    # 开启定时任务
    scheduler = BackgroundScheduler(executors=executors, timezone='Asia/Shanghai', daemon=True)

    # spy_4khdr_cn_thread = threading.Thread(target= spy, daemon=True)
    # spy_4khdr_cn_thread.start()
    
    # scheduler.add_job(func= spy, id='start_spy', trigger="interval", 
    #            minutes=60*6)
    
    scheduler.add_job(func= spy, args=[False], id='spy_4khdr_cn', trigger="cron",  hour='*', minute='*', second='0', max_instances=1, coalesce=False)
   
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
    
    # job_thread = threading.Thread(target=start_job_monitor, daemon=True)
    # job_thread.start()
    # camera_exception_thread = threading.Thread(target=start_camera_exception, daemon=True)
    # camera_exception_thread.start()

    # create_day_folder(datetime.datetime.now().strftime('%Y%m%d'))
