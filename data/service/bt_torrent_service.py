
from data.model.t_bt_torrent import BtTorrent
from sqlalchemy import func
from typing import Optional
from data.enum.model_type_enum import SourceTypeEnum

from sqlalchemy import Column, DateTime, func, Integer, String

# 根据类型以及unicode去查询记录
def get_by_unicode(db_sess, type: SourceTypeEnum, unicode: str)-> Optional[BtTorrent]:
    torrent = db_sess.query(BtTorrent).filter_by(type=type.value, unicode= unicode).first()
    return torrent


# 根据类型查询unicode最大的记录
def get_max_unicode_by_type(db_sess, type: SourceTypeEnum)-> Optional[BtTorrent]:
    max_unicode = db_sess.query(func.max(func.cast(BtTorrent.unicode, Integer))).filter_by(type=type.value).scalar()

    if max_unicode is not None:
        # Retrieve the corresponding BtTorrent record
        torrent = db_sess.query(BtTorrent).filter_by(type=type.value, unicode=max_unicode).first()
        return torrent

    return None

