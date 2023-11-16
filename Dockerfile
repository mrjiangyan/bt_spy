FROM python:3.9.6-slim

COPY . /mnt

WORKDIR /mnt

ENV LANG en_US.UTF-8 LC_ALL=en_US.UTF-8

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 vim -y
RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN sed -i s@/security.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list

RUN python3 -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r /mnt/requirements.txt -i https://pypi.douban.com/simple/ --trusted-host=pypi.douban.com/simple

ENV PYTHONIOENCODING=utf-8


RUN rm -rf logs
RUN rm -rf /var/cache/*
RUN rm -rf /tmp/*

RUN /bin/bash -c "source ort/bin/activate"

CMD python3 /mnt/main.py