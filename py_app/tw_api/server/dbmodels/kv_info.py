# 

from .db_base import LocalDB
from tinydb import Query, where
from pydantic import BaseModel
from tw_api.utils.path_tools import PathTools
import json

class KVInfo(BaseModel):

    @classmethod
    def db(cls):
        db_mdl = LocalDB.initWithFileName('kv_info.json')

        return db_mdl

    @classmethod
    def sign_out(cls, key: str):
        from tinydb import TinyDB, Query
        file_path = PathTools.app_data_file_dir().joinpath('tourist@signout.com').joinpath('db').joinpath('kv_info.json')
        kv_db = TinyDB(file_path)
        value = {
            "email": "tourist@signout.com",
            "nick": "",
            "u_id": "",
            "u_num": 0,
            "update_time": 0,
            "vip_expire_time": 0,
            "token": ""
        }
        kv_db.upsert({'key': key, 'value': {}}, where('key') == key)

        return value

    @classmethod
    def sign_in(cls, key: str, value: dict):
        from tinydb import TinyDB, Query
        file_path = PathTools.app_data_file_dir().joinpath('tourist@signout.com').joinpath('db').joinpath(
            'kv_info.json')
        kv_db = TinyDB(file_path)
        kv_db.upsert({'key': key, 'value': value}, where('key') == key)

        return value

    @classmethod
    def save(cls, key: str, value: any):
        return cls.update(key=key, value=value)

    @classmethod
    def delete(cls, key: str):
        return cls.db().remove(where('key') == key)

    @classmethod
    def update(cls, key: str, value: any):
        return cls.db().upsert({'key': key, 'value': value}, where('key') == key)

    @classmethod
    def get(cls, key: str):
        return cls.db().search(where('key') == key)

    @classmethod
    def get_value_by_key(cls, key: str):
        info_list = cls.db().search(where('key') == key)
        # print('get_value_by_key-->', key, info_list)
        if info_list is None or len(info_list) < 1:
            return None
        else:
            return info_list[0]["value"]
        
    @classmethod
    def get_json_obj_by_key(cls, key: str):
        json_str: str = cls.get_value_by_key(key=key)
        if json_str is None:
            return None
        else:
            json_obj = json.loads(json_str)
            return json_obj

        
    @classmethod
    def set_json_obj_by_key(cls, key: str, json_obj: any):
        if json_obj is None:
            return
        else:
            json_str = json.dumps(json_obj)
            cls.update(key=key, value=json_obj)

