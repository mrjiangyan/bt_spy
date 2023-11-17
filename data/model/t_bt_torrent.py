#!/usr/bin/python
# -*- coding: UTF-8 -*-
from sqlalchemy import Column, DateTime, func, Integer, String

from data.database import SqlAlchemyBase

from sqlalchemy_serializer import SerializerMixin


class BtTorrent(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 't_bt_torrent'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column("url", String, index=True, doc="原始的网页地址")
    title = Column("title", String, index=True, doc="标题")
    year = Column("year", String, index=True, doc="年份")
    country = Column("country", String, index=True, doc="country")
    release_date = Column("release_date", String, index=True, doc="release_date")
    language = Column("language", String, index=True, doc="language")
    
    
    
    imdb_link = Column("imdb_link", String, index=True, doc="imdb_link")
    douban_link = Column("douban_link", String, index=True, doc="douban_link")
    category = Column("category", String, index=True, doc="category")
    
    cover = Column("cover", String, doc="封面图片地址")
    images = Column("images", String, doc="介绍图片地址")
    torrent = Column("torrent", String, doc="种子地址,用‘,'来','分割多个地址")
    unicode = Column("unicode", String, index=True, doc="唯一标识")
    type = Column("type", Integer, doc="类型")
    gmtUpdate = Column("gmt_update", DateTime, default=func.now(), onupdate=func.now(), doc="更新时间")
   
    
