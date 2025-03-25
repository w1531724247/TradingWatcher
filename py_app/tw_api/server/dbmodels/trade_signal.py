# 

from .db_base import LocalDB
from tinydb import Query, where
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List
from tw_api.utils.time_tools import getMillisecondTimestamp
from tw_api.utils.path_tools import PathTools


class TradeSignalInfo(BaseModel):
    s_id: str
    symbol: str
    interval: str
    time: str
    name: str
    image_path: str = ""
    image_url: str = ""
    signal_info: dict = None

    @classmethod
    def parse_obj(cls, *args, **kwargs): # real signature unknown
        obj = super().parse_obj(*args, **kwargs)
        obj.s_id = getMillisecondTimestamp()

        return obj

    @classmethod
    def delete_over_datas(cls):
        # 保存100条数据, 超过的部分直接删除
        cur_db = cls.db()
        s_count = len(cur_db)
        if s_count > 110:
            # 超过110条,则删除前20条
            pre_info_list = cls.get_signal_list(skip=0, limit=20)
            id_list = []
            for s_info in pre_info_list:
                id_list.append(s_info.doc_id)
                # 删除本地图片
                PathTools.delete_file(file_path=s_info["image_path"])
            # 批量删除
            cur_db.remove(doc_ids=id_list)

    @classmethod
    def info(cls):
        a_info = TradeSignalInfo.parse_obj({
            "symbol": "",
            "interval": "",
            "signal_title": ""
        })

        return a_info

    @classmethod
    def db(cls):
        db_mdl = LocalDB.initWithFileName('trade_signal.json')

        return db_mdl

    @classmethod
    def save(cls, s_info: dict):


        return cls.db().insert(s_info)

    @classmethod
    def delete(cls, s_id: int):
        return cls.db().remove(where('s_id') == s_id)

    @classmethod
    def update(cls, s_id: int, new_info: dict):
        return cls.db().upsert(new_info, where('s_id') == s_id)

    @classmethod
    def get_signal_by_id(cls, s_id: int):
        info_list = cls.db().search(where('s_id') == s_id)
        return cls.auto_complete_image_url(info_list=info_list)

    @classmethod
    def auto_complete_image_url(cls, info_list: list):
        final_list = []
        for s_info in info_list:
            s_info['image_url'] = PathTools.auto_complete_http_url(sub_url=s_info['image_url'])
            final_list.append(s_info)

        return final_list

    @classmethod
    def get_all(cls):
        info_list = cls.db().all()
        return info_list

    @classmethod
    def get_signal_list(cls, skip: int, limit: int):
        info_list = cls.db().all()[skip:skip + limit]

        return cls.auto_complete_image_url(info_list=info_list)




