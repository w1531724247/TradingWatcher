# 
import os
import threading
import time
import traceback
from tw_api.utils.logger_tools import logger
from tw_api.const import is_Windows, is_MacOS, is_Linux
import pygame

class AudioTools:
    # 添加类变量记录上次播放时间
    _last_play_time = 0
    _min_interval = 3.0  # 最小播放间隔(秒)
    _lock = threading.Lock()  # 添加锁以确保线程安全

    @classmethod
    def play_audio(cls, file_path: str):
        """
        非阻塞方式播放音频文件，确保三秒内只调用一次
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"音频文件不存在: {file_path}")
                return False
            
            # 使用锁确保线程安全
            with cls._lock:
                current_time = time.time()
                # 检查是否在最小间隔时间内
                if current_time - cls._last_play_time < cls._min_interval:
                    logger.info(f"音频播放被限制，距离上次播放仅过去 {current_time - cls._last_play_time:.2f} 秒")
                    return False
                
                # 更新最后播放时间
                cls._last_play_time = current_time
            
            # 在新线程中播放音频
            thread = threading.Thread(target=cls._play_audio_thread, args=(file_path,))
            thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
            thread.start()
            return True
        except Exception as e:
            logger.error(f"播放音频时出错: {e}")
            logger.error(traceback.format_exc())
            return False
    
    @classmethod
    def _play_audio_thread(cls, file_path: str):
        """
        在线程中播放音频的实际实现
        """
        try:
            # 实际的音频文件路径
            audio_file = file_path.replace('.wav', '.mp3')
    
            # 初始化pygame
            pygame.mixer.init()

            # 加载音频文件
            sound = pygame.mixer.Sound(audio_file)

            # 播放音频
            sound.play()

            # 等待音频播放完成
            while pygame.mixer.get_busy():
                pygame.time.Clock().tick(10)
                
        except ImportError:
            logger.error("simpleaudio 模块导入失败，尝试使用备用方法")
            cls._play_audio_fallback(file_path)
        except Exception as e:
            logger.error(f"音频线程中出错: {e}")
            logger.error(traceback.format_exc())
    
    @classmethod
    def _play_audio_fallback(cls, file_path: str):
        """
        备用的音频播放方法，使用系统命令
        """
        try:
            if is_Windows:
                import winsound
                winsound.PlaySound(file_path, winsound.SND_FILENAME)
            elif is_MacOS:
                os.system(f"afplay {file_path}")
            elif is_Linux:
                os.system(f"aplay {file_path}")
            else:
                logger.error("未知操作系统，无法播放音频")
        except Exception as e:
            logger.error(f"备用音频播放方法失败: {e}")
            logger.error(traceback.format_exc())