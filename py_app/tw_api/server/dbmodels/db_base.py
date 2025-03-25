# 

from pathlib import Path
from tinydb import TinyDB, Query
from tw_api.utils.path_tools import PathTools

class LocalDB(TinyDB):

    @classmethod
    def initWithFileName(self, file_name):
        db_path = PathTools.app_db_dir().joinpath(file_name)
        # print('db_path->', db_path)

        return TinyDB(db_path)
