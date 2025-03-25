# 

from .db_base import LocalDB
from tinydb import Query, where
from pydantic import BaseModel

class OrderRecord(BaseModel):

    @classmethod
    def db(cls):
        db_mdl = LocalDB.initWithFileName('order_record.json')

        return db_mdl

    @classmethod
    def delete_over_datas(cls):
        # 保存100条数据, 超过的部分直接删除
        cur_db = cls.db()
        info_list = cur_db.all()
        s_count = len(info_list)
        if s_count > 110:
            # 超过110条,则删除前20条
            pre_info_list = info_list[:20]
            id_list = []
            for s_info in pre_info_list:
                id_list.append(s_info.doc_id)
            # 批量删除
            cur_db.remove(doc_ids=id_list)

    @classmethod
    def save(cls, o_infos: dict):
        # 保存前线删除旧数据
        cls.delete_over_datas()

        return cls.db().insert(o_infos)

    @classmethod
    def delete(cls, open_order_id: str):
        return cls.db().remove(where('open_order_info')["client_order_id"] == open_order_id)

    @classmethod
    def get(cls, open_order_id: str):
        info_list = cls.db().search(where('open_order_info')["client_order_id"] == open_order_id)
        if info_list is None or len(info_list) < 1:
            return None
        else:
            return info_list[0]
