# 

import pathlib
import requests
from pathlib import Path
import shutil
from tw_api.const import is_Windows
import appdirs
import subprocess

class PathTools:
    js_port = 10689
    u_email = 'tourist'
    serverDomain = ''
    _log_file_path = None
    _appDataPath = None

    @classmethod
    def getAppDataPath(cls):
        # 获取应用程序的数据目录
        if cls._appDataPath is None:
            user_data_dir = appdirs.user_data_dir(appname="TradingWatcher", appauthor="tw")
            cls._appDataPath = user_data_dir
            return cls._appDataPath
        else:
            return cls._appDataPath

    @classmethod
    def app_file_dir(cls):
        return Path(cls.getAppDataPath())

    @classmethod
    def app_data_file_dir(cls):
        app_data_path = cls.app_file_dir()
        # 根据操作系统选择目录路径
        if is_Windows:  # Windows
            pro_data_path = app_data_path / 'common'
            if not pro_data_path.exists():
                pro_data_path.mkdir(parents=True, exist_ok=True)
            subprocess.run(['attrib', '+h', str(pro_data_path)], check=True)
        else:  # Unix-like
            pro_data_path = app_data_path / '.common'
            if not pro_data_path.exists():
                pro_data_path.mkdir(parents=True, exist_ok=True)
        return pro_data_path

    @classmethod
    def app_user_data_dir(cls):
        app_user_data_dir = cls.app_data_file_dir().joinpath(cls.u_email)
        pathlib.Path(app_user_data_dir).mkdir(parents=True, exist_ok=True)
        return app_user_data_dir 

    @classmethod
    def app_db_dir(cls):
        dir_path = cls.app_user_data_dir().joinpath('db')
        # 如果文件夹不存在则创建
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
        return dir_path

    @classmethod
    def app_temp_dir(cls):
        app_temp_dir = cls.app_file_dir().joinpath('PYStatic')
        pathlib.Path(app_temp_dir).mkdir(parents=True, exist_ok=True)
        return app_temp_dir

    @classmethod
    def app_user_temp_file_dir(cls):
        # 用户缓存数据不为空
        dir_path = cls.app_temp_dir().joinpath(cls.u_email)
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
        return dir_path

    @classmethod
    def app_temp_image_file_dir(cls):
        dir_path = cls.app_user_temp_file_dir().joinpath('images')
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
        return dir_path

    @classmethod
    def temp_image_http_file_path(cls):
        return f'/py/temp/static/images'
    
    @classmethod
    def app_temp_log_file_dir(cls):
        dir_path = cls.app_temp_dir().joinpath('logs')
        # 如果文件夹不存在则创建
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
        return dir_path
    
    @classmethod
    def project_path(cls):
        # Path.cwd()，它返回当前工作目录的路径
        # 获取当前脚本文件的路径
        script_path = Path(__file__)
        # 获取脚本所在的目录
        script_dir = script_path.parent.parent
        return script_dir

    @classmethod
    def project_assets_dir(cls):
        project_path = cls.project_path()
        project_assets_dir = project_path.joinpath('assets')
        pathlib.Path(project_assets_dir).mkdir(parents=True, exist_ok=True)
        return project_assets_dir

    @classmethod
    def app_audio_file_dir(cls):
        app_audio_file_dir = cls.project_assets_dir().joinpath('audio')
        # 如果文件夹不存在则创建
        pathlib.Path(app_audio_file_dir).mkdir(parents=True, exist_ok=True)
        return app_audio_file_dir 
   

    @classmethod
    def auto_complete_http_url(cls, sub_url: str):
        url_str = f'{cls.serverDomain}{sub_url}'

        return url_str

    @classmethod
    def copy_file(cls, from_path, to_path):
        originPath = Path(from_path).resolve()
        newPath = Path(to_path).resolve()
        if originPath.is_file():
            print("--copy_file--1")
            (newPath / originPath.name).write_text(originPath.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            print("--copy_file--2")

    @classmethod
    def copy_dir(cls, from_dir, to_dir):
        originPath = Path(from_dir).resolve()
        newPath = Path(to_dir).resolve()
        if originPath.is_file():
            (newPath / originPath.name).write_text(originPath.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            if not newPath.exists():
                Path.mkdir(newPath)
            for dof in originPath.iterdir():
                cls.copy(dof, newPath / dof.name if dof.is_dir() else newPath)

    @classmethod
    def make_dir_if_not_exists(cls, dir_path: str):
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)

    @classmethod
    def delete_file(cls, file_path: str):
        pth = pathlib.Path(file_path)
        if pth.is_file():
            pth.unlink()
        else:
            pass

    @classmethod
    def delete_dir(cls, dir_path: str):
        pth = pathlib.Path(dir_path)
        for child in pth.iterdir():
            if child.is_file():
                child.unlink()
            else:
                cls.delete_dir(child)
        pth.rmdir()

    @classmethod
    def detele_all_files_in_dir(cls, dir_path: str):
        pth = pathlib.Path(dir_path)
        for child in pth.iterdir():
            if child.is_file():
                child.unlink()
            else:
                pass