# 
import os
import logging
import time
from concurrent_log_handler import ConcurrentRotatingFileHandler
import pathlib
from pathlib import Path
from .path_tools import PathTools

def get_logger(app_env: str = 'DEBUG'):
    if app_env == 'RELEASE':
        level = logging.ERROR
    else:
        level = logging.DEBUG
    # 配置logger对象
    logger = logging.getLogger()
    # 设置日志基础级别
    logger.setLevel(level)
    # 日志格式
    formatter = '[%(asctime)s] [%(threadName)s] [%(filename)s] [%(funcName)s] [line:%(lineno)d] %(levelname)s: %(message)s'

    log_formatter = logging.Formatter(formatter)
    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    # 日志文件名
    log_file_name = 'log-' + time.strftime(
        '%Y-%m-%d', time.localtime(time.time())) + '.log'
    log_dir_path = PathTools.app_temp_log_file_dir()

    # 最多保留10份文件,超过则删除
    file_path_list = []
    pth = pathlib.Path(log_dir_path)
    for child in pth.iterdir():
        if child.is_file():
            if str(child).startswith('.'):
                pass
            else:
                file_path_list.append(child)
        else:
            pass
    # 根据文件创建日期排序
    file_path_list = sorted(file_path_list, key=lambda x: os.path.getmtime(x))
    if len(file_path_list) > 10:
        for index in range(0, len(file_path_list)-10):
            child = file_path_list[index]
            child.unlink()
    else:
        pass

    log_file_path = Path(log_dir_path).joinpath(log_file_name)
    print('log_file_path---->', log_file_path);
    PathTools._log_file_path = str(log_file_path)
    # Rotate log after reaching 1Mb, keep 10 old copies.
    log_handler = ConcurrentRotatingFileHandler(log_file_path, "a", 1024 * 1024, 10)
    # 设置文件里写入的格式
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(level)
    # 添加日志处理器
    logger.addHandler(log_handler)

    return logger

logger = get_logger()
# logger = get_logger(app_env='RELEASE')