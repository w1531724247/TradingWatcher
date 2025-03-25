# 

from .db_base import LocalDB
from tinydb import Query
from pydantic import BaseModel
from .db_base import LocalDB
from tinydb import Query, where
from pydantic import BaseModel

class TVTempateInfo(BaseModel):
    @classmethod
    def db(cls):
        db_mdl = LocalDB.initWithFileName('tv_tempate_info.json')

        return db_mdl

    @classmethod
    def save(cls, chart_info: dict):
        return cls.db().insert(chart_info)

    @classmethod
    def delete_tempate_by_name(cls, name: str, user_id: str, client_id: str):
        query = Query().fragment({'user_id': user_id, 'client_id': client_id, 'name': name})
        return cls.db().remove(query)

    @classmethod
    def get_all(cls, user_id: str, client_id: str):
        query = Query().fragment({'user_id': user_id, 'client_id': client_id})

        return cls.db().search(query)

    @classmethod
    def get_tempate_by_name(cls, name: str, user_id: str, client_id: str):
        query = Query().fragment({'user_id': user_id, 'client_id': client_id, 'name': name})
        chart_list = cls.db().search(query)
        if len(chart_list) > 0:
            return chart_list[0]
        else:
            return None



