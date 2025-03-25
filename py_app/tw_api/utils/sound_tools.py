# 
import os
import simpleaudio as sa

class AudioTools:

    @classmethod
    def play_audio(cls, file_path: str):
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # 等待音频播放完毕