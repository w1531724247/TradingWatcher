# 

from .db_base import LocalDB
from tinydb import Query
from pydantic import BaseModel
from .db_base import LocalDB
from tinydb import Query, where
from pydantic import BaseModel

class TVChartInfo(BaseModel):
    @classmethod
    def db(cls):
        db_mdl = LocalDB.initWithFileName('tv_chart_info.json')

        return db_mdl

    @classmethod
    def save(cls, chart_info: dict):
        return cls.db().insert(chart_info)

    @classmethod
    def delete_chart_by_id(cls, chart_id: int, user_id: str, client_id: str):
        query = Query().fragment({'user_id': user_id, 'client_id': client_id, 'id': chart_id})
        return cls.db().remove(query)

    @classmethod
    def update(cls, chart_id: int, user_id: str, client_id: str, chart_info: dict):
        query = Query().fragment({'user_id': user_id, 'client_id': client_id, 'id': chart_id})

        return cls.db().upsert(chart_info, query)

    @classmethod
    def get_all(cls, user_id: str, client_id: str):
        query = Query().fragment({'user_id': user_id, 'client_id': client_id})

        return cls.db().search(query)

    @classmethod
    def get_chart_by_id(cls, chart_id: int, user_id: str, client_id: str):
        query = Query().fragment({'user_id': user_id, 'client_id': client_id, 'id': chart_id})
        chart_list = cls.db().search(query)
        # print("get_chart_by_id-->", chart_id, user_id, client_id, chart_list)
        if len(chart_list) > 0:
            return chart_list[0]
        else:
            return None



