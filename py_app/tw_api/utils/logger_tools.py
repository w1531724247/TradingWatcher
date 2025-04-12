import os
import logging
import time
from concurrent_log_handler import ConcurrentRotatingFileHandler
import pathlib
from pathlib import Path
from .path_tools import PathTools
import traceback
import sys

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
        print(f"日志文件路径: {log_file_path}")
        # 创建日志目录（如果不存在）
        try:
            os.makedirs(log_dir_path, exist_ok=True)
            # 测试目录是否可写
            test_file = os.path.join(log_dir_path, '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception as e:
            print(f"无法创建或写入日志目录 {log_dir_path}: {e}")
            # 尝试使用临时目录
            log_dir_path = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 'sniper_logs')
            os.makedirs(log_dir_path, exist_ok=True)
            log_file_path = os.path.join(log_dir_path, log_file_name)
            print(f"改用临时日志目录: {log_dir_path}")
        
        # 设置文件日志处理器
        file_handler = ConcurrentRotatingFileHandler(
            log_file_path,
            mode='a',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=30,  # 保留30个备份
            encoding='utf-8',
            delay=True  # 延迟打开文件，避免启动时文件锁问题
        )
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
        
        # 清理旧日志文件
        clean_old_logs(log_dir_path, max_files=30)
        
        return log_file_path
    except Exception as e:
        print(f"设置文件处理器失败: {e}")
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
                print(f"删除旧日志文件失败 {old_file}: {e}")
    except Exception as e:
        print(f"清理旧日志失败: {e}")
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
            for handler in logger.handlers:
                # 检查是否需要更新级别
                handler.setLevel(level)
            return logger
            
        # 控制台日志处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console_handler)
        
        # 文件日志处理器
        try:
            log_dir_path = PathTools.app_temp_log_file_dir()
        except Exception as e:
            # 如果获取应用日志目录失败，使用备用目录
            print(f"获取应用日志目录失败: {e}")
            log_dir_path = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 'sniper_logs')
            
        log_file_path = setup_file_handler(logger, log_dir_path, level)
        if log_file_path:
            try:
                PathTools._log_file_path = str(log_file_path)
            except:
                pass
        
        # 确保异常被记录
        sys.excepthook = lambda *args: logger.error('未捕获的异常', exc_info=args)
        
        return logger
    except Exception as e:
        print(f"初始化日志记录器失败: {e}")
        traceback.print_exc()
        # 创建一个基本的日志记录器作为后备
        fallback_logger = logging.getLogger('sniper_fallback')
        if not fallback_logger.handlers:
            fallback_logger.setLevel(logging.DEBUG)
            fallback_logger.addHandler(logging.StreamHandler())
        return fallback_logger

# 初始化全局日志记录器
try:
    logger = get_logger()
    # 验证日志记录器是否正常工作
    logger.debug("日志系统初始化成功")
except Exception as e:
    print(f"初始化日志系统失败: {e}")
    # 创建一个简单的控制台日志记录器
    logger = logging.getLogger('sniper_emergency')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    logger.error(f"日志系统初始化失败: {e}", exc_info=True)