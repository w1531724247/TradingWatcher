# 

import pathlib
import requests
from pathlib import Path
import shutil
from tw_api.const import is_Windows
import appdirs
import subprocess
import tempfile, os

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
    def create_dir_if_not_exists(cls, dir_path):
        try:
            # 确保路径是字符串或Path对象
            path_obj = pathlib.Path(dir_path)
            
            # 检查路径是否已存在
            if path_obj.exists():
                if not path_obj.is_dir():
                    print(f"警告: 路径存在但不是目录: {dir_path}")
                    # 尝试使用不同的路径名
                    path_obj = pathlib.Path(str(dir_path) + "_dir")
                return path_obj
            
            # 尝试使用pathlib创建目录
            path_obj.mkdir(parents=True, exist_ok=True)
            
            # 验证目录是否创建成功
            if not path_obj.exists():
                print(f"警告: pathlib创建目录失败，尝试使用os.makedirs: {dir_path}")
                # 使用os.makedirs作为备选方案
                os.makedirs(str(path_obj), exist_ok=True)
            
            return path_obj
            
        except PermissionError as e:
            print(f"权限错误: 无法创建目录 {dir_path}: {e}")
            # 尝试在临时目录创建
            temp_dir = os.path.join(tempfile.gettempdir(), os.path.basename(str(dir_path)))
            print(f"尝试在临时目录创建: {temp_dir}")
            os.makedirs(temp_dir, exist_ok=True)
            return pathlib.Path(temp_dir)
        except Exception as e:
            print(f"创建目录时出错: {dir_path}: {e}")
            import traceback
            traceback.print_exc()
            
            # 返回当前目录作为最后的备选方案
            return pathlib.Path(".")
    
    @classmethod
    def app_file_dir(cls):
        return Path(cls.getAppDataPath())

    @classmethod
    def app_data_file_dir(cls):
        app_data_path = cls.app_file_dir()
        # 根据操作系统选择目录路径
        if is_Windows:  # Windows
            pro_data_path = app_data_path.joinpath('common')
            if not pro_data_path.exists():
                cls.create_dir_if_not_exists(pro_data_path)
            subprocess.run(['attrib', '+h', str(pro_data_path)], check=True)
        else:  # Unix-like
            pro_data_path = app_data_path.joinpath('.common')
            if not pro_data_path.exists():
                cls.create_dir_if_not_exists(pro_data_path)
        return pro_data_path

    @classmethod
    def app_user_data_dir(cls):
        app_user_data_dir = cls.app_data_file_dir().joinpath(cls.u_email)
        cls.create_dir_if_not_exists(app_user_data_dir)
        return app_user_data_dir 

    @classmethod
    def app_db_dir(cls):
        dir_path = cls.app_user_data_dir().joinpath('db')
        # 如果文件夹不存在则创建
        cls.create_dir_if_not_exists(dir_path)
        return dir_path

    @classmethod
    def app_temp_dir(cls):
        app_temp_dir = cls.app_file_dir().joinpath('PYStatic')
        cls.create_dir_if_not_exists(app_temp_dir)
        return app_temp_dir

    @classmethod
    def app_user_temp_file_dir(cls):
        # 用户缓存数据不为空
        dir_path = cls.app_temp_dir().joinpath(cls.u_email)
        cls.create_dir_if_not_exists(dir_path)
        return dir_path

    @classmethod
    def app_temp_image_file_dir(cls):
        dir_path = cls.app_user_temp_file_dir().joinpath('images')
        cls.create_dir_if_not_exists(dir_path)
        return dir_path

    @classmethod
    def temp_image_http_file_path(cls):
        return f'/py/temp/static/images'
    
    @classmethod
    def app_temp_log_file_dir(cls):
        dir_path = cls.app_temp_dir().joinpath('logs')
        # 如果文件夹不存在则创建
        cls.create_dir_if_not_exists(dir_path)
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
        cls.create_dir_if_not_exists(project_assets_dir)
        return project_assets_dir

    @classmethod
    def app_audio_file_dir(cls):
        app_audio_file_dir = cls.project_assets_dir().joinpath('audio')
        # 如果文件夹不存在则创建
        cls.create_dir_if_not_exists(app_audio_file_dir)
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
        cls.create_dir_if_not_exists(dir_path)

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