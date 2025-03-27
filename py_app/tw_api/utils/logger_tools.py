import os
import logging
import time
from concurrent_log_handler import ConcurrentRotatingFileHandler
import pathlib
from pathlib import Path
from .path_tools import PathTools
import traceback

# 新增日志配置类
class LoggerConfig:
    DEBUG = 'DEBUG'
    RELEASE = 'RELEASE'
    TEST = 'TEST'

# 优化后的日志格式
LOG_FORMAT = '[%(asctime)s] [%(process)d] [%(threadName)s] [%(filename)s:%(lineno)d] [%(funcName)s] %(levelname)s: %(message)s'

def setup_file_handler(logger, log_dir_path, level):
    """设置文件日志处理器"""
    try:
        # 日志文件名
        log_file_name = f'log-{time.strftime("%Y-%m-%d")}.log'
        log_file_path = Path(log_dir_path).joinpath(log_file_name)
        
        # 创建日志目录（如果不存在）
        os.makedirs(log_dir_path, exist_ok=True)
        
        # 设置文件日志处理器
        file_handler = ConcurrentRotatingFileHandler(
            log_file_path,
            mode='a',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=30,  # 保留30个备份
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
        
        # 清理旧日志文件
        clean_old_logs(log_dir_path, max_files=30)
        
        return log_file_path
    except Exception as e:
        print(f"Failed to setup file handler: {e}")
        traceback.print_exc()
        return None

def clean_old_logs(log_dir_path, max_files=30):
    """清理旧的日志文件"""
    try:
        pth = pathlib.Path(log_dir_path)
        file_path_list = [
            child for child in pth.iterdir() 
            if child.is_file() and not str(child).startswith('.')
        ]
        
        # 按修改时间排序
        file_path_list.sort(key=os.path.getmtime, reverse=True)
        
        # 删除超出数量的旧日志
        for old_file in file_path_list[max_files:]:
            try:
                old_file.unlink()
            except Exception as e:
                print(f"Failed to delete old log file {old_file}: {e}")
    except Exception as e:
        print(f"Failed to clean old logs: {e}")
        traceback.print_exc()

def get_logger(app_env: str = LoggerConfig.DEBUG):
    """获取配置好的日志记录器"""
    try:
        # 设置日志级别
        level_config = {
            LoggerConfig.DEBUG: logging.DEBUG,
            LoggerConfig.RELEASE: logging.INFO,
            LoggerConfig.TEST: logging.WARNING
        }
        level = level_config.get(app_env, logging.DEBUG)
        
        # 创建日志记录器
        logger = logging.getLogger('sniper')
        logger.setLevel(level)
        
        # 防止重复添加handler
        if logger.handlers:
            return logger
            
        # 控制台日志处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console_handler)
        
        # 文件日志处理器
        log_dir_path = PathTools.app_temp_log_file_dir()
        log_file_path = setup_file_handler(logger, log_dir_path, level)
        if log_file_path:
            PathTools._log_file_path = str(log_file_path)
        
        return logger
    except Exception as e:
        print(f"Failed to initialize logger: {e}")
        traceback.print_exc()
        return logging.getLogger('sniper_fallback')

# 初始化全局日志记录器
logger = get_logger()